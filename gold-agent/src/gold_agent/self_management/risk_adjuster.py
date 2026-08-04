"""Risk Adjuster (Tier 5) — Dynamically adjust risk limits based on performance."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class RiskAdjustment:
    """Record of a risk limit adjustment."""
    timestamp: datetime
    parameter_name: str
    old_value: float
    new_value: float
    reason: str
    trigger_metric: str  # What triggered the adjustment


@dataclass
class RiskAnalysis:
    """Risk analysis for current trading state."""
    current_drawdown: float  # $
    drawdown_percent: float  # %
    max_position_size: float  # %
    daily_loss_limit: float  # %
    risk_level: str  # "low", "medium", "high", "critical"
    recommended_adjustments: Dict[str, float]  # parameter -> new_value


class RiskAdjuster:
    """
    Tier 5: Self-Management - Dynamic Risk Adjustment.

    Adjusts position size and loss limits based on current drawdown and performance.
    """

    def __init__(self, config):
        self.config = config
        self.adjustment_history: list[RiskAdjustment] = []
        self.last_adjustment_time: Optional[datetime] = None
        self.min_adjustment_interval_hours = 1
        self.risk_thresholds = {
            "low": {"max_drawdown": 2.5, "max_loss_daily": 2.0},
            "medium": {"max_drawdown": 5.0, "max_loss_daily": 3.0},
            "high": {"max_drawdown": 7.5, "max_loss_daily": 4.0},
            "critical": {"max_drawdown": 10.0, "max_loss_daily": 5.0},
        }

    def analyze_risk(
        self,
        current_capital: float,
        peak_capital: float,
        daily_losses: float,
        recent_trades: list[Dict],
    ) -> RiskAnalysis:
        """
        Analyze current risk state.

        Args:
            current_capital: Current account capital
            peak_capital: Peak capital reached
            daily_losses: Daily losses so far
            recent_trades: Recent closed trades

        Returns:
            RiskAnalysis with current risk metrics
        """
        # Calculate drawdown
        drawdown = peak_capital - current_capital
        drawdown_percent = (drawdown / peak_capital * 100) if peak_capital > 0 else 0

        # Calculate daily loss as percent
        daily_loss_percent = (daily_losses / peak_capital * 100) if peak_capital > 0 else 0

        # Determine risk level
        if drawdown_percent < 2.5 and daily_loss_percent < 2.0:
            risk_level = "low"
        elif drawdown_percent < 5.0 and daily_loss_percent < 3.0:
            risk_level = "medium"
        elif drawdown_percent < 7.5 and daily_loss_percent < 4.0:
            risk_level = "high"
        else:
            risk_level = "critical"

        # Get current risk limits
        current_position_size = self.config.execution.capital.max_position_size_percent
        current_daily_limit = self.config.execution.capital.daily_loss_limit_percent

        # Generate recommendations
        recommendations = {}

        if drawdown_percent > 5.0:
            # Drawdown is high, reduce position size
            recommendations["max_position_size_percent"] = max(current_position_size * 0.7, 0.5)

        if daily_loss_percent > 3.0:
            # Daily losses are high, tighten daily limit
            recommendations["daily_loss_limit_percent"] = max(current_daily_limit * 0.6, 1.0)

        if len(recent_trades) > 10:
            # Check win rate
            win_rate = sum(1 for t in recent_trades if t.get("final_p_l", 0) > 0) / len(recent_trades)
            if win_rate < 0.30:
                # Very low win rate, be more conservative
                recommendations["max_position_size_percent"] = min(recommendations.get("max_position_size_percent", current_position_size), current_position_size * 0.5)

        return RiskAnalysis(
            current_drawdown=drawdown,
            drawdown_percent=drawdown_percent,
            max_position_size=current_position_size,
            daily_loss_limit=current_daily_limit,
            risk_level=risk_level,
            recommended_adjustments=recommendations,
        )

    def should_adjust_risk(self) -> bool:
        """Check if enough time has passed since last adjustment."""
        if self.last_adjustment_time is None:
            return True

        time_since_adjustment = (datetime.utcnow() - self.last_adjustment_time).total_seconds() / 3600
        return time_since_adjustment >= self.min_adjustment_interval_hours

    def apply_risk_adjustment(
        self,
        parameter_name: str,
        new_value: float,
        reason: str,
        trigger_metric: str,
    ) -> bool:
        """
        Apply a risk limit adjustment.

        Args:
            parameter_name: Name of parameter to adjust
            new_value: New value for parameter
            reason: Reason for adjustment
            trigger_metric: What metric triggered this

        Returns:
            True if successful
        """
        try:
            # Get current value
            if parameter_name == "max_position_size_percent":
                old_value = self.config.execution.capital.max_position_size_percent
                self.config.execution.capital.max_position_size_percent = new_value
            elif parameter_name == "daily_loss_limit_percent":
                old_value = self.config.execution.capital.daily_loss_limit_percent
                self.config.execution.capital.daily_loss_limit_percent = new_value
            else:
                return False

            # Record adjustment
            adjustment = RiskAdjustment(
                timestamp=datetime.utcnow(),
                parameter_name=parameter_name,
                old_value=old_value,
                new_value=new_value,
                reason=reason,
                trigger_metric=trigger_metric,
            )
            self.adjustment_history.append(adjustment)
            self.last_adjustment_time = datetime.utcnow()

            print(f"✓ Risk adjusted {parameter_name}: {old_value:.2f} → {new_value:.2f} ({trigger_metric})")
            return True

        except Exception as e:
            print(f"✗ Failed to adjust risk {parameter_name}: {e}")
            return False

    def get_adjustment_history(self) -> list[RiskAdjustment]:
        """Get risk adjustment history."""
        return self.adjustment_history

    def get_status(self) -> dict:
        """Get risk adjuster status."""
        return {
            "total_adjustments": len(self.adjustment_history),
            "last_adjustment": self.adjustment_history[-1].timestamp.isoformat() if self.adjustment_history else None,
            "current_position_size": self.config.execution.capital.max_position_size_percent,
            "current_daily_limit": self.config.execution.capital.daily_loss_limit_percent,
        }
