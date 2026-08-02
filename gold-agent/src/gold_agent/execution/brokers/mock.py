"""Mock Broker Adapter — for testing without real credentials."""

from datetime import datetime
from typing import List, Dict, Optional
import random

from src.gold_agent.core.models import Order, OrderStatus
from src.gold_agent.execution.engine import BrokerAdapter, ExecutionResult


class MockBrokerAdapter(BrokerAdapter):
    """Mock broker for development and testing."""

    def __init__(self, config, initial_balance: float = 100000.0):
        self.config = config
        self.connected = False
        self.account_balance = initial_balance
        self.open_positions: Dict[str, Dict] = {}
        self.order_history: Dict[str, Order] = {}
        self.last_xau_price = 2000.0  # Mock initial gold price

    async def connect(self) -> bool:
        """Connect to mock broker."""
        self.connected = True
        print(f"Mock Broker: Connected (initial balance: ${self.account_balance:,.2f})")
        return True

    async def disconnect(self) -> bool:
        """Disconnect from mock broker."""
        self.connected = False
        print("Mock Broker: Disconnected")
        return True

    async def is_connected(self) -> bool:
        """Check connection status."""
        return self.connected

    async def place_order(self, order: Order) -> ExecutionResult:
        """Place an order (mock execution)."""
        if not self.connected:
            return ExecutionResult(
                success=False,
                message="Not connected to broker"
            )

        # Simulate market price with slight spread
        spread = random.uniform(0.5, 2.0)
        if order.side.value == "BUY":
            price = self.last_xau_price + spread
        else:
            price = self.last_xau_price - spread

        # Simulate partial fills or rejections (5% chance)
        if random.random() < 0.05:
            return ExecutionResult(
                success=False,
                message="Order rejected: Insufficient liquidity"
            )

        # Calculate cost
        cost = price * order.quantity

        # Check if sufficient balance
        if cost > self.account_balance * 0.95:
            return ExecutionResult(
                success=False,
                message=f"Insufficient balance: need ${cost:,.2f}, have ${self.account_balance:,.2f}"
            )

        # Execute order
        order_id = f"MOCK-{datetime.utcnow().timestamp()}"
        filled_qty = order.quantity * random.uniform(0.95, 1.0)  # Simulate slight slippage

        # Update balance
        if order.side.value == "BUY":
            self.account_balance -= price * filled_qty
            # Track position
            if order.symbol not in self.open_positions:
                self.open_positions[order.symbol] = {
                    "quantity": 0,
                    "entry_price": 0,
                }
            pos = self.open_positions[order.symbol]
            pos["quantity"] = filled_qty
            pos["entry_price"] = price
        else:
            self.account_balance += price * filled_qty
            if order.symbol in self.open_positions:
                del self.open_positions[order.symbol]

        self.order_history[order_id] = order

        return ExecutionResult(
            success=True,
            order_id=order_id,
            message=f"Order executed",
            filled_quantity=filled_qty,
            average_fill_price=price
        )

    async def cancel_order(self, order_id: str) -> ExecutionResult:
        """Cancel an order."""
        if order_id not in self.order_history:
            return ExecutionResult(
                success=False,
                message=f"Order {order_id} not found"
            )

        return ExecutionResult(
            success=True,
            message=f"Order {order_id} cancelled"
        )

    async def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get order status."""
        return self.order_history.get(order_id)

    async def close_position(self, symbol: str, quantity: float) -> ExecutionResult:
        """Close a position."""
        if symbol not in self.open_positions:
            return ExecutionResult(
                success=False,
                message=f"No position in {symbol}"
            )

        pos = self.open_positions[symbol]
        if pos["quantity"] < quantity:
            return ExecutionResult(
                success=False,
                message=f"Cannot close {quantity}, only have {pos['quantity']}"
            )

        # Simulate exit price
        exit_price = self.last_xau_price - random.uniform(0.5, 2.0)
        proceeds = exit_price * quantity

        # Update balance
        self.account_balance += proceeds

        # Update position
        pos["quantity"] -= quantity
        if pos["quantity"] == 0:
            del self.open_positions[symbol]

        return ExecutionResult(
            success=True,
            order_id=f"CLOSE-{datetime.utcnow().timestamp()}",
            message=f"Position closed",
            filled_quantity=quantity,
            average_fill_price=exit_price
        )

    async def get_account_balance(self) -> Optional[float]:
        """Get account balance."""
        return self.account_balance

    async def get_open_positions(self) -> List[Dict]:
        """Get all open positions."""
        return [
            {
                "symbol": symbol,
                "quantity": pos["quantity"],
                "entry_price": pos["entry_price"],
                "current_price": self.last_xau_price,
                "unrealized_p_l": (self.last_xau_price - pos["entry_price"]) * pos["quantity"],
            }
            for symbol, pos in self.open_positions.items()
        ]

    def update_market_price(self, price: float) -> None:
        """Update mock market price (for testing)."""
        self.last_xau_price = price
