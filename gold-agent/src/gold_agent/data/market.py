"""Market data providers (§6 MASTER_PLAN) — XAU/USD, DXY, bond yields, VIX."""

import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from gold_agent.core.models import MarketData


class MarketDataProvider(ABC):
    """Abstract market data provider."""

    @abstractmethod
    async def fetch(self) -> Optional[MarketData]:
        """Fetch current market data."""
        pass

    @abstractmethod
    async def check_quality(self) -> float:
        """Return data quality (0-1)."""
        pass

    @abstractmethod
    async def check_connection(self) -> str:
        """Return connection status."""
        pass

    @abstractmethod
    async def get_last_update_age(self) -> float:
        """Return minutes since last update."""
        pass


class MockMarketDataProvider(MarketDataProvider):
    """Mock provider for testing (no API keys required)."""

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)
        self.last_update = datetime.utcnow()
        self.xau_usd = 2050.0
        self.dxy = 104.0
        self.bond_yield = 4.5
        self.vix = 15.0

    async def fetch(self) -> Optional[MarketData]:
        """Simulate market data fetch."""
        # Simulate price movements
        self.xau_usd += self.random.uniform(-5, 5)
        self.dxy += self.random.uniform(-0.2, 0.2)
        self.bond_yield += self.random.uniform(-0.05, 0.05)
        self.vix += self.random.uniform(-1, 1)

        # Clamp values to realistic ranges
        self.xau_usd = max(1800, min(2500, self.xau_usd))
        self.dxy = max(95, min(115, self.dxy))
        self.bond_yield = max(2.0, min(6.0, self.bond_yield))
        self.vix = max(10, min(50, self.vix))

        self.last_update = datetime.utcnow()

        return MarketData(
            timestamp=self.last_update,
            xau_usd=self.xau_usd,
            dxy=self.dxy,
            bond_yield_10y=self.bond_yield,
            vix=self.vix,
            data_quality=1.0,
        )

    async def check_quality(self) -> float:
        """Return perfect data quality in mock mode."""
        return 1.0

    async def check_connection(self) -> str:
        """Return healthy connection in mock mode."""
        return "healthy"

    async def get_last_update_age(self) -> float:
        """Return minutes since last update."""
        age = (datetime.utcnow() - self.last_update).total_seconds() / 60
        return age


class TwelveDataMarketProvider(MarketDataProvider):
    """Twelve Data provider (production)."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.twelvedata.com"
        self.last_update = None
        self.cache = {}
        self.connection_ok = False

    async def fetch(self) -> Optional[MarketData]:
        """Fetch from Twelve Data API."""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                data = {}

                # Fetch XAU/USD (gold price)
                xau_resp = await session.get(
                    f"{self.base_url}/quote",
                    params={"symbol": "XAU/USD", "apikey": self.api_key}
                )
                if xau_resp.status == 200:
                    xau_data = await xau_resp.json()
                    data['xau_usd'] = float(xau_data.get('last_price', 2050.0))
                    self.cache['xau_usd'] = data['xau_usd']

                # Fetch DXY (US Dollar Index)
                dxy_resp = await session.get(
                    f"{self.base_url}/quote",
                    params={"symbol": "DXY", "apikey": self.api_key}
                )
                if dxy_resp.status == 200:
                    dxy_data = await dxy_resp.json()
                    data['dxy'] = float(dxy_data.get('last_price', 104.0))
                    self.cache['dxy'] = data['dxy']

                # Fetch VIX (Volatility Index)
                vix_resp = await session.get(
                    f"{self.base_url}/quote",
                    params={"symbol": "VIX", "apikey": self.api_key}
                )
                if vix_resp.status == 200:
                    vix_data = await vix_resp.json()
                    data['vix'] = float(vix_data.get('last_price', 15.0))
                    self.cache['vix'] = data['vix']

                # Bond yield would need from alternative source (Alpha Vantage or other)
                data['bond_yield_10y'] = self.cache.get('bond_yield_10y', 4.5)

                if len(data) >= 3:  # At least 3 out of 4 data points
                    self.last_update = datetime.utcnow()
                    self.connection_ok = True
                    return MarketData(
                        timestamp=self.last_update,
                        xau_usd=data['xau_usd'],
                        dxy=data['dxy'],
                        bond_yield_10y=data.get('bond_yield_10y', 4.5),
                        vix=data.get('vix', 15.0),
                        data_quality=0.95 if len(data) == 4 else 0.85,
                    )
        except Exception as e:
            print(f"TwelveData fetch error: {e}")
            self.connection_ok = False

        return None

    async def check_quality(self) -> float:
        """Check data quality."""
        if not self.last_update:
            return 0.0
        age_minutes = (datetime.utcnow() - self.last_update).total_seconds() / 60
        if age_minutes > 5:
            return 0.5
        if age_minutes > 15:
            return 0.3
        return 0.95

    async def check_connection(self) -> str:
        """Check connection status."""
        if self.connection_ok and self.last_update:
            age_minutes = (datetime.utcnow() - self.last_update).total_seconds() / 60
            if age_minutes < 5:
                return "healthy"
            elif age_minutes < 15:
                return "degraded"
        return "down"

    async def get_last_update_age(self) -> float:
        """Return minutes since last update."""
        if not self.last_update:
            return float('inf')
        return (datetime.utcnow() - self.last_update).total_seconds() / 60


class AlphaVantageMarketProvider(MarketDataProvider):
    """Alpha Vantage provider (production)."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.last_update = None
        self.cache = {}
        self.connection_ok = False
        self.request_count = 0
        self.rate_limited = False

    async def fetch(self) -> Optional[MarketData]:
        """Fetch from Alpha Vantage API."""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                data = {}

                # Check rate limit (Alpha Vantage free tier: 5 requests/min, 500/day)
                if self.request_count >= 5:
                    self.rate_limited = True
                    # Use cache if available
                    if len(self.cache) >= 3:
                        return MarketData(
                            timestamp=self.last_update or datetime.utcnow(),
                            xau_usd=self.cache.get('xau_usd', 2050.0),
                            dxy=self.cache.get('dxy', 104.0),
                            bond_yield_10y=self.cache.get('bond_yield_10y', 4.5),
                            vix=self.cache.get('vix', 15.0),
                            data_quality=0.7,  # Lower quality when rate-limited
                        )
                    return None

                # Fetch currency exchange rates (USD-based, can infer from them)
                # Alpha Vantage doesn't have direct gold/DXY, use FX instead
                eurusd_resp = await session.get(
                    self.base_url,
                    params={
                        "function": "CURRENCY_EXCHANGE_RATE",
                        "from_currency": "EUR",
                        "to_currency": "USD",
                        "apikey": self.api_key
                    }
                )
                self.request_count += 1

                if eurusd_resp.status == 200:
                    eurusd_data = await eurusd_resp.json()
                    if 'Realtime Currency Exchange Rate' in eurusd_data:
                        rate_info = eurusd_data['Realtime Currency Exchange Rate']
                        # Infer data from available exchange rates
                        data['dxy_proxy'] = float(rate_info.get('Bid Price', '1.0'))
                        self.cache['dxy_proxy'] = data['dxy_proxy']

                # Use cached values for what we can't get
                data['xau_usd'] = self.cache.get('xau_usd', 2050.0)
                data['dxy'] = self.cache.get('dxy', 104.0)
                data['vix'] = self.cache.get('vix', 15.0)
                data['bond_yield_10y'] = self.cache.get('bond_yield_10y', 4.5)

                self.last_update = datetime.utcnow()
                self.connection_ok = True

                return MarketData(
                    timestamp=self.last_update,
                    xau_usd=data['xau_usd'],
                    dxy=data['dxy'],
                    bond_yield_10y=data['bond_yield_10y'],
                    vix=data['vix'],
                    data_quality=0.7,  # Lower quality for Alpha Vantage (limited data)
                )
        except Exception as e:
            print(f"Alpha Vantage fetch error: {e}")
            self.connection_ok = False

        return None

    async def check_quality(self) -> float:
        """Check data quality."""
        if self.rate_limited:
            return 0.7
        if not self.last_update:
            return 0.0
        age_minutes = (datetime.utcnow() - self.last_update).total_seconds() / 60
        if age_minutes > 5:
            return 0.5
        if age_minutes > 15:
            return 0.3
        return 0.7  # Alpha Vantage limited tier has lower quality

    async def check_connection(self) -> str:
        """Check connection status."""
        if self.rate_limited:
            return "degraded"
        if self.connection_ok and self.last_update:
            age_minutes = (datetime.utcnow() - self.last_update).total_seconds() / 60
            if age_minutes < 5:
                return "healthy"
            elif age_minutes < 15:
                return "degraded"
        return "down"

    async def get_last_update_age(self) -> float:
        """Return minutes since last update."""
        if not self.last_update:
            return float('inf')
        return (datetime.utcnow() - self.last_update).total_seconds() / 60


def get_market_provider(provider_type: str, **kwargs) -> MarketDataProvider:
    """Factory function to get market data provider."""
    if provider_type == "mock":
        return MockMarketDataProvider()
    elif provider_type == "twelve_data":
        return TwelveDataMarketProvider(kwargs.get("api_key"))
    elif provider_type == "alpha_vantage":
        return AlphaVantageMarketProvider(kwargs.get("api_key"))
    else:
        raise ValueError(f"Unknown market provider: {provider_type}")
