"""Decision Engine (§7 MASTER_PLAN) — Generate BUY/SELL/WAIT decisions."""

import logging
from typing import Optional, Tuple

from gold_agent.brain.llm_brain import BrainResult
from gold_agent.core.models import ActionType, MarketData, Score
from gold_agent.learning.walk_forward_validator import WalkForwardValidator, ParameterAdjustmentAudit

logger = logging.getLogger(__name__)


class DecisionEngine:
    """Generates trading decisions based on score and brain analysis."""

    def __init__(self, config):
        self.config = config
        self.walk_forward = WalkForwardValidator(min_sample_size=50)
        self.parameter_audit = ParameterAdjustmentAudit()

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

    def propose_parameter_change(
        self,
        parameter_name: str,
        old_value: float,
        new_value: float,
        strategy: str = "trend_follow",
        regime: str = "trending"
    ) -> Tuple[bool, dict]:
        """
        Validate a parameter change using walk-forward testing before applying it.

        Split trade history into 60% train, 40% test. Calculate performance with old and new
        parameter values on test set. Approve only if new > old AND minimum sample size met.

        Args:
            parameter_name: Name of parameter to change (e.g., "rsi_weight")
            old_value: Current parameter value
            new_value: Proposed new value
            strategy: Trading strategy (default: "trend_follow")
            regime: Market regime (default: "trending")

        Returns:
            (approved: bool, report: dict with metrics and approval reason)
        """
        # Validate using walk-forward testing
        approved, report = self.walk_forward.validate_parameter_change(
            parameter_name=parameter_name,
            old_value=old_value,
            new_value=new_value,
            strategy=strategy,
            regime=regime
        )

        # Record in audit trail
        self.parameter_audit.record_adjustment(
            parameter=parameter_name,
            old_value=old_value,
            new_value=new_value,
            approved=approved,
            validation_report=report,
            reason=f"Walk-forward validation: {report.get('reason', 'No reason provided')}"
        )

        if approved:
            logger.info(
                f"Parameter change APPROVED: {parameter_name} {old_value} → {new_value} "
                f"(win_rate {report['old_performance']['win_rate']:.1f}% → "
                f"{report['new_performance']['win_rate']:.1f}%)"
            )
        else:
            logger.warning(
                f"Parameter change REJECTED: {parameter_name} {old_value} → {new_value} "
                f"({report.get('reason', 'Insufficient data')})"
            )

        return approved, report

    def add_trade_result(self, trade_result) -> None:
        """Add a completed trade result to history for walk-forward learning."""
        self.walk_forward.add_trade(trade_result)

    def get_parameter_audit_trail(self) -> dict:
        """Get complete parameter adjustment audit trail."""
        return self.parameter_audit.get_audit_trail()
