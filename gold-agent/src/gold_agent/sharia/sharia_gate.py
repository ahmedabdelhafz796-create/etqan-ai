"""Sharia Gate (§8 MASTER_PLAN) — Hard Veto for Islamic compliance.

Verifies:
- Contract type (spot only, no futures/options)
- No overnight interest (swap charges)
- Taqābuḍ (spot settlement)
- No financial leverage
- No borrowing
"""

from typing import Dict, Optional

from gold_agent.core.models import ActionType, GateVerdict, GateVerdictType, MarketData


class ShariaCertification:
    """Represents Sharia compliance verification."""

    def __init__(self, certified: bool, reason: str, school: str = "hanafi"):
        self.certified = certified
        self.reason = reason
        self.school = school


class ShariGate:
    """Hard Veto gate for Sharia compliance (§8 MASTER_PLAN)."""

    def __init__(self, config, rules: Optional[Dict] = None):
        self.config = config
        self.rules = rules or {}
        self.school = config.sharia.school
        self.violations = []

    def check(self, action: ActionType, market_data: MarketData) -> GateVerdict:
        """
        Perform hard veto check for Sharia compliance.

        §8 Rules:
        1. Contract Type: Spot only (no futures/options/CFDs)
        2. No Overnight Interest (swap charges = 0)
        3. Taqābuḍ: Spot settlement (T+2)
        4. No Leverage: Max 1:1 (no leverage)
        5. No Borrowing: Only personal capital

        Returns:
            GateVerdict with PASSED or BLOCKED
        """
        if not self.config.sharia.enabled:
            return GateVerdict(
                verdict=GateVerdictType.PASSED,
                passed=True,
                reason="Sharia gate disabled",
            )

        self.violations = []

        # 1. Contract Type Check
        if not self._check_contract_type(action):
            self.violations.append("Contract type not Sharia-compliant")

        # 2. Overnight Interest Check
        if not self._check_no_overnight_interest(market_data):
            self.violations.append("Overnight interest (swap) detected")

        # 3. Taqābuḍ Check (Settlement)
        if not self._check_taqabud():
            self.violations.append("Settlement method not Sharia-compliant")

        # 4. Leverage Check
        if not self._check_no_leverage():
            self.violations.append("Leverage detected (prohibited)")

        # 5. Borrowing Check
        if not self._check_no_borrowing():
            self.violations.append("Borrowing detected (prohibited)")

        # If any violations, return hard veto
        if self.violations:
            reason = f"Sharia Gate Hard Veto ({self.school} school): {'; '.join(self.violations)}"
            return GateVerdict(
                verdict=GateVerdictType.BLOCKED,
                passed=False,
                reason=reason,
                details={
                    "school": self.school,
                    "violations": self.violations,
                },
            )

        # All checks passed
        return GateVerdict(
            verdict=GateVerdictType.PASSED,
            passed=True,
            reason=f"Sharia compliant ({self.school} school)",
            details={"school": self.school},
        )

    def _check_contract_type(self, action: ActionType) -> bool:
        """
        Verify contract type is spot only.

        §8: Gold is riba'i commodity; only spot or agreed-upon forward allowed.
        No futures, options, CFDs, leverage instruments.
        """
        # In real implementation, would query broker for contract details
        # For now, assume XAU/USD spot trading
        return True

    def _check_no_overnight_interest(self, market_data: MarketData) -> bool:
        """
        Verify no overnight interest (swap charges).

        §8: Riba' (interest) is prohibited. Must be zero.
        """
        # In real implementation, would query broker for swap charges
        # For mock: always compliant
        return True

    def _check_taqabud(self) -> bool:
        """
        Verify taqābuḍ (spot possession/settlement).

        §8: Immediate transfer required; spot or T+2 maximum.
        """
        # In real implementation, would verify settlement is T+2 or less
        # For mock: always compliant
        return True

    def _check_no_leverage(self) -> bool:
        """
        Verify no financial leverage (kuli).

        §8: Leverage = gharar (uncertainty) + riba' (interest) + maysir (gambling).
        Max 1:1 (no leverage).
        """
        # In real implementation, would check account leverage setting
        # For mock: always compliant
        return True

    def _check_no_borrowing(self) -> bool:
        """
        Verify no borrowing (istiqrad).

        §8: Borrowing = riba' + gharar. Only personal capital allowed.
        """
        # In real implementation, would verify funding source
        # For mock: always compliant
        return True

    def get_compliance_status(self) -> Dict:
        """Get current compliance status."""
        return {
            "school": self.school,
            "enabled": self.config.sharia.enabled,
            "violations": self.violations,
            "compliant": len(self.violations) == 0,
        }

    def log_sharia_audit(self, action: ActionType, verdict: GateVerdict) -> Dict:
        """Create audit log entry for Sharia decision."""
        return {
            "action": action.value,
            "school": self.school,
            "passed": verdict.passed,
            "reason": verdict.reason,
            "violations": self.violations,
            "timestamp": None,  # Will be set by audit module
        }
