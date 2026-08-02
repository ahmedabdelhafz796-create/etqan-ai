"""Technical indicators (§7 MASTER_PLAN) — RSI, MACD, Moving Averages."""

from datetime import datetime
from typing import List, Optional

import pandas as pd

from gold_agent.core.models import IndicatorValues, MarketData


class IndicatorEngine:
    """Calculates technical indicators for market data."""

    def __init__(self, config):
        self.config = config
        self.price_history: List[MarketData] = []
        self.max_history = 200  # Keep enough for 200-day MA

    def add_price(self, market_data: MarketData) -> None:
        """Add price data point to history."""
        self.price_history.append(market_data)
        if len(self.price_history) > self.max_history:
            self.price_history = self.price_history[-self.max_history :]

    def calculate(self, market_data: MarketData) -> IndicatorValues:
        """Calculate all indicators for current market data."""
        self.add_price(market_data)

        # Need at least 200 data points for full calculation
        if len(self.price_history) < self.config.indicators.ma_long:
            # Return partial indicators
            return IndicatorValues(
                timestamp=market_data.timestamp,
                rsi=50.0,  # Neutral
                macd=0.0,
                macd_signal=0.0,
                macd_histogram=0.0,
                ma_short=market_data.xau_usd,
                ma_long=market_data.xau_usd,
            )

        # Convert to pandas Series
        prices = [p.xau_usd for p in self.price_history]
        series = pd.Series(prices)

        # Calculate RSI
        rsi = self._calculate_rsi(series)

        # Calculate MACD
        macd, macd_signal, macd_histogram = self._calculate_macd(series)

        # Calculate Moving Averages
        ma_short, ma_long = self._calculate_mas(series)

        return IndicatorValues(
            timestamp=market_data.timestamp,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            ma_short=ma_short,
            ma_long=ma_long,
        )

    def _calculate_rsi(self, series: pd.Series) -> float:
        """Calculate Relative Strength Index (RSI) natively."""
        period = self.config.indicators.rsi_period
        if len(series) < period:
            return 50.0

        # Calculate price changes
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Avoid division by zero
        rs = gain / loss.replace(0, 0.00001)
        rsi = 100 - (100 / (1 + rs))

        rsi_value = rsi.iloc[-1]
        return float(rsi_value) if pd.notna(rsi_value) else 50.0

    def _calculate_macd(
        self, series: pd.Series
    ) -> tuple[float, float, float]:
        """Calculate MACD natively."""
        fast = self.config.indicators.macd_fast
        slow = self.config.indicators.macd_slow
        signal = self.config.indicators.macd_signal

        if len(series) < slow:
            return 0.0, 0.0, 0.0

        # Calculate exponential moving averages
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()

        # MACD line
        macd_line = ema_fast - ema_slow

        # Signal line (EMA of MACD)
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        # Histogram
        histogram = macd_line - signal_line

        return (
            float(macd_line.iloc[-1]) if pd.notna(macd_line.iloc[-1]) else 0.0,
            float(signal_line.iloc[-1]) if pd.notna(signal_line.iloc[-1]) else 0.0,
            float(histogram.iloc[-1]) if pd.notna(histogram.iloc[-1]) else 0.0,
        )

    def _calculate_mas(self, series: pd.Series) -> tuple[float, float]:
        """Calculate Moving Averages natively."""
        short_period = self.config.indicators.ma_short
        long_period = self.config.indicators.ma_long

        ma_short = series.rolling(window=short_period).mean().iloc[-1]
        ma_long = series.rolling(window=long_period).mean().iloc[-1]

        return float(ma_short), float(ma_long)

    def get_signal_count(self, indicators: IndicatorValues) -> int:
        """Count how many indicators are giving bullish signals."""
        count = 0

        # RSI oversold = bullish
        if indicators.rsi < self.config.indicators.rsi_oversold:
            count += 1

        # MACD histogram positive = bullish
        if indicators.macd_histogram > 0:
            count += 1

        # Price above short MA = bullish
        if indicators.ma_short > indicators.ma_long:
            count += 1

        return count

    def get_divergence(self, indicators: IndicatorValues) -> float:
        """
        Calculate divergence between indicators (0-1).
        0 = all aligned, 1 = maximum disagreement.
        """
        signals = [
            indicators.rsi < self.config.indicators.rsi_oversold,  # Bullish
            indicators.macd_histogram > 0,  # Bullish
            indicators.ma_short > indicators.ma_long,  # Bullish
        ]

        # Count divergence: bullish vs bearish
        bullish_count = sum(signals)
        bearish_count = len(signals) - bullish_count

        # 0.5 = maximum conflict (50/50), 0 or 1 = aligned
        divergence = min(bullish_count, bearish_count) / len(signals)
        return divergence
