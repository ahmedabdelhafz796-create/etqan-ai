"""Performance Monitor (Tier 5) — Monitor system performance and alert on issues."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class PerformanceAlert:
    """Performance alert/issue detected."""
    timestamp: datetime
    alert_type: str  # "win_rate", "drawdown", "sharpe_ratio", "profit_factor", "consistency"
    severity: str  # "info", "warning", "critical"
    message: str
    metric_value: float
    threshold: float
    recommended_action: str


@dataclass
class PerformanceMetrics:
    """Current performance snapshot."""
    timestamp: datetime
    trades_today: int
    win_rate: float
    avg_pnl: float
    daily_pnl: float
    sharpe_ratio: float
    profit_factor: float
    consistency_score: float  # How consistent are wins/losses


class PerformanceMonitor:
    """
    Tier 5: Self-Management - Performance Monitoring.

    Monitors trading performance and alerts on issues.
    """

    def __init__(self, config):
        self.config = config
        self.alert_history: List[PerformanceAlert] = []
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history = 100

        # Alert thresholds
        self.thresholds = {
            "min_win_rate": 0.40,
            "max_drawdown_alert": 5000,  # $5k
            "min_sharpe_ratio": 0.5,
            "min_profit_factor": 1.2,
            "max_consecutive_losses": 5,
        }

    def analyze_performance(
        self,
        trades_today: List[Dict],
        recent_trades: List[Dict],
        daily_pnl: float,
        current_drawdown: float,
    ) -> List[PerformanceAlert]:
        """
        Analyze performance and generate alerts.

        Args:
            trades_today: Trades closed today
            recent_trades: Last 20-50 trades
            daily_pnl: Today's P&L
            current_drawdown: Current drawdown amount

        Returns:
            List of PerformanceAlert for any issues detected
        """
        alerts = []

        if not recent_trades:
            return alerts

        # Analyze win rate
        win_rate = sum(1 for t in recent_trades if t.get("final_p_l", 0) > 0) / len(recent_trades)
        if win_rate < self.thresholds["min_win_rate"]:
            alerts.append(PerformanceAlert(
                timestamp=datetime.utcnow(),
                alert_type="win_rate",
                severity="warning" if win_rate > 0.30 else "critical",
                message=f"Win rate is {win_rate*100:.1f}%, below threshold of {self.thresholds['min_win_rate']*100:.1f}%",
                metric_value=win_rate * 100,
                threshold=self.thresholds["min_win_rate"] * 100,
                recommended_action="Review trading rules and increase confidence threshold",
            ))

        # Analyze drawdown
        if current_drawdown > self.thresholds["max_drawdown_alert"]:
            alerts.append(PerformanceAlert(
                timestamp=datetime.utcnow(),
                alert_type="drawdown",
                severity="critical" if current_drawdown > 7500 else "warning",
                message=f"Drawdown is ${current_drawdown:,.0f}, exceeds threshold of ${self.thresholds['max_drawdown_alert']:,.0f}",
                metric_value=current_drawdown,
                threshold=self.thresholds["max_drawdown_alert"],
                recommended_action="Reduce position size and tighten stop losses",
            ))

        # Analyze Sharpe ratio
        avg_pnl = sum(t.get("final_p_l", 0) for t in recent_trades) / len(recent_trades)
        if len(recent_trades) > 1:
            import statistics
            pnls = [t.get("final_p_l", 0) for t in recent_trades]
            stdev = statistics.stdev(pnls) if len(pnls) > 1 else 1.0
            sharpe_ratio = (avg_pnl / stdev) if stdev > 0 else 0.0

            if sharpe_ratio < self.thresholds["min_sharpe_ratio"]:
                alerts.append(PerformanceAlert(
                    timestamp=datetime.utcnow(),
                    alert_type="sharpe_ratio",
                    severity="warning",
                    message=f"Sharpe ratio is {sharpe_ratio:.2f}, below threshold of {self.thresholds['min_sharpe_ratio']:.2f}",
                    metric_value=sharpe_ratio,
                    threshold=self.thresholds["min_sharpe_ratio"],
                    recommended_action="Increase position size when confidence is very high",
                ))

        # Analyze profit factor
        winning_trades = [t for t in recent_trades if t.get("final_p_l", 0) > 0]
        losing_trades = [t for t in recent_trades if t.get("final_p_l", 0) < 0]
        gross_profit = sum(t.get("final_p_l", 0) for t in winning_trades)
        gross_loss = abs(sum(t.get("final_p_l", 0) for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit / 1

        if profit_factor < self.thresholds["min_profit_factor"]:
            alerts.append(PerformanceAlert(
                timestamp=datetime.utcnow(),
                alert_type="profit_factor",
                severity="warning",
                message=f"Profit factor is {profit_factor:.2f}, below threshold of {self.thresholds['min_profit_factor']:.2f}",
                metric_value=profit_factor,
                threshold=self.thresholds["min_profit_factor"],
                recommended_action="Improve position entry timing or exit strategy",
            ))

        # Analyze consecutive losses
        consecutive_losses = 0
        max_consecutive = 0
        for trade in reversed(recent_trades):
            if trade.get("final_p_l", 0) < 0:
                consecutive_losses += 1
                max_consecutive = max(max_consecutive, consecutive_losses)
            else:
                consecutive_losses = 0

        if max_consecutive > self.thresholds["max_consecutive_losses"]:
            alerts.append(PerformanceAlert(
                timestamp=datetime.utcnow(),
                alert_type="consistency",
                severity="warning",
                message=f"Detected {max_consecutive} consecutive losses",
                metric_value=max_consecutive,
                threshold=self.thresholds["max_consecutive_losses"],
                recommended_action="Take a break or review trading conditions",
            ))

        # Store alerts
        self.alert_history.extend(alerts)
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]

        return alerts

    def get_recent_alerts(self, alert_type: Optional[str] = None, severity: Optional[str] = None) -> List[PerformanceAlert]:
        """Get recent alerts, optionally filtered."""
        alerts = self.alert_history

        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts[-10:]  # Last 10

    def get_critical_alerts(self) -> List[PerformanceAlert]:
        """Get all critical alerts."""
        return [a for a in self.alert_history if a.severity == "critical"]

    def get_status(self) -> dict:
        """Get performance monitor status."""
        critical_alerts = self.get_critical_alerts()
        return {
            "total_alerts": len(self.alert_history),
            "critical_alerts": len(critical_alerts),
            "recent_alerts": [
                {
                    "type": a.alert_type,
                    "severity": a.severity,
                    "message": a.message,
                }
                for a in self.get_recent_alerts()[-5:]
            ],
        }
