"""MT5 Broker Adapter — MetaTrader 5 integration."""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional

from gold_agent.core.models import Order, OrderStatus
from gold_agent.execution.engine import BrokerAdapter, ExecutionResult

logger = logging.getLogger(__name__)


class MT5BrokerAdapter(BrokerAdapter):
    """MetaTrader 5 broker adapter with connection recovery."""

    def __init__(self, config):
        self.config = config
        self.connected = False
        self.mt5 = None
        self.login = config.execution.brokers.mt5.login
        self.password = config.execution.brokers.mt5.password
        self.server = config.execution.brokers.mt5.server
        self.max_retries = 3
        self.failed_connection_attempts = 0

    async def connect(self) -> bool:
        """Connect to MT5 with retry logic (exponential backoff)."""
        for attempt in range(self.max_retries):
            try:
                import MetaTrader5 as mt5

                self.mt5 = mt5

                if not mt5.initialize(login=self.login, password=self.password, server=self.server):
                    logger.warning(f"MT5 initialization failed (attempt {attempt+1}): {mt5.last_error()}")
                    if attempt < self.max_retries - 1:
                        # Exponential backoff: 2^attempt seconds
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return False

                self.connected = True
                self.failed_connection_attempts = 0
                account_info = mt5.account_info()
                if account_info:
                    logger.info(f"✓ MT5 Connected: {account_info.name} (Balance: ${account_info.balance:,.2f})")
                return True
            except ImportError:
                logger.error("MetaTrader5 library not installed: pip install MetaTrader5")
                return False
            except Exception as e:
                logger.warning(f"MT5 connection failed (attempt {attempt+1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        logger.error(f"MT5 connection failed after {self.max_retries} attempts")
        return False

    async def disconnect(self) -> bool:
        """Disconnect from MT5."""
        try:
            if self.mt5:
                self.mt5.shutdown()
            self.connected = False
            return True
        except Exception as e:
            print(f"MT5 disconnection failed: {e}")
            return False

    async def is_connected(self) -> bool:
        """Check if connected."""
        if not self.mt5:
            return False
        return self.mt5.terminal_info().connected

    async def _ensure_connected(self) -> bool:
        """Verify connection, reconnect if needed."""
        if not self.connected or not self.mt5:
            logger.warning("MT5 connection missing, attempting to connect...")
            return await self.connect()

        try:
            if not self.mt5.terminal_info().connected:
                logger.warning("MT5 connection lost, attempting to reconnect...")
                return await self.connect()
        except Exception as e:
            logger.warning(f"Connection check failed: {e}, attempting reconnect...")
            return await self.connect()

        return True

    async def place_order(self, order: Order) -> ExecutionResult:
        """Place an order via MT5 with connection verification."""
        if not await self._ensure_connected():
            return ExecutionResult(
                success=False,
                message="Failed to establish MT5 connection"
            )

        try:
            import MetaTrader5 as mt5

            # Map our ActionType to MT5 order type
            action_map = {
                "BUY": mt5.ORDER_TYPE_BUY,
                "SELL": mt5.ORDER_TYPE_SELL,
            }

            order_type = action_map.get(order.side.value, mt5.ORDER_TYPE_BUY)

            # Get current symbol price
            tick = mt5.symbol_info_tick(order.symbol)
            if not tick:
                return ExecutionResult(
                    success=False,
                    message=f"Cannot get price for {order.symbol}"
                )

            price = tick.ask if order.side.value == "BUY" else tick.bid

            # Create order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": order.symbol,
                "volume": order.quantity,
                "type": order_type,
                "price": price,
                "comment": f"Autonomous Agent",
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Add stop loss if specified
            if order.stop_price:
                request["sl"] = order.stop_price

            # Add take profit if specified
            if order.price:
                request["tp"] = order.price

            # Send order
            result = mt5.order_send(request)

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                return ExecutionResult(
                    success=True,
                    order_id=str(result.deal),
                    message=f"Order executed",
                    filled_quantity=order.quantity,
                    average_fill_price=price
                )
            else:
                return ExecutionResult(
                    success=False,
                    message=f"MT5 error: {result.comment}"
                )

        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"MT5 order placement failed: {str(e)}"
            )

    async def cancel_order(self, order_id: str) -> ExecutionResult:
        """Cancel an order with connection verification."""
        try:
            if not await self._ensure_connected():
                return ExecutionResult(
                    success=False,
                    message="Failed to establish MT5 connection"
                )

            import MetaTrader5 as mt5

            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": int(order_id),
            }

            result = self.mt5.order_send(request)

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                return ExecutionResult(
                    success=True,
                    message=f"Order {order_id} cancelled"
                )
            else:
                return ExecutionResult(
                    success=False,
                    message=f"Failed to cancel order: {result.comment}"
                )

        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Cancel failed: {str(e)}"
            )

    async def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get order status with connection verification."""
        try:
            if not await self._ensure_connected():
                return None

            order = self.mt5.orders_get(ticket=int(order_id))
            if order:
                return order[0]  # Return MT5 order structure
            return None
        except Exception:
            return None

    async def close_position(self, symbol: str, quantity: float) -> ExecutionResult:
        """Close a position with connection verification."""
        try:
            if not await self._ensure_connected():
                return ExecutionResult(
                    success=False,
                    message="Failed to establish MT5 connection"
                )

            import MetaTrader5 as mt5

            # Get current position
            positions = self.mt5.positions_get(symbol=symbol)
            if not positions:
                return ExecutionResult(
                    success=False,
                    message=f"No position in {symbol}"
                )

            position = positions[0]

            # Determine exit action (opposite of position direction)
            if position.type == mt5.ORDER_TYPE_BUY:
                action_type = mt5.ORDER_TYPE_SELL
            else:
                action_type = mt5.ORDER_TYPE_BUY

            # Get current price
            tick = self.mt5.symbol_info_tick(symbol)
            if not tick:
                return ExecutionResult(
                    success=False,
                    message=f"Cannot get price for {symbol}"
                )

            price = tick.bid if action_type == mt5.ORDER_TYPE_SELL else tick.ask

            # Create close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": quantity,
                "type": action_type,
                "price": price,
                "position": position.ticket,
                "comment": "Autonomous Agent - Position Close",
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = self.mt5.order_send(request)

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                return ExecutionResult(
                    success=True,
                    order_id=str(result.deal),
                    message=f"Position closed",
                    filled_quantity=quantity,
                    average_fill_price=price
                )
            else:
                return ExecutionResult(
                    success=False,
                    message=f"Failed to close position: {result.comment}"
                )

        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Close position failed: {str(e)}"
            )

    async def get_account_balance(self) -> Optional[float]:
        """Get account balance with connection verification."""
        try:
            if not await self._ensure_connected():
                return None

            account_info = self.mt5.account_info()
            if account_info:
                return account_info.balance
            return None
        except Exception:
            return None

    async def get_open_positions(self) -> List[Dict]:
        """Get all open positions with connection verification."""
        try:
            if not await self._ensure_connected():
                return []

            positions = self.mt5.positions_get()
            if not positions:
                return []

            result = []
            for pos in positions:
                result.append({
                    "symbol": pos.symbol,
                    "quantity": pos.volume,
                    "entry_price": pos.price_open,
                    "current_price": pos.price_current,
                    "unrealized_p_l": pos.profit,
                    "type": "LONG" if pos.type == 0 else "SHORT",
                })
            return result
        except Exception:
            return []
