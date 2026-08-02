"""Backtester (Tier 3) — Replay historical data through complete pipeline."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import asyncio

from src.gold_agent.core.models import Decision, MarketData, IndicatorValues, Score, ActionType, PositionSide
from src.gold_agent.execution.position_manager import PositionManager
from src.gold_agent.execution.capital_manager import CapitalManager
from src.gold_agent.execution.trade_lifecycle_manager import TradeLifecycleManager
from src.gold_agent.learning.trade_analyzer import TradeAnalyzer, TradeStatistics


@dataclass
class BacktestMetrics:
    """Results from a backtest run."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: Optional[float]
    sortino_ratio: Optional[float]
    best_trade: float
    worst_trade: float
    avg_trade_duration_minutes: float
    trading_days: int
    total_return_percent: float
    monthly_return_percent: float
    annual_return_percent: float
    recovery_factor: float


class BacktestResult:
    """Complete backtest result with metrics and trade log."""

    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
        trades: List[Dict],
        metrics: BacktestMetrics,
        equity_curve: List[Tuple[datetime, float]],
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.trades = trades
        self.metrics = metrics
        self.equity_curve = equity_curve

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "total_trades": self.metrics.total_trades,
            "winning_trades": self.metrics.winning_trades,
            "losing_trades": self.metrics.losing_trades,
            "win_rate": self.metrics.win_rate,
            "profit_factor": self.metrics.profit_factor,
            "total_pnl": self.metrics.total_pnl,
            "max_drawdown": self.metrics.max_drawdown,
            "sharpe_ratio": self.metrics.sharpe_ratio,
            "total_return_percent": self.metrics.total_return_percent,
            "recovery_factor": self.metrics.recovery_factor,
        }


class Backtester:
    """
    Tier 3: Validation & Testing.

    Replays historical market data through the complete pipeline to validate strategy.
    """

    def __init__(self, config, pipeline):
        self.config = config
        self.pipeline = pipeline
        self.analyzer = TradeAnalyzer(config)

    async def backtest(
        self,
        market_data_list: List[MarketData],
        initial_capital: float = 100000.0,
        slippage_percent: float = 0.1,
        commission_percent: float = 0.05,
    ) -> BacktestResult:
        """
        Run a complete backtest on historical data.

        Args:
            market_data_list: Historical market data points (chronological order)
            initial_capital: Starting capital in USD
            slippage_percent: Slippage as % of price
            commission_percent: Commission as % of trade value

        Returns:
            BacktestResult with full metrics and trade log
        """
        print(f"Starting backtest: {len(market_data_list)} candles")

        position_manager = PositionManager(self.config)
        capital_manager = CapitalManager(self.config, initial_capital)
        trade_lifecycle = TradeLifecycleManager(position_manager, capital_manager, self.config)

        trades = []
        equity_curve = [(market_data_list[0].timestamp, initial_capital)]
        current_capital = initial_capital

        for i, market_data in enumerate(market_data_list):
            # Run pipeline on this candle
            decision = await self.pipeline.run_once_simulation(market_data)

            if not decision or decision.action == ActionType.WAIT:
                # Update position prices if holding
                for position in position_manager.get_open_positions():
                    position_manager.update_position_price(position.symbol, market_data.xau_usd)

                    # Check stop loss / take profit
                    for trade_id in position.trade_ids:
                        trade = trade_lifecycle.get_trade(trade_id)
                        if trade and trade.state == "open":
                            # Update trade price
                            await trade_lifecycle.update_trade_price(trade_id, market_data.xau_usd)

                            # Check exit conditions
                            if await trade_lifecycle.check_stop_loss(trade_id, market_data.xau_usd):
                                closed = await trade_lifecycle.close_trade(
                                    trade_id, market_data.xau_usd, "stop_loss"
                                )
                                if closed:
                                    trades.append({
                                        "trade_id": closed.trade_id,
                                        "entry_price": closed.entry_price,
                                        "exit_price": closed.exit_price,
                                        "quantity": closed.quantity,
                                        "final_p_l": closed.final_p_l,
                                        "final_p_l_percent": closed.final_p_l_percent,
                                        "exit_reason": "stop_loss",
                                    })

                            elif await trade_lifecycle.check_take_profit(trade_id, market_data.xau_usd):
                                closed = await trade_lifecycle.close_trade(
                                    trade_id, market_data.xau_usd, "take_profit"
                                )
                                if closed:
                                    trades.append({
                                        "trade_id": closed.trade_id,
                                        "entry_price": closed.entry_price,
                                        "exit_price": closed.exit_price,
                                        "quantity": closed.quantity,
                                        "final_p_l": closed.final_p_l,
                                        "final_p_l_percent": closed.final_p_l_percent,
                                        "exit_reason": "take_profit",
                                    })

                # Record equity
                current_capital = capital_manager.current_capital
                equity_curve.append((market_data.timestamp, current_capital))
                continue

            # Execute trade
            position_value = market_data.xau_usd * self.config.execution.default_position_size
            can_trade, reason = capital_manager.can_place_trade(position_value)

            if not can_trade:
                print(f"Backtest {i}: {reason}")
                continue

            # Create trade
            trade = await trade_lifecycle.open_trade(
                decision_action=decision.action,
                entry_price=market_data.xau_usd * (1 + slippage_percent / 100) if decision.action == ActionType.BUY else market_data.xau_usd * (1 - slippage_percent / 100),
                quantity=self.config.execution.default_position_size,
                entry_order_id=f"BACKTEST-{i}",
                decision_id=i,
                stop_loss=market_data.xau_usd * 0.98 if decision.action == ActionType.BUY else market_data.xau_usd * 1.02,
                take_profit=market_data.xau_usd * 1.02 if decision.action == ActionType.BUY else market_data.xau_usd * 0.98,
            )

            # Deduct commission
            commission = (trade.entry_price * trade.quantity) * (commission_percent / 100)
            capital_manager.set_current_capital(capital_manager.current_capital - commission)

            # Record equity
            equity_curve.append((market_data.timestamp, capital_manager.current_capital))

        # Close any remaining open trades at last price
        last_price = market_data_list[-1].xau_usd
        for trade in trade_lifecycle.get_open_trades():
            closed = await trade_lifecycle.close_trade(trade.trade_id, last_price, "end_of_backtest")
            if closed:
                trades.append({
                    "trade_id": closed.trade_id,
                    "entry_price": closed.entry_price,
                    "exit_price": closed.exit_price,
                    "quantity": closed.quantity,
                    "final_p_l": closed.final_p_l,
                    "final_p_l_percent": closed.final_p_l_percent,
                    "exit_reason": "end_of_backtest",
                })

        # Calculate metrics
        stats = self.analyzer.analyze_trades(trades)
        total_return_percent = ((capital_manager.current_capital - initial_capital) / initial_capital) * 100
        monthly_return = total_return_percent / ((market_data_list[-1].timestamp - market_data_list[0].timestamp).days / 30)
        annual_return = total_return_percent / ((market_data_list[-1].timestamp - market_data_list[0].timestamp).days / 365)

        metrics = BacktestMetrics(
            total_trades=stats.total_trades,
            winning_trades=stats.winning_trades,
            losing_trades=stats.losing_trades,
            win_rate=stats.win_rate,
            profit_factor=stats.profit_factor,
            total_pnl=stats.total_pnl,
            max_drawdown=stats.max_drawdown,
            sharpe_ratio=stats.sharpe_ratio,
            sortino_ratio=None,  # TODO: Implement
            best_trade=stats.largest_win,
            worst_trade=stats.largest_loss,
            avg_trade_duration_minutes=stats.average_duration_minutes,
            trading_days=(market_data_list[-1].timestamp - market_data_list[0].timestamp).days,
            total_return_percent=total_return_percent,
            monthly_return_percent=monthly_return,
            annual_return_percent=annual_return,
            recovery_factor=stats.recovery_factor,
        )

        result = BacktestResult(
            start_date=market_data_list[0].timestamp,
            end_date=market_data_list[-1].timestamp,
            trades=trades,
            metrics=metrics,
            equity_curve=equity_curve,
        )

        print(f"Backtest complete: {metrics.total_trades} trades, "
              f"Win Rate: {metrics.win_rate:.1f}%, "
              f"P&L: ${metrics.total_pnl:,.2f}, "
              f"Return: {metrics.total_return_percent:.2f}%")

        return result

    def print_backtest_report(self, result: BacktestResult) -> None:
        """Print a detailed backtest report."""
        print("\n" + "="*80)
        print("BACKTEST REPORT")
        print("="*80)
        print(f"Period: {result.start_date.date()} to {result.end_date.date()}")
        print(f"Trading Days: {result.metrics.trading_days}")
        print()
        print("TRADE STATISTICS")
        print("-"*80)
        print(f"Total Trades:        {result.metrics.total_trades}")
        print(f"Winning Trades:      {result.metrics.winning_trades}")
        print(f"Losing Trades:       {result.metrics.losing_trades}")
        print(f"Win Rate:            {result.metrics.win_rate:.2f}%")
        print(f"Profit Factor:       {result.metrics.profit_factor:.2f}")
        print()
        print("PROFITABILITY")
        print("-"*80)
        print(f"Total P&L:           ${result.metrics.total_pnl:,.2f}")
        print(f"Best Trade:          ${result.metrics.best_trade:,.2f}")
        print(f"Worst Trade:         ${result.metrics.worst_trade:,.2f}")
        print(f"Avg Trade Duration:  {result.metrics.avg_trade_duration_minutes:.1f} minutes")
        print()
        print("RETURNS")
        print("-"*80)
        print(f"Total Return:        {result.metrics.total_return_percent:+.2f}%")
        print(f"Monthly Return:      {result.metrics.monthly_return_percent:+.2f}%")
        print(f"Annual Return:       {result.metrics.annual_return_percent:+.2f}%")
        print()
        print("RISK METRICS")
        print("-"*80)
        print(f"Max Drawdown:        {result.metrics.max_drawdown:,.2f}")
        print(f"Recovery Factor:     {result.metrics.recovery_factor:.2f}")
        if result.metrics.sharpe_ratio:
            print(f"Sharpe Ratio:        {result.metrics.sharpe_ratio:.2f}")
        print("="*80)
