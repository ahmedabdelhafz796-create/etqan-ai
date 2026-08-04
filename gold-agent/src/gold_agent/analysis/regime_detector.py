"""Market Regime Detector (Tier 4) — Identify market conditions and trading regimes."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import statistics


@dataclass
class RegimeAnalysis:
    """Market regime and condition analysis."""
    timestamp: datetime
    regime: str  # "trending_up", "trending_down", "mean_reverting", "range_bound", "volatile", "consolidating"
    trend_strength: float  # 0-100 (how strong is the trend)
    correlation_mean_reversion: float  # 0-1 (0=no mean reversion, 1=perfect)
    price_from_ma50: float  # % away from 50-day MA
    price_from_ma200: float  # % away from 200-day MA
    recent_volatility: float  # Recent price volatility
    breakout_potential: float  # 0-100 (likelihood of breakout)
    mean_reversion_potential: float  # 0-100 (likelihood of reversion)


class RegimeDetector:
    """
    Tier 4: Advanced Analysis - Market Regime Detection.

    Identifies current market conditions to adapt trading strategy.
    """

    def __init__(self, config):
        self.config = config
        self.price_history: List[float] = []
        self.max_history = 200

    def analyze_regime(
        self,
        prices: List[float],
        ma_short: float,
        ma_long: float,
        current_volatility: float,
    ) -> RegimeAnalysis:
        """
        Analyze market regime from price history.

        Args:
            prices: Price history (list)
            ma_short: 50-period moving average
            ma_long: 200-period moving average
            current_volatility: Current volatility metric

        Returns:
            RegimeAnalysis with regime and metrics
        """
        if len(prices) < 20:
            return RegimeAnalysis(
                timestamp=datetime.utcnow(),
                regime="unknown",
                trend_strength=0.0,
                correlation_mean_reversion=0.0,
                price_from_ma50=0.0,
                price_from_ma200=0.0,
                recent_volatility=current_volatility,
                breakout_potential=0.0,
                mean_reversion_potential=0.0,
            )

        current_price = prices[-1]

        # Calculate trend
        trend_strength = self._calculate_trend_strength(prices)
        trend_direction = "up" if trend_strength > 0 else "down"

        # Calculate mean reversion correlation
        mr_correlation = self._calculate_mean_reversion(prices)

        # Distance from moving averages
        price_from_ma50 = ((current_price - ma_short) / ma_short) * 100 if ma_short > 0 else 0
        price_from_ma200 = ((current_price - ma_long) / ma_long) * 100 if ma_long > 0 else 0

        # Determine regime
        regime = self._determine_regime(
            trend_strength=abs(trend_strength),
            mr_correlation=mr_correlation,
            price_from_ma50=price_from_ma50,
            price_from_ma200=price_from_ma200,
            volatility=current_volatility,
        )

        # Calculate breakout potential
        breakout_potential = self._calculate_breakout_potential(prices)

        # Calculate mean reversion potential
        mean_reversion_potential = mr_correlation * 100

        return RegimeAnalysis(
            timestamp=datetime.utcnow(),
            regime=regime,
            trend_strength=abs(trend_strength) * 100,  # Convert to 0-100 scale
            correlation_mean_reversion=mr_correlation,
            price_from_ma50=price_from_ma50,
            price_from_ma200=price_from_ma200,
            recent_volatility=current_volatility,
            breakout_potential=breakout_potential,
            mean_reversion_potential=mean_reversion_potential,
        )

    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """
        Calculate trend strength using linear regression.

        Returns:
            Trend strength (-100 to +100, positive = uptrend)
        """
        if len(prices) < 2:
            return 0.0

        recent_prices = prices[-30:]  # Last 30 candles
        x = list(range(len(recent_prices)))
        y = recent_prices

        # Calculate linear regression slope
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(len(x)))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(len(x)))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Normalize slope to -100 to +100
        normalized = (slope / (y_mean * 0.01)) * 100
        return max(-100, min(100, normalized))

    def _calculate_mean_reversion(self, prices: List[float]) -> float:
        """
        Calculate mean reversion strength.

        Returns:
            Correlation with mean (0-1, higher = stronger mean reversion)
        """
        if len(prices) < 10:
            return 0.0

        recent_prices = prices[-30:]
        mean_price = statistics.mean(recent_prices)

        # Calculate distance from mean and velocity
        distances = [abs(p - mean_price) for p in recent_prices]
        avg_distance = statistics.mean(distances)

        # If prices oscillate around mean, mean reversion is high
        if avg_distance == 0:
            return 0.0

        # Look for oscillations (price going up/down/up pattern)
        changes = [recent_prices[i+1] - recent_prices[i] for i in range(len(recent_prices)-1)]
        sign_changes = sum(1 for i in range(len(changes)-1) if changes[i] * changes[i+1] < 0)

        # Higher sign changes = more oscillation = more mean reversion
        oscillation_score = sign_changes / len(changes) if changes else 0.0

        return min(1.0, oscillation_score)

    def _determine_regime(
        self,
        trend_strength: float,
        mr_correlation: float,
        price_from_ma50: float,
        price_from_ma200: float,
        volatility: float,
    ) -> str:
        """Determine market regime from metrics."""
        # Trending up
        if trend_strength > 50 and price_from_ma50 > 2 and price_from_ma200 > 5:
            return "trending_up"

        # Trending down
        if trend_strength > 50 and price_from_ma50 < -2 and price_from_ma200 < -5:
            return "trending_down"

        # Mean reverting
        if mr_correlation > 0.6 and abs(price_from_ma50) > 3:
            return "mean_reverting"

        # Range bound
        if trend_strength < 30 and mr_correlation > 0.4 and abs(price_from_ma50) < 2:
            return "range_bound"

        # Volatile
        if volatility > 3.0 and trend_strength < 30:
            return "volatile"

        # Consolidating
        if trend_strength < 20 and volatility < 1.0:
            return "consolidating"

        return "consolidating"

    def _calculate_breakout_potential(self, prices: List[float]) -> float:
        """
        Calculate probability of breakout (price leaving range).

        Returns:
            0-100 score
        """
        if len(prices) < 20:
            return 0.0

        recent = prices[-20:]
        high = max(recent)
        low = min(recent)
        range_size = high - low

        if range_size == 0:
            return 0.0

        # Calculate how close we are to range extremes
        current = prices[-1]
        distance_from_high = (high - current) / range_size
        distance_from_low = (current - low) / range_size

        # Higher if at edge of range
        edge_proximity = max(distance_from_high, distance_from_low)

        # Check for increasing volatility (sign of breakout)
        recent_vol = statistics.stdev([prices[i+1] - prices[i] for i in range(len(prices)-10, len(prices)-1)])
        older_vol = statistics.stdev([prices[i+1] - prices[i] for i in range(len(prices)-20, len(prices)-10)]) if len(prices) >= 20 else 0.001

        vol_increase = recent_vol / older_vol if older_vol > 0 else 1.0

        breakout_score = (edge_proximity * 50 + min(vol_increase - 1, 1) * 50)
        return max(0, min(100, breakout_score))

    def get_best_strategy_for_regime(self, regime: RegimeAnalysis) -> str:
        """
        Recommend best trading strategy for current regime.

        Returns:
            Strategy name: "breakout", "mean_reversion", "trend_following", "range_trading"
        """
        if regime.regime == "trending_up" or regime.regime == "trending_down":
            return "trend_following"
        elif regime.regime == "mean_reverting":
            return "mean_reversion"
        elif regime.regime == "range_bound":
            return "range_trading"
        elif regime.regime == "volatile":
            return "breakout"
        else:
            return "neutral"

    def get_status(self) -> dict:
        """Get regime detector status."""
        return {
            "price_history_length": len(self.price_history),
            "max_history": self.max_history,
        }
