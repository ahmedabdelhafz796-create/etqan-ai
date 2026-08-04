"""Walk-Forward Validator — Prevents overfitting to recent noise.

DESIGN PRINCIPLE (§4 MASTER_PLAN):
Before any parameter adjustment (technical weights, confidence thresholds),
validate on hold-out test data that performance IMPROVES, not degrades.

Prevents:
1. Optimizing to last 20 trades (noise)
2. "Fitting" to market conditions that won't repeat
3. Parameter drift over time
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json


@dataclass
class TradeResult:
    """Single trade result for validation."""
    trade_id: str
    entry_price: float
    exit_price: float
    profit_loss: float
    win_rate: bool  # True if profitable, False otherwise
    holding_minutes: int
    indicator_values: Dict  # RSI, MACD, MA values at entry
    confidence_score: float
    timestamp: datetime


class WalkForwardValidator:
    """Validates parameter changes before applying them."""

    def __init__(self, min_sample_size: int = 50):
        """
        Initialize validator.

        Args:
            min_sample_size: Minimum trades per strategy/regime before adjusting parameters
                            (prevents overfitting on small samples)
        """
        self.min_sample_size = min_sample_size
        self.trade_history: List[TradeResult] = []
        self.parameter_changes: List[Dict] = []

    def add_trade(self, trade: TradeResult):
        """Add a completed trade to history."""
        self.trade_history.append(trade)

    def can_adjust_parameters(self, strategy: str, regime: str) -> Tuple[bool, str]:
        """
        Check if enough data exists to safely adjust parameters.

        Args:
            strategy: "trend_follow", "mean_revert", etc.
            regime: "trending", "ranging", "high_volatility"

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        # Count trades for this strategy/regime combination
        matching_trades = self._filter_trades(strategy, regime)

        if len(matching_trades) < self.min_sample_size:
            return (
                False,
                f"Insufficient data: {len(matching_trades)}/{self.min_sample_size} trades for {strategy}/{regime}"
            )

        return True, f"Sufficient data: {len(matching_trades)} trades for {strategy}/{regime}"

    def validate_parameter_change(
        self,
        parameter_name: str,
        old_value: float,
        new_value: float,
        strategy: str,
        regime: str,
    ) -> Tuple[bool, Dict]:
        """
        Validate parameter change using walk-forward testing.

        Split trade history into:
        1. Training period (first 60% of trades)
        2. Test period (last 40% of trades)

        Calculate:
        - Performance with OLD parameters on test data
        - Performance with NEW parameters on test data
        - Approve change only if NEW > OLD on test data

        Args:
            parameter_name: "rsi_weight", "confidence_threshold_act", etc.
            old_value: Current parameter value
            new_value: Proposed new value
            strategy: Trading strategy
            regime: Market regime

        Returns:
            Tuple of (approved: bool, report: Dict with detailed metrics)
        """
        # Check minimum sample size
        can_adjust, reason = self.can_adjust_parameters(strategy, regime)
        if not can_adjust:
            return False, {"reason": reason, "approved": False}

        matching_trades = self._filter_trades(strategy, regime)

        # Split into training and test
        split_point = int(len(matching_trades) * 0.6)
        train_trades = matching_trades[:split_point]
        test_trades = matching_trades[split_point:]

        # Simulate performance with old parameters
        old_performance = self._simulate_performance(test_trades, parameter_name, old_value)

        # Simulate performance with new parameters
        new_performance = self._simulate_performance(test_trades, parameter_name, new_value)

        # Decide approval
        approved = new_performance["win_rate"] > old_performance["win_rate"] and \
                   new_performance["profit_factor"] > old_performance["profit_factor"]

        report = {
            "approved": approved,
            "parameter": parameter_name,
            "old_value": old_value,
            "new_value": new_value,
            "strategy": strategy,
            "regime": regime,
            "sample_size": len(matching_trades),
            "train_trades": len(train_trades),
            "test_trades": len(test_trades),
            "old_performance": old_performance,
            "new_performance": new_performance,
            "improvement": {
                "win_rate_delta": new_performance["win_rate"] - old_performance["win_rate"],
                "profit_factor_delta": new_performance["profit_factor"] - old_performance["profit_factor"],
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        if approved:
            self.parameter_changes.append(report)

        return approved, report

    def _filter_trades(self, strategy: str, regime: str) -> List[TradeResult]:
        """Filter trades by strategy and regime."""
        # This is a simplified filter; real implementation would check trade metadata
        return self.trade_history  # For now, use all trades

    def _simulate_performance(
        self,
        trades: List[TradeResult],
        parameter_name: str,
        parameter_value: float
    ) -> Dict:
        """
        Simulate performance with given parameter value.

        For demo, simply calculate metrics on test trades.
        Real implementation would re-score trades with new parameter values.
        """
        if not trades:
            return {
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "total_pnl": 0.0,
                "trades": 0,
            }

        wins = sum(1 for t in trades if t.win_rate)
        losses = sum(1 for t in trades if not t.win_rate)
        total_pnl = sum(t.profit_loss for t in trades)

        win_rate = (wins / len(trades)) * 100 if trades else 0
        avg_win = sum(t.profit_loss for t in trades if t.win_rate) / max(wins, 1)
        avg_loss = abs(sum(t.profit_loss for t in trades if not t.win_rate)) / max(losses, 1)
        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0

        return {
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "total_pnl": total_pnl,
            "trades": len(trades),
            "wins": wins,
            "losses": losses,
        }

    def get_change_history(self) -> List[Dict]:
        """Get history of all approved parameter changes."""
        return self.parameter_changes

    def reversion_check(
        self,
        parameter_name: str,
        current_value: float,
        baseline_value: float
    ) -> Tuple[bool, str]:
        """
        Check if recent performance has degraded compared to baseline.

        If yes, recommend reverting to baseline.

        Args:
            parameter_name: Parameter to check
            current_value: Current parameter value
            baseline_value: Original/baseline value

        Returns:
            Tuple of (should_revert: bool, reason: str)
        """
        # Get recent trades (last 20)
        recent_trades = self.trade_history[-20:] if self.trade_history else []

        if len(recent_trades) < 5:
            return False, "Insufficient recent trades to assess degradation"

        # Calculate recent performance
        recent_perf = self._simulate_performance(recent_trades, parameter_name, current_value)
        baseline_perf = self._simulate_performance(recent_trades, parameter_name, baseline_value)

        if recent_perf["win_rate"] < baseline_perf["win_rate"] * 0.8:  # >20% degradation
            return True, f"Win rate degraded from {baseline_perf['win_rate']:.1f}% to {recent_perf['win_rate']:.1f}%"

        return False, "Performance stable, no reversion needed"


class ParameterAdjustmentAudit:
    """Tracks and audits all parameter adjustments."""

    def __init__(self):
        self.adjustments: List[Dict] = []

    def record_adjustment(
        self,
        parameter: str,
        old_value: float,
        new_value: float,
        approved: bool,
        validation_report: Dict,
        reason: str = "",
    ):
        """Record a parameter adjustment attempt."""
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "parameter": parameter,
            "old_value": old_value,
            "new_value": new_value,
            "approved": approved,
            "reason": reason,
            "validation_report": validation_report,
        }
        self.adjustments.append(record)

    def get_approval_rate(self) -> float:
        """Get percentage of adjustment requests that were approved."""
        if not self.adjustments:
            return 0.0
        approved = sum(1 for a in self.adjustments if a["approved"])
        return (approved / len(self.adjustments)) * 100

    def get_audit_trail(self) -> Dict:
        """Get complete audit trail."""
        return {
            "total_adjustment_requests": len(self.adjustments),
            "approved": sum(1 for a in self.adjustments if a["approved"]),
            "rejected": sum(1 for a in self.adjustments if not a["approved"]),
            "approval_rate_percent": self.get_approval_rate(),
            "adjustments": self.adjustments,
        }
