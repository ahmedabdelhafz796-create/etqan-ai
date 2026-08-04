"""Trade Analyzer (Tier 2) — Analyze historical trades and identify patterns."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TradeStatistics:
    """Statistics from a set of trades."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float  # 0-100%
    average_win: float
    average_loss: float
    profit_factor: float  # avg_win / avg_loss
    total_pnl: float
    largest_win: float
    largest_loss: float
    average_duration_minutes: float
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    max_drawdown: float = 0.0
    recovery_factor: float = 0.0  # Total P&L / Max Drawdown


@dataclass
class SignalPerformance:
    """Performance of a particular signal/indicator combination."""
    signal_type: str  # e.g., "RSI", "MACD", "MA_Cross"
    total_signals: int
    profitable_signals: int
    unprofitable_signals: int
    win_rate: float  # 0-100%
    average_pnl: float
    average_pnl_percent: float
    best_performance: float
    worst_performance: float
    consistency: float  # std dev of returns


class TradeAnalyzer:
    """Analyzes trade outcomes and identifies patterns."""

    def __init__(self, config):
        self.config = config

    def analyze_trades(self, trades: List[Dict]) -> TradeStatistics:
        """
        Analyze a list of closed trades.

        Args:
            trades: List of closed trade dictionaries with pnl fields

        Returns:
            TradeStatistics object
        """
        if not trades:
            return TradeStatistics(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                average_win=0.0,
                average_loss=0.0,
                profit_factor=0.0,
                total_pnl=0.0,
                largest_win=0.0,
                largest_loss=0.0,
                average_duration_minutes=0.0,
            )

        pnls = [trade.get("final_p_l", 0.0) for trade in trades]
        durations = [trade.get("duration_minutes", 0.0) for trade in trades]

        winning_pnls = [pnl for pnl in pnls if pnl > 0]
        losing_pnls = [pnl for pnl in pnls if pnl < 0]

        total_pnl = sum(pnls)
        win_rate = (len(winning_pnls) / len(pnls) * 100) if pnls else 0.0
        avg_win = sum(winning_pnls) / len(winning_pnls) if winning_pnls else 0.0
        avg_loss = abs(sum(losing_pnls) / len(losing_pnls)) if losing_pnls else 0.0
        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0.0
        largest_win = max(winning_pnls) if winning_pnls else 0.0
        largest_loss = abs(min(losing_pnls)) if losing_pnls else 0.0
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        # Calculate Sharpe ratio (assuming ~252 trading days per year)
        returns = [pnl / 100000 for pnl in pnls]  # Normalize to percentages
        sharpe = self._calculate_sharpe_ratio(returns)

        # Calculate max drawdown
        max_dd, _ = self._calculate_max_drawdown(pnls)

        recovery_factor = total_pnl / abs(max_dd) if max_dd < 0 else 0.0

        return TradeStatistics(
            total_trades=len(pnls),
            winning_trades=len(winning_pnls),
            losing_trades=len(losing_pnls),
            win_rate=win_rate,
            average_win=avg_win,
            average_loss=avg_loss,
            profit_factor=profit_factor,
            total_pnl=total_pnl,
            largest_win=largest_win,
            largest_loss=largest_loss,
            average_duration_minutes=avg_duration,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            recovery_factor=recovery_factor,
        )

    def analyze_by_signal_type(
        self,
        trades: List[Dict],
        signal_field: str = "entry_signal",
    ) -> Dict[str, SignalPerformance]:
        """
        Analyze trade performance by signal type.

        Args:
            trades: List of closed trades
            signal_field: Field name containing signal type

        Returns:
            Dict mapping signal type to performance
        """
        performance = {}

        # Group trades by signal type
        trades_by_signal = {}
        for trade in trades:
            signal = trade.get(signal_field, "unknown")
            if signal not in trades_by_signal:
                trades_by_signal[signal] = []
            trades_by_signal[signal].append(trade)

        # Analyze each signal type
        for signal_type, signal_trades in trades_by_signal.items():
            pnls = [t.get("final_p_l", 0.0) for t in signal_trades]
            pnl_pcts = [t.get("final_p_l_percent", 0.0) for t in signal_trades]

            profitable = sum(1 for pnl in pnls if pnl > 0)
            unprofitable = sum(1 for pnl in pnls if pnl < 0)
            win_rate = (profitable / len(pnls) * 100) if pnls else 0.0

            avg_pnl = sum(pnls) / len(pnls) if pnls else 0.0
            avg_pnl_pct = sum(pnl_pcts) / len(pnl_pcts) if pnl_pcts else 0.0

            best_pnl = max(pnls) if pnls else 0.0
            worst_pnl = min(pnls) if pnls else 0.0

            consistency = self._calculate_std_dev(pnls)

            performance[signal_type] = SignalPerformance(
                signal_type=signal_type,
                total_signals=len(pnls),
                profitable_signals=profitable,
                unprofitable_signals=unprofitable,
                win_rate=win_rate,
                average_pnl=avg_pnl,
                average_pnl_percent=avg_pnl_pct,
                best_performance=best_pnl,
                worst_performance=worst_pnl,
                consistency=consistency,
            )

        return performance

    def identify_best_trades(
        self,
        trades: List[Dict],
        top_n: int = 10,
    ) -> List[Dict]:
        """Get the best performing trades."""
        sorted_trades = sorted(
            trades,
            key=lambda t: t.get("final_p_l", 0.0),
            reverse=True
        )
        return sorted_trades[:top_n]

    def identify_worst_trades(
        self,
        trades: List[Dict],
        top_n: int = 10,
    ) -> List[Dict]:
        """Get the worst performing trades."""
        sorted_trades = sorted(
            trades,
            key=lambda t: t.get("final_p_l", 0.0),
        )
        return sorted_trades[:top_n]

    def analyze_time_performance(
        self,
        trades: List[Dict],
        time_unit: str = "hour",  # "hour", "day", "weekday", "month"
    ) -> Dict[str, TradeStatistics]:
        """
        Analyze performance by time period.

        Returns:
            Dict mapping time period to statistics
        """
        trades_by_time = {}

        for trade in trades:
            entry_time = trade.get("entry_timestamp")
            if not entry_time:
                continue

            # Parse time if string
            if isinstance(entry_time, str):
                entry_time = datetime.fromisoformat(entry_time)

            # Extract time unit
            if time_unit == "hour":
                key = entry_time.strftime("%H")
            elif time_unit == "weekday":
                key = entry_time.strftime("%A")
            elif time_unit == "month":
                key = entry_time.strftime("%m")
            elif time_unit == "day":
                key = entry_time.strftime("%Y-%m-%d")
            else:
                key = "unknown"

            if key not in trades_by_time:
                trades_by_time[key] = []
            trades_by_time[key].append(trade)

        # Analyze each time period
        results = {}
        for time_period, period_trades in trades_by_time.items():
            results[time_period] = self.analyze_trades(period_trades)

        return results

    def find_correlation_with_confidence(
        self,
        trades: List[Dict],
    ) -> float:
        """
        Find correlation between decision confidence and actual profitability.

        Higher correlation means confidence is predictive of actual outcomes.
        """
        if len(trades) < 2:
            return 0.0

        confidences = []
        pnls = []

        for trade in trades:
            confidence = trade.get("confidence")
            pnl = trade.get("final_p_l", 0.0)

            if confidence is not None:
                confidences.append(confidence)
                pnls.append(pnl)

        if len(confidences) < 2:
            return 0.0

        return self._calculate_correlation(confidences, pnls)

    def identify_improvement_areas(self, trades: List[Dict]) -> Dict[str, str]:
        """
        Identify specific areas for improvement based on trade analysis.

        Returns:
            Dict of area -> recommendation
        """
        if len(trades) < 5:
            return {"data": "Insufficient trades for analysis (need >= 5)"}

        stats = self.analyze_trades(trades)
        recommendations = {}

        # Win rate analysis
        if stats.win_rate < 50:
            recommendations["win_rate"] = f"Low win rate ({stats.win_rate:.1f}%). Consider tighter entry/exit rules."

        # Profit factor analysis
        if stats.profit_factor < 1.5:
            recommendations["profit_factor"] = f"Low profit factor ({stats.profit_factor:.2f}). Increase winning trade size or decrease losses."

        # Loss analysis
        if stats.average_loss > stats.average_win * 0.8:
            recommendations["risk_reward"] = "Poor risk/reward ratio. Tighten stop losses or set higher take profits."

        # Duration analysis
        if stats.average_duration_minutes < 30:
            recommendations["holding_time"] = "Very short average holding time. Trades may be overfit to noise. Use wider stops."

        # Max drawdown
        if stats.max_drawdown < -10000:
            recommendations["drawdown"] = "Large maximum drawdown. Implement position sizing or reduce trade frequency."

        # Consistency
        if stats.sharpe_ratio and stats.sharpe_ratio < 1.0:
            recommendations["consistency"] = "Low Sharpe ratio. Trade returns are inconsistent. Need more reliable signal generation."

        return recommendations

    @staticmethod
    def _calculate_sharpe_ratio(returns: List[float]) -> Optional[float]:
        """Calculate Sharpe ratio from returns."""
        if len(returns) < 2:
            return None

        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return None

        # Assuming ~252 trading days per year
        annualized_sharpe = (mean / std_dev) * (252 ** 0.5)
        return annualized_sharpe

    @staticmethod
    def _calculate_sortino_ratio(returns: List[float]) -> Optional[float]:
        """Calculate Sortino ratio (downside risk only)."""
        if len(returns) < 2:
            return None

        mean = sum(returns) / len(returns)
        downside_returns = [r for r in returns if r < mean]

        if not downside_returns:
            return None

        downside_variance = sum((r - mean) ** 2 for r in downside_returns) / len(returns)
        downside_std_dev = downside_variance ** 0.5

        if downside_std_dev == 0:
            return None

        sortino = (mean / downside_std_dev) * (252 ** 0.5)
        return sortino

    @staticmethod
    def _calculate_max_drawdown(pnls: List[float]) -> Tuple[float, int]:
        """Calculate maximum drawdown and when it occurred."""
        if not pnls:
            return 0.0, 0

        cumulative = 0
        peak = 0
        max_dd = 0
        dd_idx = 0

        for i, pnl in enumerate(pnls):
            cumulative += pnl
            if cumulative > peak:
                peak = cumulative
            dd = cumulative - peak
            if dd < max_dd:
                max_dd = dd
                dd_idx = i

        return max_dd, dd_idx

    @staticmethod
    def _calculate_std_dev(values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return variance ** 0.5

    @staticmethod
    def _calculate_correlation(x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) < 2 or len(y) < 2 or len(x) != len(y):
            return 0.0

        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
        denominator_x = (sum((xi - mean_x) ** 2 for xi in x)) ** 0.5
        denominator_y = (sum((yi - mean_y) ** 2 for yi in y)) ** 0.5

        if denominator_x == 0 or denominator_y == 0:
            return 0.0

        correlation = numerator / (denominator_x * denominator_y)
        return max(-1.0, min(1.0, correlation))
