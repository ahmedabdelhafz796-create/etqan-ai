"""Order Manager (Tier 1) — Track order execution and status."""

from datetime import datetime
from typing import Optional, List, Dict

from src.gold_agent.core.models import Order, OrderStatus


class OrderManager:
    """Manages all orders and their lifecycle."""

    def __init__(self, config):
        self.config = config
        self.orders: Dict[str, Order] = {}  # order_id -> Order

    def register_order(self, order: Order) -> None:
        """Register a new order."""
        self.orders[order.order_id] = order

    def update_order_status(
        self,
        order_id: str,
        status: OrderStatus,
        filled_quantity: Optional[float] = None,
        average_fill_price: Optional[float] = None,
        rejection_reason: Optional[str] = None,
    ) -> Optional[Order]:
        """Update order status."""
        if order_id not in self.orders:
            return None

        order = self.orders[order_id]
        order.status = status

        if filled_quantity is not None:
            order.filled_quantity = filled_quantity

        if average_fill_price is not None:
            order.average_fill_price = average_fill_price

        if rejection_reason is not None:
            order.rejection_reason = rejection_reason

        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get an order by ID."""
        return self.orders.get(order_id)

    def get_pending_orders(self) -> List[Order]:
        """Get all pending orders."""
        return [
            order for order in self.orders.values()
            if order.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]
        ]

    def get_filled_orders(self) -> List[Order]:
        """Get all filled orders."""
        return [
            order for order in self.orders.values()
            if order.status == OrderStatus.FILLED
        ]

    def get_rejected_orders(self) -> List[Order]:
        """Get all rejected orders."""
        return [
            order for order in self.orders.values()
            if order.status == OrderStatus.REJECTED
        ]

    def get_orders_by_symbol(self, symbol: str) -> List[Order]:
        """Get orders for a specific symbol."""
        return [
            order for order in self.orders.values()
            if order.symbol == symbol
        ]

    def get_orders_by_side(self, side: str) -> List[Order]:
        """Get orders for a specific side (BUY/SELL)."""
        return [
            order for order in self.orders.values()
            if order.side.value == side
        ]

    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Get orders with a specific status."""
        return [
            order for order in self.orders.values()
            if order.status == status
        ]

    def get_orders_today(self) -> List[Order]:
        """Get all orders placed today."""
        today = datetime.utcnow().date()
        return [
            order for order in self.orders.values()
            if order.timestamp.date() == today
        ]

    def get_total_filled_quantity(self, symbol: str) -> float:
        """Get total filled quantity for a symbol."""
        orders = self.get_orders_by_symbol(symbol)
        return sum(order.filled_quantity for order in orders)

    def get_average_fill_price(self, symbol: str) -> Optional[float]:
        """Get average fill price for a symbol."""
        filled_orders = [
            order for order in self.get_orders_by_symbol(symbol)
            if order.average_fill_price is not None
        ]

        if not filled_orders:
            return None

        total_value = sum(
            order.average_fill_price * order.filled_quantity
            for order in filled_orders
        )
        total_qty = sum(order.filled_quantity for order in filled_orders)

        if total_qty == 0:
            return None

        return total_value / total_qty

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]

        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
            return False  # Cannot cancel already filled/cancelled/rejected orders

        order.status = OrderStatus.CANCELLED
        return True

    def get_status(self) -> dict:
        """Get order manager status."""
        orders_today = self.get_orders_today()
        pending = self.get_pending_orders()
        filled = self.get_filled_orders()
        rejected = self.get_rejected_orders()

        return {
            "total_orders": len(self.orders),
            "orders_today": len(orders_today),
            "pending_orders": len(pending),
            "filled_orders": len(filled),
            "rejected_orders": len(rejected),
            "success_rate": len(filled) / (len(filled) + len(rejected)) if (len(filled) + len(rejected)) > 0 else 0,
        }
