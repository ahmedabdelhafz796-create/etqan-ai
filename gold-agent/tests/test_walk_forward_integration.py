"""Unit tests for walk-forward validator integration (P1 FIX #2)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from datetime import datetime
from unittest.mock import MagicMock
from gold_agent.decision.decision_engine import DecisionEngine
from gold_agent.learning.walk_forward_validator import TradeResult


class MockConfig:
    """Mock configuration object."""
    class Scoring:
        confidence_threshold_wait = 50
    
    class Brain:
        enabled = False
    
    scoring = Scoring()
    brain = Brain()


@pytest.fixture
def engine():
    """Create decision engine with walk-forward validator."""
    return DecisionEngine(MockConfig())


def test_walk_forward_validator_integrated(engine):
    """Test that walk-forward validator is integrated into decision engine."""
    assert engine.walk_forward is not None
    assert engine.parameter_audit is not None


def test_add_trade_result(engine):
    """Test adding trade results to walk-forward validator."""
    trade = TradeResult(
        trade_id="t1",
        entry_price=2050.0,
        exit_price=2060.0,
        profit_loss=100.0,
        win_rate=True,
        holding_minutes=30,
        indicator_values={"rsi": 45, "macd": 0.5, "ma": 2055},
        confidence_score=75.0,
        timestamp=datetime.utcnow()
    )
    
    engine.add_trade_result(trade)
    assert len(engine.walk_forward.trade_history) == 1


def test_parameter_change_with_insufficient_data(engine):
    """Test parameter change rejection with insufficient data."""
    # No trades added yet (minimum is 50)
    approved, report = engine.propose_parameter_change(
        parameter_name="rsi_weight",
        old_value=0.3,
        new_value=0.4,
        strategy="trend_follow",
        regime="trending"
    )
    
    assert not approved
    assert "Insufficient data" in report['reason']


def test_parameter_change_audit_trail(engine):
    """Test that parameter changes are recorded in audit trail."""
    # Add minimal trades
    for i in range(5):
        trade = TradeResult(
            trade_id=f"t{i}",
            entry_price=2050.0 + i,
            exit_price=2060.0 + i,
            profit_loss=100.0,
            win_rate=True,
            holding_minutes=30,
            indicator_values={"rsi": 45, "macd": 0.5, "ma": 2055},
            confidence_score=75.0,
            timestamp=datetime.utcnow()
        )
        engine.add_trade_result(trade)
    
    # Propose a parameter change (will be rejected due to insufficient data, but recorded)
    approved, report = engine.propose_parameter_change(
        parameter_name="rsi_weight",
        old_value=0.3,
        new_value=0.4,
        strategy="trend_follow",
        regime="trending"
    )
    
    # Check audit trail
    audit = engine.get_parameter_audit_trail()
    assert audit['total_adjustment_requests'] >= 1
    assert audit['rejected'] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
