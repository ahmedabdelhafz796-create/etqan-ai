"""Macro Agent (§2 Phase 2 MASTER_PLAN) — Macroeconomic signal analysis.

Analyzes:
- Bond yields (10Y): Inverse correlation with gold (lower rates = higher gold)
- DXY trends: Strong inverse correlation (weaker dollar = higher gold)
- VIX (volatility): Positive correlation with gold (risk-off = gold demand)
- Real yields (implied): Fisher equation (nominal - inflation)
- Fed policy signals: Rate expectations
"""

from datetime import datetime
from typing import Optional
from gold_agent.core.models import MarketData


class MacroSignal:
    """Macro signal result."""

    def __init__(
        self,
        timestamp: datetime,
        bond_yield_signal: float,  # -1.0 to 1.0 (bearish to bullish for gold)
        dxy_signal: float,  # -1.0 to 1.0 (weak to strong USD)
        vix_signal: float,  # 0.0 to 1.0 (calm to panic)
        risk_sentiment: str,  # "risk-on", "risk-off", "neutral"
        macro_score: float,  # 0-100 weighted macro strength
    ):
        self.timestamp = timestamp
        self.bond_yield_signal = bond_yield_signal
        self.dxy_signal = dxy_signal
        self.vix_signal = vix_signal
        self.risk_sentiment = risk_sentiment
        self.macro_score = macro_score


class MacroAgent:
    """Analyzes macroeconomic signals affecting gold prices."""

    def __init__(self, config):
        self.config = config
        self.bond_yield_history = []
        self.dxy_history = []
        self.vix_history = []
        self.max_history = 20  # Track last 20 data points for trends

    def analyze(self, market_data: MarketData) -> MacroSignal:
        """Analyze macro environment and produce signal."""
        # Update history
        if market_data.bond_yield_10y:
            self.bond_yield_history.append(market_data.bond_yield_10y)
            if len(self.bond_yield_history) > self.max_history:
                self.bond_yield_history = self.bond_yield_history[-self.max_history:]

        self.dxy_history.append(market_data.dxy)
        if len(self.dxy_history) > self.max_history:
            self.dxy_history = self.dxy_history[-self.max_history:]

        if market_data.vix:
            self.vix_history.append(market_data.vix)
            if len(self.vix_history) > self.max_history:
                self.vix_history = self.vix_history[-self.max_history:]

        # Analyze bond yields (inverse correlation with gold)
        bond_yield_signal = self._analyze_bond_yields(market_data.bond_yield_10y)

        # Analyze DXY trend (inverse correlation with gold)
        dxy_signal = self._analyze_dxy(market_data.dxy)

        # Analyze VIX (positive correlation with gold)
        vix_signal = self._analyze_vix(market_data.vix) if market_data.vix else 0.0

        # Determine risk sentiment
        risk_sentiment = self._determine_risk_sentiment(
            bond_yield_signal, dxy_signal, vix_signal
        )

        # Combine into macro score
        macro_score = self._calculate_macro_score(
            bond_yield_signal, dxy_signal, vix_signal
        )

        return MacroSignal(
            timestamp=market_data.timestamp,
            bond_yield_signal=bond_yield_signal,
            dxy_signal=dxy_signal,
            vix_signal=vix_signal,
            risk_sentiment=risk_sentiment,
            macro_score=macro_score,
        )

    def _analyze_bond_yields(self, current_yield: Optional[float]) -> float:
        """
        Analyze bond yields.

        Lower yields → Bullish for gold (negative signal means bullish)
        Higher yields → Bearish for gold (positive signal means bearish)

        Returns: -1.0 (very low, bullish) to 1.0 (very high, bearish)
        """
        if not current_yield or len(self.bond_yield_history) < 2:
            return 0.0

        # Normalize to -1 to 1 scale (assuming 0-5% range)
        normalized = (current_yield - 2.5) / 2.5
        normalized = max(-1.0, min(1.0, normalized))

        # Trend analysis
        recent_avg = sum(self.bond_yield_history[-5:]) / min(5, len(self.bond_yield_history))
        trend = current_yield - recent_avg

        # Combined signal (higher yields = bearish for gold)
        signal = normalized * 0.7 + (trend * 0.1 if trend > 0 else 0.0)
        return max(-1.0, min(1.0, signal))

    def _analyze_dxy(self, current_dxy: float) -> float:
        """
        Analyze US Dollar Index.

        Weak dollar (lower DXY) → Bullish for gold
        Strong dollar (higher DXY) → Bearish for gold

        Returns: -1.0 (weak USD, bullish) to 1.0 (strong USD, bearish)
        """
        if len(self.dxy_history) < 2:
            return 0.0

        # Normalize to -1 to 1 scale (assuming 95-110 range)
        normalized = (current_dxy - 102.5) / 7.5
        normalized = max(-1.0, min(1.0, normalized))

        # Trend analysis
        recent_avg = sum(self.dxy_history[-5:]) / min(5, len(self.dxy_history))
        trend = current_dxy - recent_avg

        # Combined signal (stronger USD = bearish for gold)
        signal = normalized * 0.7 + (trend * 0.1 if trend > 0 else 0.0)
        return max(-1.0, min(1.0, signal))

    def _analyze_vix(self, current_vix: float) -> float:
        """
        Analyze Volatility Index.

        High VIX (panic) → Bullish for gold (risk-off demand)
        Low VIX (calm) → Neutral/bearish for gold

        Returns: 0.0 (calm) to 1.0 (panic)
        """
        if not current_vix:
            return 0.0

        # VIX: typically 10-40, peaks 50-80
        # Normalize to 0-1 scale
        vix_normalized = current_vix / 40.0
        vix_normalized = max(0.0, min(1.0, vix_normalized))

        # Trend analysis
        if len(self.vix_history) > 1:
            recent_avg = sum(self.vix_history[-5:]) / min(5, len(self.vix_history))
            trend = current_vix - recent_avg
            # Rising VIX = more bullish for gold
            vix_normalized += trend * 0.01
        else:
            trend = 0.0

        return max(0.0, min(1.0, vix_normalized))

    def _determine_risk_sentiment(
        self, bond_signal: float, dxy_signal: float, vix_signal: float
    ) -> str:
        """Determine overall risk sentiment."""
        # Risk-off: low rates (-), weak USD (-), high VIX (+)
        risk_off_score = (-bond_signal + 1) / 2 + (-dxy_signal + 1) / 2 + vix_signal
        risk_off_score /= 3

        if risk_off_score > 0.65:
            return "risk-off"
        elif risk_off_score < 0.35:
            return "risk-on"
        else:
            return "neutral"

    def _calculate_macro_score(
        self, bond_signal: float, dxy_signal: float, vix_signal: float
    ) -> float:
        """
        Calculate macro score (0-100).

        Bullish signals:
        - Low bond yields (bond_signal < 0)
        - Weak USD (dxy_signal < 0)
        - High VIX (vix_signal > 0.5)
        """
        # Convert signals to 0-100 scale
        bond_score = (1 - bond_signal) * 50  # 0-100
        dxy_score = (1 - dxy_signal) * 50  # 0-100
        vix_score = vix_signal * 100  # 0-100

        # Weight: bonds 40%, DXY 40%, VIX 20%
        macro_score = bond_score * 0.40 + dxy_score * 0.40 + vix_score * 0.20

        return round(macro_score, 1)

    def get_macro_strength(self) -> str:
        """Qualitative description of macro environment."""
        if len(self.dxy_history) == 0:
            return "insufficient_data"

        recent_dxy = self.dxy_history[-1]
        recent_yields = (
            self.bond_yield_history[-1]
            if self.bond_yield_history
            else None
        )
        recent_vix = self.vix_history[-1] if self.vix_history else None

        bullish_factors = 0

        # Weak dollar is bullish
        if recent_dxy < 100:
            bullish_factors += 1

        # Low yields are bullish
        if recent_yields and recent_yields < 3.5:
            bullish_factors += 1

        # High VIX is bullish (risk-off)
        if recent_vix and recent_vix > 25:
            bullish_factors += 1

        if bullish_factors >= 2:
            return "strongly_bullish"
        elif bullish_factors == 1:
            return "mildly_bullish"
        else:
            return "bearish"
