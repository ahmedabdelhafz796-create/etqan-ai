"""Execution Engine (Tier 1) — Broker-agnostic order execution abstraction."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, List

from gold_agent.core.models import Order, OrderStatus, OrderType, ActionType, Trade, PositionSide


class ExecutionResult:
    """Result of an execution attempt."""

    def __init__(
        self,
        success: bool,
        order_id: Optional[str] = None,
        message: str = "",
        filled_quantity: float = 0.0,
        average_fill_price: Optional[float] = None,
    ):
        self.success = success
        self.order_id = order_id
        self.message = message
        self.filled_quantity = filled_quantity
        self.average_fill_price = average_fill_price


class BrokerAdapter(ABC):
    """Abstract broker adapter interface."""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to broker."""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from broker."""
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if connected."""
        pass

    @abstractmethod
    async def place_order(self, order: Order) -> ExecutionResult:
        """Place an order."""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> ExecutionResult:
        """Cancel an order."""
        pass

    @abstractmethod
    async def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get order status."""
        pass

    @abstractmethod
    async def close_position(self, symbol: str, quantity: float) -> ExecutionResult:
        """Close a position."""
        pass

    @abstractmethod
    async def get_account_balance(self) -> Optional[float]:
        """Get account balance in USD."""
        pass

    @abstractmethod
    async def get_open_positions(self) -> List[Dict]:
        """Get all open positions."""
        pass


class ExecutionEngine:
    """Main execution engine — orchestrates order placement and lifecycle."""

    def __init__(self, broker_adapter: BrokerAdapter, config):
        self.broker = broker_adapter
        self.config = config
        self.enabled = False  # OFF by default, Kill Switch
        self.pending_orders: Dict[str, Order] = {}
        self.active_trades: Dict[str, Trade] = {}

    async def initialize(self) -> bool:
        """Initialize the execution engine."""
        try:
            connected = await self.broker.connect()
            if not connected:
                print("Failed to connect to broker")
                return False
            print("✓ Execution Engine initialized (disabled by default)")
            return True
        except Exception as e:
            print(f"Failed to initialize execution engine: {e}")
            return False

    async def shutdown(self) -> bool:
        """Shutdown the execution engine."""
        try:
            return await self.broker.disconnect()
        except Exception as e:
            print(f"Failed to shutdown execution engine: {e}")
            return False

    def enable(self) -> bool:
        """Enable execution (after validation)."""
        if not self.enabled:
            self.enabled = True
            print("⚠️  Execution Engine ENABLED - trading will proceed")
            return True
        return True

    def disable(self) -> bool:
        """Disable execution (Kill Switch)."""
        if self.enabled:
            self.enabled = False
            print("⚠️  Execution Engine DISABLED - no trades will be placed")
            return True
        return True

    def is_enabled(self) -> bool:
        """Check if execution is enabled."""
        return self.enabled

    async def execute_decision(
        self,
        decision_action: ActionType,
        symbol: str = "XAUUSD",
        quantity: Optional[float] = None,
        decision_id: Optional[int] = None,
    ) -> Optional[Order]:
        """
        Execute a decision by placing an order.

        Args:
            decision_action: BUY, SELL, or WAIT
            symbol: Trading symbol (default XAUUSD)
            quantity: Quantity to trade (default from config)
            decision_id: Decision ID for audit trail

        Returns:
            Order object if successful, None otherwise
        """
        if not self.enabled:
            print("Execution disabled - not placing order")
            return None

        if decision_action == ActionType.WAIT:
            return None

        if not quantity:
            quantity = self.config.execution.default_position_size

        # Create order
        order = Order(
            order_id=f"ORD-{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            symbol=symbol,
            side=decision_action,
            quantity=quantity,
            order_type=OrderType.MARKET,
        )

        # Execute via broker
        result = await self.broker.place_order(order)

        if result.success:
            order.status = OrderStatus.FILLED
            order.filled_quantity = result.filled_quantity
            order.average_fill_price = result.average_fill_price
            order.broker_order_id = result.order_id
            self.pending_orders[order.order_id] = order
            print(f"✓ Order placed: {decision_action.value} {quantity} {symbol} @ {result.average_fill_price}")
            return order
        else:
            order.status = OrderStatus.REJECTED
            order.rejection_reason = result.message
            print(f"✗ Order rejected: {result.message}")
            return None

    async def close_trade(
        self,
        trade_id: str,
        symbol: str = "XAUUSD",
        quantity: Optional[float] = None,
    ) -> Optional[Order]:
        """
        Close a trade by placing an exit order.

        Args:
            trade_id: Trade ID being closed
            symbol: Trading symbol
            quantity: Quantity to close (default from trade)

        Returns:
            Order object if successful, None otherwise
        """
        if not self.enabled:
            print("Execution disabled - not closing trade")
            return None

        if trade_id not in self.active_trades:
            print(f"Trade {trade_id} not found")
            return None

        trade = self.active_trades[trade_id]

        if not quantity:
            quantity = trade.quantity

        # Determine exit side (opposite of entry)
        exit_side = ActionType.SELL if trade.side == PositionSide.LONG else ActionType.BUY

        # Create exit order
        order = Order(
            order_id=f"EXIT-{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            symbol=symbol,
            side=exit_side,
            quantity=quantity,
            order_type=OrderType.MARKET,
        )

        # Execute via broker
        result = await self.broker.close_position(symbol, quantity)

        if result.success:
            order.status = OrderStatus.FILLED
            order.filled_quantity = result.filled_quantity
            order.average_fill_price = result.average_fill_price
            order.broker_order_id = result.order_id
            print(f"✓ Trade closed: {trade_id} @ {result.average_fill_price}")
            return order
        else:
            order.status = OrderStatus.REJECTED
            order.rejection_reason = result.message
            print(f"✗ Trade close rejected: {result.message}")
            return None

    async def get_account_balance(self) -> Optional[float]:
        """Get current account balance."""
        try:
            return await self.broker.get_account_balance()
        except Exception as e:
            print(f"Failed to get account balance: {e}")
            return None

    async def get_open_positions(self) -> List[Dict]:
        """Get all open positions from broker."""
        try:
            return await self.broker.get_open_positions()
        except Exception as e:
            print(f"Failed to get open positions: {e}")
            return []

    async def get_connection_status(self) -> bool:
        """Check actual broker connection status."""
        try:
            return await self.broker.is_connected()
        except:
            return False

    def get_status(self) -> dict:
        """Get execution engine status."""
        return {
            "enabled": self.enabled,
            "pending_orders": len(self.pending_orders),
            "active_trades": len(self.active_trades),
            "kill_switch": "ARMED" if not self.enabled else "DISARMED",
        }
