"""Decision Engine (§7 MASTER_PLAN) — Generate BUY/SELL/WAIT decisions."""

from typing import Optional, Tuple

from src.gold_agent.brain.llm_brain import BrainResult
from src.gold_agent.core.models import ActionType, MarketData, Score


class DecisionEngine:
    """Generates trading decisions based on score and brain analysis."""

    def __init__(self, config):
        self.config = config

    def decide(
        self,
        score: Score,
        brain_result: Optional[BrainResult],
        market_data: MarketData,
    ) -> Tuple[ActionType, float, str]:
        """
        Generate decision from score and brain analysis.

        Returns:
            (action, confidence, reason)
        """
        # 1. Check confidence threshold
        if score.combined_score < self.config.scoring.confidence_threshold_wait:
            return (
                ActionType.WAIT,
                score.combined_score,
                f"Score {score.combined_score:.1f}% below threshold {self.config.scoring.confidence_threshold_wait}%",
            )

        # 2. Use brain result if available
        if brain_result:
            confidence = brain_result.confidence
            reason = brain_result.reason

            if brain_result.signal == "bullish":
                action = ActionType.BUY
            elif brain_result.signal == "bearish":
                action = ActionType.SELL
            else:
                action = ActionType.WAIT
        else:
            # 3. Fallback: use score directly
            confidence = score.combined_score
            reason = self._reason_from_score(score)

            if confidence > 65:
                # Determine BUY vs SELL from indicators
                if score.rsi_score < 30 or (score.macd_score > 60 and score.ma_score > 60):
                    action = ActionType.BUY
                else:
                    action = ActionType.SELL
            else:
                action = ActionType.WAIT

        return action, confidence, reason

    def _reason_from_score(self, score: Score) -> str:
        """Build reason string from score components."""
        reasons = []

        # RSI component
        if score.rsi_score < 30:
            reasons.append(f"RSI oversold ({score.rsi_score:.0f})")
        elif score.rsi_score > 70:
            reasons.append(f"RSI overbought ({score.rsi_score:.0f})")

        # MACD component
        if score.macd_score > 60:
            reasons.append("MACD bullish")
        elif score.macd_score < 40:
            reasons.append("MACD bearish")

        # MA component
        if score.ma_score > 65:
            reasons.append("MAs aligned")

        # Overall
        reasons.append(f"Score {score.combined_score:.0f}%")
        reasons.append(f"{score.signals_aligned} signals aligned")

        return " | ".join(reasons)
