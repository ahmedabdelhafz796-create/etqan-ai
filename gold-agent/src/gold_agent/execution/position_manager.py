"""Position Manager (Tier 1) — Track open positions and P&L."""

from datetime import datetime
from typing import Dict, Optional, List

from src.gold_agent.core.models import Position, PositionSide, Trade


class PositionManager:
    """Manages all open positions and their P&L calculations."""

    def __init__(self, config):
        self.config = config
        self.positions: Dict[str, Position] = {}  # symbol -> Position
        self.trades: Dict[str, Trade] = {}  # trade_id -> Trade

    def open_position(
        self,
        symbol: str,
        side: PositionSide,
        quantity: float,
        entry_price: float,
        entry_timestamp: datetime,
        trade_ids: List[str],
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> Position:
        """Open a new position."""
        position = Position(
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            current_price=entry_price,
            entry_timestamp=entry_timestamp,
            unrealized_p_l=0.0,
            unrealized_p_l_percent=0.0,
            trade_ids=trade_ids,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
        self.positions[symbol] = position
        return position

    def close_position(self, symbol: str) -> Optional[Position]:
        """Close a position."""
        if symbol not in self.positions:
            return None

        position = self.positions.pop(symbol)
        return position

    def update_position_price(self, symbol: str, current_price: float) -> Optional[Position]:
        """Update position current price and recalculate P&L."""
        if symbol not in self.positions:
            return None

        position = self.positions[symbol]
        position.current_price = current_price

        # Calculate unrealized P&L
        if position.side == PositionSide.LONG:
            position.unrealized_p_l = (current_price - position.entry_price) * position.quantity
            position.unrealized_p_l_percent = ((current_price - position.entry_price) / position.entry_price) * 100
        else:  # SHORT
            position.unrealized_p_l = (position.entry_price - current_price) * position.quantity
            position.unrealized_p_l_percent = ((position.entry_price - current_price) / position.entry_price) * 100

        return position

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get a position by symbol."""
        return self.positions.get(symbol)

    def get_open_positions(self) -> List[Position]:
        """Get all open positions."""
        return list(self.positions.values())

    def has_position(self, symbol: str) -> bool:
        """Check if position exists."""
        return symbol in self.positions

    def get_total_unrealized_p_l(self) -> float:
        """Get total unrealized P&L across all positions."""
        return sum(pos.unrealized_p_l for pos in self.positions.values())

    def get_total_unrealized_p_l_percent(self) -> float:
        """Get total unrealized P&L percentage across all positions."""
        if not self.positions:
            return 0.0

        total_pl = sum(pos.unrealized_p_l for pos in self.positions.values())
        total_investment = sum(pos.entry_price * pos.quantity for pos in self.positions.values())

        if total_investment == 0:
            return 0.0

        return (total_pl / total_investment) * 100

    def get_position_count(self) -> int:
        """Get number of open positions."""
        return len(self.positions)

    def register_trade(self, trade_id: str, trade: Trade) -> None:
        """Register a trade."""
        self.trades[trade_id] = trade

    def get_trade(self, trade_id: str) -> Optional[Trade]:
        """Get a trade by ID."""
        return self.trades.get(trade_id)

    def get_trades_for_position(self, symbol: str) -> List[Trade]:
        """Get all trades for a position."""
        position = self.positions.get(symbol)
        if not position:
            return []

        return [self.trades[tid] for tid in position.trade_ids if tid in self.trades]

    def get_status(self) -> dict:
        """Get position manager status."""
        return {
            "open_positions": len(self.positions),
            "total_unrealized_p_l": self.get_total_unrealized_p_l(),
            "total_unrealized_p_l_percent": self.get_total_unrealized_p_l_percent(),
            "positions": {
                symbol: {
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "current_price": pos.current_price,
                    "unrealized_p_l": pos.unrealized_p_l,
                    "unrealized_p_l_percent": pos.unrealized_p_l_percent,
                }
                for symbol, pos in self.positions.items()
            }
        }
