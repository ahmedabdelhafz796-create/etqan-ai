"""Risk Gate (§4, §8 MASTER_PLAN) — Veto trades violating risk rules."""

from typing import Optional

from gold_agent.core.models import ActionType, GateVerdict, GateVerdictType, MarketData, Score


class RiskGate:
    """Risk management gate with veto authority."""

    def __init__(self, config):
        self.config = config
        self.cumulative_drawdown = 0.0
        self.daily_loss = 0.0
        self.consecutive_losses = 0

    def check(
        self,
        action: ActionType,
        market_data: MarketData,
        score: Score,
    ) -> GateVerdict:
        """
        Check if action violates risk rules.

        §8 Risk rules:
        - Max drawdown: 5%
        - Max position size: 2% of capital
        - Daily loss limit: 3%
        - Max consecutive losses: 5
        - Market volatility (VIX) limit: 40
        """
        if not self.config.risk_gate.enabled:
            return GateVerdict(
                verdict=GateVerdictType.PASSED,
                passed=True,
                reason="Risk gate disabled",
            )

        # 1. Check data quality
        if market_data.data_quality < 0.95:
            return GateVerdict(
                verdict=GateVerdictType.BLOCKED,
                passed=False,
                reason=f"Data quality {market_data.data_quality:.0%} below threshold",
                details={"data_quality": market_data.data_quality},
            )

        # 2. Check drawdown
        if self.cumulative_drawdown > self.config.risk_gate.max_drawdown_percent:
            return GateVerdict(
                verdict=GateVerdictType.BLOCKED,
                passed=False,
                reason=f"Drawdown {self.cumulative_drawdown:.1f}% exceeds limit {self.config.risk_gate.max_drawdown_percent}%",
                details={"drawdown": self.cumulative_drawdown},
            )

        # 3. Check daily loss
        if self.daily_loss > self.config.risk_gate.daily_loss_limit_percent:
            return GateVerdict(
                verdict=GateVerdictType.BLOCKED,
                passed=False,
                reason=f"Daily loss {self.daily_loss:.1f}% exceeds limit {self.config.risk_gate.daily_loss_limit_percent}%",
                details={"daily_loss": self.daily_loss},
            )

        # 4. Check consecutive losses
        if self.consecutive_losses > self.config.risk_gate.max_consecutive_losses:
            return GateVerdict(
                verdict=GateVerdictType.BLOCKED,
                passed=False,
                reason=f"Consecutive losses {self.consecutive_losses} exceed limit {self.config.risk_gate.max_consecutive_losses}",
                details={"consecutive_losses": self.consecutive_losses},
            )

        # 5. Check market volatility
        if market_data.vix and market_data.vix > self.config.risk_gate.market_volatility_limit_vix:
            return GateVerdict(
                verdict=GateVerdictType.BLOCKED,
                passed=False,
                reason=f"VIX {market_data.vix:.1f} exceeds limit {self.config.risk_gate.market_volatility_limit_vix}",
                details={"vix": market_data.vix},
            )

        # 6. Check confidence level
        if score.combined_score < self.config.scoring.confidence_threshold_act:
            return GateVerdict(
                verdict=GateVerdictType.BLOCKED,
                passed=False,
                reason=f"Confidence {score.combined_score:.0f}% below action threshold {self.config.scoring.confidence_threshold_act}%",
                details={"confidence": score.combined_score},
            )

        # All checks passed
        return GateVerdict(
            verdict=GateVerdictType.PASSED,
            passed=True,
            reason="All risk checks passed",
            details={
                "drawdown": self.cumulative_drawdown,
                "daily_loss": self.daily_loss,
                "consecutive_losses": self.consecutive_losses,
                "vix": market_data.vix,
                "data_quality": market_data.data_quality,
            },
        )

    def record_trade_result(self, profit_loss_percent: float) -> None:
        """Record result of a trade for risk tracking."""
        self.cumulative_drawdown += profit_loss_percent
        self.daily_loss += max(0, -profit_loss_percent)

        if profit_loss_percent < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

    def reset_daily_loss(self) -> None:
        """Reset daily loss counter (called at EOD)."""
        self.daily_loss = 0.0

    def get_risk_status(self) -> dict:
        """Get current risk metrics."""
        return {
            "drawdown": self.cumulative_drawdown,
            "daily_loss": self.daily_loss,
            "consecutive_losses": self.consecutive_losses,
        }
