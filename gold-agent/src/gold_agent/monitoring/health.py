"""Monitoring (§12-18 MASTER_PLAN) — Data health + agent performance."""

from datetime import datetime
from typing import Dict, List, Optional

from gold_agent.core.models import HealthStatus, StateType


class Monitor:
    """System health monitoring and performance tracking."""

    def __init__(self, config):
        self.config = config
        self.health_checks: List[HealthStatus] = []
        self.performance_metrics: Dict = {
            "decisions_today": 0,
            "buys": 0,
            "sells": 0,
            "waits": 0,
            "risk_gate_blocks": 0,
            "sharia_gate_blocks": 0,
            "errors": 0,
        }
        self.last_check: Optional[HealthStatus] = None

    async def check_data_health(self, pipeline) -> HealthStatus:
        """Check data health and return status."""
        try:
            # Get health from pipeline
            health = await pipeline.check_health()

            if health:
                self.last_check = health
                self.health_checks.append(health)

                # Trim history to last 100
                if len(self.health_checks) > 100:
                    self.health_checks = self.health_checks[-100:]

            return health

        except Exception as e:
            print(f"Health check error: {e}")
            return None

    def record_decision(self, action: str, gate_block: Optional[str] = None):
        """Record a decision for metrics."""
        self.performance_metrics["decisions_today"] += 1

        if gate_block:
            if gate_block == "Risk Gate":
                self.performance_metrics["risk_gate_blocks"] += 1
            elif gate_block == "Sharia Gate":
                self.performance_metrics["sharia_gate_blocks"] += 1
        else:
            if action == "BUY":
                self.performance_metrics["buys"] += 1
            elif action == "SELL":
                self.performance_metrics["sells"] += 1
            elif action == "WAIT":
                self.performance_metrics["waits"] += 1

    def record_error(self):
        """Record an error."""
        self.performance_metrics["errors"] += 1

    def get_status(self) -> Dict:
        """Get current health status."""
        if self.last_check:
            state_value = (
                self.last_check.state.value
                if hasattr(self.last_check.state, "value")
                else str(self.last_check.state)
            )
            return {
                "timestamp": self.last_check.timestamp.isoformat(),
                "state": state_value,
                "data_quality": self.last_check.data_quality,
                "connection": self.last_check.connection_status,
                "last_data_age_minutes": self.last_check.last_data_age_minutes,
                "requires_intervention": self.last_check.requires_intervention,
                "reason": self.last_check.reason,
            }
        return {"status": "No health check yet"}

    def get_performance(self) -> Dict:
        """Get performance metrics."""
        return self.performance_metrics.copy()

    def should_escalate_to_safe_mode(self) -> bool:
        """Check if escalation to Safe Mode is needed."""
        if not self.last_check:
            return False

        return (
            self.last_check.data_quality < 0.95
            or self.last_check.connection_status != "healthy"
            or self.last_check.agent_errors_last_hour > 5
        )

    def should_escalate_to_emergency(self) -> bool:
        """Check if escalation to Emergency is needed."""
        if not self.last_check:
            return False

        return (
            self.last_check.connection_status == "down"
            or self.last_check.agent_errors_last_hour > 10
        )

    def generate_report(self) -> str:
        """Generate monitoring report."""
        health = self.get_status()
        perf = self.get_performance()

        report = f"""
=== GOLD AGENT HEALTH REPORT ===
Timestamp: {health.get('timestamp', 'N/A')}
State: {health.get('state', 'N/A')}
Data Quality: {health.get('data_quality', 'N/A'):.0%}
Connection: {health.get('connection', 'N/A')}
Last Data Age: {health.get('last_data_age_minutes', 'N/A'):.1f} minutes

=== PERFORMANCE (TODAY) ===
Decisions: {perf['decisions_today']}
  - BUY: {perf['buys']}
  - SELL: {perf['sells']}
  - WAIT: {perf['waits']}
Gate Blocks:
  - Risk Gate: {perf['risk_gate_blocks']}
  - Sharia Gate: {perf['sharia_gate_blocks']}
Errors: {perf['errors']}

Intervention Required: {health.get('requires_intervention', False)}
Reason: {health.get('reason', 'None')}
"""
        return report
