"""Main data-to-decision pipeline (§6-7 MASTER_PLAN)."""

from datetime import datetime
from typing import List, Optional, Tuple

from src.gold_agent.core.models import (
    Decision,
    GateVerdict,
    GateVerdictType,
    HealthStatus,
    IndicatorValues,
    MarketData,
    NewsItem,
    Score,
    StateType,
)


class Pipeline:
    """
    Orchestrates the complete data → decision flow.

    §6 Data Flow:
    1. Fetch market data (XAU/USD, DXY, bond yields, VIX)
    2. Fetch news (NewsAPI/RSS)
    3. Calculate indicators (RSI, MACD, MA)
    4. Score (weighted combination)
    5. LLM brain (Claude API or fallback)
    6. Decision engine (action + confidence)
    7. Risk Gate (veto)
    8. Sharia Gate (hard veto)
    9. Notification (Telegram)
    10. Audit log (database)
    """

    def __init__(
        self,
        market_data_provider,
        news_provider,
        indicator_engine,
        scoring_engine,
        macro_agent,
        correlation_agent,
        brain_engine,
        decision_engine,
        risk_gate,
        sharia_gate,
        notifier,
        audit_log,
        state_machine,
        config,
    ):
        self.market_data = market_data_provider
        self.news = news_provider
        self.indicators = indicator_engine
        self.scoring = scoring_engine
        self.macro = macro_agent
        self.correlation = correlation_agent
        self.brain = brain_engine
        self.decision = decision_engine
        self.risk_gate = risk_gate
        self.sharia_gate = sharia_gate
        self.notifier = notifier
        self.audit = audit_log
        self.state_machine = state_machine
        self.config = config
        self.last_decision: Optional[Decision] = None
        self.last_health_status: Optional[HealthStatus] = None

    async def run_once(self) -> Optional[Decision]:
        """
        Execute one complete analysis cycle.

        Returns:
            Decision object with action + confidence, or None if blocked
        """
        try:
            # 1. Fetch market data
            market_data = await self.market_data.fetch()
            if not market_data:
                await self._handle_data_error("No market data available")
                return None

            # 2. Fetch news
            news_items = await self.news.fetch()

            # 3. Calculate indicators
            indicator_values = self.indicators.calculate(market_data)

            # 3b. Phase 2: Macro and Correlation Analysis
            macro_signal = self.macro.analyze(market_data)
            correlation_signal = self.correlation.analyze(market_data)

            # 4. Score
            score = self.scoring.score(
                indicators=indicator_values,
                news=news_items,
                market_data=market_data,
            )

            # 5. Check if confidence is above threshold
            if score.combined_score < self.config.scoring.confidence_threshold_wait:
                decision = self._create_wait_decision(
                    indicator_values, score, "Confidence below threshold"
                )
                await self.audit.log_decision(decision)
                await self.notifier.notify_wait(decision)
                return decision

            # 6. LLM brain (Claude API or fallback)
            brain_result = await self.brain.analyze(
                market_data=market_data,
                indicators=indicator_values,
                score=score,
                news=news_items,
            )

            # 7. Decision engine
            decision_action, decision_confidence, decision_reason = self.decision.decide(
                score=score,
                brain_result=brain_result,
                market_data=market_data,
            )

            # 8. Risk Gate
            risk_verdict = self.risk_gate.check(decision_action, market_data, score)
            if not risk_verdict.passed:
                decision = Decision(
                    timestamp=datetime.utcnow(),
                    action=decision_action,
                    confidence=decision_confidence,
                    reason=f"Risk Gate blocked: {risk_verdict.reason}",
                    indicators=indicator_values,
                    score=score,
                    risk_gate_verdict=risk_verdict,
                    sharia_gate_verdict=None,
                    llm_brain_used=brain_result is not None,
                    state=self.state_machine.current_state,
                )
                await self.audit.log_decision(decision)
                await self.notifier.notify_blocked(decision, "Risk Gate")
                return decision

            # 9. Sharia Gate (Hard Veto)
            sharia_verdict = self.sharia_gate.check(decision_action, market_data)
            if not sharia_verdict.passed:
                decision = Decision(
                    timestamp=datetime.utcnow(),
                    action=decision_action,
                    confidence=decision_confidence,
                    reason=f"Sharia Gate blocked: {sharia_verdict.reason}",
                    indicators=indicator_values,
                    score=score,
                    risk_gate_verdict=risk_verdict,
                    sharia_gate_verdict=sharia_verdict,
                    llm_brain_used=brain_result is not None,
                    state=self.state_machine.current_state,
                )
                await self.audit.log_decision(decision)
                await self.audit.log_sharia_decision(decision)
                await self.notifier.notify_blocked(decision, "Sharia Gate")
                return decision

            # 10. Final decision
            final_decision = Decision(
                timestamp=datetime.utcnow(),
                action=decision_action,
                confidence=decision_confidence,
                reason=decision_reason,
                indicators=indicator_values,
                score=score,
                risk_gate_verdict=risk_verdict,
                sharia_gate_verdict=sharia_verdict,
                llm_brain_used=brain_result is not None,
                state=self.state_machine.current_state,
            )

            # 11. Check state machine
            if not self.state_machine.can_trade():
                final_decision.reason = f"State machine: {self.state_machine.current_state.value}. Decision blocked."
                await self.audit.log_decision(final_decision)
                return final_decision

            # 12. Audit log
            await self.audit.log_decision(final_decision)

            # 13. Notify
            await self.notifier.notify_decision(final_decision)

            self.last_decision = final_decision
            return final_decision

        except Exception as e:
            await self._handle_error(str(e))
            return None

    async def check_health(self) -> HealthStatus:
        """Check system health and update state machine if needed."""
        try:
            # Check data quality
            data_quality = await self.market_data.check_quality()

            # Check connection
            connection_status = await self.market_data.check_connection()
            last_data_age = await self.market_data.get_last_update_age()

            # Count errors
            errors_last_hour = await self.audit.count_errors_last_hour()
            alerts_today = await self.audit.count_alerts_today()

            health = HealthStatus(
                timestamp=datetime.utcnow(),
                data_quality=data_quality,
                connection_status=connection_status,
                last_data_age_minutes=last_data_age,
                agent_errors_last_hour=errors_last_hour,
                alerts_sent_today=alerts_today,
                state=self.state_machine.current_state,
                requires_intervention=False,
            )

            # Trigger state transitions if needed
            if data_quality < 0.95:
                if self.state_machine.trigger("data_quality_degradation", data_quality=data_quality):
                    health.requires_intervention = True
                    health.reason = f"Data quality degraded: {data_quality:.2%}"

            if connection_status != "healthy":
                if self.state_machine.trigger("connection_loss", timeout_seconds=last_data_age * 60):
                    health.requires_intervention = True
                    health.reason = f"Connection {connection_status}"

            self.last_health_status = health
            return health

        except Exception as e:
            await self._handle_error(f"Health check failed: {str(e)}")
            return None

    def _create_wait_decision(
        self,
        indicators: IndicatorValues,
        score: Score,
        reason: str,
    ) -> Decision:
        """Create a WAIT decision."""
        from src.gold_agent.core.models import ActionType

        return Decision(
            timestamp=datetime.utcnow(),
            action=ActionType.WAIT,
            confidence=score.combined_score,
            reason=reason,
            indicators=indicators,
            score=score,
            state=self.state_machine.current_state,
        )

    async def _handle_data_error(self, error_msg: str) -> None:
        """Handle data errors and trigger Safe Mode if persistent."""
        await self.audit.log_error(error_msg)
        if self.state_machine.trigger("data_quality_degradation", data_quality=0.0):
            await self.notifier.notify_state_change("safe_mode", error_msg)

    async def _handle_error(self, error_msg: str) -> None:
        """Handle critical errors and trigger Emergency state."""
        await self.audit.log_error(error_msg)
        if self.state_machine.trigger("bug_detected", error=True):
            await self.notifier.notify_emergency(error_msg)
