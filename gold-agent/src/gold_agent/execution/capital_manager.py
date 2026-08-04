"""Capital Manager (Tier 1) — Position sizing, leverage, and drawdown management."""

from datetime import datetime
from typing import Optional


class CapitalManager:
    """Manages capital allocation, position sizing, and risk limits."""

    def __init__(self, config, initial_capital: float):
        self.config = config
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.peak_capital = initial_capital
        self.daily_loss_limit = config.execution.capital.daily_loss_limit_percent / 100.0
        self.max_drawdown_limit = config.execution.capital.max_drawdown_percent / 100.0
        self.max_position_size = config.execution.capital.max_position_size_percent / 100.0
        self.max_leverage = config.execution.capital.max_leverage
        self.daily_losses_today = 0.0
        self.session_start_time = datetime.utcnow()

    def set_current_capital(self, capital: float) -> None:
        """Update current capital balance."""
        self.current_capital = capital
        if capital > self.peak_capital:
            self.peak_capital = capital

    def reset_daily_losses(self) -> None:
        """Reset daily loss tracking (call at market open)."""
        self.daily_losses_today = 0.0
        self.session_start_time = datetime.utcnow()

    def add_daily_loss(self, loss: float) -> None:
        """Record a loss for today."""
        if loss > 0:
            self.daily_losses_today += loss

    def calculate_position_size(
        self,
        risk_amount: Optional[float] = None,
    ) -> float:
        """
        Calculate position size based on risk management rules.

        If risk_amount not specified, uses percentage of capital.
        """
        if not risk_amount:
            # Default: risk 1% of capital per trade
            risk_amount = self.current_capital * 0.01

        # Max position size
        max_position_value = self.current_capital * self.max_position_size
        return max_position_value

    def can_place_trade(self, position_value: float) -> tuple[bool, str]:
        """
        Check if a trade can be placed given capital constraints.

        Returns: (can_trade, reason)
        """
        # Check daily loss limit
        daily_loss_pct = self.daily_losses_today / self.initial_capital
        if daily_loss_pct > self.daily_loss_limit:
            return False, f"Daily loss limit reached ({daily_loss_pct:.2%})"

        # Check drawdown limit
        current_drawdown = self._calculate_drawdown()
        if current_drawdown > self.max_drawdown_limit:
            return False, f"Max drawdown limit exceeded ({current_drawdown:.2%})"

        # Check position size
        position_pct = position_value / self.current_capital
        if position_pct > self.max_position_size:
            return False, f"Position size exceeds limit ({position_pct:.2%} > {self.max_position_size:.2%})"

        # Check available capital
        if position_value > self.current_capital * 0.95:
            return False, "Insufficient capital"

        return True, "OK"

    def _calculate_drawdown(self) -> float:
        """Calculate current drawdown from peak."""
        if self.peak_capital == 0:
            return 0.0
        return (self.peak_capital - self.current_capital) / self.peak_capital

    def get_risk_free_capital(self) -> float:
        """Get capital available for trading."""
        used = self.current_capital * 0.95  # Reserve 5%
        return max(0, self.current_capital - used)

    def calculate_leverage_needed(self, position_value: float) -> float:
        """Calculate leverage needed for a position."""
        if self.current_capital == 0:
            return 0.0

        leverage = position_value / self.current_capital

        if leverage > self.max_leverage:
            return self.max_leverage

        return leverage

    def validate_leverage(self, position_value: float) -> tuple[bool, str]:
        """Validate that position doesn't exceed leverage limits."""
        leverage = self.calculate_leverage_needed(position_value)

        if leverage > self.max_leverage:
            return False, f"Leverage {leverage:.2f}x exceeds limit {self.max_leverage:.2f}x"

        return True, "OK"

    def get_status(self) -> dict:
        """Get capital manager status."""
        drawdown = self._calculate_drawdown()
        daily_loss_pct = self.daily_losses_today / self.initial_capital if self.initial_capital > 0 else 0.0

        return {
            "initial_capital": self.initial_capital,
            "current_capital": self.current_capital,
            "peak_capital": self.peak_capital,
            "current_drawdown_percent": drawdown * 100,
            "max_drawdown_limit_percent": self.max_drawdown_limit * 100,
            "daily_losses_today": self.daily_losses_today,
            "daily_loss_limit_percent": self.daily_loss_limit * 100,
            "daily_loss_today_percent": daily_loss_pct * 100,
            "max_position_size_percent": self.max_position_size * 100,
            "max_leverage": self.max_leverage,
            "risk_free_capital": self.get_risk_free_capital(),
        }
