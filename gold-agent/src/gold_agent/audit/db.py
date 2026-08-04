"""Audit Log Database (§12-18 MASTER_PLAN) — SQLite, later PostgreSQL."""

import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

from gold_agent.core.models import Decision


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

    @abstractmethod
    async def log_order(self, order) -> bool:
        """Log an order execution."""
        pass

    @abstractmethod
    async def log_trade(self, trade) -> bool:
        """Log a trade."""
        pass

    @abstractmethod
    async def update_trade(self, trade_id: str, updates: dict) -> bool:
        """Update a trade record."""
        pass

    @abstractmethod
    async def log_position(self, position) -> bool:
        """Log a position."""
        pass

    @abstractmethod
    async def log_portfolio_metrics(self, metrics) -> bool:
        """Log portfolio metrics."""
        pass

    @abstractmethod
    async def log_trade_outcome(self, trade_id: str, decision_id: int, outcome: dict) -> bool:
        """Log a trade outcome for learning purposes."""
        pass

    @abstractmethod
    async def get_trade(self, trade_id: str) -> Optional[dict]:
        """Get a trade by ID."""
        pass

    @abstractmethod
    async def get_open_trades(self, symbol: Optional[str] = None) -> List[dict]:
        """Get all open trades, optionally filtered by symbol."""
        pass

    @abstractmethod
    async def get_closed_trades_today(self) -> List[dict]:
        """Get all closed trades today."""
        pass

    @abstractmethod
    async def get_portfolio_performance(self) -> dict:
        """Get portfolio performance metrics."""
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

        # Tier 1: Trade History Store
        # Orders table - track all order executions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                order_type TEXT NOT NULL,
                price REAL,
                stop_price REAL,
                status TEXT NOT NULL,
                filled_quantity REAL DEFAULT 0.0,
                average_fill_price REAL,
                rejection_reason TEXT,
                broker_order_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Trades table - track individual opened trades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                decision_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                quantity REAL NOT NULL,
                entry_timestamp TEXT NOT NULL,
                entry_order_id TEXT NOT NULL,
                current_price REAL,
                current_p_l REAL,
                current_p_l_percent REAL,
                stop_loss REAL,
                take_profit REAL,
                risk_reward_ratio REAL,
                exit_price REAL,
                exit_timestamp TEXT,
                exit_reason TEXT,
                exit_order_id TEXT,
                final_p_l REAL,
                final_p_l_percent REAL,
                state TEXT DEFAULT 'open',
                duration_minutes REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(decision_id) REFERENCES decisions(id),
                FOREIGN KEY(entry_order_id) REFERENCES orders(order_id),
                FOREIGN KEY(exit_order_id) REFERENCES orders(order_id)
            )
        """)

        # Positions table - track current open positions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL NOT NULL,
                entry_timestamp TEXT NOT NULL,
                unrealized_p_l REAL,
                unrealized_p_l_percent REAL,
                stop_loss REAL,
                take_profit REAL,
                trade_ids TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Portfolio metrics table - track portfolio performance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_value REAL NOT NULL,
                cash_balance REAL NOT NULL,
                positions_value REAL NOT NULL,
                unrealized_p_l REAL,
                realized_p_l_today REAL,
                max_drawdown_percent REAL,
                num_open_positions INTEGER,
                num_winning_trades_today INTEGER,
                num_losing_trades_today INTEGER,
                win_rate REAL,
                average_win REAL,
                average_loss REAL,
                risk_reward_ratio REAL,
                sharpe_ratio REAL,
                max_leverage_used REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Trade outcomes table - for learning purposes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT NOT NULL,
                decision_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                quantity REAL NOT NULL,
                duration_minutes REAL,
                profit_loss REAL,
                profit_loss_percent REAL,
                exit_reason TEXT,
                entry_indicators_json TEXT,
                entry_score_json TEXT,
                entry_macro_signal_json TEXT,
                entry_correlation_signal_json TEXT,
                confidence REAL,
                was_correct BOOLEAN,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(trade_id) REFERENCES trades(trade_id),
                FOREIGN KEY(decision_id) REFERENCES decisions(id)
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

    async def log_order(self, order) -> bool:
        """Log an order execution."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO orders
                (order_id, timestamp, symbol, side, quantity, order_type, price, stop_price,
                 status, filled_quantity, average_fill_price, rejection_reason, broker_order_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order.order_id,
                order.timestamp.isoformat(),
                order.symbol,
                order.side.value,
                order.quantity,
                order.order_type.value,
                order.price,
                order.stop_price,
                order.status.value,
                order.filled_quantity,
                order.average_fill_price,
                order.rejection_reason,
                order.broker_order_id,
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error logging order: {e}")
            return False

    async def log_trade(self, trade) -> bool:
        """Log a trade."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO trades
                (trade_id, decision_id, symbol, side, entry_price, quantity, entry_timestamp,
                 entry_order_id, current_price, current_p_l, current_p_l_percent, stop_loss,
                 take_profit, risk_reward_ratio, state)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.trade_id,
                trade.entry_decision_id,
                trade.symbol,
                trade.side.value,
                trade.entry_price,
                trade.quantity,
                trade.entry_timestamp.isoformat(),
                trade.entry_order_id,
                trade.current_price,
                trade.current_p_l,
                trade.current_p_l_percent,
                trade.stop_loss,
                trade.take_profit,
                trade.risk_reward_ratio,
                trade.state,
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error logging trade: {e}")
            return False

    async def update_trade(self, trade_id: str, updates: dict) -> bool:
        """Update a trade record."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [trade_id]

            cursor.execute(f"""
                UPDATE trades SET {set_clause} WHERE trade_id = ?
            """, values)

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error updating trade: {e}")
            return False

    async def log_position(self, position) -> bool:
        """Log a position."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            trade_ids = ",".join(position.trade_ids) if position.trade_ids else ""

            cursor.execute("""
                INSERT OR REPLACE INTO positions
                (symbol, side, quantity, entry_price, current_price, entry_timestamp,
                 unrealized_p_l, unrealized_p_l_percent, stop_loss, take_profit, trade_ids)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                position.symbol,
                position.side.value,
                position.quantity,
                position.entry_price,
                position.current_price,
                position.entry_timestamp.isoformat(),
                position.unrealized_p_l,
                position.unrealized_p_l_percent,
                position.stop_loss,
                position.take_profit,
                trade_ids,
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error logging position: {e}")
            return False

    async def log_portfolio_metrics(self, metrics) -> bool:
        """Log portfolio metrics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO portfolio_metrics
                (timestamp, total_value, cash_balance, positions_value, unrealized_p_l,
                 realized_p_l_today, max_drawdown_percent, num_open_positions,
                 num_winning_trades_today, num_losing_trades_today, win_rate,
                 average_win, average_loss, risk_reward_ratio, sharpe_ratio, max_leverage_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp.isoformat(),
                metrics.total_value,
                metrics.cash_balance,
                metrics.positions_value,
                metrics.unrealized_p_l,
                metrics.realized_p_l_today,
                metrics.max_drawdown_percent,
                metrics.num_open_positions,
                metrics.num_winning_trades_today,
                metrics.num_losing_trades_today,
                metrics.win_rate,
                metrics.average_win,
                metrics.average_loss,
                metrics.risk_reward_ratio,
                metrics.sharpe_ratio,
                metrics.max_leverage_used,
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error logging portfolio metrics: {e}")
            return False

    async def log_trade_outcome(self, trade_id: str, decision_id: int, outcome: dict) -> bool:
        """Log a trade outcome for learning purposes."""
        try:
            import json

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO trade_outcomes
                (trade_id, decision_id, symbol, side, entry_price, exit_price, quantity,
                 duration_minutes, profit_loss, profit_loss_percent, exit_reason,
                 entry_indicators_json, entry_score_json, entry_macro_signal_json,
                 entry_correlation_signal_json, confidence, was_correct)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade_id,
                decision_id,
                outcome.get("symbol"),
                outcome.get("side"),
                outcome.get("entry_price"),
                outcome.get("exit_price"),
                outcome.get("quantity"),
                outcome.get("duration_minutes"),
                outcome.get("profit_loss"),
                outcome.get("profit_loss_percent"),
                outcome.get("exit_reason"),
                json.dumps(outcome.get("entry_indicators", {})),
                json.dumps(outcome.get("entry_score", {})),
                json.dumps(outcome.get("entry_macro_signal", {})),
                json.dumps(outcome.get("entry_correlation_signal", {})),
                outcome.get("confidence"),
                outcome.get("was_correct"),
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error logging trade outcome: {e}")
            return False

    async def get_trade(self, trade_id: str) -> Optional[dict]:
        """Get a trade by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM trades WHERE trade_id = ?", (trade_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        except Exception:
            return None

    async def get_open_trades(self, symbol: Optional[str] = None) -> List[dict]:
        """Get all open trades, optionally filtered by symbol."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if symbol:
                cursor.execute("SELECT * FROM trades WHERE state = 'open' AND symbol = ?", (symbol,))
            else:
                cursor.execute("SELECT * FROM trades WHERE state = 'open'")

            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return []

            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except Exception:
            return []

    async def get_closed_trades_today(self) -> List[dict]:
        """Get all closed trades today."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            today = datetime.utcnow().date()
            cursor.execute(
                "SELECT * FROM trades WHERE state = 'closed' AND DATE(exit_timestamp) = ?",
                (today.isoformat(),)
            )

            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return []

            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except Exception:
            return []

    async def get_portfolio_performance(self) -> dict:
        """Get portfolio performance metrics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT total_value, unrealized_p_l, realized_p_l_today, max_drawdown_percent,
                       win_rate, average_win, average_loss, sharpe_ratio
                FROM portfolio_metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """)

            row = cursor.fetchone()
            conn.close()

            if not row:
                return {}

            return {
                "total_value": row[0],
                "unrealized_p_l": row[1],
                "realized_p_l_today": row[2],
                "max_drawdown_percent": row[3],
                "win_rate": row[4],
                "average_win": row[5],
                "average_loss": row[6],
                "sharpe_ratio": row[7],
            }
        except Exception:
            return {}


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
        """Log a trading decision (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        Returns False for now (PostgreSQL not yet configured).
        """
        logger.info(f"PostgreSQL log_decision stub: would log decision {decision.id} to PostgreSQL")
        return False  # Phase 3+ implementation

    async def log_sharia_decision(self, decision: Decision) -> bool:
        """Log a Sharia compliance decision (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        """
        logger.info(f"PostgreSQL log_sharia_decision stub: would log Sharia decision to PostgreSQL")
        return False  # Phase 3+ implementation

    async def log_error(self, error_msg: str) -> bool:
        """Log an error (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        """
        logger.info(f"PostgreSQL log_error stub: would log error to PostgreSQL: {error_msg}")
        return False  # Phase 3+ implementation

    async def count_errors_last_hour(self) -> int:
        """Count errors in last hour (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        Returns 0 for now.
        """
        logger.info("PostgreSQL count_errors_last_hour stub: returns 0 (PostgreSQL not yet configured)")
        return 0  # Phase 3+ implementation

    async def count_alerts_today(self) -> int:
        """Count alerts today (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        Returns 0 for now.
        """
        logger.info("PostgreSQL count_alerts_today stub: returns 0 (PostgreSQL not yet configured)")
        return 0  # Phase 3+ implementation

    async def log_order(self, order) -> bool:
        """Log an order (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        """
        logger.info(f"PostgreSQL log_order stub: would log order {order.id if hasattr(order, 'id') else order}")
        return False  # Phase 3+ implementation

    async def log_trade(self, trade) -> bool:
        """Log a trade (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        """
        logger.info(f"PostgreSQL log_trade stub: would log trade to PostgreSQL")
        return False  # Phase 3+ implementation

    async def update_trade(self, trade_id: str, updates: dict) -> bool:
        """Update a trade record (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        """
        logger.info(f"PostgreSQL update_trade stub: would update trade {trade_id} with {updates}")
        return False  # Phase 3+ implementation

    async def log_position(self, position) -> bool:
        """Log a position (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        """
        logger.info(f"PostgreSQL log_position stub: would log position to PostgreSQL")
        return False  # Phase 3+ implementation

    async def log_portfolio_metrics(self, metrics) -> bool:
        """Log portfolio metrics (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        """
        logger.info(f"PostgreSQL log_portfolio_metrics stub: would log metrics to PostgreSQL")
        return False  # Phase 3+ implementation

    async def log_trade_outcome(self, trade_id: str, decision_id: int, outcome: dict) -> bool:
        """Log trade outcome and P&L (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        """
        logger.info(f"PostgreSQL log_trade_outcome stub: would log outcome for trade {trade_id}")
        return False  # Phase 3+ implementation

    async def get_trade(self, trade_id: str) -> Optional[dict]:
        """Retrieve a trade by ID (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        Returns None for now.
        """
        logger.info(f"PostgreSQL get_trade stub: would retrieve trade {trade_id} from PostgreSQL")
        return None  # Phase 3+ implementation

    async def get_open_trades(self, symbol: Optional[str] = None) -> List[dict]:
        """Get all open trades (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        Returns empty list for now.
        """
        logger.info(f"PostgreSQL get_open_trades stub: would query PostgreSQL for open trades")
        return []  # Phase 3+ implementation

    async def get_closed_trades_today(self) -> List[dict]:
        """Get closed trades today (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        Returns empty list for now.
        """
        logger.info("PostgreSQL get_closed_trades_today stub: would query PostgreSQL")
        return []  # Phase 3+ implementation

    async def get_portfolio_performance(self) -> dict:
        """Get portfolio performance metrics (PostgreSQL implementation).

        NOTE: Phase 1 uses SQLite. PostgreSQL is Phase 3+ enhancement.
        Returns empty dict for now.
        """
        logger.info("PostgreSQL get_portfolio_performance stub: would query PostgreSQL")
        return {}  # Phase 3+ implementation


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
