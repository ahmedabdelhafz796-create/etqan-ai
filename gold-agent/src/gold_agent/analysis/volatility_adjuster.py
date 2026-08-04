"""Volatility Adjuster (Tier 4) — Dynamic position sizing based on market volatility."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import statistics


@dataclass
class VolatilityMetrics:
    """Volatility and market condition metrics."""
    timestamp: datetime
    current_volatility: float  # Historical volatility (%)
    volatility_percentile: float  # 0-100 (where we are in vol distribution)
    volatility_regime: str  # "low", "medium", "high", "extreme"
    adjusted_position_size: float  # Position size multiplier (0.5-2.0)
    adjusted_confidence: float  # Confidence adjustment due to vol (-20 to +20%)


class VolatilityAdjuster:
    """
    Tier 4: Advanced Analysis - Dynamic Position Sizing.

    Adjusts position size and confidence based on current market volatility.
    """

    def __init__(self, config):
        self.config = config
        self.volatility_history = []
        self.max_history = 100  # Keep last 100 volatility readings

        # Volatility regime thresholds (% per day)
        self.low_vol_threshold = 1.0
        self.medium_vol_threshold = 2.0
        self.high_vol_threshold = 3.5

        # Position size multipliers by regime
        self.position_multipliers = {
            "low": 1.5,      # Increase size when volatility is low
            "medium": 1.0,   # Normal size in medium volatility
            "high": 0.75,    # Reduce size when volatility is high
            "extreme": 0.5,  # Halve size in extreme volatility
        }

        # Confidence adjustments
        self.confidence_adjustments = {
            "low": 10.0,     # +10% confidence when vol is low
            "medium": 0.0,   # No adjustment in medium vol
            "high": -10.0,   # -10% confidence when vol is high
            "extreme": -20.0, # -20% confidence in extreme vol
        }

    def calculate_volatility(self, price_history: list) -> float:
        """
        Calculate historical volatility (standard deviation of returns).

        Args:
            price_history: List of prices (at least 2 required)

        Returns:
            Volatility as percentage per day
        """
        if len(price_history) < 2:
            return 0.0

        # Calculate daily returns
        returns = []
        for i in range(1, len(price_history)):
            ret = (price_history[i] - price_history[i-1]) / price_history[i-1]
            returns.append(ret)

        if not returns:
            return 0.0

        # Calculate standard deviation
        std_dev = statistics.stdev(returns) if len(returns) > 1 else 0.0

        # Annualize (sqrt(252) for daily data)
        annual_vol = std_dev * (252 ** 0.5)

        # Convert to daily percentage
        daily_vol = annual_vol / (252 ** 0.5) * 100

        return daily_vol

    def analyze_volatility(
        self,
        price_history: list,
        current_price: float,
        market_data = None,
    ) -> VolatilityMetrics:
        """
        Analyze current volatility and market regime.

        Args:
            price_history: Historical price data
            current_price: Current price
            market_data: Optional MarketData object for additional context (VIX, etc.)

        Returns:
            VolatilityMetrics with analysis results
        """
        # Calculate historical volatility
        current_vol = self.calculate_volatility(price_history)

        # Store in history
        self.volatility_history.append(current_vol)
        if len(self.volatility_history) > self.max_history:
            self.volatility_history.pop(0)

        # Calculate volatility percentile
        if len(self.volatility_history) > 1:
            sorted_vols = sorted(self.volatility_history)
            percentile = (sorted_vols.index(current_vol) / len(sorted_vols)) * 100
        else:
            percentile = 50.0

        # Determine regime
        if current_vol < self.low_vol_threshold:
            regime = "low"
        elif current_vol < self.medium_vol_threshold:
            regime = "medium"
        elif current_vol < self.high_vol_threshold:
            regime = "high"
        else:
            regime = "extreme"

        # Adjust for VIX if available
        if market_data and hasattr(market_data, 'vix') and market_data.vix:
            if market_data.vix > 40:
                regime = "extreme"
            elif market_data.vix > 30:
                regime = "high"

        # Get multipliers
        position_mult = self.position_multipliers.get(regime, 1.0)
        confidence_adj = self.confidence_adjustments.get(regime, 0.0)

        return VolatilityMetrics(
            timestamp=datetime.utcnow(),
            current_volatility=current_vol,
            volatility_percentile=percentile,
            volatility_regime=regime,
            adjusted_position_size=position_mult,
            adjusted_confidence=confidence_adj,
        )

    def adjust_position_size(
        self,
        base_size: float,
        volatility_metrics: VolatilityMetrics,
    ) -> float:
        """Adjust position size based on volatility."""
        adjusted_size = base_size * volatility_metrics.adjusted_position_size
        return adjusted_size

    def adjust_confidence(
        self,
        base_confidence: float,
        volatility_metrics: VolatilityMetrics,
    ) -> float:
        """Adjust confidence based on volatility."""
        adjusted = base_confidence + volatility_metrics.adjusted_confidence
        return max(0, min(100, adjusted))  # Clamp to 0-100

    def should_trade_in_current_regime(
        self,
        volatility_metrics: VolatilityMetrics,
        min_regime: str = "low",  # Minimum acceptable regime for trading
    ) -> bool:
        """
        Check if current volatility regime allows trading.

        Args:
            volatility_metrics: Current volatility analysis
            min_regime: Minimum acceptable regime ("low", "medium", "high")

        Returns:
            True if trading allowed in current regime
        """
        regime_hierarchy = {"low": 1, "medium": 2, "high": 3, "extreme": 4}
        current_level = regime_hierarchy.get(volatility_metrics.volatility_regime, 4)
        min_level = regime_hierarchy.get(min_regime, 2)

        return current_level <= min_level

    def get_status(self) -> dict:
        """Get volatility adjuster status."""
        if self.volatility_history:
            current = self.volatility_history[-1]
            avg = statistics.mean(self.volatility_history)
            std = statistics.stdev(self.volatility_history) if len(self.volatility_history) > 1 else 0
        else:
            current = 0.0
            avg = 0.0
            std = 0.0

        return {
            "current_volatility": current,
            "average_volatility": avg,
            "volatility_std_dev": std,
            "history_length": len(self.volatility_history),
            "low_threshold": self.low_vol_threshold,
            "high_threshold": self.high_vol_threshold,
        }
