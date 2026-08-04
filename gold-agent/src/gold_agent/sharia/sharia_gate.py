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

        IMPLEMENTATION: Currently cannot query broker for contract type.
        SAFE DEFAULT: Return False (REJECT) — if we can't verify, we don't allow.
        """
        # TODO: Implement broker API call: contract_type = self.broker.get_instrument_type(symbol)
        # Return True only if contract_type == "SPOT"
        # For now: cannot verify, so REJECT (return False)
        return False

    def _check_no_overnight_interest(self, market_data: MarketData) -> bool:
        """
        Verify no overnight interest (swap charges).

        §8: Riba' (interest) is prohibited. Must be zero.

        IMPLEMENTATION: Cannot query broker for swap charges without real connection.
        SAFE DEFAULT: Return False (REJECT) — if we can't verify, we don't allow.
        """
        # TODO: Implement broker API call: swap_pct = self.broker.get_swap_charges(symbol)
        # Return True only if swap_pct == 0.0
        # For now: cannot verify, so REJECT (return False)
        return False

    def _check_taqabud(self) -> bool:
        """
        Verify taqābuḍ (spot possession/settlement).

        §8: Immediate transfer required; spot or T+2 maximum.

        IMPLEMENTATION: Cannot query broker for settlement terms without real connection.
        SAFE DEFAULT: Return False (REJECT) — if we can't verify, we don't allow.
        """
        # TODO: Implement broker API call: settlement = self.broker.get_settlement_type(symbol)
        # Return True only if settlement in ["T+0", "T+1", "T+2"]
        # For now: cannot verify, so REJECT (return False)
        return False

    def _check_no_leverage(self) -> bool:
        """
        Verify no financial leverage (kuli).

        §8: Leverage = gharar (uncertainty) + riba' (interest) + maysir (gambling).
        Max 1:1 (no leverage).

        IMPLEMENTATION: Cannot query broker for account leverage without real connection.
        SAFE DEFAULT: Return False (REJECT) — if we can't verify, we don't allow.
        """
        # TODO: Implement broker API call: leverage = self.broker.get_account_leverage(account_id)
        # Return True only if leverage == 1.0
        # For now: cannot verify, so REJECT (return False)
        return False

    def _check_no_borrowing(self) -> bool:
        """
        Verify no borrowing (istiqrad).

        §8: Borrowing = riba' + gharar. Only personal capital allowed.

        IMPLEMENTATION: Cannot verify funding source without real broker/audit data.
        SAFE DEFAULT: Return False (REJECT) — if we can't verify, we don't allow.
        """
        # TODO: Implement broker/audit verification: check account funding source
        # Return True only if no borrowed funds detected
        # For now: cannot verify, so REJECT (return False)
        return False

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
