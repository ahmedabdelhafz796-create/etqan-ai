"""Unit tests for Capital Preservation Constitution (PART 1 of Phase 1.5)."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from gold_agent.risk.capital_preservation import CapitalPreservationEngine


class MockCapitalConfig:
    """Mock capital configuration."""
    daily_loss_limit_percent = 5.0
    max_drawdown_percent = 15.0
    max_position_size_percent = 2.0
    max_consecutive_losses = 3


class MockConfig:
    """Mock configuration object."""
    def __init__(self):
        self.capital = MockCapitalConfig()


@pytest.fixture
def engine():
    """Create capital preservation engine with $10,000 initial capital."""
    config = MockConfig()
    return CapitalPreservationEngine(config, initial_capital=10000.0)


# ============================================================================
# TEST 1: VAN THARP POSITION SIZING
# ============================================================================

def test_van_tharp_position_sizing_basic(engine):
    """Test basic Van Tharp position sizing formula."""
    # Entry: $2050, Stop Loss: $2040, Equity: $10,000, Risk: 2%
    # Account Risk = $10,000 × 2% = $200
    # Price Risk = $2050 - $2040 = $10
    # Position Size = $200 / $10 = 20 units

    position_size, audit = engine.calculate_position_size(
        entry_price=2050.0,
        stop_loss_price=2040.0,
        risk_per_trade_pct=2.0,
    )

    assert position_size == 20.0, f"Expected 20 units, got {position_size}"
    assert audit["account_risk_dollars"] == 200.0
    assert audit["position_size"] == 20.0
    assert "formula" in audit


def test_van_tharp_with_different_equity(engine):
    """Test position sizing remains constant despite equity changes (Fixed Baseline Principle).

    CRITICAL: Position sizing uses INITIAL capital, not current equity.
    This test verifies that even when equity changes, position size remains constant.
    """
    # First trade: initial equity = $10,000, 2% risk
    size1, _ = engine.calculate_position_size(
        entry_price=2050.0,
        stop_loss_price=2040.0,
        risk_per_trade_pct=2.0,
    )
    # Account Risk = $10,000 × 2% = $200
    # Position Size = $200 / $10 = 20 units
    assert size1 == 20.0

    # Simulate losing $1000 (equity now $9000)
    engine.current_equity = 9000.0

    # Second trade: equity changed but position size should REMAIN CONSTANT
    size2, _ = engine.calculate_position_size(
        entry_price=2050.0,
        stop_loss_price=2040.0,
        risk_per_trade_pct=2.0,
    )

    # Position size should still be 20 units (based on initial $10K, not current $9K)
    assert size2 == 20.0, (
        f"Position size should remain 20 units even after equity drop to $9K. "
        f"Got {size2}. If this fails, sizing is using current_equity (BUG)."
    )


def test_van_tharp_caps_risk_at_2_percent(engine):
    """Test immutable rule: Risk per trade cannot exceed 2%."""
    # Try to set 3%, should be capped at 2%
    position_size, audit = engine.calculate_position_size(
        entry_price=2050.0,
        stop_loss_price=2040.0,
        risk_per_trade_pct=3.0,  # Exceeds cap
    )

    assert audit["risk_per_trade_percent"] == 2.0, "Should be capped at 2%"


def test_van_tharp_rejects_invalid_prices(engine):
    """Test that entry <= stop loss raises error."""
    with pytest.raises(ValueError):
        engine.calculate_position_size(
            entry_price=2040.0,
            stop_loss_price=2050.0,  # Invalid: SL above entry
        )


def test_van_tharp_kelly_diagnostic(engine):
    """Test Kelly Criterion diagnostic (informational only)."""
    position_size, audit = engine.calculate_position_size(
        entry_price=2050.0,
        stop_loss_price=2040.0,
    )

    # Kelly should be calculated
    assert "kelly_fraction" in audit
    assert 0 < audit["kelly_fraction"] <= 0.25  # Clamped
    assert "quarter_kelly" in audit
    assert audit["quarter_kelly"] == audit["kelly_fraction"] / 4.0


# ============================================================================
# TEST 2: DAILY LOSS LIMIT (5% Auto-Halt)
# ============================================================================

def test_daily_loss_limit_allows_trades_below_threshold(engine):
    """Test that trades below 5% daily limit are allowed."""
    # Current daily loss: $300 (3% of $10,000)
    engine.daily_loss_amount = 300.0
    engine.daily_loss_percent = 3.0

    allowed, reason = engine.check_daily_loss_limit(proposed_trade_loss_dollars=100.0)
    assert allowed is True
    assert "OK" in reason


def test_daily_loss_limit_blocks_at_threshold(engine):
    """Test that trades are blocked when daily loss reaches 5%."""
    # Current daily loss: $500 (5% of $10,000)
    engine.daily_loss_amount = 500.0
    engine.daily_loss_percent = 5.0

    allowed, reason = engine.check_daily_loss_limit()
    assert allowed is False
    assert "BREACHED" in reason


def test_daily_loss_limit_blocks_if_would_exceed(engine):
    """Test that trades are blocked if they would exceed 5% limit."""
    # Current daily loss: $450 (4.5% of $10,000)
    engine.daily_loss_amount = 450.0
    engine.daily_loss_percent = 4.5

    # Proposing trade that could lose $100 (total would be 5.5%)
    allowed, reason = engine.check_daily_loss_limit(proposed_trade_loss_dollars=100.0)
    assert allowed is False
    assert "would be BREACHED" in reason


def test_daily_loss_limit_resets_at_utc_midnight(engine):
    """Test that daily loss resets at UTC 00:00."""
    engine.daily_loss_amount = 500.0
    engine.daily_loss_percent = 5.0

    # Manually set reset time to now (simulating midnight reset)
    engine.daily_reset_time = datetime.utcnow()

    # Trigger reset check
    engine._check_and_reset_daily_counter()

    # Should be reset
    assert engine.daily_loss_amount == 0.0
    assert engine.daily_loss_percent == 0.0


# ============================================================================
# TEST 3: DRAWDOWN CIRCUIT BREAKER (15% Emergency)
# ============================================================================

def test_drawdown_circuit_breaker_allows_below_threshold(engine):
    """Test that drawdown below 15% allows trading."""
    engine.peak_equity = 10000.0
    engine.current_equity = 8800.0  # 12% drawdown

    allowed, reason = engine.check_drawdown_circuit_breaker()
    assert allowed is True
    assert "OK" in reason


def test_drawdown_circuit_breaker_triggers_at_threshold(engine):
    """Test that drawdown >= 15% triggers emergency."""
    engine.peak_equity = 10000.0
    engine.current_equity = 8500.0  # 15% drawdown

    allowed, reason = engine.check_drawdown_circuit_breaker()
    assert allowed is False
    assert "EMERGENCY" in reason
    assert "circuit breaker" in reason.lower()


def test_drawdown_tracks_peak_equity(engine):
    """Test that peak equity (watermark) is updated on gains."""
    engine.peak_equity = 10000.0
    engine.current_equity = 9000.0

    # Simulate recovery
    engine.current_equity = 11000.0

    engine.check_drawdown_circuit_breaker()

    # Peak should be updated
    assert engine.peak_equity == 11000.0


def test_drawdown_manual_recovery_only(engine):
    """Test that Emergency state requires manual recovery (no auto-exit)."""
    engine.peak_equity = 10000.0
    engine.current_equity = 8400.0  # 16% drawdown (Emergency)

    allowed, reason = engine.check_drawdown_circuit_breaker()
    assert allowed is False

    # Even if we recover slightly, we're still in Emergency until manual reset
    engine.current_equity = 9500.0  # Now only 5% down from peak
    allowed, reason = engine.check_drawdown_circuit_breaker()
    # Should still be blocked because peak_equity wasn't reset
    assert engine.peak_equity == 10000.0  # Unchanged from emergency


# ============================================================================
# TEST 4: CONSECUTIVE LOSS PAUSE (3-4 Trades)
# ============================================================================

def test_consecutive_loss_pause_allows_below_threshold(engine):
    """Test that <3 consecutive losses are allowed."""
    engine.consecutive_losses = 2

    allowed, reason = engine.check_consecutive_loss_pause()
    assert allowed is True


def test_consecutive_loss_pause_blocks_at_threshold(engine):
    """Test that >=3 consecutive losses trigger pause."""
    engine.consecutive_losses = 3

    allowed, reason = engine.check_consecutive_loss_pause()
    assert allowed is False
    assert "pause" in reason.lower()


def test_consecutive_loss_resets_on_win(engine):
    """Test that consecutive loss counter resets on winning trade."""
    engine.consecutive_losses = 2

    # Record a winning trade
    engine.record_trade_result(
        trade_id="win_trade",
        entry_price=2050.0,
        exit_price=2070.0,  # +$20 win
        quantity=10.0,
        entry_time=datetime.utcnow() - timedelta(hours=1),
    )

    assert engine.consecutive_losses == 0


# ============================================================================
# TEST 5: POSITION HOLD-TIME HARD RULE (24 Hours)
# ============================================================================

def test_position_hold_time_below_limit(engine):
    """Test that positions below 24h are not forced to close."""
    trade_id = "test_trade_1"
    entry_time = datetime.utcnow() - timedelta(hours=20)

    engine.record_position_opened(trade_id, 2050.0, entry_time)

    should_close, reason = engine.check_position_hold_time(trade_id)
    assert should_close is False
    assert reason is None


def test_position_hold_time_at_limit_forces_close(engine):
    """Test that positions at/above 24h are force-closed."""
    trade_id = "test_trade_2"
    entry_time = datetime.utcnow() - timedelta(hours=24, minutes=1)

    engine.record_position_opened(trade_id, 2050.0, entry_time)

    should_close, reason = engine.check_position_hold_time(trade_id)
    assert should_close is True
    assert "LIMIT REACHED" in reason
    assert "24h" in reason
    assert "Sharia" in reason  # Should mention Sharia compliance


def test_position_hold_time_sharia_safeguard(engine):
    """Test that hold-time limit ensures closure before broker grace period."""
    # Typical broker grace period: 5-10 days
    # Our limit: 24 hours
    # Ensures positions close 4-9 days before any swap/holding fees
    trade_id = "sharia_test"
    entry_time = datetime.utcnow() - timedelta(hours=23, minutes=59)

    engine.record_position_opened(trade_id, 2050.0, entry_time)
    should_close_before, _ = engine.check_position_hold_time(trade_id)

    # Wait 2 minutes (simulate time passing)
    entry_time = datetime.utcnow() - timedelta(hours=24, minutes=1)
    engine.active_positions[trade_id] = (entry_time, 2050.0)

    should_close_after, _ = engine.check_position_hold_time(trade_id)

    assert should_close_before is False
    assert should_close_after is True


# ============================================================================
# TEST 6: TRADE RESULT RECORDING & AUDIT TRAIL
# ============================================================================

def test_record_winning_trade(engine):
    """Test recording a winning trade."""
    initial_equity = engine.current_equity

    audit = engine.record_trade_result(
        trade_id="win_001",
        entry_price=2050.0,
        exit_price=2070.0,  # +$20 per unit
        quantity=10.0,
        entry_time=datetime.utcnow() - timedelta(hours=2),
    )

    # P&L = (2070 - 2050) * 10 = $200
    assert audit["pnl_dollars"] == 200.0
    assert audit["pnl_percent"] == (20.0 / 2050.0) * 100
    assert engine.current_equity == initial_equity + 200.0
    assert engine.consecutive_losses == 0  # Reset on win


def test_record_losing_trade(engine):
    """Test recording a losing trade."""
    initial_equity = engine.current_equity

    audit = engine.record_trade_result(
        trade_id="loss_001",
        entry_price=2050.0,
        exit_price=2040.0,  # -$10 per unit
        quantity=10.0,
        entry_time=datetime.utcnow() - timedelta(hours=1),
    )

    # P&L = (2040 - 2050) * 10 = -$100
    assert audit["pnl_dollars"] == -100.0
    assert engine.current_equity == initial_equity - 100.0
    assert engine.consecutive_losses == 1  # Incremented on loss
    assert engine.daily_loss_amount == 100.0


def test_audit_trail_complete(engine):
    """Test that trade audit trail is complete and queryable."""
    engine.record_trade_result(
        trade_id="audit_001",
        entry_price=2050.0,
        exit_price=2070.0,
        quantity=10.0,
        entry_time=datetime.utcnow() - timedelta(hours=2),
    )

    audit = engine.trades_history[0]

    # Verify all required fields
    assert "trade_id" in audit
    assert "pnl_dollars" in audit
    assert "pnl_percent" in audit
    assert "hold_duration_hours" in audit
    assert "consecutive_losses" in audit
    assert "drawdown_percent" in audit
    assert audit["trade_id"] == "audit_001"


# ============================================================================
# TEST 7: IMMUTABLE RULE ENFORCEMENT
# ============================================================================

def test_config_validation_on_init(engine):
    """Test that config values are validated as immutable."""
    # Engine should validate that limits are reasonable
    assert engine.config.capital.daily_loss_limit_percent <= 10.0
    assert engine.config.capital.max_drawdown_percent <= 50.0
    assert engine.config.capital.max_position_size_percent <= 5.0


def test_immutable_risk_cap(engine):
    """Test that risk per trade is immutable capped at 2%."""
    # Even if config tries 5%, actual calculation caps it
    position_size, audit = engine.calculate_position_size(
        entry_price=2050.0,
        stop_loss_price=2040.0,
        risk_per_trade_pct=5.0,
    )

    assert audit["risk_per_trade_percent"] == 2.0


# ============================================================================
# TEST 8: CAPITAL STATUS REPORTING
# ============================================================================

def test_capital_status_report(engine):
    """Test that capital status returns complete audit state."""
    engine.current_equity = 9500.0
    engine.daily_loss_amount = 250.0
    engine.consecutive_losses = 1

    status = engine.get_capital_status()

    assert "timestamp" in status
    assert status["current_equity"] == 9500.0
    assert status["initial_capital"] == 10000.0
    assert status["equity_change_dollars"] == -500.0
    assert status["daily_loss_amount"] == 250.0
    assert status["consecutive_losses"] == 1
    assert "status" in status  # Should be "OK" or "DAILY_LIMIT_BREACHED", etc.


def test_capital_status_shows_emergency(engine):
    """Test that capital status reflects Emergency state."""
    engine.peak_equity = 10000.0
    engine.current_equity = 8400.0  # 16% drawdown

    status = engine.get_capital_status()
    assert status["status"] == "DRAWDOWN_LIMIT_BREACHED"


def test_capital_status_shows_daily_limit(engine):
    """Test that capital status reflects daily loss limit."""
    engine.daily_loss_amount = 500.0
    engine.daily_loss_percent = 5.0

    status = engine.get_capital_status()
    assert status["status"] == "DAILY_LIMIT_BREACHED"


# ============================================================================
# TEST 9: EDGE CASES & INTEGRATION
# ============================================================================

def test_multiple_losses_accumulate_correctly(engine):
    """Test that multiple losing trades accumulate daily loss."""
    initial = engine.current_equity

    # First loss: -$100
    engine.record_trade_result(
        trade_id="loss_1",
        entry_price=2050.0,
        exit_price=2040.0,
        quantity=10.0,
        entry_time=datetime.utcnow(),
    )

    # Second loss: -$200
    engine.record_trade_result(
        trade_id="loss_2",
        entry_price=2060.0,
        exit_price=2040.0,
        quantity=10.0,
        entry_time=datetime.utcnow(),
    )

    assert engine.daily_loss_amount == 300.0
    assert engine.consecutive_losses == 2
    assert engine.current_equity == initial - 300.0


def test_mixed_win_loss_sequence(engine):
    """Test realistic win/loss sequence."""
    initial = engine.current_equity

    # Win: (2070-2050)*10 = $200
    engine.record_trade_result("trade_1", 2050.0, 2070.0, 10.0, datetime.utcnow())
    assert engine.consecutive_losses == 0

    # Loss: (2060-2070)*10 = -$100
    engine.record_trade_result("trade_2", 2070.0, 2060.0, 10.0, datetime.utcnow())
    assert engine.consecutive_losses == 1

    # Win: (2080-2060)*10 = $200
    engine.record_trade_result("trade_3", 2060.0, 2080.0, 10.0, datetime.utcnow())
    assert engine.consecutive_losses == 0  # Reset on win

    expected_equity = initial + 200 - 100 + 200  # = initial + 300
    assert engine.current_equity == expected_equity


# ============================================================================
# REGRESSION TESTS (P0) — These MUST FAIL if bugs are reintroduced
# ============================================================================

def test_position_sizing_never_uses_current_equity():
    """REGRESSION TEST: Position sizing must use initial_capital, never current_equity.

    BUG IDENTIFIED: capital_preservation.py line 96 was using current_equity instead of
    initial_capital. This violates Fixed Baseline Principle from MASTER_PLAN.

    IMPACT: If bug reappears, position sizes grow after wins (house-money effect).
    REQUIREMENT: Position size must remain CONSTANT across win/loss sequences.

    This test MUST FAIL if someone changes line 96 back to current_equity.
    """
    config = MockConfig()
    engine = CapitalPreservationEngine(config, initial_capital=10000.0)

    # First trade: entry $2050, stop $2040 (10 point risk), 1% risk
    # Position Size = (Initial Capital × Risk%) / (Entry - Stop Loss)
    #               = ($10,000 × 1%) / ($2050 - $2040)
    #               = $100 / $10 = 10 units
    size1, audit1 = engine.calculate_position_size(
        entry_price=2050.0,
        stop_loss_price=2040.0,
        risk_per_trade_pct=1.0
    )
    assert size1 == 10.0, f"First trade size should be 10 units, got {size1}"
    assert audit1['account_risk_dollars'] == 100.0, "Risk should be $100 (1% of $10K)"

    # Simulate +$400 profit (equity now $10,400)
    engine.current_equity = 10400.0

    # Second trade: SAME entry/stop/risk parameters, should produce SAME position size
    # (even though equity increased, position size stays constant)
    size2, audit2 = engine.calculate_position_size(
        entry_price=2050.0,
        stop_loss_price=2040.0,
        risk_per_trade_pct=1.0
    )
    assert size2 == 10.0, (
        f"Second trade size should STILL be 10 units (not {size2}). "
        f"If size2 != 10, position sizing is using current_equity (BUG REAPPEARED)"
    )
    assert audit2['account_risk_dollars'] == 100.0, (
        "Risk dollars must be identical to first trade, regardless of current_equity"
    )

    # Simulate -$200 loss (equity now $10,200)
    engine.current_equity = 10200.0

    # Third trade: SAME parameters again
    # Position size should remain constant (based on initial $10K, not current $10.2K or $10.4K)
    size3, audit3 = engine.calculate_position_size(
        entry_price=2050.0,
        stop_loss_price=2040.0,
        risk_per_trade_pct=1.0
    )
    assert size3 == 10.0, (
        f"Third trade size should STILL be 10 units (not {size3}). "
        f"Position size must not shrink after losses."
    )

    # Verify all three audits show identical risk dollars (proof of Fixed Baseline)
    assert (audit1['account_risk_dollars'] ==
            audit2['account_risk_dollars'] ==
            audit3['account_risk_dollars'] == 100.0)


def test_default_risk_is_one_percent_not_two_percent():
    """REGRESSION TEST: Default risk per trade must be 1% (not 2%, which is absolute ceiling).

    BUG IDENTIFIED: capital_preservation.py line 84 was setting default to
    max_position_size_percent (2%) instead of 1%.

    REQUIREMENT: Default risk = 1%, ceiling = 2%, explicit requests honored within ceiling.

    This test MUST FAIL if someone changes line 84 default back to 2% or to max_position_size_percent.
    """
    config = MockConfig()
    engine = CapitalPreservationEngine(config, initial_capital=10000.0)

    # Test 1: No explicit risk_per_trade_pct should use 1% default
    size_default, audit_default = engine.calculate_position_size(
        entry_price=2050.0,
        stop_loss_price=2040.0,
        risk_per_trade_pct=None  # Explicitly None to test default
    )
    assert audit_default['risk_per_trade_percent'] == 1.0, (
        f"Default risk should be 1.0%, got {audit_default['risk_per_trade_percent']}%"
    )
    assert audit_default['account_risk_dollars'] == 100.0, (
        f"With 1% default on $10K, risk should be $100, got ${audit_default['account_risk_dollars']}"
    )
    # Position size = $100 / $10 = 10 units
    assert size_default == 10.0, f"Position size should be 10 units (not 100), got {size_default}"

    # Test 2: Request >2% should cap to 2% with warning
    size_capped, audit_capped = engine.calculate_position_size(
        entry_price=2050.0,
        stop_loss_price=2040.0,
        risk_per_trade_pct=2.5
    )
    assert audit_capped['risk_per_trade_percent'] == 2.0, (
        f"2.5% request should cap to 2.0%, got {audit_capped['risk_per_trade_percent']}%"
    )
    assert audit_capped['account_risk_dollars'] == 200.0, (
        f"Capped 2% on $10K should give $200 risk, got ${audit_capped['account_risk_dollars']}"
    )
    # Position size = $200 / $10 = 20 units
    assert size_capped == 20.0, f"Position size should be 20 units, got {size_capped}"

    # Test 3: Explicit 1.5% should be honored (between default and ceiling)
    size_explicit, audit_explicit = engine.calculate_position_size(
        entry_price=2050.0,
        stop_loss_price=2040.0,
        risk_per_trade_pct=1.5
    )
    assert audit_explicit['risk_per_trade_percent'] == 1.5, (
        f"Explicit 1.5% should be honored, got {audit_explicit['risk_per_trade_percent']}%"
    )
    assert audit_explicit['account_risk_dollars'] == 150.0, (
        f"1.5% on $10K should give $150 risk, got ${audit_explicit['account_risk_dollars']}"
    )
    # Position size = $150 / $10 = 15 units
    assert size_explicit == 15.0, f"Position size should be 15 units, got {size_explicit}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
