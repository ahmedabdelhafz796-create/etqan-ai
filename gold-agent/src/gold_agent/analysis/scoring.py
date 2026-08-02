"""Scoring engine (§7 MASTER_PLAN) — Weighted combination of signals."""

from datetime import datetime
from typing import List, Optional

from src.gold_agent.core.models import (
    IndicatorValues,
    MarketData,
    NewsItem,
    Score,
)


class ScoringEngine:
    """Combines indicators, news, and macro signals into weighted score."""

    def __init__(self, config):
        self.config = config

    def score(
        self,
        indicators: IndicatorValues,
        news: List[NewsItem],
        market_data: MarketData,
    ) -> Score:
        """
        Calculate weighted score from all signals (§7).

        Weights:
        - RSI: 0.30
        - MACD: 0.35
        - MA: 0.35
        - News: 0.20
        - Macro: 0.15
        """
        # 1. Score individual indicators (0-100 scale)
        rsi_score = self._score_rsi(indicators.rsi)
        macd_score = self._score_macd(indicators.macd_histogram)
        ma_score = self._score_ma(
            indicators.ma_short, indicators.ma_long, market_data.xau_usd
        )

        # 2. Score news sentiment
        news_score = self._score_news(news) if news else 50.0

        # 3. Score macro signals
        macro_score = self._score_macro(market_data)

        # 4. Weighted combination
        combined = (
            rsi_score * self.config.scoring.rsi_weight
            + macd_score * self.config.scoring.macd_weight
            + ma_score * self.config.scoring.ma_weight
            + news_score * self.config.scoring.news_weight
            + macro_score * self.config.scoring.macro_weight
        )

        # Count aligned signals
        signals_aligned = 0
        if rsi_score > 60:
            signals_aligned += 1
        if macd_score > 60:
            signals_aligned += 1
        if ma_score > 60:
            signals_aligned += 1
        if news_score > 60:
            signals_aligned += 1
        if macro_score > 60:
            signals_aligned += 1

        return Score(
            timestamp=datetime.utcnow(),
            rsi_score=rsi_score,
            macd_score=macd_score,
            ma_score=ma_score,
            news_score=news_score,
            macro_score=macro_score,
            combined_score=combined,
            signals_aligned=signals_aligned,
        )

    def _score_rsi(self, rsi: float) -> float:
        """
        Score RSI (0-100).
        Oversold (<30) = bullish = high score
        Overbought (>70) = bearish = low score
        Middle (30-70) = neutral = 50
        """
        if rsi < 30:
            return 70 + (30 - rsi)  # 70-100
        elif rsi > 70:
            return rsi - 70  # 0-30
        else:
            return 50  # Neutral

    def _score_macd(self, macd_histogram: float) -> float:
        """
        Score MACD histogram.
        Positive = bullish = high score
        Negative = bearish = low score
        """
        # Normalize to 0-100 scale (assuming histogram -100 to +100)
        score = 50 + (macd_histogram / 2)
        return max(0, min(100, score))

    def _score_ma(self, ma_short: float, ma_long: float, current_price: float) -> float:
        """
        Score Moving Average alignment.
        Price > short > long = strong bullish = 80-100
        Price < short < long = strong bearish = 0-20
        Middle = 40-60
        """
        if current_price > ma_short > ma_long:
            return 85  # Strong bullish alignment
        elif current_price > ma_long:
            return 65  # Price above long MA
        elif current_price < ma_short < ma_long:
            return 15  # Strong bearish alignment
        elif current_price < ma_long:
            return 35  # Price below long MA
        else:
            return 50  # Neutral

    def _score_news(self, news_items: List[NewsItem]) -> float:
        """
        Score news sentiment (0-100).
        Average sentiment across recent news.
        """
        if not news_items:
            return 50.0

        sentiments = [
            n.sentiment for n in news_items if n.sentiment is not None
        ]
        if not sentiments:
            return 50.0

        avg_sentiment = sum(sentiments) / len(sentiments)
        # Convert -1 to 1 range to 0 to 100 range
        score = 50 + (avg_sentiment * 50)
        return max(0, min(100, score))

    def _score_macro(self, market_data: MarketData) -> float:
        """
        Score macro indicators (0-100).

        Macro signals:
        - Weaker dollar (lower DXY) = good for gold = higher score
        - Higher yields = bad for gold = lower score
        - Higher VIX = more risk = good for safe-haven gold = higher score
        """
        score = 50.0

        # DXY: inverse relationship with gold
        # Normal range 95-115; center at 105
        if market_data.dxy:
            dxy_deviation = 105 - market_data.dxy
            score += (dxy_deviation / 10) * 10  # Adjust +/- 10 for +/- 10 DXY

        # Bond yields: inverse relationship with gold
        # Normal range 2-5%; center at 3.5%
        if market_data.bond_yield_10y:
            yield_deviation = 3.5 - market_data.bond_yield_10y
            score += (yield_deviation / 0.5) * 5  # Adjust +/- 5 for +/- 0.5% yield

        # VIX: positive relationship with gold (safe haven)
        # Normal range 10-40; center at 20
        if market_data.vix:
            vix_deviation = market_data.vix - 20
            score += (vix_deviation / 10) * 10  # Adjust +/- 10 for +/- 10 VIX

        return max(0, min(100, score))
