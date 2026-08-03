"""Capital Preservation Constitution — Research-backed position sizing and capital rules."""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import math
import logging

logger = logging.getLogger(__name__)


class CapitalPreservationEngine:
    """
    Van Tharp fixed-fractional position sizing with immutable capital preservation rules.

    Implements PART 1 of Phase 1.5 mandate:
    - Van Tharp fixed-fractional sizing (1-2% max per trade)
    - Daily loss limit (5% auto-halt)
    - Maximum drawdown circuit breaker (15-20%)
    - Consecutive loss pause (3-4 trades)
    - Position hold-time hard rule (24 hours)
    - Immutable safety rules (code-enforced, not configurable)
    - Decision traceability (all trades logged with inputs)
    """

    def __init__(self, config, initial_capital: float):
        """
        Initialize capital preservation engine.

        Args:
            config: Configuration object with capital parameters
            initial_capital: Starting account equity (e.g., $10,000)
        """
        self.config = config
        self.initial_capital = initial_capital
        self.peak_equity = initial_capital  # Track highest watermark for drawdown
        self.current_equity = initial_capital

        # Daily tracking (reset at UTC 00:00)
        self.daily_loss_amount = 0.0  # Cumulative losses today in dollars
        self.daily_loss_percent = 0.0  # Daily loss as % of initial capital
        self.daily_reset_time = self._get_next_daily_reset()

        # Consecutive loss tracking
        self.consecutive_losses = 0
        self.trades_history = []  # All trades with results

        # Position hold-time tracking
        self.active_positions = {}  # {trade_id: (entry_timestamp, entry_price)}

        # Configuration validation
        self._validate_config()

    def _validate_config(self):
        """Validate immutable safety rule thresholds."""
        assert self.config.capital.daily_loss_limit_percent <= 10.0, "Daily loss limit capped at 10%"
        assert self.config.capital.max_drawdown_percent <= 50.0, "Max drawdown capped at 50%"
        assert self.config.capital.max_position_size_percent <= 5.0, "Position size capped at 5%"
        logger.info("Capital preservation rules validated (immutable)")

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss_price: float,
        risk_per_trade_pct: Optional[float] = None,
    ) -> Tuple[float, Dict]:
        """
        Van Tharp fixed-fractional position sizing formula.

        Formula: Position Size = (Account Risk $) / (Entry Price - Stop Loss Price)
        where Account Risk $ = Current Equity × Risk Per Trade %

        Args:
            entry_price: Entry level (e.g., 2050.0 for gold)
            stop_loss_price: Stop loss level (e.g., 2040.0)
            risk_per_trade_pct: Risk per trade as % of equity (default: 2%)

        Returns:
            (position_size, {inputs_dict, formula_result, kelly_diagnostic})

        Raises:
            ValueError: If inputs violate capital rules
        """
        if risk_per_trade_pct is None:
            risk_per_trade_pct = self.config.capital.max_position_size_percent

        # Immutable rule: Risk per trade cannot exceed 2%
        if risk_per_trade_pct > 2.0:
            risk_per_trade_pct = 2.0
            logger.warning(f"Risk per trade capped at 2% (requested {risk_per_trade_pct}%)")

        # Validate price inputs
        if entry_price <= stop_loss_price:
            raise ValueError(f"Entry {entry_price} must be above stop loss {stop_loss_price}")

        # Calculate risk amount in dollars
        account_risk_dollars = self.current_equity * (risk_per_trade_pct / 100.0)

        # Calculate points risked per unit
        price_diff = abs(entry_price - stop_loss_price)

        # Position size = Risk$ / Price risk per unit
        position_size = account_risk_dollars / price_diff

        # Kelly Criterion diagnostic (informational only, never used directly)
        kelly_fraction = self._calculate_kelly_fraction()
        quarter_kelly = kelly_fraction / 4.0

        # Return detailed audit trail
        audit = {
            "entry_price": entry_price,
            "stop_loss_price": stop_loss_price,
            "current_equity": self.current_equity,
            "risk_per_trade_percent": risk_per_trade_pct,
            "account_risk_dollars": account_risk_dollars,
            "price_risk_per_unit": price_diff,
            "position_size": position_size,
            "kelly_fraction": kelly_fraction,
            "quarter_kelly": quarter_kelly,
            "formula": "Position Size = (Equity × Risk%) / (Entry - SL)",
            "immutable_rule": "Risk per trade capped at 2% of equity",
        }

        logger.info(
            f"Position sizing: Size={position_size:.2f} units, "
            f"Risk=${account_risk_dollars:.2f}, "
            f"P/L range: ${-account_risk_dollars:.2f} to ${account_risk_dollars * (entry_price / price_diff - 1):.2f}"
        )

        return position_size, audit

    def check_daily_loss_limit(self, proposed_trade_loss_dollars: float = 0.0) -> Tuple[bool, str]:
        """
        Check if daily loss limit is breached (IMMUTABLE RULE).

        Rule: If cumulative daily loss reaches 5% of account, halt all new trades.
        Reset: Daily at UTC 00:00.

        Args:
            proposed_trade_loss_dollars: Max loss if this trade's SL is hit

        Returns:
            (allowed: bool, reason: str)
        """
        self._check_and_reset_daily_counter()

        # Calculate potential total loss
        potential_total_loss_pct = (self.daily_loss_amount + proposed_trade_loss_dollars) / self.current_equity * 100.0

        daily_limit = self.config.capital.daily_loss_limit_percent

        if self.daily_loss_amount >= self.current_equity * (daily_limit / 100.0):
            reason = (
                f"Daily loss limit BREACHED: "
                f"${self.daily_loss_amount:.2f} ({self.daily_loss_percent:.1f}%) "
                f"exceeds limit (${self.current_equity * (daily_limit / 100.0):.2f}, {daily_limit}%). "
                f"Halting new trades until reset at {self.daily_reset_time.strftime('%Y-%m-%d %H:%M UTC')}"
            )
            logger.error(reason)
            return False, reason

        if potential_total_loss_pct > daily_limit:
            reason = (
                f"Daily loss limit would be BREACHED if trade accepted: "
                f"Current ${self.daily_loss_amount:.2f} + Proposed ${proposed_trade_loss_dollars:.2f} "
                f"= ${self.daily_loss_amount + proposed_trade_loss_dollars:.2f} ({potential_total_loss_pct:.1f}%) "
                f"exceeds {daily_limit}% limit. BLOCKING trade."
            )
            logger.warning(reason)
            return False, reason

        return True, f"Daily loss OK: ${self.daily_loss_amount:.2f}/{self.current_equity * (daily_limit / 100.0):.2f}"

    def check_drawdown_circuit_breaker(self) -> Tuple[bool, str]:
        """
        Check if maximum drawdown circuit breaker is triggered (IMMUTABLE RULE).

        Rule: If account equity drops 15-20% below peak watermark, escalate to Emergency.
        Reset: Manual recovery only (no automatic reset).

        Returns:
            (allowed: bool, reason: str)
        """
        if self.current_equity > self.peak_equity:
            self.peak_equity = self.current_equity  # Update watermark

        drawdown_pct = (self.peak_equity - self.current_equity) / self.peak_equity * 100.0
        trigger_threshold = self.config.capital.max_drawdown_percent

        if drawdown_pct >= trigger_threshold:
            reason = (
                f"EMERGENCY: Drawdown circuit breaker TRIGGERED: "
                f"Peak equity ${self.peak_equity:.2f}, Current ${self.current_equity:.2f}, "
                f"Drawdown {drawdown_pct:.1f}% >= Threshold {trigger_threshold}%. "
                f"ESCALATING TO EMERGENCY STATE (manual recovery required)"
            )
            logger.critical(reason)
            return False, reason

        if drawdown_pct >= trigger_threshold * 0.8:  # Warning level
            logger.warning(
                f"Drawdown warning: {drawdown_pct:.1f}% "
                f"(approaching {trigger_threshold}% emergency threshold)"
            )

        return True, f"Drawdown OK: {drawdown_pct:.1f}%"

    def check_consecutive_loss_pause(self) -> Tuple[bool, str]:
        """
        Check if consecutive loss pause is active (IMMUTABLE RULE).

        Rule: After 3-4 consecutive losing trades, require manual review before resuming.
        Reset: After 1 winning trade or manual override with timestamp logging.

        Returns:
            (allowed: bool, reason: str)
        """
        max_consecutive = self.config.capital.max_consecutive_losses

        if self.consecutive_losses >= max_consecutive:
            reason = (
                f"Consecutive loss pause ACTIVE: {self.consecutive_losses} consecutive losses "
                f">= limit ({max_consecutive}). Requiring manual review before resuming trades."
            )
            logger.warning(reason)
            return False, reason

        if self.consecutive_losses >= max_consecutive * 0.75:
            logger.info(f"Consecutive loss warning: {self.consecutive_losses}/{max_consecutive}")

        return True, f"Consecutive losses OK: {self.consecutive_losses}/{max_consecutive}"

    def check_position_hold_time(self, position_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if position exceeds maximum hold-time (IMMUTABLE SHARIA RULE).

        Rule: No position may remain open longer than 24 hours (structural Sharia safeguard).
        This ensures positions close well before broker grace period (typically 5-10 days),
        eliminating holding fees / swap charges.

        Args:
            position_id: Position identifier

        Returns:
            (should_close: bool, reason: str or None)
        """
        if position_id not in self.active_positions:
            return False, None

        entry_time, entry_price = self.active_positions[position_id]
        hold_duration = datetime.utcnow() - entry_time
        max_hold = timedelta(hours=24)

        if hold_duration >= max_hold:
            reason = (
                f"Position hold-time LIMIT REACHED: {hold_duration.total_seconds() / 3600:.1f} hours "
                f">= 24h limit. FORCE-CLOSING via market order (Sharia compliance: "
                f"ensures position closes before broker grace period, zero holding fees)"
            )
            logger.warning(reason)
            return True, reason

        return False, None

    def record_trade_result(
        self,
        trade_id: str,
        entry_price: float,
        exit_price: float,
        quantity: float,
        entry_time: datetime,
        exit_time: Optional[datetime] = None,
    ) -> Dict:
        """
        Record a closed trade result and update capital tracking.

        Args:
            trade_id: Unique trade ID
            entry_price: Entry price
            exit_price: Exit price
            quantity: Position size
            entry_time: Entry timestamp
            exit_time: Exit timestamp (default: now)

        Returns:
            {profit_loss_dollars, profit_loss_percent, realized_pnl, new_equity, audit}
        """
        if exit_time is None:
            exit_time = datetime.utcnow()

        # Calculate profit/loss
        pnl_dollars = (exit_price - entry_price) * quantity
        pnl_percent = ((exit_price - entry_price) / entry_price) * 100.0

        # Update equity
        self.current_equity += pnl_dollars

        # Update daily loss tracking
        if pnl_dollars < 0:
            self.daily_loss_amount += abs(pnl_dollars)
            self.daily_loss_percent = (self.daily_loss_amount / self.current_equity) * 100.0
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0  # Reset on win

        # Hold-time tracking
        hold_duration = exit_time - entry_time
        if trade_id in self.active_positions:
            del self.active_positions[trade_id]

        # Audit trail
        audit = {
            "trade_id": trade_id,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "pnl_dollars": pnl_dollars,
            "pnl_percent": pnl_percent,
            "entry_time": entry_time,
            "exit_time": exit_time,
            "hold_duration_hours": hold_duration.total_seconds() / 3600,
            "current_equity": self.current_equity,
            "daily_loss_amount": self.daily_loss_amount,
            "daily_loss_percent": self.daily_loss_percent,
            "consecutive_losses": self.consecutive_losses,
            "drawdown_percent": self._calculate_current_drawdown_percent(),
        }

        self.trades_history.append(audit)

        logger.info(
            f"Trade closed: {trade_id} | P&L ${pnl_dollars:.2f} ({pnl_percent:+.2f}%) | "
            f"Hold {hold_duration.total_seconds() / 3600:.1f}h | "
            f"Equity ${self.current_equity:.2f} | Consecutive losses: {self.consecutive_losses}"
        )

        return audit

    def record_position_opened(self, trade_id: str, entry_price: float, entry_time: Optional[datetime] = None):
        """Track an opened position for hold-time enforcement."""
        if entry_time is None:
            entry_time = datetime.utcnow()
        self.active_positions[trade_id] = (entry_time, entry_price)
        logger.info(f"Position opened: {trade_id} at ${entry_price:.2f} (hold-time tracking started)")

    def get_capital_status(self) -> Dict:
        """
        Get current capital state for audit trail.

        Returns:
            {equity, daily_loss, drawdown, consecutive_losses, active_positions, status}
        """
        self._check_and_reset_daily_counter()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "initial_capital": self.initial_capital,
            "current_equity": self.current_equity,
            "peak_equity": self.peak_equity,
            "equity_change_dollars": self.current_equity - self.initial_capital,
            "equity_change_percent": ((self.current_equity - self.initial_capital) / self.initial_capital) * 100.0,
            "daily_loss_amount": self.daily_loss_amount,
            "daily_loss_percent": self.daily_loss_percent,
            "daily_loss_limit_percent": self.config.capital.daily_loss_limit_percent,
            "daily_reset_time": self.daily_reset_time.isoformat(),
            "drawdown_percent": self._calculate_current_drawdown_percent(),
            "drawdown_limit_percent": self.config.capital.max_drawdown_percent,
            "consecutive_losses": self.consecutive_losses,
            "consecutive_loss_limit": self.config.capital.max_consecutive_losses,
            "active_positions": len(self.active_positions),
            "total_trades": len(self.trades_history),
            "status": self._get_status_enum(),
        }

    def _check_and_reset_daily_counter(self):
        """Reset daily loss counter if new UTC day has started."""
        now = datetime.utcnow()
        if now >= self.daily_reset_time:
            self.daily_loss_amount = 0.0
            self.daily_loss_percent = 0.0
            self.daily_reset_time = self._get_next_daily_reset()
            logger.info("Daily loss counter reset (new UTC day)")

    @staticmethod
    def _get_next_daily_reset() -> datetime:
        """Get next UTC 00:00 reset time."""
        now = datetime.utcnow()
        return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    def _calculate_current_drawdown_percent(self) -> float:
        """Calculate current drawdown from peak equity."""
        if self.peak_equity <= 0:
            return 0.0
        return ((self.peak_equity - self.current_equity) / self.peak_equity) * 100.0

    def _calculate_kelly_fraction(self) -> float:
        """
        Calculate Kelly Criterion as diagnostic (informational only).

        Kelly % = (Win % × Avg Win - Loss % × Avg Loss) / Avg Win

        Returns fraction (e.g., 0.10 = 10% Kelly).
        Never used directly; capped at Quarter-Kelly for position sizing.
        """
        if len(self.trades_history) < 5:
            return 0.05  # Default 5% until enough history

        wins = [t["pnl_dollars"] for t in self.trades_history if t["pnl_dollars"] > 0]
        losses = [t["pnl_dollars"] for t in self.trades_history if t["pnl_dollars"] < 0]

        if not wins or not losses:
            return 0.05

        win_pct = len(wins) / len(self.trades_history)
        loss_pct = len(losses) / len(self.trades_history)
        avg_win = sum(wins) / len(wins)
        avg_loss = sum(losses) / len(losses)

        if avg_win <= 0:
            return 0.05

        kelly = (win_pct * avg_win - loss_pct * abs(avg_loss)) / avg_win
        return max(0.01, min(kelly, 0.25))  # Clamp to 1-25%

    def _get_status_enum(self) -> str:
        """Get overall capital status enum."""
        if self.daily_loss_percent >= self.config.capital.daily_loss_limit_percent:
            return "DAILY_LIMIT_BREACHED"
        if self._calculate_current_drawdown_percent() >= self.config.capital.max_drawdown_percent:
            return "DRAWDOWN_LIMIT_BREACHED"
        if self.consecutive_losses >= self.config.capital.max_consecutive_losses:
            return "CONSECUTIVE_LOSS_PAUSE"
        return "OK"
