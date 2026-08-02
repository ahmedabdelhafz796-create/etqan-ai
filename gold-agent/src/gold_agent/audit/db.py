"""Audit Log Database (§12-18 MASTER_PLAN) — SQLite, later PostgreSQL."""

import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

from src.gold_agent.core.models import Decision


class AuditLog(ABC):
    """Abstract audit log interface."""

    @abstractmethod
    async def log_decision(self, decision: Decision) -> bool:
        """Log a decision."""
        pass

    @abstractmethod
    async def log_sharia_decision(self, decision: Decision) -> bool:
        """Log to Sharia audit log."""
        pass

    @abstractmethod
    async def log_error(self, error_msg: str) -> bool:
        """Log an error."""
        pass

    @abstractmethod
    async def count_errors_last_hour(self) -> int:
        """Count errors in last hour."""
        pass

    @abstractmethod
    async def count_alerts_today(self) -> int:
        """Count alerts sent today."""
        pass


class SQLiteAuditLog(AuditLog):
    """SQLite-based audit log (Phase 1-2)."""

    def __init__(self, db_path: str = "data/gold_agent.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Decisions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                confidence REAL NOT NULL,
                reason TEXT,
                indicators_json TEXT,
                score_json TEXT,
                risk_gate_passed BOOLEAN,
                sharia_gate_passed BOOLEAN,
                llm_used BOOLEAN,
                state TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sharia audit log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sharia_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                school TEXT NOT NULL,
                passed BOOLEAN NOT NULL,
                violations TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Error log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # State changes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                from_state TEXT,
                to_state TEXT,
                trigger TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    async def log_decision(self, decision: Decision) -> bool:
        """Log a decision to database."""
        try:
            import json

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            indicators_json = json.dumps({
                "rsi": decision.indicators.rsi,
                "macd": decision.indicators.macd,
                "ma_short": decision.indicators.ma_short,
                "ma_long": decision.indicators.ma_long,
            })

            score_json = json.dumps({
                "rsi_score": decision.score.rsi_score,
                "macd_score": decision.score.macd_score,
                "ma_score": decision.score.ma_score,
                "combined_score": decision.score.combined_score,
            })

            cursor.execute("""
                INSERT INTO decisions
                (timestamp, action, confidence, reason, indicators_json, score_json,
                 risk_gate_passed, sharia_gate_passed, llm_used, state)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision.timestamp.isoformat(),
                decision.action.value,
                decision.confidence,
                decision.reason,
                indicators_json,
                score_json,
                decision.risk_gate_verdict.passed if decision.risk_gate_verdict else None,
                decision.sharia_gate_verdict.passed if decision.sharia_gate_verdict else None,
                decision.llm_brain_used,
                decision.state.value,
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False

    async def log_sharia_decision(self, decision: Decision) -> bool:
        """Log to Sharia audit log."""
        try:
            if not decision.sharia_gate_verdict:
                return False

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO sharia_audit
                (timestamp, action, school, passed, violations)
                VALUES (?, ?, ?, ?, ?)
            """, (
                decision.timestamp.isoformat(),
                decision.action.value,
                "hanafi",  # TODO: get from config
                decision.sharia_gate_verdict.passed,
                decision.sharia_gate_verdict.reason,
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False

    async def log_error(self, error_msg: str) -> bool:
        """Log an error."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO errors (timestamp, message)
                VALUES (?, ?)
            """, (datetime.utcnow().isoformat(), error_msg))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False

    async def count_errors_last_hour(self) -> int:
        """Count errors in last hour."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
            cursor.execute(
                "SELECT COUNT(*) FROM errors WHERE timestamp > ?",
                (one_hour_ago,)
            )

            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0

    async def count_alerts_today(self) -> int:
        """Count alerts sent today."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            today = datetime.utcnow().date()
            cursor.execute(
                "SELECT COUNT(*) FROM decisions WHERE DATE(timestamp) = ?",
                (today.isoformat(),)
            )

            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0


class PostgreSQLAuditLog(AuditLog):
    """PostgreSQL-based audit log (Phase 3+)."""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        # TODO: Initialize connection pool
        pass

    async def log_decision(self, decision: Decision) -> bool:
        # TODO: Implement
        pass

    async def log_sharia_decision(self, decision: Decision) -> bool:
        # TODO: Implement
        pass

    async def log_error(self, error_msg: str) -> bool:
        # TODO: Implement
        pass

    async def count_errors_last_hour(self) -> int:
        # TODO: Implement
        pass

    async def count_alerts_today(self) -> int:
        # TODO: Implement
        pass


def get_audit_log(config) -> AuditLog:
    """Factory function to get audit log."""
    if config.audit.database_type == "sqlite":
        return SQLiteAuditLog(config.audit.sqlite_path)
    elif config.audit.database_type == "postgresql":
        return PostgreSQLAuditLog(
            host=config.audit.postgresql.host,
            port=config.audit.postgresql.port,
            database=config.audit.postgresql.database,
            user=config.audit.postgresql.user,
            password=config.audit.postgresql.password,
        )
    else:
        raise ValueError(f"Unknown audit log type: {config.audit.database_type}")
