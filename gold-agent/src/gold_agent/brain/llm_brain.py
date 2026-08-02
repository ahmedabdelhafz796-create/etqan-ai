"""LLM Brain (§7 MASTER_PLAN) — Claude API integration with fallback rule engine."""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.gold_agent.core.models import (
    IndicatorValues,
    MarketData,
    NewsItem,
    Score,
)


class BrainResult:
    """Result from LLM brain analysis."""

    def __init__(
        self,
        confidence: float,
        reason: str,
        signal: str,  # "bullish", "bearish", "neutral"
        used_llm: bool = False,
        used_fallback: bool = False,
    ):
        self.confidence = confidence
        self.reason = reason
        self.signal = signal
        self.used_llm = used_llm
        self.used_fallback = used_fallback


class Brain(ABC):
    """Abstract brain interface."""

    @abstractmethod
    async def analyze(
        self,
        market_data: MarketData,
        indicators: IndicatorValues,
        score: Score,
        news: List[NewsItem],
    ) -> Optional[BrainResult]:
        """Analyze and return decision."""
        pass


class AnthropicBrain(Brain):
    """Claude API brain (production)."""

    def __init__(self, api_key: str, model: str, config):
        self.api_key = api_key
        self.model = model
        self.config = config
        self.client = None
        # TODO: Initialize Anthropic client
        pass

    async def analyze(
        self,
        market_data: MarketData,
        indicators: IndicatorValues,
        score: Score,
        news: List[NewsItem],
    ) -> Optional[BrainResult]:
        """Call Claude API for analysis."""
        # TODO: Implement
        pass

    def _build_prompt(
        self,
        market_data: MarketData,
        indicators: IndicatorValues,
        score: Score,
        news: List[NewsItem],
    ) -> str:
        """Build prompt for Claude."""
        # TODO: Implement
        pass


class FallbackRuleEngine(Brain):
    """
    Rule-based fallback engine when LLM unavailable.

    Phase 1: Conservative approach (3 of 5 indicators must agree)
    Phase 2: Enhanced with macro and correlation signals
    - Reduce confidence by 10% from what LLM would give
    """

    def __init__(self, config):
        self.config = config
        self.macro_signal = None
        self.correlation_signal = None

    def set_macro_correlation_signals(self, macro_signal, correlation_signal):
        """Set macro and correlation signals for enhanced analysis."""
        self.macro_signal = macro_signal
        self.correlation_signal = correlation_signal

    async def analyze(
        self,
        market_data: MarketData,
        indicators: IndicatorValues,
        score: Score,
        news: List[NewsItem],
    ) -> BrainResult:
        """Analyze using simple rule-based logic."""
        # Count bullish signals
        bullish_signals = 0
        signals_list = []

        # 1. RSI signal
        if indicators.rsi < 30:
            bullish_signals += 1
            signals_list.append("RSI oversold")
        elif indicators.rsi > 70:
            signals_list.append("RSI overbought")

        # 2. MACD signal
        if indicators.macd_histogram > 0:
            bullish_signals += 1
            signals_list.append("MACD bullish")
        else:
            signals_list.append("MACD bearish")

        # 3. MA signal
        if indicators.ma_short > indicators.ma_long:
            bullish_signals += 1
            signals_list.append("MAs aligned bullish")
        else:
            signals_list.append("MAs aligned bearish")

        # 4. Score signal
        if score.combined_score > 60:
            bullish_signals += 1
            signals_list.append("Score bullish")

        # 5. News sentiment
        if score.news_score and score.news_score > 60:
            bullish_signals += 1
            signals_list.append("News bullish")

        # Determine action based on signal count
        if bullish_signals >= 3:
            signal = "bullish"
            base_confidence = 70.0
        elif bullish_signals <= 1:
            signal = "bearish"
            base_confidence = 70.0
        else:
            signal = "neutral"
            base_confidence = 50.0

        # Phase 2: Apply macro and correlation signal boost/penalty
        macro_boost = self._calculate_macro_boost()
        correlation_boost = self._calculate_correlation_boost()

        # Apply boosts (positive values boost confidence, negative reduce it)
        adjusted_confidence = base_confidence + macro_boost + correlation_boost

        # Apply conservative reduction (10% as per design)
        final_confidence = adjusted_confidence * (1 - self.config.fallback_engine.conservative_confidence_reduction)
        final_confidence = max(0, min(100, final_confidence))

        # Build detailed reason
        reason_parts = [
            f"Fallback rule engine: {bullish_signals}/5 signals aligned.",
            f"Signals: {', '.join(signals_list)}."
        ]
        if self.macro_signal:
            reason_parts.append(f"Macro: {self.macro_signal.risk_sentiment} (score {self.macro_signal.macro_score:.0f})")
        if self.correlation_signal:
            reason_parts.append(f"Regime: {self.correlation_signal.regime}")

        reason = " ".join(reason_parts)

        return BrainResult(
            confidence=final_confidence,
            reason=reason,
            signal=signal,
            used_llm=False,
            used_fallback=True,
        )

    def _calculate_macro_boost(self) -> float:
        """
        Calculate confidence boost from macro signals.

        Bullish macro environment = boost confidence
        Bearish macro environment = reduce confidence
        """
        if not self.macro_signal:
            return 0.0

        # Risk-off environment boosts gold confidence
        if self.macro_signal.risk_sentiment == "risk-off":
            return 5.0  # +5% confidence boost
        elif self.macro_signal.risk_sentiment == "risk-on":
            return -3.0  # -3% confidence reduction
        else:
            return 0.0  # Neutral macro, no boost

    def _calculate_correlation_boost(self) -> float:
        """
        Calculate confidence boost from correlation signals.

        Strong expected correlations = more reliable signals
        Broken correlations = less reliable (reduce confidence)
        """
        if not self.correlation_signal:
            return 0.0

        correlation_quality_score = self.correlation_signal.correlation_score

        # Strong correlations (>70) boost confidence, weak (<30) reduce it
        if correlation_quality_score > 70:
            return 5.0  # +5% confidence boost
        elif correlation_quality_score < 30:
            return -5.0  # -5% confidence reduction (broken correlations = unreliable)
        else:
            return 0.0  # Moderate correlations, no adjustment


class HybridBrain(Brain):
    """Hybrid brain: Claude API with fallback rule engine."""

    def __init__(self, api_key: Optional[str], model: str, config):
        self.config = config
        self.llm_brain = (
            AnthropicBrain(api_key, model, config) if api_key else None
        )
        self.fallback_brain = FallbackRuleEngine(config)

    async def analyze(
        self,
        market_data: MarketData,
        indicators: IndicatorValues,
        score: Score,
        news: List[NewsItem],
    ) -> BrainResult:
        """Try LLM, fall back to rules if unavailable."""
        if self.llm_brain:
            try:
                result = await self.llm_brain.analyze(
                    market_data, indicators, score, news
                )
                if result:
                    return result
            except Exception as e:
                print(f"LLM brain failed: {e}. Using fallback engine.")

        # Use fallback
        return await self.fallback_brain.analyze(
            market_data, indicators, score, news
        )


def get_brain(provider_type: str, config) -> Brain:
    """Factory function to get brain."""
    api_key = None  # TODO: Load from env

    if provider_type == "mock":
        return FallbackRuleEngine(config)
    elif provider_type == "anthropic":
        return HybridBrain(api_key, config.brain.model, config)
    else:
        raise ValueError(f"Unknown brain provider: {provider_type}")
