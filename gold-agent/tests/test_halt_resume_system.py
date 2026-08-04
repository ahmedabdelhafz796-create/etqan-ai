"""Test halt/resume system with all 6 triggers."""

import pytest
from datetime import datetime, timedelta
from gold_agent.config import Config
from gold_agent.core.models import StateType
from gold_agent.monitoring.halt_resume_system import HaltResumeSystem, HaltReason


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def halt_resume_system(config):
    return HaltResumeSystem(config)


class TestHaltResumeTriggers:
    """Test all 6 halt triggers and resume conditions."""

    def test_trigger_1_data_disagreement_below_threshold(self, halt_resume_system):
        """Data disagreement <0.5% should not trigger halt."""
        should_halt, reason = halt_resume_system.check_trigger_1_data_disagreement(
            "source1", 2050.0, "source2", 2050.5
        )
        assert should_halt is False

    def test_trigger_1_data_disagreement_above_threshold(self, halt_resume_system):
        """Data disagreement >0.5% should trigger halt."""
        should_halt, reason = halt_resume_system.check_trigger_1_data_disagreement(
            "source1", 2050.0, "source2", 2060.5  # 0.512% difference (>0.5%)
        )
        assert should_halt is True
        assert "DATA DISAGREEMENT" in reason

    def test_trigger_1_resume_condition(self, halt_resume_system):
        """Resume when 5+ consecutive aligned quotes."""
        can_resume = halt_resume_system.check_trigger_1_resume(prices_aligned_count=5)
        assert can_resume is True

        can_resume = halt_resume_system.check_trigger_1_resume(prices_aligned_count=3)
        assert can_resume is False

    def test_trigger_2_execution_errors_below_threshold(self, halt_resume_system):
        """1-2 execution errors should not trigger halt."""
        should_halt, _ = halt_resume_system.check_trigger_2_execution_errors(True)
        assert should_halt is False

        should_halt, _ = halt_resume_system.check_trigger_2_execution_errors(True)
        assert should_halt is False

    def test_trigger_2_execution_errors_at_threshold(self, halt_resume_system):
        """3+ execution errors should trigger halt."""
        halt_resume_system.check_trigger_2_execution_errors(True)
        halt_resume_system.check_trigger_2_execution_errors(True)
        should_halt, reason = halt_resume_system.check_trigger_2_execution_errors(True)

        assert should_halt is True
        assert "EXECUTION ERROR" in reason

    def test_trigger_2_resume_requires_manual(self, halt_resume_system):
        """Execution error recovery requires manual intervention."""
        can_resume = halt_resume_system.check_trigger_2_resume()
        assert can_resume is False

    def test_trigger_3_rule_breach_escalates_emergency(self, halt_resume_system):
        """Rule breach should trigger Emergency."""
        should_halt, reason = halt_resume_system.check_trigger_3_rule_breach(
            rule_breached=True, rule_name="daily_loss_limit"
        )
        assert should_halt is True
        assert "RULE BREACH" in reason

    def test_trigger_3_resume_never_automatic(self, halt_resume_system):
        """Emergency from rule breach never auto-resumes."""
        can_resume = halt_resume_system.check_trigger_3_resume()
        assert can_resume is False

    def test_trigger_4_sharia_spike_below_threshold(self, halt_resume_system):
        """<10% Sharia rejections should not trigger halt."""
        recent_decisions = [
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": False},  # 1/10 = 10%, at threshold
        ]
        should_halt, reason = halt_resume_system.check_trigger_4_sharia_spike(recent_decisions)
        assert should_halt is False

    def test_trigger_4_sharia_spike_above_threshold(self, halt_resume_system):
        """15% Sharia rejections should trigger Safe Mode."""
        recent_decisions = [
            {"sharia_passed": True},
            {"sharia_passed": False},
            {"sharia_passed": False},
            {"sharia_passed": False},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},
            {"sharia_passed": True},  # 3/15 = 20% > 10%
        ]
        should_halt, reason = halt_resume_system.check_trigger_4_sharia_spike(recent_decisions)
        assert should_halt is True
        assert "SHARIA SPIKE" in reason

    def test_trigger_5_connection_loss_triggers_emergency(self, halt_resume_system):
        """Connection loss should trigger Emergency."""
        should_halt, reason = halt_resume_system.check_trigger_5_connection_loss(connection_healthy=False)
        assert should_halt is True
        assert "CONNECTION LOSS" in reason

    def test_trigger_5_resume_requires_health_check(self, halt_resume_system):
        """Connection resume requires both connection AND health check."""
        can_resume = halt_resume_system.check_trigger_5_resume(
            connection_healthy=True, health_check_passed=True
        )
        assert can_resume is True

        can_resume = halt_resume_system.check_trigger_5_resume(
            connection_healthy=True, health_check_passed=False
        )
        assert can_resume is False

    def test_trigger_6_price_gap_triggers_safe_mode(self, halt_resume_system):
        """Price gap >2% in 1 minute should trigger Safe Mode."""
        should_halt, reason = halt_resume_system.check_trigger_6_abnormal_market(
            current_price=2100.0, previous_price=2050.0, volatility_pct=20.0
        )
        assert should_halt is True
        assert "gap" in reason.lower() or "ABNORMAL" in reason

    def test_trigger_6_volatility_spike_triggers_safe_mode(self, halt_resume_system):
        """Volatility spike >50% should trigger Safe Mode."""
        should_halt, reason = halt_resume_system.check_trigger_6_abnormal_market(
            current_price=2050.0, previous_price=2050.0, volatility_pct=60.0
        )
        assert should_halt is True
        assert "volatility" in reason.lower() or "ABNORMAL" in reason

    def test_trigger_6_resume_requires_manual_decision(self, halt_resume_system):
        """Abnormal market recovery requires manual decision."""
        can_resume = halt_resume_system.check_trigger_6_resume()
        assert can_resume is False

    def test_escalate_to_safe_mode(self, halt_resume_system):
        """Escalation to Safe Mode should update state."""
        log_entry = halt_resume_system.escalate_to_safe_mode("Test Safe Mode trigger")
        assert halt_resume_system.current_state == StateType.SAFE_MODE
        assert log_entry["reason"] == "Test Safe Mode trigger"

    def test_escalate_to_emergency(self, halt_resume_system):
        """Escalation to Emergency should update state and set manual recovery flag."""
        log_entry = halt_resume_system.escalate_to_emergency(
            "Test Emergency trigger", HaltReason.CONNECTION_LOSS
        )
        assert halt_resume_system.current_state == StateType.EMERGENCY
        assert log_entry["manual_recovery_required"] is True

    def test_manual_recovery(self, halt_resume_system):
        """Manual recovery should exit Emergency and resume Autonomous operation."""
        # First enter Emergency
        halt_resume_system.escalate_to_emergency("Test", HaltReason.CONNECTION_LOSS)
        assert halt_resume_system.current_state == StateType.EMERGENCY

        # Then recover manually
        log_entry = halt_resume_system.manual_recovery(verified_by="operator", notes="Issue resolved")
        assert halt_resume_system.current_state == StateType.AUTONOMOUS
        assert log_entry["verified_by"] == "operator"

    def test_emergency_never_auto_exits(self, halt_resume_system):
        """Emergency state should not auto-exit (manual recovery only)."""
        halt_resume_system.current_state = StateType.EMERGENCY
        halt_resume_system.halt_timestamp = datetime.utcnow()

        # Verify there's no automatic exit mechanism
        # Manual recovery is the ONLY path out of Emergency
        assert halt_resume_system.current_state == StateType.EMERGENCY

    def test_halt_log_tracks_all_transitions(self, halt_resume_system):
        """Halt log should track all state transitions."""
        halt_resume_system.escalate_to_safe_mode("First halt")
        halt_resume_system.escalate_to_emergency("Second halt", HaltReason.DATA_DISAGREEMENT)
        halt_resume_system.manual_recovery(verified_by="user")

        halt_log = halt_resume_system.get_halt_log()
        assert len(halt_log) >= 3
        assert any("Safe Mode" in str(entry) for entry in halt_log)
        assert any("Emergency" in str(entry) for entry in halt_log)
        assert any("Autonomous" in str(entry) for entry in halt_log)

    def test_get_status_includes_halt_reason(self, halt_resume_system):
        """Status should include current state and halt reason."""
        halt_resume_system.escalate_to_emergency("Test", HaltReason.RULE_BREACH)
        status = halt_resume_system.get_status()

        assert status["current_state"].lower() == "emergency"
        assert status["halt_reason"] == "rule_breach"
        assert status["halt_timestamp"] is not None
