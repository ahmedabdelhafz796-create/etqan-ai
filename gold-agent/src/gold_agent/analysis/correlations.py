"""Correlation Agent (§2 Phase 2 MASTER_PLAN) — Asset correlation detection.

Analyzes relationships between:
- Gold/USD correlation (typically negative: weaker USD = higher gold)
- Gold/Rates correlation (typically negative: higher rates = lower gold)
- Gold/VIX correlation (typically positive: risk-off = higher gold)
- Gold/Equity correlation (typically negative in crisis)
"""

from datetime import datetime
from typing import Dict, Optional, Tuple
from gold_agent.core.models import MarketData


class CorrelationSignal:
    """Correlation signal result."""

    def __init__(
        self,
        timestamp: datetime,
        gold_usd_correlation: float,  # -1.0 to 1.0
        gold_rates_correlation: float,  # -1.0 to 1.0
        gold_vix_correlation: float,  # -1.0 to 1.0
        correlation_score: float,  # 0-100 (strength of correlations)
        regime: str,  # "normal", "stress", "flight-to-safety"
    ):
        self.timestamp = timestamp
        self.gold_usd_correlation = gold_usd_correlation
        self.gold_rates_correlation = gold_rates_correlation
        self.gold_vix_correlation = gold_vix_correlation
        self.correlation_score = correlation_score
        self.regime = regime


class CorrelationAgent:
    """Detects and analyzes asset correlations affecting gold."""

    def __init__(self, config):
        self.config = config
        self.gold_prices = []
        self.dxy_values = []
        self.yield_values = []
        self.vix_values = []
        self.max_history = 50  # Need enough history for meaningful correlation

    def analyze(self, market_data: MarketData) -> CorrelationSignal:
        """Analyze correlations and produce signal."""
        # Update price histories
        self.gold_prices.append(market_data.xau_usd)
        self.dxy_values.append(market_data.dxy)
        if market_data.bond_yield_10y:
            self.yield_values.append(market_data.bond_yield_10y)
        if market_data.vix:
            self.vix_values.append(market_data.vix)

        # Trim to max history
        if len(self.gold_prices) > self.max_history:
            self.gold_prices = self.gold_prices[-self.max_history:]
            self.dxy_values = self.dxy_values[-self.max_history:]
            self.yield_values = self.yield_values[-self.max_history:]
            self.vix_values = self.vix_values[-self.max_history:]

        # Calculate correlations
        gold_usd_corr = self._calculate_gold_usd_correlation()
        gold_rates_corr = self._calculate_gold_rates_correlation()
        gold_vix_corr = self._calculate_gold_vix_correlation()

        # Determine market regime
        regime = self._determine_regime(gold_usd_corr, gold_rates_corr, gold_vix_corr)

        # Calculate correlation score (how strong are the relationships?)
        correlation_score = self._calculate_correlation_score(
            gold_usd_corr, gold_rates_corr, gold_vix_corr
        )

        return CorrelationSignal(
            timestamp=market_data.timestamp,
            gold_usd_correlation=gold_usd_corr,
            gold_rates_correlation=gold_rates_corr,
            gold_vix_correlation=gold_vix_corr,
            correlation_score=correlation_score,
            regime=regime,
        )

    def _calculate_gold_usd_correlation(self) -> float:
        """
        Calculate Gold/USD correlation.

        Typically negative (weaker USD = higher gold prices).
        Returns: -1.0 to 1.0 (perfect negative to perfect positive)
        """
        if len(self.gold_prices) < 10 or len(self.dxy_values) < 10:
            return 0.0

        # Use recent data (last 30 points)
        recent_gold = self.gold_prices[-30:]
        recent_dxy = self.dxy_values[-30:]

        correlation = self._pearson_correlation(recent_gold, recent_dxy)
        return correlation

    def _calculate_gold_rates_correlation(self) -> float:
        """
        Calculate Gold/Rates correlation.

        Typically negative (higher rates = lower gold prices).
        Returns: -1.0 to 1.0 (perfect negative to perfect positive)
        """
        if len(self.gold_prices) < 10 or len(self.yield_values) < 10:
            return 0.0

        # Use recent data (last 30 points)
        recent_gold = self.gold_prices[-30:]
        recent_yields = self.yield_values[-30:]

        correlation = self._pearson_correlation(recent_gold, recent_yields)
        return correlation

    def _calculate_gold_vix_correlation(self) -> float:
        """
        Calculate Gold/VIX correlation.

        Typically positive (high VIX = higher gold prices, risk-off).
        Returns: -1.0 to 1.0 (perfect negative to perfect positive)
        """
        if len(self.gold_prices) < 10 or len(self.vix_values) < 10:
            return 0.0

        # Use recent data (last 30 points)
        recent_gold = self.gold_prices[-30:]
        recent_vix = self.vix_values[-30:]

        correlation = self._pearson_correlation(recent_gold, recent_vix)
        return correlation

    @staticmethod
    def _pearson_correlation(x: list, y: list) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) < 2 or len(y) < 2 or len(x) != len(y):
            return 0.0

        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
        denominator_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5

        if denominator_x == 0 or denominator_y == 0:
            return 0.0

        correlation = numerator / (denominator_x * denominator_y)
        return max(-1.0, min(1.0, correlation))

    def _determine_regime(
        self, gold_usd: float, gold_rates: float, gold_vix: float
    ) -> str:
        """Determine market regime based on correlations."""
        # Normal regime: correlations as expected
        # Stress regime: USD correlation breaks down (flight to safety)
        # Flight-to-safety: VIX correlation strengthens (panic)

        if gold_vix > 0.5 and gold_usd > -0.3:
            return "flight-to-safety"  # Risk-off, normal correlation dynamics broken
        elif gold_usd < -0.6 and gold_rates < -0.5:
            return "normal"  # Standard correlations holding
        else:
            return "stress"  # Regime uncertainty

    def _calculate_correlation_score(
        self, gold_usd: float, gold_rates: float, gold_vix: float
    ) -> float:
        """
        Calculate correlation score (0-100).

        Higher score means correlations are working as expected
        (better predictability).
        """
        # Expected correlations:
        # Gold/USD: -0.6 to -0.8 (negative, strong)
        # Gold/Rates: -0.4 to -0.6 (negative, moderate)
        # Gold/VIX: 0.3 to 0.5 (positive, weak to moderate)

        # Measure deviation from expected
        usd_strength = abs(gold_usd + 0.70) * 50  # Closer to -0.70 is better
        rates_strength = abs(gold_rates + 0.50) * 50  # Closer to -0.50 is better
        vix_strength = abs(gold_vix - 0.40) * 50  # Closer to 0.40 is better

        # Weight: USD 50%, Rates 30%, VIX 20%
        score = (100 - usd_strength) * 0.5 + (100 - rates_strength) * 0.3 + (
            100 - vix_strength
        ) * 0.2

        return max(0.0, min(100.0, score))

    def get_correlation_quality(self) -> str:
        """Qualitative assessment of correlation quality."""
        if len(self.gold_prices) < 10:
            return "insufficient_data"

        gold_usd = self._calculate_gold_usd_correlation()
        gold_rates = self._calculate_gold_rates_correlation()
        gold_vix = self._calculate_gold_vix_correlation()

        # Count how many correlations are in expected range
        strong_correlations = 0

        if -0.8 <= gold_usd <= -0.5:  # Negative, as expected
            strong_correlations += 1

        if -0.7 <= gold_rates <= -0.3:  # Negative, as expected
            strong_correlations += 1

        if 0.1 <= gold_vix <= 0.7:  # Positive, as expected
            strong_correlations += 1

        if strong_correlations >= 2:
            return "reliable"
        elif strong_correlations == 1:
            return "moderate"
        else:
            return "unreliable"

    def get_correlation_insights(
        self,
    ) -> Dict[str, str]:
        """Generate insights from current correlations."""
        gold_usd = self._calculate_gold_usd_correlation()
        gold_rates = self._calculate_gold_rates_correlation()
        gold_vix = self._calculate_gold_vix_correlation()

        insights = {}

        # USD correlation insight
        if gold_usd < -0.6:
            insights["usd"] = "Strong negative correlation: weaker USD supports gold"
        elif gold_usd > -0.3:
            insights["usd"] = "Weak or broken USD correlation: unusual market conditions"
        else:
            insights["usd"] = "Moderate negative correlation: normal USD/gold dynamics"

        # Rates correlation insight
        if gold_rates < -0.5:
            insights["rates"] = "Strong negative correlation: rising rates pressure gold"
        elif gold_rates > -0.2:
            insights["rates"] = "Weak rates correlation: gold decoupling from yields"
        else:
            insights["rates"] = "Moderate negative correlation: normal rate sensitivity"

        # VIX correlation insight
        if gold_vix > 0.5:
            insights["vix"] = "Strong positive VIX correlation: gold benefits from risk-off"
        elif gold_vix < 0.1:
            insights["vix"] = "Weak VIX correlation: risk sentiment not driving gold"
        else:
            insights["vix"] = "Moderate positive VIX correlation: typical risk-off behavior"

        return insights
