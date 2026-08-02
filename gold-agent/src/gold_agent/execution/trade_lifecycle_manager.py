"""Trade Lifecycle Manager (Tier 1) — Orchestrate entry→management→exit."""

from datetime import datetime
from typing import Optional
import uuid

from src.gold_agent.core.models import Trade, PositionSide, ActionType, IndicatorValues, Score
from src.gold_agent.execution.position_manager import PositionManager
from src.gold_agent.execution.capital_manager import CapitalManager


class TradeLifecycleManager:
    """Orchestrates the complete lifecycle of a trade."""

    def __init__(
        self,
        position_manager: PositionManager,
        capital_manager: CapitalManager,
        config,
    ):
        self.position_manager = position_manager
        self.capital_manager = capital_manager
        self.config = config
        self.active_trades: dict = {}  # trade_id -> Trade

    async def open_trade(
        self,
        decision_action: ActionType,
        entry_price: float,
        quantity: float,
        entry_order_id: str,
        decision_id: int,
        symbol: str = "XAUUSD",
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        indicators: Optional[IndicatorValues] = None,
        score: Optional[Score] = None,
    ) -> Optional[Trade]:
        """
        Open a new trade.

        Returns: Trade object if successful, None otherwise
        """
        # Determine position side from action
        if decision_action == ActionType.BUY:
            side = PositionSide.LONG
        elif decision_action == ActionType.SELL:
            side = PositionSide.SHORT
        else:
            return None

        # Create trade
        trade_id = f"TRADE-{uuid.uuid4().hex[:8]}"
        trade = Trade(
            trade_id=trade_id,
            entry_decision_id=decision_id,
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            quantity=quantity,
            entry_timestamp=datetime.utcnow(),
            entry_order_id=entry_order_id,
            current_price=entry_price,
            current_p_l=0.0,
            current_p_l_percent=0.0,
            stop_loss=stop_loss,
            take_profit=take_profit,
            state="open",
        )

        # Calculate risk/reward ratio
        if stop_loss and take_profit:
            if side == PositionSide.LONG:
                risk = entry_price - stop_loss
                reward = take_profit - entry_price
            else:
                risk = stop_loss - entry_price
                reward = entry_price - take_profit

            if risk > 0:
                trade.risk_reward_ratio = reward / risk

        # Register trade
        self.active_trades[trade_id] = trade
        self.position_manager.register_trade(trade_id, trade)

        # Open position
        self.position_manager.open_position(
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            entry_timestamp=trade.entry_timestamp,
            trade_ids=[trade_id],
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

        return trade

    async def close_trade(
        self,
        trade_id: str,
        exit_price: float,
        exit_reason: str = "manual",
    ) -> Optional[Trade]:
        """
        Close a trade.

        Returns: Closed Trade object if successful, None otherwise
        """
        if trade_id not in self.active_trades:
            return None

        trade = self.active_trades[trade_id]

        # Calculate realized P&L
        if trade.side == PositionSide.LONG:
            final_p_l = (exit_price - trade.entry_price) * trade.quantity
        else:
            final_p_l = (trade.entry_price - exit_price) * trade.quantity

        final_p_l_percent = (final_p_l / (trade.entry_price * trade.quantity)) * 100

        # Update trade
        trade.exit_price = exit_price
        trade.exit_timestamp = datetime.utcnow()
        trade.exit_reason = exit_reason
        trade.final_p_l = final_p_l
        trade.final_p_l_percent = final_p_l_percent
        trade.state = "closed"

        # Calculate duration
        duration = (trade.exit_timestamp - trade.entry_timestamp).total_seconds() / 60
        trade.duration_minutes = duration

        # Record losses for capital manager
        if final_p_l < 0:
            self.capital_manager.add_daily_loss(abs(final_p_l))

        # Close position
        self.position_manager.close_position(trade.symbol)

        return trade

    async def update_trade_price(self, trade_id: str, current_price: float) -> Optional[Trade]:
        """Update trade current price and P&L."""
        if trade_id not in self.active_trades:
            return None

        trade = self.active_trades[trade_id]

        # Update position price
        self.position_manager.update_position_price(trade.symbol, current_price)

        # Update trade
        trade.current_price = current_price

        if trade.side == PositionSide.LONG:
            trade.current_p_l = (current_price - trade.entry_price) * trade.quantity
            trade.current_p_l_percent = ((current_price - trade.entry_price) / trade.entry_price) * 100
        else:
            trade.current_p_l = (trade.entry_price - current_price) * trade.quantity
            trade.current_p_l_percent = ((trade.entry_price - current_price) / trade.entry_price) * 100

        return trade

    async def check_stop_loss(self, trade_id: str, current_price: float) -> bool:
        """Check if trade hit stop loss."""
        if trade_id not in self.active_trades:
            return False

        trade = self.active_trades[trade_id]

        if not trade.stop_loss:
            return False

        if trade.side == PositionSide.LONG and current_price <= trade.stop_loss:
            return True

        if trade.side == PositionSide.SHORT and current_price >= trade.stop_loss:
            return True

        return False

    async def check_take_profit(self, trade_id: str, current_price: float) -> bool:
        """Check if trade hit take profit."""
        if trade_id not in self.active_trades:
            return False

        trade = self.active_trades[trade_id]

        if not trade.take_profit:
            return False

        if trade.side == PositionSide.LONG and current_price >= trade.take_profit:
            return True

        if trade.side == PositionSide.SHORT and current_price <= trade.take_profit:
            return True

        return False

    def get_trade(self, trade_id: str) -> Optional[Trade]:
        """Get a trade by ID."""
        return self.active_trades.get(trade_id)

    def get_open_trades(self) -> list:
        """Get all open trades."""
        return [t for t in self.active_trades.values() if t.state == "open"]

    def get_closed_trades(self) -> list:
        """Get all closed trades."""
        return [t for t in self.active_trades.values() if t.state == "closed"]

    def get_today_trades(self) -> list:
        """Get all trades from today."""
        today = datetime.utcnow().date()
        return [
            t for t in self.active_trades.values()
            if t.entry_timestamp.date() == today
        ]

    def get_today_pnl(self) -> float:
        """Get P&L for trades closed today."""
        today_trades = self.get_today_trades()
        closed_today = [t for t in today_trades if t.state == "closed"]
        return sum(t.final_p_l or 0.0 for t in closed_today)

    def get_today_win_rate(self) -> Optional[float]:
        """Get win rate for trades closed today."""
        today_trades = [t for t in self.get_today_trades() if t.state == "closed"]
        if not today_trades:
            return None

        wins = sum(1 for t in today_trades if (t.final_p_l or 0.0) > 0)
        return wins / len(today_trades)

    def get_status(self) -> dict:
        """Get trade lifecycle manager status."""
        open_trades = self.get_open_trades()
        closed_trades = self.get_closed_trades()
        today_trades = self.get_today_trades()

        return {
            "open_trades": len(open_trades),
            "closed_trades": len(closed_trades),
            "today_trades": len(today_trades),
            "today_pnl": self.get_today_pnl(),
            "today_win_rate": self.get_today_win_rate(),
            "total_trades": len(self.active_trades),
        }
