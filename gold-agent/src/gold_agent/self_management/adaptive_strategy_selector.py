"""Adaptive Strategy Selector (Tier 5) — Select best strategy based on market regime."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class StrategyAllocation:
    """Allocation of capital to different strategies."""
    strategy_name: str
    allocation_percent: float  # 0-100
    confidence: float  # 0-100
    reason: str


@dataclass
class StrategyPerformance:
    """Performance metrics for a strategy in current regime."""
    strategy_name: str
    win_rate: float  # 0-1
    profit_factor: float
    avg_pnl: float
    sharpe_ratio: float
    trade_count: int
    regime: str


class AdaptiveStrategySelector:
    """
    Tier 5: Self-Management - Adaptive Strategy Selection.

    Selects and allocates capital to strategies based on current market regime
    and their historical performance.
    """

    def __init__(self, config):
        self.config = config
        self.strategy_performance: Dict[str, Dict] = {}
        self.current_allocation: List[StrategyAllocation] = []
        self.allocation_history: List[List[StrategyAllocation]] = []
        self.max_history = 30

    def select_strategies_for_regime(
        self,
        regime: str,
        recent_trades: List[Dict],
    ) -> List[StrategyAllocation]:
        """
        Select best strategies for current market regime.

        Args:
            regime: Current market regime (trending_up, mean_reverting, etc)
            recent_trades: Recent closed trades

        Returns:
            List of StrategyAllocation with capital allocation percentages
        """
        allocations = []

        if regime in ["trending_up", "trending_down"]:
            # Trend-following works best in trending markets
            allocations.append(StrategyAllocation(
                strategy_name="trend_following",
                allocation_percent=70,
                confidence=85,
                reason="Strong trend detected; trend-following strategy optimal",
            ))
            allocations.append(StrategyAllocation(
                strategy_name="breakout",
                allocation_percent=30,
                confidence=70,
                reason="Trend continuation possible; breakout catches momentum",
            ))

        elif regime == "mean_reverting":
            # Mean reversion works best when price oscillates
            allocations.append(StrategyAllocation(
                strategy_name="mean_reversion",
                allocation_percent=80,
                confidence=90,
                reason="Price oscillating around MA; mean reversion strategy optimal",
            ))
            allocations.append(StrategyAllocation(
                strategy_name="range_trading",
                allocation_percent=20,
                confidence=65,
                reason="Support/resistance levels forming",
            ))

        elif regime == "range_bound":
            # Range trading in consolidating markets
            allocations.append(StrategyAllocation(
                strategy_name="range_trading",
                allocation_percent=75,
                confidence=85,
                reason="Price in established range; range trading optimal",
            ))
            allocations.append(StrategyAllocation(
                strategy_name="mean_reversion",
                allocation_percent=25,
                confidence=60,
                reason="Price reversions within range",
            ))

        elif regime == "volatile":
            # Breakout in volatile, directionless markets
            allocations.append(StrategyAllocation(
                strategy_name="breakout",
                allocation_percent=85,
                confidence=80,
                reason="High volatility; breakout captures directional moves",
            ))
            allocations.append(StrategyAllocation(
                strategy_name="range_trading",
                allocation_percent=15,
                confidence=50,
                reason="Volatile swings create range opportunities",
            ))

        else:  # consolidating or unknown
            # Defensive allocation in consolidation
            allocations.append(StrategyAllocation(
                strategy_name="neutral",
                allocation_percent=100,
                confidence=50,
                reason="Consolidating; wait for regime clarity",
            ))

        # Store allocation
        self.current_allocation = allocations
        self.allocation_history.append(allocations)
        if len(self.allocation_history) > self.max_history:
            self.allocation_history.pop(0)

        return allocations

    def analyze_strategy_performance(
        self,
        strategy_name: str,
        trades: List[Dict],
        regime: str,
    ) -> StrategyPerformance:
        """
        Analyze performance of a strategy in a specific regime.

        Args:
            strategy_name: Name of the strategy
            trades: Trades tagged with this strategy
            regime: Regime when trades were made

        Returns:
            StrategyPerformance with metrics
        """
        if not trades:
            return StrategyPerformance(
                strategy_name=strategy_name,
                win_rate=0.0,
                profit_factor=0.0,
                avg_pnl=0.0,
                sharpe_ratio=0.0,
                trade_count=0,
                regime=regime,
            )

        winning_trades = [t for t in trades if t.get("final_p_l", 0) > 0]
        losing_trades = [t for t in trades if t.get("final_p_l", 0) < 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0

        # Calculate profit factor
        gross_profit = sum(t.get("final_p_l", 0) for t in winning_trades)
        gross_loss = abs(sum(t.get("final_p_l", 0) for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit / 1

        # Calculate average P&L
        avg_pnl = sum(t.get("final_p_l", 0) for t in trades) / len(trades)

        # Calculate Sharpe ratio (simplified)
        pnls = [t.get("final_p_l", 0) for t in trades]
        if len(pnls) > 1:
            import statistics
            mean_pnl = statistics.mean(pnls)
            stdev = statistics.stdev(pnls) if len(pnls) > 1 else 1.0
            sharpe_ratio = (mean_pnl / stdev) if stdev > 0 else 0.0
        else:
            sharpe_ratio = 0.0

        return StrategyPerformance(
            strategy_name=strategy_name,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_pnl=avg_pnl,
            sharpe_ratio=sharpe_ratio,
            trade_count=len(trades),
            regime=regime,
        )

    def get_status(self) -> dict:
        """Get strategy selector status."""
        return {
            "current_allocation": [
                {
                    "strategy": a.strategy_name,
                    "allocation": f"{a.allocation_percent:.1f}%",
                    "confidence": f"{a.confidence:.1f}%",
                }
                for a in self.current_allocation
            ],
            "allocation_history_length": len(self.allocation_history),
        }
