"""OANDA Broker Adapter — OANDA v20 API integration."""

from datetime import datetime
from typing import List, Dict, Optional

from gold_agent.core.models import Order, OrderStatus
from gold_agent.execution.engine import BrokerAdapter, ExecutionResult


class OANDABrokerAdapter(BrokerAdapter):
    """OANDA v20 API broker adapter."""

    def __init__(self, config):
        self.config = config
        self.connected = False
        self.api_key = config.execution.brokers.oanda.api_key
        self.account_id = config.execution.brokers.oanda.account_id
        self.environment = config.execution.brokers.oanda.environment  # "practice" or "live"
        self.client = None
        self.session = None

    async def connect(self) -> bool:
        """Connect to OANDA."""
        try:
            import requests

            self.session = requests.Session()

            # Set up API headers
            base_url = f"https://{self.environment}-stream.oanda.com/v3" if self.environment == "practice" else f"https://stream.oanda.com/v3"
            self.base_url = base_url
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })

            # Test connection
            response = self.session.get(f"{self.base_url}/accounts/{self.account_id}")

            if response.status_code == 200:
                account_info = response.json()
                self.connected = True
                balance = account_info.get("account", {}).get("balance", 0)
                print(f"✓ OANDA Connected (Balance: ${balance})")
                return True
            else:
                print(f"OANDA connection failed: {response.status_code}")
                return False

        except ImportError:
            print("requests library not installed: pip install requests")
            return False
        except Exception as e:
            print(f"OANDA connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """Disconnect from OANDA."""
        try:
            if self.session:
                self.session.close()
            self.connected = False
            return True
        except Exception as e:
            print(f"OANDA disconnection failed: {e}")
            return False

    async def is_connected(self) -> bool:
        """Check if connected."""
        return self.connected

    async def place_order(self, order: Order) -> ExecutionResult:
        """Place an order via OANDA API."""
        if not self.connected or not self.session:
            return ExecutionResult(
                success=False,
                message="Not connected to OANDA"
            )

        try:
            # Map our ActionType to OANDA side
            side_map = {
                "BUY": "BUY",
                "SELL": "SELL",
            }

            side = side_map.get(order.side.value, "BUY")

            # Create order payload
            payload = {
                "order": {
                    "instrument": order.symbol,
                    "units": int(order.quantity) if side == "BUY" else -int(order.quantity),
                    "type": "MARKET",
                    "timeInForce": "FOK",
                }
            }

            # Add stop loss if specified
            if order.stop_price:
                payload["order"]["stopLossOnFill"] = {"price": str(order.stop_price)}

            # Add take profit if specified
            if order.price:
                payload["order"]["takeProfitOnFill"] = {"price": str(order.price)}

            # Send order
            response = self.session.post(
                f"{self.base_url}/accounts/{self.account_id}/orders",
                json=payload
            )

            if response.status_code in [200, 201]:
                data = response.json()
                trade = data.get("orderFillTransaction", {})
                price = float(trade.get("price", 0))

                return ExecutionResult(
                    success=True,
                    order_id=str(trade.get("id", "")),
                    message=f"Order executed",
                    filled_quantity=order.quantity,
                    average_fill_price=price
                )
            else:
                error_msg = response.json().get("errorMessage", "Unknown error")
                return ExecutionResult(
                    success=False,
                    message=f"OANDA error: {error_msg}"
                )

        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"OANDA order placement failed: {str(e)}"
            )

    async def cancel_order(self, order_id: str) -> ExecutionResult:
        """Cancel an order."""
        try:
            if not self.connected or not self.session:
                return ExecutionResult(
                    success=False,
                    message="Not connected to OANDA"
                )

            response = self.session.put(
                f"{self.base_url}/accounts/{self.account_id}/orders/{order_id}/cancel"
            )

            if response.status_code == 200:
                return ExecutionResult(
                    success=True,
                    message=f"Order {order_id} cancelled"
                )
            else:
                return ExecutionResult(
                    success=False,
                    message=f"Failed to cancel order"
                )

        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Cancel failed: {str(e)}"
            )

    async def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get order status."""
        try:
            if not self.connected or not self.session:
                return None

            response = self.session.get(
                f"{self.base_url}/accounts/{self.account_id}/orders/{order_id}"
            )

            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    async def close_position(self, symbol: str, quantity: float) -> ExecutionResult:
        """Close a position."""
        try:
            if not self.connected or not self.session:
                return ExecutionResult(
                    success=False,
                    message="Not connected to OANDA"
                )

            # Get current position
            response = self.session.get(
                f"{self.base_url}/accounts/{self.account_id}/positions/{symbol}"
            )

            if response.status_code != 200:
                return ExecutionResult(
                    success=False,
                    message=f"No position in {symbol}"
                )

            position = response.json().get("position", {})
            current_units = position.get("long", {}).get("units", 0)

            if current_units == 0:
                return ExecutionResult(
                    success=False,
                    message=f"No open position in {symbol}"
                )

            # Create close order
            payload = {
                "longUnits": "ALL" if current_units > 0 else "NONE",
                "shortUnits": "ALL" if current_units < 0 else "NONE",
            }

            response = self.session.put(
                f"{self.base_url}/accounts/{self.account_id}/positions/{symbol}/close",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                # Extract price from close transactions
                price = float(data.get("longOrderFillTransaction", {}).get("price", 0)) or \
                        float(data.get("shortOrderFillTransaction", {}).get("price", 0))

                return ExecutionResult(
                    success=True,
                    message=f"Position closed",
                    filled_quantity=quantity,
                    average_fill_price=price
                )
            else:
                return ExecutionResult(
                    success=False,
                    message=f"Failed to close position"
                )

        except Exception as e:
            return ExecutionResult(
                success=False,
                message=f"Close position failed: {str(e)}"
            )

    async def get_account_balance(self) -> Optional[float]:
        """Get account balance."""
        try:
            if not self.connected or not self.session:
                return None

            response = self.session.get(f"{self.base_url}/accounts/{self.account_id}")

            if response.status_code == 200:
                account = response.json().get("account", {})
                return float(account.get("balance", 0))
            return None
        except Exception:
            return None

    async def get_open_positions(self) -> List[Dict]:
        """Get all open positions."""
        try:
            if not self.connected or not self.session:
                return []

            response = self.session.get(
                f"{self.base_url}/accounts/{self.account_id}/positions"
            )

            if response.status_code != 200:
                return []

            positions = response.json().get("positions", [])
            result = []

            for pos in positions:
                if pos.get("long", {}).get("units", 0) != 0:
                    result.append({
                        "symbol": pos["instrument"],
                        "quantity": float(pos["long"]["units"]),
                        "entry_price": float(pos["long"].get("averagePrice", 0)),
                        "current_price": float(pos.get("closeoutAsk", 0)),
                        "unrealized_p_l": float(pos["long"].get("unrealizedPL", 0)),
                        "type": "LONG",
                    })

                if pos.get("short", {}).get("units", 0) != 0:
                    result.append({
                        "symbol": pos["instrument"],
                        "quantity": abs(float(pos["short"]["units"])),
                        "entry_price": float(pos["short"].get("averagePrice", 0)),
                        "current_price": float(pos.get("closeoutBid", 0)),
                        "unrealized_p_l": float(pos["short"].get("unrealizedPL", 0)),
                        "type": "SHORT",
                    })

            return result
        except Exception:
            return []
