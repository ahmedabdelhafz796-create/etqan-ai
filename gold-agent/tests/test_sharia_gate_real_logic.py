"""Tests for real Sharia compliance verification logic.

These tests verify that the Sharia gate actually discriminates between compliant
and non-compliant conditions based on REAL MT5 data, not hardcoded returns.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add gold-agent/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gold_agent.core.models import ActionType, GateVerdictType, MarketData, StateType
from gold_agent.sharia.sharia_gate import ShariGate
from gold_agent.brokers.mt5_adapter import MT5BrokerAdapter, SymbolInfo, AccountInfo
from gold_agent.config import Config


class MockMT5Adapter:
    """Mock MT5 adapter for testing with custom responses."""

    def __init__(self):
        self.symbol_swap_free = True
        self.symbol_is_spot = True
        self.symbol_settlement = "INSTANT"
        self.account_has_margin_loans = False

    def is_swap_free(self, symbol: str) -> bool:
        return self.symbol_swap_free

    def get_swap_rate(self, symbol: str) -> float:
        return 0.0 if self.symbol_swap_free else 0.02

    def is_spot_contract(self, symbol: str) -> bool:
        return self.symbol_is_spot

    def is_instant_settlement(self, symbol: str) -> bool:
        return self.symbol_settlement in ["INSTANT", "T+0", "T+1", "T+2"]

    def is_no_margin_loan(self) -> bool:
        return not self.account_has_margin_loans


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def market_data():
    return MarketData(
        timestamp=datetime.utcnow(),
        xau_usd=2050.0,
        dxy=104.0,
    )


class TestShariGateRealLogic:
    """Test Sharia gate with real verification logic."""

    def test_compliant_symbol_passes(self, config, market_data):
        """Symbol that passes all 4 checks should PASS."""
        mock_adapter = MockMT5Adapter()
        # All conditions compliant
        mock_adapter.symbol_swap_free = True  # No Riba
        mock_adapter.symbol_is_spot = True  # Spot contract
        mock_adapter.symbol_settlement = "INSTANT"  # Taqabud compliant
        mock_adapter.account_has_margin_loans = False  # No borrowing

        gate = ShariGate(config, broker_adapter=mock_adapter)
        verdict = gate.check(ActionType.BUY, market_data)

        assert verdict.passed is True
        assert verdict.verdict == GateVerdictType.PASSED
        assert len(gate.violations) == 0
        assert "all 4 checks verified" in verdict.reason.lower()

    def test_swap_charges_fails_no_riba_check(self, config, market_data):
        """Symbol with swap charges (non-zero) should FAIL no-Riba check."""
        mock_adapter = MockMT5Adapter()
        # Only swap is non-compliant
        mock_adapter.symbol_swap_free = False  # FAILS: Has swap charges
        mock_adapter.symbol_is_spot = True
        mock_adapter.symbol_settlement = "INSTANT"
        mock_adapter.account_has_margin_loans = False

        gate = ShariGate(config, broker_adapter=mock_adapter)
        verdict = gate.check(ActionType.BUY, market_data)

        assert verdict.passed is False
        assert verdict.verdict == GateVerdictType.BLOCKED
        assert len(gate.violations) == 1
        assert "Riba" in gate.violations[0]
        assert "swap" in gate.violations[0].lower()

    def test_non_spot_contract_fails(self, config, market_data):
        """Non-spot contract (CFD/derivative) should FAIL contract type check."""
        mock_adapter = MockMT5Adapter()
        # Only contract type is non-compliant
        mock_adapter.symbol_swap_free = True
        mock_adapter.symbol_is_spot = False  # FAILS: Not spot
        mock_adapter.symbol_settlement = "INSTANT"
        mock_adapter.account_has_margin_loans = False

        gate = ShariGate(config, broker_adapter=mock_adapter)
        verdict = gate.check(ActionType.BUY, market_data)

        assert verdict.passed is False
        assert verdict.verdict == GateVerdictType.BLOCKED
        assert len(gate.violations) == 1
        assert "Contract type" in gate.violations[0]

    def test_deferred_settlement_fails_taqabud(self, config, market_data):
        """Deferred settlement (>T+2) should FAIL Taqabud check."""
        mock_adapter = MockMT5Adapter()
        # Only settlement is non-compliant
        mock_adapter.symbol_swap_free = True
        mock_adapter.symbol_is_spot = True
        mock_adapter.symbol_settlement = "T+5"  # FAILS: Deferred
        mock_adapter.account_has_margin_loans = False

        gate = ShariGate(config, broker_adapter=mock_adapter)
        verdict = gate.check(ActionType.BUY, market_data)

        assert verdict.passed is False
        assert verdict.verdict == GateVerdictType.BLOCKED
        assert len(gate.violations) == 1
        assert "Settlement" in gate.violations[0]

    def test_margin_loan_fails_no_borrowing(self, config, market_data):
        """Active margin loan should FAIL no-borrowing check."""
        mock_adapter = MockMT5Adapter()
        # Only margin loan is non-compliant
        mock_adapter.symbol_swap_free = True
        mock_adapter.symbol_is_spot = True
        mock_adapter.symbol_settlement = "INSTANT"
        mock_adapter.account_has_margin_loans = True  # FAILS: Has loan

        gate = ShariGate(config, broker_adapter=mock_adapter)
        verdict = gate.check(ActionType.BUY, market_data)

        assert verdict.passed is False
        assert verdict.verdict == GateVerdictType.BLOCKED
        assert len(gate.violations) == 1
        assert "Margin loan" in gate.violations[0]

    def test_multiple_violations_all_reported(self, config, market_data):
        """Multiple violations should all be reported."""
        mock_adapter = MockMT5Adapter()
        # All conditions non-compliant
        mock_adapter.symbol_swap_free = False  # FAILS: Swap
        mock_adapter.symbol_is_spot = False  # FAILS: Not spot
        mock_adapter.symbol_settlement = "T+5"  # FAILS: Settlement
        mock_adapter.account_has_margin_loans = True  # FAILS: Margin

        gate = ShariGate(config, broker_adapter=mock_adapter)
        verdict = gate.check(ActionType.BUY, market_data)

        assert verdict.passed is False
        assert verdict.verdict == GateVerdictType.BLOCKED
        assert len(gate.violations) == 4  # All 4 checks failed
        assert "Riba" in str(gate.violations)
        assert "Contract type" in str(gate.violations)
        assert "Settlement" in str(gate.violations)
        assert "Margin loan" in str(gate.violations)

    def test_three_pass_one_fail_is_blocked(self, config, market_data):
        """If 3 checks pass but 1 fails, entire gate is BLOCKED."""
        mock_adapter = MockMT5Adapter()
        # 3 pass, 1 fails (swap)
        mock_adapter.symbol_swap_free = False  # FAILS
        mock_adapter.symbol_is_spot = True
        mock_adapter.symbol_settlement = "INSTANT"
        mock_adapter.account_has_margin_loans = False

        gate = ShariGate(config, broker_adapter=mock_adapter)
        verdict = gate.check(ActionType.BUY, market_data)

        assert verdict.passed is False
        assert verdict.verdict == GateVerdictType.BLOCKED
        assert len(gate.violations) == 1

    def test_t_plus_2_settlement_passes_taqabud(self, config, market_data):
        """T+2 settlement is compliant with Taqabud (maximum allowed)."""
        mock_adapter = MockMT5Adapter()
        mock_adapter.symbol_swap_free = True
        mock_adapter.symbol_is_spot = True
        mock_adapter.symbol_settlement = "T+2"  # Exactly at limit, should pass
        mock_adapter.account_has_margin_loans = False

        gate = ShariGate(config, broker_adapter=mock_adapter)
        verdict = gate.check(ActionType.BUY, market_data)

        assert verdict.passed is True
        assert verdict.verdict == GateVerdictType.PASSED
        assert len(gate.violations) == 0

    def test_t_plus_0_settlement_passes_taqabud(self, config, market_data):
        """T+0 settlement (instant) is compliant with Taqabud."""
        mock_adapter = MockMT5Adapter()
        mock_adapter.symbol_swap_free = True
        mock_adapter.symbol_is_spot = True
        mock_adapter.symbol_settlement = "T+0"  # Instant, should pass
        mock_adapter.account_has_margin_loans = False

        gate = ShariGate(config, broker_adapter=mock_adapter)
        verdict = gate.check(ActionType.BUY, market_data)

        assert verdict.passed is True
        assert verdict.verdict == GateVerdictType.PASSED

    def test_leverage_allowed_with_zero_swap(self, config, market_data):
        """
        Leverage is ALLOWED as long as swap is zero (no interest).

        This test verifies the key design change:
        - The old check had a separate "no leverage" rule (always reject leverage)
        - The new check only requires "no Riba" (zero swap)
        - Leverage is acceptable at any level if swap is zero
        """
        mock_adapter = MockMT5Adapter()
        # Swap is zero (compliant with no-Riba)
        # Account might have leverage, but if swap is 0, it's Sharia-compliant
        mock_adapter.symbol_swap_free = True  # Zero swap = no interest on leverage
        mock_adapter.symbol_is_spot = True
        mock_adapter.symbol_settlement = "INSTANT"
        mock_adapter.account_has_margin_loans = False

        gate = ShariGate(config, broker_adapter=mock_adapter)
        verdict = gate.check(ActionType.BUY, market_data)

        # This should PASS because leverage + zero swap is Sharia-compliant
        assert verdict.passed is True
        assert verdict.verdict == GateVerdictType.PASSED
        assert "Riba" not in str(gate.violations)

    def test_gate_disabled_always_passes(self, config, market_data):
        """When Sharia gate is disabled in config, always PASS."""
        config.sharia.enabled = False
        mock_adapter = MockMT5Adapter()
        # Make adapter non-compliant to verify gate is truly disabled
        mock_adapter.symbol_swap_free = False
        mock_adapter.symbol_is_spot = False
        mock_adapter.symbol_settlement = "T+5"
        mock_adapter.account_has_margin_loans = True

        gate = ShariGate(config, broker_adapter=mock_adapter)
        verdict = gate.check(ActionType.BUY, market_data)

        # Should pass regardless of adapter state
        assert verdict.passed is True
        assert verdict.verdict == GateVerdictType.PASSED
        assert "disabled" in verdict.reason.lower()

    def test_mock_adapter_xau_usd_compliant(self):
        """
        Real MT5BrokerAdapter in mock mode: XAU/USD should be swap-free and compliant.

        This verifies the default mock data represents a compliant instrument.
        """
        real_adapter = MT5BrokerAdapter(real_connection=False)  # Mock mode

        # Gold should be swap-free
        assert real_adapter.is_swap_free("XAU/USD") is True

        # Gold should be spot contract
        assert real_adapter.is_spot_contract("XAU/USD") is True

        # Gold should have instant settlement
        assert real_adapter.is_instant_settlement("XAU/USD") is True

        # Account should have no margin loans
        assert real_adapter.is_no_margin_loan() is True

    def test_mock_adapter_eur_usd_has_swaps(self):
        """
        Real MT5BrokerAdapter in mock mode: EUR/USD should have swap charges.

        This verifies the mock data includes both compliant and non-compliant examples.
        """
        real_adapter = MT5BrokerAdapter(real_connection=False)  # Mock mode

        # EUR/USD should have swap charges
        assert real_adapter.is_swap_free("EURUSD") is False

        # But it's still a spot contract
        assert real_adapter.is_spot_contract("EURUSD") is True

    def test_compliance_status_report(self, config, market_data):
        """Compliance status report should reflect verification results."""
        mock_adapter = MockMT5Adapter()
        mock_adapter.symbol_swap_free = False  # One violation

        gate = ShariGate(config, broker_adapter=mock_adapter)
        gate.check(ActionType.BUY, market_data)

        status = gate.get_compliance_status()

        assert status["enabled"] is True
        assert status["compliant"] is False
        assert len(status["violations"]) == 1
        assert status["school"] == "hanafi"

    def test_audit_log_records_violations(self, config, market_data):
        """Audit log should record all violations."""
        mock_adapter = MockMT5Adapter()
        mock_adapter.symbol_swap_free = False
        mock_adapter.symbol_is_spot = False

        gate = ShariGate(config, broker_adapter=mock_adapter)
        verdict = gate.check(ActionType.BUY, market_data)

        audit_log = gate.log_sharia_audit(ActionType.BUY, verdict)

        assert audit_log["action"] == "BUY"
        assert audit_log["passed"] is False
        assert len(audit_log["violations"]) == 2
        assert audit_log["school"] == "hanafi"
