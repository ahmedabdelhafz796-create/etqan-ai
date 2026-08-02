"""Learning Engine (Tier 2) — Extract patterns and learnings from trade outcomes."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json

from src.gold_agent.learning.trade_analyzer import TradeAnalyzer, TradeStatistics


class LearningSignal:
    """A learning insight extracted from trade data."""

    def __init__(
        self,
        signal_type: str,  # "confidence_calibration", "indicator_improvement", "risk_management", etc.
        severity: str,  # "critical", "high", "medium", "low"
        recommendation: str,
        supporting_data: Dict,
        confidence_in_signal: float,  # 0-100%
    ):
        self.signal_type = signal_type
        self.severity = severity
        self.recommendation = recommendation
        self.supporting_data = supporting_data
        self.confidence_in_signal = confidence_in_signal
        self.created_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "signal_type": self.signal_type,
            "severity": self.severity,
            "recommendation": self.recommendation,
            "supporting_data": self.supporting_data,
            "confidence": self.confidence_in_signal,
            "created_at": self.created_at.isoformat(),
        }


class LearningEngine:
    """
    Tier 2: Learning & Memory.

    Extracts patterns from closed trades and recommends improvements.
    """

    def __init__(self, config, audit_log):
        self.config = config
        self.audit_log = audit_log
        self.analyzer = TradeAnalyzer(config)
        self.learning_history: List[LearningSignal] = []
        self.last_learning_run = None

    async def analyze_and_learn(
        self,
        lookback_days: int = 30,
    ) -> Tuple[List[LearningSignal], TradeStatistics]:
        """
        Analyze recent trades and extract learnings.

        Args:
            lookback_days: How far back to analyze

        Returns:
            Tuple of (learning signals, overall statistics)
        """
        # Get recent closed trades
        closed_trades = await self.audit_log.get_closed_trades_today()

        if not closed_trades:
            print("No closed trades found for analysis")
            return [], TradeStatistics(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                average_win=0.0,
                average_loss=0.0,
                profit_factor=0.0,
                total_pnl=0.0,
                largest_win=0.0,
                largest_loss=0.0,
                average_duration_minutes=0.0,
            )

        signals = []
        stats = self.analyzer.analyze_trades(closed_trades)

        # Analyze confidence calibration
        confidence_signals = self._analyze_confidence_calibration(closed_trades, stats)
        signals.extend(confidence_signals)

        # Analyze indicator effectiveness
        indicator_signals = self._analyze_indicator_performance(closed_trades, stats)
        signals.extend(indicator_signals)

        # Analyze risk management
        risk_signals = self._analyze_risk_management(stats)
        signals.extend(risk_signals)

        # Analyze time-based patterns
        time_signals = self._analyze_time_patterns(closed_trades)
        signals.extend(time_signals)

        # Analyze trade duration patterns
        duration_signals = self._analyze_duration_patterns(closed_trades, stats)
        signals.extend(duration_signals)

        # Store signals
        self.learning_history.extend(signals)
        self.last_learning_run = datetime.utcnow()

        # Log to audit
        await self.audit_log.log_error(f"Learning analysis complete: {len(signals)} signals extracted")

        return signals, stats

    def _analyze_confidence_calibration(
        self,
        trades: List[Dict],
        stats: TradeStatistics,
    ) -> List[LearningSignal]:
        """
        Check if decision confidence correlates with actual profitability.

        If it doesn't, our confidence calculation needs recalibration.
        """
        signals = []

        correlation = self.analyzer.find_correlation_with_confidence(trades)

        if correlation < 0.3:
            signals.append(LearningSignal(
                signal_type="confidence_calibration",
                severity="high",
                recommendation="Confidence scores are not predictive of outcomes. Recalibrate scoring weights or LLM prompts.",
                supporting_data={
                    "correlation": correlation,
                    "trades_analyzed": len(trades),
                },
                confidence_in_signal=80.0,
            ))
        elif correlation < 0.5:
            signals.append(LearningSignal(
                signal_type="confidence_calibration",
                severity="medium",
                recommendation="Confidence calibration could be improved. Consider adjusting indicator weights.",
                supporting_data={
                    "correlation": correlation,
                    "trades_analyzed": len(trades),
                },
                confidence_in_signal=70.0,
            ))

        return signals

    def _analyze_indicator_performance(
        self,
        trades: List[Dict],
        stats: TradeStatistics,
    ) -> List[LearningSignal]:
        """
        Analyze which indicators/signals are most predictive.
        """
        signals = []

        # Analyze by signal type (if available in trade data)
        performance = self.analyzer.analyze_by_signal_type(trades)

        # Find underperforming signals
        for signal_type, perf in performance.items():
            if perf.win_rate < 45:
                signals.append(LearningSignal(
                    signal_type="indicator_quality",
                    severity="medium",
                    recommendation=f"Signal '{signal_type}' has low win rate ({perf.win_rate:.1f}%). Consider reducing weight or removing.",
                    supporting_data={
                        "signal_type": signal_type,
                        "win_rate": perf.win_rate,
                        "total_trades": perf.total_signals,
                        "profit_factor": perf.average_pnl / perf.average_loss if perf.average_loss > 0 else 0,
                    },
                    confidence_in_signal=75.0,
                ))

        return signals

    def _analyze_risk_management(self, stats: TradeStatistics) -> List[LearningSignal]:
        """
        Check if risk management parameters need adjustment.
        """
        signals = []

        # Check max drawdown
        if stats.max_drawdown < -50000:  # $50k loss
            signals.append(LearningSignal(
                signal_type="risk_management",
                severity="critical",
                recommendation="Maximum drawdown is excessive. Reduce position size or increase stop loss width.",
                supporting_data={
                    "max_drawdown": stats.max_drawdown,
                    "recovery_factor": stats.recovery_factor,
                },
                confidence_in_signal=90.0,
            ))

        # Check risk/reward ratio
        if stats.profit_factor < 1.2:
            signals.append(LearningSignal(
                signal_type="risk_management",
                severity="high",
                recommendation="Profit factor is low. Increase take profit levels or tighten stop losses.",
                supporting_data={
                    "profit_factor": stats.profit_factor,
                    "avg_win": stats.average_win,
                    "avg_loss": stats.average_loss,
                },
                confidence_in_signal=85.0,
            ))

        # Check win rate
        if stats.win_rate < 40:
            signals.append(LearningSignal(
                signal_type="signal_quality",
                severity="high",
                recommendation="Win rate is below 40%. Signal generation needs significant improvement.",
                supporting_data={
                    "win_rate": stats.win_rate,
                    "total_trades": stats.total_trades,
                    "winning": stats.winning_trades,
                },
                confidence_in_signal=85.0,
            ))

        return signals

    def _analyze_time_patterns(self, trades: List[Dict]) -> List[LearningSignal]:
        """
        Identify time-based patterns (best trading hours, days, etc.).
        """
        signals = []

        # Analyze by hour of day
        hourly_stats = self.analyzer.analyze_time_performance(trades, "hour")

        # Find best and worst hours
        if hourly_stats:
            best_hour = max(hourly_stats.items(), key=lambda x: x[1].win_rate)
            worst_hour = min(hourly_stats.items(), key=lambda x: x[1].win_rate)

            if best_hour[1].win_rate > worst_hour[1].win_rate + 20:  # 20% difference
                signals.append(LearningSignal(
                    signal_type="time_pattern",
                    severity="medium",
                    recommendation=f"Hour {best_hour[0]} has {best_hour[1].win_rate:.1f}% win rate vs {worst_hour[0]} at {worst_hour[1].win_rate:.1f}%. Consider trading selectively by time.",
                    supporting_data={
                        "best_hour": best_hour[0],
                        "best_wr": best_hour[1].win_rate,
                        "worst_hour": worst_hour[0],
                        "worst_wr": worst_hour[1].win_rate,
                    },
                    confidence_in_signal=60.0,
                ))

        return signals

    def _analyze_duration_patterns(
        self,
        trades: List[Dict],
        stats: TradeStatistics,
    ) -> List[LearningSignal]:
        """
        Analyze if trade holding time affects profitability.
        """
        signals = []

        if stats.average_duration_minutes < 15:
            signals.append(LearningSignal(
                signal_type="trade_duration",
                severity="medium",
                recommendation="Average holding time is very short (<15 min). Trades may be overfit to noise. Use wider stops.",
                supporting_data={
                    "avg_duration": stats.average_duration_minutes,
                },
                confidence_in_signal=65.0,
            ))

        return signals

    def get_high_priority_learnings(self) -> List[LearningSignal]:
        """Get all high or critical severity signals."""
        return [
            s for s in self.learning_history
            if s.severity in ["critical", "high"]
        ]

    def get_recent_learnings(self, hours: int = 24) -> List[LearningSignal]:
        """Get learnings from the last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            s for s in self.learning_history
            if s.created_at >= cutoff_time
        ]

    def get_learning_summary(self) -> Dict:
        """Get summary of all learnings."""
        if not self.learning_history:
            return {
                "total_signals": 0,
                "by_severity": {},
                "by_type": {},
                "last_run": None,
            }

        severity_counts = {}
        type_counts = {}

        for signal in self.learning_history:
            severity_counts[signal.severity] = severity_counts.get(signal.severity, 0) + 1
            type_counts[signal.signal_type] = type_counts.get(signal.signal_type, 0) + 1

        return {
            "total_signals": len(self.learning_history),
            "by_severity": severity_counts,
            "by_type": type_counts,
            "critical_signals": len([s for s in self.learning_history if s.severity == "critical"]),
            "high_signals": len([s for s in self.learning_history if s.severity == "high"]),
            "last_run": self.last_learning_run.isoformat() if self.last_learning_run else None,
        }

    def export_learnings(self, filepath: str) -> bool:
        """Export all learnings to a JSON file."""
        try:
            learnings_data = {
                "export_time": datetime.utcnow().isoformat(),
                "total_signals": len(self.learning_history),
                "signals": [s.to_dict() for s in self.learning_history],
                "summary": self.get_learning_summary(),
            }

            with open(filepath, "w") as f:
                json.dump(learnings_data, f, indent=2)

            return True
        except Exception as e:
            print(f"Failed to export learnings: {e}")
            return False

    def get_status(self) -> dict:
        """Get learning engine status."""
        return {
            "total_signals": len(self.learning_history),
            "high_priority": len(self.get_high_priority_learnings()),
            "recent_signals": len(self.get_recent_learnings(24)),
            "last_run": self.last_learning_run.isoformat() if self.last_learning_run else None,
            "summary": self.get_learning_summary(),
        }
