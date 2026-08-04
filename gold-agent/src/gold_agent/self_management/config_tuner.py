"""Configuration Tuner (Tier 5) — Automatically adjust parameters based on performance."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple


@dataclass
class ParameterAdjustment:
    """Record of a parameter adjustment."""
    timestamp: datetime
    parameter_name: str
    old_value: float
    new_value: float
    reason: str
    expected_impact: str  # "positive", "neutral", "negative"
    actual_impact: Optional[str] = None  # Set after observation


@dataclass
class TuningResult:
    """Result of parameter tuning analysis."""
    parameter_name: str
    current_value: float
    recommended_value: float
    confidence: float  # 0-100% confidence in recommendation
    reason: str
    expected_improvement: float  # % improvement expected


class ConfigurationTuner:
    """
    Tier 5: Self-Management - Automatic Parameter Tuning.

    Monitors trading performance and automatically adjusts configuration parameters
    to optimize results.
    """

    def __init__(self, config):
        self.config = config
        self.adjustment_history: List[ParameterAdjustment] = []
        self.performance_baseline = None
        self.last_tuning_time = None
        self.tuning_interval_hours = 24

    def analyze_and_recommend_tuning(
        self,
        recent_trades: List[Dict],
        recent_performance: Dict,
    ) -> List[TuningResult]:
        """
        Analyze recent performance and recommend parameter adjustments.

        Args:
            recent_trades: List of recent closed trades
            recent_performance: Dict with recent performance metrics

        Returns:
            List of TuningResult with recommended adjustments
        """
        if not recent_trades or len(recent_trades) < 10:
            return []

        recommendations = []

        # Analyze win rate and confidence
        win_rate = sum(1 for t in recent_trades if t.get("final_p_l", 0) > 0) / len(recent_trades)
        avg_confidence = sum(t.get("confidence", 50) for t in recent_trades) / len(recent_trades)

        # Recommendation 1: Adjust confidence threshold based on actual win rate
        if win_rate < 0.40:
            # Win rate is poor, increase confidence threshold to be more selective
            current_threshold = self.config.scoring.confidence_threshold_wait
            new_threshold = min(current_threshold + 5, 75)
            recommendations.append(TuningResult(
                parameter_name="confidence_threshold_wait",
                current_value=current_threshold,
                recommended_value=new_threshold,
                confidence=70.0,
                reason="Low win rate detected. Increasing threshold to be more selective.",
                expected_improvement=8.0,
            ))
        elif win_rate > 0.60:
            # Win rate is good, can lower threshold slightly
            current_threshold = self.config.scoring.confidence_threshold_wait
            new_threshold = max(current_threshold - 3, 40)
            recommendations.append(TuningResult(
                parameter_name="confidence_threshold_wait",
                current_value=current_threshold,
                recommended_value=new_threshold,
                confidence=60.0,
                reason="Good win rate. Lowering threshold to capture more opportunities.",
                expected_improvement=5.0,
            ))

        # Recommendation 2: Adjust position size based on drawdown
        max_drawdown = recent_performance.get("max_drawdown", 0)
        if max_drawdown > 5000:  # $5k drawdown
            current_position_size = self.config.execution.capital.max_position_size_percent
            new_position_size = max(current_position_size * 0.8, 1.0)  # Reduce by 20%, minimum 1%
            recommendations.append(TuningResult(
                parameter_name="max_position_size_percent",
                current_value=current_position_size,
                recommended_value=new_position_size,
                confidence=80.0,
                reason="Drawdown exceeds threshold. Reducing position size for risk control.",
                expected_improvement=15.0,
            ))

        # Recommendation 3: Adjust daily loss limit
        daily_losses = recent_performance.get("daily_losses_today", 0)
        if daily_losses > 3000:  # $3k daily loss
            current_limit = self.config.execution.capital.daily_loss_limit_percent
            new_limit = max(current_limit * 0.7, 1.0)  # Reduce by 30%, minimum 1%
            recommendations.append(TuningResult(
                parameter_name="daily_loss_limit_percent",
                current_value=current_limit,
                recommended_value=new_limit,
                confidence=75.0,
                reason="Daily losses exceed threshold. Tightening daily loss limit.",
                expected_improvement=20.0,
            ))

        # Recommendation 4: Adjust risk reward ratio expectations
        avg_pnl = sum(t.get("final_p_l", 0) for t in recent_trades) / len(recent_trades)
        if avg_pnl < 0:
            # On average losing money, might need to adjust strategy parameters
            # This is a signal to use more conservative settings
            recommendations.append(TuningResult(
                parameter_name="trading_mode",
                current_value=1.0,  # Normal mode
                recommended_value=0.8,  # Conservative mode
                confidence=65.0,
                reason="Average P&L is negative. Recommend switching to conservative mode.",
                expected_improvement=10.0,
            ))

        return recommendations

    def apply_tuning(
        self,
        parameter_name: str,
        new_value: float,
        reason: str,
    ) -> bool:
        """
        Apply a configuration adjustment.

        Args:
            parameter_name: Name of parameter to adjust
            new_value: New value for parameter
            reason: Reason for adjustment

        Returns:
            True if successful
        """
        try:
            # Get current value
            old_value = self._get_parameter_value(parameter_name)

            # Update configuration
            self._set_parameter_value(parameter_name, new_value)

            # Record adjustment
            adjustment = ParameterAdjustment(
                timestamp=datetime.utcnow(),
                parameter_name=parameter_name,
                old_value=old_value,
                new_value=new_value,
                reason=reason,
                expected_impact="unknown",
            )
            self.adjustment_history.append(adjustment)

            print(f"✓ Tuned {parameter_name}: {old_value} → {new_value}")
            return True
        except Exception as e:
            print(f"✗ Failed to tune {parameter_name}: {e}")
            return False

    def should_tune(self) -> bool:
        """Check if enough time has passed since last tuning."""
        if self.last_tuning_time is None:
            return True

        time_since_tuning = (datetime.utcnow() - self.last_tuning_time).total_seconds() / 3600
        return time_since_tuning >= self.tuning_interval_hours

    def get_adjustment_history(self, parameter_name: Optional[str] = None) -> List[ParameterAdjustment]:
        """Get adjustment history, optionally filtered by parameter."""
        if parameter_name:
            return [a for a in self.adjustment_history if a.parameter_name == parameter_name]
        return self.adjustment_history

    def _get_parameter_value(self, parameter_name: str) -> float:
        """Get current parameter value from config."""
        parts = parameter_name.split(".")
        obj = self.config
        for part in parts:
            obj = getattr(obj, part)
        return float(obj)

    def _set_parameter_value(self, parameter_name: str, value: float) -> None:
        """Set parameter value in config."""
        parts = parameter_name.split(".")
        obj = self.config
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], value)

    def get_status(self) -> dict:
        """Get configuration tuner status."""
        return {
            "total_adjustments": len(self.adjustment_history),
            "last_adjustment": self.adjustment_history[-1].timestamp.isoformat() if self.adjustment_history else None,
            "last_tuning": self.last_tuning_time.isoformat() if self.last_tuning_time else None,
            "tuning_interval_hours": self.tuning_interval_hours,
        }
