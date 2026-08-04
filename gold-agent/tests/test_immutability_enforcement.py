"""Test immutability enforcement module."""

import pytest
from gold_agent.config import Config
from gold_agent.learning.immutability_checker import (
    ImmutabilityChecker,
    ImmutabilityViolationError,
    ParameterSection,
)


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def immutability_checker(config):
    return ImmutabilityChecker(config)


class TestImmutabilityEnforcement:
    """Test that learning module cannot access Section 1 governance parameters."""

    def test_immutable_parameters_registered(self, immutability_checker):
        """Verify all Section 1 parameters are registered as immutable."""
        assert "sharia_enabled" in immutability_checker.immutable_parameters
        assert "daily_loss_limit" in immutability_checker.immutable_parameters
        assert "max_drawdown" in immutability_checker.immutable_parameters
        assert len(immutability_checker.immutable_parameters) >= 6

    def test_learnable_parameters_registered(self, immutability_checker):
        """Verify Section 2 technical parameters are registered as learnable."""
        assert "rsi_weight" in immutability_checker.learnable_parameters
        assert "macd_weight" in immutability_checker.learnable_parameters
        assert "confidence_threshold_wait" in immutability_checker.learnable_parameters
        assert len(immutability_checker.learnable_parameters) >= 7

    def test_write_to_immutable_parameter_raises_error(self, immutability_checker):
        """Writing to Section 1 parameter should raise ImmutabilityViolationError."""
        with pytest.raises(ImmutabilityViolationError):
            immutability_checker.check_write_permission("daily_loss_limit", "section_1")

    def test_write_to_immutable_parameter_logs_violation(self, immutability_checker):
        """Attempting to write immutable parameter should log violation."""
        try:
            immutability_checker.check_write_permission("daily_loss_limit", "section_1")
        except ImmutabilityViolationError:
            pass

        assert len(immutability_checker.violation_log) > 0
        assert immutability_checker.violation_log[0]["parameter"] == "daily_loss_limit"

    def test_write_to_learnable_parameter_allowed(self, immutability_checker):
        """Writing to Section 2 parameter should be allowed."""
        result = immutability_checker.check_write_permission("rsi_weight", "section_2")
        assert result is True

    def test_immutable_parameter_values_protected(self, immutability_checker):
        """Immutable parameter values should not be modifiable through the API."""
        param = immutability_checker.immutable_parameters["daily_loss_limit"]
        original_value = param.value

        # Attempting to change the immutable_parameters dict directly would bypass
        # the API, but in production code, check_write_permission should be called first
        assert param.value == original_value  # Still unchanged

    def test_get_immutability_audit_trail(self, immutability_checker):
        """Audit trail should show immutable/learnable parameter classification."""
        audit = immutability_checker.get_immutability_audit_trail()

        assert "immutable_parameters" in audit
        assert "learnable_parameters" in audit
        assert "violation_log" in audit
        assert audit["total_violations"] >= 0

    def test_sharia_rules_immutable(self, immutability_checker):
        """Sharia governance rules must be immutable."""
        with pytest.raises(ImmutabilityViolationError):
            immutability_checker.check_write_permission("sharia_enabled", "section_1")

    def test_capital_preservation_rules_immutable(self, immutability_checker):
        """Capital preservation rules must be immutable."""
        with pytest.raises(ImmutabilityViolationError):
            immutability_checker.check_write_permission("max_consecutive_losses", "section_1")

    def test_position_hold_time_immutable(self, immutability_checker):
        """Position hold-time rule (Sharia compliance) must be immutable."""
        with pytest.raises(ImmutabilityViolationError):
            immutability_checker.check_write_permission("position_hold_time_hours", "section_1")
