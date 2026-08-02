"""Parameter Optimizer (Tier 5) — Find optimal parameter values through exploration."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple


@dataclass
class ParameterVariation:
    """A variation of a parameter to test."""
    parameter_name: str
    test_value: float
    performance_metric: float  # win_rate, sharpe, etc.
    trade_count: int
    recommendation: str


@dataclass
class OptimizationResult:
    """Result of parameter optimization."""
    parameter_name: str
    current_value: float
    optimal_value: float
    improvement_percent: float
    confidence: float  # 0-100
    variations_tested: int
    recommendation: str


class ParameterOptimizer:
    """
    Tier 5: Self-Management - Parameter Optimization.

    Tests variations of parameters to find optimal values.
    """

    def __init__(self, config):
        self.config = config
        self.optimization_history: List[OptimizationResult] = []
        self.variation_history: List[ParameterVariation] = []
        self.max_history = 50

        # Parameters that can be optimized
        self.tunable_parameters = {
            "confidence_threshold_wait": {
                "min": 30,
                "max": 80,
                "step": 5,
                "metric": "sharpe_ratio",
            },
            "max_position_size_percent": {
                "min": 0.5,
                "max": 5.0,
                "step": 0.5,
                "metric": "profit_factor",
            },
            "daily_loss_limit_percent": {
                "min": 1.0,
                "max": 5.0,
                "step": 0.5,
                "metric": "win_rate",
            },
        }

    def generate_parameter_variations(
        self,
        parameter_name: str,
        current_value: float,
    ) -> List[float]:
        """
        Generate parameter values to test.

        Args:
            parameter_name: Parameter to optimize
            current_value: Current value

        Returns:
            List of values to test around current
        """
        if parameter_name not in self.tunable_parameters:
            return []

        config = self.tunable_parameters[parameter_name]
        step = config["step"]

        # Generate values: current - 2*step, current - step, current, current + step, current + 2*step
        variations = []
        for offset in [-2, -1, 0, 1, 2]:
            value = current_value + (offset * step)
            value = max(config["min"], min(config["max"], value))
            if value not in variations:
                variations.append(value)

        return sorted(set(variations))

    def evaluate_parameter_value(
        self,
        parameter_name: str,
        test_value: float,
        trades: List[Dict],
    ) -> float:
        """
        Evaluate performance with a specific parameter value.

        Args:
            parameter_name: Parameter name
            test_value: Value to test
            trades: Trades to evaluate on

        Returns:
            Performance score (depends on metric for this parameter)
        """
        if not trades or len(trades) < 5:
            return 0.0

        metric_name = self.tunable_parameters.get(parameter_name, {}).get("metric", "sharpe_ratio")

        if metric_name == "win_rate":
            return sum(1 for t in trades if t.get("final_p_l", 0) > 0) / len(trades)

        elif metric_name == "sharpe_ratio":
            import statistics
            pnls = [t.get("final_p_l", 0) for t in trades]
            mean_pnl = statistics.mean(pnls)
            stdev = statistics.stdev(pnls) if len(pnls) > 1 else 1.0
            return mean_pnl / stdev if stdev > 0 else 0.0

        elif metric_name == "profit_factor":
            winning = sum(t.get("final_p_l", 0) for t in trades if t.get("final_p_l", 0) > 0)
            losing = abs(sum(t.get("final_p_l", 0) for t in trades if t.get("final_p_l", 0) < 0))
            return winning / losing if losing > 0 else winning

        else:  # avg_pnl
            return sum(t.get("final_p_l", 0) for t in trades) / len(trades)

    def optimize_parameter(
        self,
        parameter_name: str,
        historical_trades: List[Dict],
    ) -> OptimizationResult:
        """
        Find optimal value for a parameter.

        Args:
            parameter_name: Parameter to optimize
            historical_trades: Historical trades to optimize on

        Returns:
            OptimizationResult with recommended value
        """
        if parameter_name not in self.tunable_parameters:
            return OptimizationResult(
                parameter_name=parameter_name,
                current_value=0.0,
                optimal_value=0.0,
                improvement_percent=0.0,
                confidence=0.0,
                variations_tested=0,
                recommendation="Parameter not supported for optimization",
            )

        if len(historical_trades) < 20:
            return OptimizationResult(
                parameter_name=parameter_name,
                current_value=0.0,
                optimal_value=0.0,
                improvement_percent=0.0,
                confidence=0.0,
                variations_tested=0,
                recommendation="Insufficient trade history (need 20+ trades)",
            )

        # Get current value
        if parameter_name == "confidence_threshold_wait":
            current_value = self.config.scoring.confidence_threshold_wait
        elif parameter_name == "max_position_size_percent":
            current_value = self.config.execution.capital.max_position_size_percent
        elif parameter_name == "daily_loss_limit_percent":
            current_value = self.config.execution.capital.daily_loss_limit_percent
        else:
            current_value = 0.0

        # Test variations
        variations = self.generate_parameter_variations(parameter_name, current_value)
        results = {}

        for test_value in variations:
            score = self.evaluate_parameter_value(parameter_name, test_value, historical_trades)
            results[test_value] = score

            self.variation_history.append(ParameterVariation(
                parameter_name=parameter_name,
                test_value=test_value,
                performance_metric=score,
                trade_count=len(historical_trades),
                recommendation="" if score == max(results.values()) else "Not optimal",
            ))

        # Find best value
        optimal_value = max(results.keys(), key=lambda k: results[k])
        optimal_score = results[optimal_value]
        current_score = results.get(current_value, 0.0)

        improvement_percent = ((optimal_score - current_score) / abs(current_score) * 100) if current_score != 0 else 0

        # Confidence based on improvement magnitude
        if improvement_percent > 20:
            confidence = 85.0
        elif improvement_percent > 10:
            confidence = 70.0
        elif improvement_percent > 5:
            confidence = 55.0
        else:
            confidence = 40.0

        result = OptimizationResult(
            parameter_name=parameter_name,
            current_value=current_value,
            optimal_value=optimal_value,
            improvement_percent=improvement_percent,
            confidence=confidence,
            variations_tested=len(variations),
            recommendation=f"Change {parameter_name} from {current_value} to {optimal_value}" if improvement_percent > 5 else "Current value is near optimal",
        )

        self.optimization_history.append(result)
        if len(self.optimization_history) > self.max_history:
            self.optimization_history.pop(0)

        return result

    def get_optimization_history(self) -> List[OptimizationResult]:
        """Get optimization history."""
        return self.optimization_history

    def get_status(self) -> dict:
        """Get optimizer status."""
        return {
            "total_optimizations": len(self.optimization_history),
            "tunable_parameters": list(self.tunable_parameters.keys()),
            "variations_tested": len(self.variation_history),
        }
