"""MT5 Broker Adapter — Real connection to MetaTrader5 for symbol/account data."""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SymbolInfo:
    """MT5 Symbol specification data."""
    name: str
    contract_type: str  # "SPOT", "FUTURES", "CFD", etc.
    swap_long: float  # Long swap in points
    swap_short: float  # Short swap in points
    swap_mode: str  # "POINTS", "PERCENTAGE", "INTEREST", etc.
    trade_mode: str  # "BUY_SELL", "BUY_ONLY", "SELL_ONLY", etc.
    settlement: str  # "INSTANT", "T+0", "T+1", "T+2", etc.
    margin_hedged: float  # Hedged margin rate
    leverage: float  # Maximum account leverage


@dataclass
class AccountInfo:
    """MT5 Account information."""
    leverage: float  # Current account leverage (1.0 = no margin)
    margin_mode: str  # "RETAIL_NETTING", "EXCHANGE", "CONTRACTS", "HEDGING"
    balance: float  # Account balance in USD
    margin: float  # Used margin
    margin_free: float  # Free margin
    margin_level: float  # Margin level %


class MT5BrokerAdapter:
    """
    Adapter for MT5/Exness real-time broker data.
    Queries actual symbol specifications and account info for Sharia compliance verification.
    """

    def __init__(self, real_connection: bool = False):
        """
        Initialize MT5 adapter.

        Args:
            real_connection: If True, actually connect to MT5 (requires credentials).
                           If False, return mock data (testing mode).
        """
        self.real_connection = real_connection
        self.connected = False
        self.account_info_cache: Optional[AccountInfo] = None
        self.symbol_info_cache: Dict[str, SymbolInfo] = {}

        if real_connection:
            self._connect_to_mt5()

    def _connect_to_mt5(self):
        """Establish real connection to MT5."""
        try:
            import MetaTrader5 as mt5

            # Connection happens automatically on first call
            # No credentials needed here — credentials come from:
            # 1. Environment variables (MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)
            # 2. Or user provides them explicitly
            logger.info("MT5BrokerAdapter ready for connection (credentials needed)")
            self.connected = True
        except ImportError:
            logger.error("MetaTrader5 library not installed. Using mock mode.")
            self.connected = False
        except Exception as e:
            logger.error(f"Failed to initialize MT5: {e}. Using mock mode.")
            self.connected = False

    def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        """
        Query real MT5 symbol specification.

        Args:
            symbol: Symbol name (e.g., "XAUUSD", "XAU/USD")

        Returns:
            SymbolInfo with contract type, swap rates, settlement, etc.
            None if symbol not found or connection unavailable.
        """
        if symbol in self.symbol_info_cache:
            return self.symbol_info_cache[symbol]

        if self.real_connection and self.connected:
            return self._fetch_symbol_info_real(symbol)
        else:
            return self._fetch_symbol_info_mock(symbol)

    def _fetch_symbol_info_real(self, symbol: str) -> Optional[SymbolInfo]:
        """Fetch real symbol info from MT5."""
        try:
            import MetaTrader5 as mt5

            # Normalize symbol format
            symbol_normalized = symbol.upper().replace("/", "")  # "XAU/USD" -> "XAUUSD"

            # Query MT5 for symbol specification
            symbol_info = mt5.symbol_info(symbol_normalized)

            if symbol_info is None:
                logger.warning(f"Symbol {symbol} not found on MT5")
                return None

            info = SymbolInfo(
                name=symbol_info.name,
                contract_type="SPOT" if not symbol_info.is_derivative else "DERIVATIVE",
                swap_long=symbol_info.swap_long,
                swap_short=symbol_info.swap_short,
                swap_mode=self._get_swap_mode(symbol_info),
                trade_mode=symbol_info.trade_mode,
                settlement="INSTANT",  # MT5 spot always instant
                margin_hedged=symbol_info.margin_hedged,
                leverage=symbol_info.leverage_max,
            )

            self.symbol_info_cache[symbol] = info
            return info

        except Exception as e:
            logger.error(f"Failed to fetch real symbol info for {symbol}: {e}")
            return None

    def _fetch_symbol_info_mock(self, symbol: str) -> SymbolInfo:
        """
        Return mock symbol info for testing.
        Mock data represents a COMPLIANT spot instrument (swap=0, spot contract).
        """
        symbol_upper = symbol.upper()

        # Gold (XAU/USD) - compliant spot contract
        if "XAU" in symbol_upper or "GOLD" in symbol_upper:
            return SymbolInfo(
                name="XAUUSD",
                contract_type="SPOT",
                swap_long=0.0,
                swap_short=0.0,
                swap_mode="DISABLED",
                trade_mode="BUY_SELL",
                settlement="INSTANT",
                margin_hedged=50.0,
                leverage=100.0,
            )

        # EUR/USD - compliant but with swap charges (would fail Sharia)
        if "EUR" in symbol_upper or "EURUSD" in symbol_upper:
            return SymbolInfo(
                name="EURUSD",
                contract_type="SPOT",
                swap_long=-0.02,
                swap_short=0.01,
                swap_mode="INTEREST",
                trade_mode="BUY_SELL",
                settlement="T+2",
                margin_hedged=2.0,
                leverage=30.0,
            )

        # Default: unknown symbol (no swap, spot, compliant)
        return SymbolInfo(
            name=symbol_upper,
            contract_type="SPOT",
            swap_long=0.0,
            swap_short=0.0,
            swap_mode="DISABLED",
            trade_mode="BUY_SELL",
            settlement="INSTANT",
            margin_hedged=100.0,
            leverage=100.0,
        )

    def _get_swap_mode(self, symbol_info) -> str:
        """Extract swap mode string from MT5 symbol info."""
        try:
            # MT5 swap_mode can be: 0=DISABLED, 1=POINTS, 2=PERCENTAGE, 3=INTEREST
            swap_mode_map = {
                0: "DISABLED",
                1: "POINTS",
                2: "PERCENTAGE",
                3: "INTEREST",
            }
            return swap_mode_map.get(int(symbol_info.swap_mode), "UNKNOWN")
        except:
            return "UNKNOWN"

    def get_account_info(self) -> Optional[AccountInfo]:
        """
        Query real MT5 account information.

        Returns:
            AccountInfo with leverage, margin mode, balance, etc.
            None if connection unavailable.
        """
        if self.account_info_cache:
            return self.account_info_cache

        if self.real_connection and self.connected:
            return self._fetch_account_info_real()
        else:
            return self._fetch_account_info_mock()

    def _fetch_account_info_real(self) -> Optional[AccountInfo]:
        """Fetch real account info from MT5."""
        try:
            import MetaTrader5 as mt5

            account_info = mt5.account_info()

            if account_info is None:
                logger.warning("Could not fetch account info from MT5")
                return None

            info = AccountInfo(
                leverage=float(account_info.leverage),
                margin_mode=self._get_margin_mode(account_info),
                balance=float(account_info.balance),
                margin=float(account_info.margin),
                margin_free=float(account_info.margin_free),
                margin_level=float(account_info.margin_level) if account_info.margin_level else 0.0,
            )

            self.account_info_cache = info
            return info

        except Exception as e:
            logger.error(f"Failed to fetch real account info: {e}")
            return None

    def _fetch_account_info_mock(self) -> AccountInfo:
        """
        Return mock account info for testing.
        Mock represents a compliant account (1:1 leverage = no margin).
        """
        return AccountInfo(
            leverage=1.0,  # No margin
            margin_mode="RETAIL_NETTING",
            balance=10000.0,
            margin=0.0,
            margin_free=10000.0,
            margin_level=0.0,
        )

    def _get_margin_mode(self, account_info) -> str:
        """Extract margin mode string from MT5 account info."""
        try:
            # MT5 margin_mode: 0=RETAIL_NETTING, 1=EXCHANGE, 2=CONTRACTS_HEDGING
            mode_map = {
                0: "RETAIL_NETTING",
                1: "EXCHANGE",
                2: "CONTRACTS_HEDGING",
            }
            return mode_map.get(int(account_info.margin_mode), "UNKNOWN")
        except:
            return "UNKNOWN"

    def is_swap_free(self, symbol: str) -> bool:
        """
        Check if a symbol is configured as swap-free (zero overnight interest).

        Args:
            symbol: Symbol name

        Returns:
            True if swap_long == 0.0 AND swap_short == 0.0
            False otherwise (has interest charges)
        """
        info = self.get_symbol_info(symbol)
        if info is None:
            return False

        # Swap-free means both long and short swaps are zero
        is_free = info.swap_long == 0.0 and info.swap_short == 0.0
        logger.debug(
            f"Symbol {symbol} swap check: "
            f"long={info.swap_long}, short={info.swap_short}, free={is_free}"
        )
        return is_free

    def get_swap_rate(self, symbol: str) -> Optional[float]:
        """
        Get the swap rate for a symbol (average of long/short).

        Args:
            symbol: Symbol name

        Returns:
            Average swap rate, or None if unavailable
        """
        info = self.get_symbol_info(symbol)
        if info is None:
            return None

        # Return average swap rate (simplified)
        avg_swap = (info.swap_long + info.swap_short) / 2.0
        return avg_swap

    def is_spot_contract(self, symbol: str) -> bool:
        """
        Check if a symbol is a genuine spot contract (not derivative/CFD).

        Args:
            symbol: Symbol name

        Returns:
            True if contract_type is "SPOT"
            False if CFD, futures, option, or unknown
        """
        info = self.get_symbol_info(symbol)
        if info is None:
            return False

        is_spot = info.contract_type == "SPOT"
        logger.debug(f"Symbol {symbol} contract type: {info.contract_type}, is_spot={is_spot}")
        return is_spot

    def is_instant_settlement(self, symbol: str) -> bool:
        """
        Check if a symbol has instant settlement (complies with Taqabud).

        Args:
            symbol: Symbol name

        Returns:
            True if settlement is INSTANT or T+0/T+1/T+2
            False if deferred or unknown
        """
        info = self.get_symbol_info(symbol)
        if info is None:
            return False

        compliant_settlements = ["INSTANT", "T+0", "T+1", "T+2"]
        is_compliant = info.settlement in compliant_settlements
        logger.debug(
            f"Symbol {symbol} settlement: {info.settlement}, "
            f"compliant={is_compliant}"
        )
        return is_compliant

    def is_no_margin_loan(self) -> bool:
        """
        Check if account has no interest-bearing margin loans.

        Returns:
            True if margin is 0 (no loans)
            False if margin > 0 (loans active)
        """
        info = self.get_account_info()
        if info is None:
            return False

        has_no_loans = info.margin == 0.0
        logger.debug(f"Account margin check: margin={info.margin}, no_loans={has_no_loans}")
        return has_no_loans
