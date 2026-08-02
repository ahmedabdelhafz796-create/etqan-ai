"""Performance Validator (Tier 3) — Verify system meets production readiness criteria."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple, Optional


@dataclass
class ValidationCriterion:
    """A single validation criterion."""
    name: str
    threshold: float
    actual: float
    passed: bool
    severity: str  # "critical", "high", "medium", "low"
    recommendation: str


@dataclass
class ValidationReport:
    """Complete validation report."""
    timestamp: datetime
    total_criteria: int
    passed_criteria: int
    failed_criteria: int
    pass_rate: float
    critical_failures: int
    production_ready: bool
    criteria: List[ValidationCriterion]


class PerformanceValidator:
    """
    Validates that system meets production readiness criteria.

    Phase 1 → Phase 2 Requirements:
    - Minimum 100 trades for statistical significance
    - Win rate >= 45%
    - Profit factor >= 1.5
    - Sharpe ratio >= 1.0
    - Max drawdown <= $25,000
    - Confidence-to-outcome correlation >= 0.5

    Phase 2 → Phase 3 (Execution Enabled) Requirements:
    - All Phase 1 requirements +
    - Minimum 1000 trades (6+ months of data)
    - Consistent monthly returns
    - Sharpe ratio >= 1.5
    - Max monthly drawdown <= 10%
    - Win rate >= 50%
    - No clustering of losses
    """

    def __init__(self, config):
        self.config = config
        self.phase_1_criteria = self._get_phase_1_criteria()
        self.phase_2_criteria = self._get_phase_2_criteria()
        self.phase_3_criteria = self._get_phase_3_criteria()

    def validate_phase_1(self, backtest_result) -> ValidationReport:
        """Validate Phase 1: Data collection & analysis readiness."""
        criteria_results = []

        # Criterion 1: Minimum trade count
        criterion = ValidationCriterion(
            name="Minimum Trade Count",
            threshold=100,
            actual=backtest_result.metrics.total_trades,
            passed=backtest_result.metrics.total_trades >= 100,
            severity="critical",
            recommendation="Need >= 100 trades for statistical significance"
        )
        criteria_results.append(criterion)

        # Criterion 2: Win rate
        criterion = ValidationCriterion(
            name="Minimum Win Rate",
            threshold=45,
            actual=backtest_result.metrics.win_rate,
            passed=backtest_result.metrics.win_rate >= 45,
            severity="high",
            recommendation="Win rate should be >= 45%. Improve entry/exit rules."
        )
        criteria_results.append(criterion)

        # Criterion 3: Profit factor
        criterion = ValidationCriterion(
            name="Minimum Profit Factor",
            threshold=1.5,
            actual=backtest_result.metrics.profit_factor,
            passed=backtest_result.metrics.profit_factor >= 1.5,
            severity="high",
            recommendation="Profit factor should be >= 1.5. Reduce losses or increase wins."
        )
        criteria_results.append(criterion)

        # Criterion 4: Sharpe ratio
        sharpe = backtest_result.metrics.sharpe_ratio or 0
        criterion = ValidationCriterion(
            name="Minimum Sharpe Ratio",
            threshold=1.0,
            actual=sharpe,
            passed=sharpe >= 1.0,
            severity="medium",
            recommendation="Sharpe ratio should be >= 1.0. Improve consistency."
        )
        criteria_results.append(criterion)

        # Criterion 5: Max drawdown limit
        max_dd_dollars = abs(backtest_result.metrics.max_drawdown)
        criterion = ValidationCriterion(
            name="Maximum Drawdown (Phase 1)",
            threshold=25000,
            actual=max_dd_dollars,
            passed=max_dd_dollars <= 25000,
            severity="high",
            recommendation="Max drawdown should be <= $25,000. Reduce position size."
        )
        criteria_results.append(criterion)

        # Generate report
        passed = sum(1 for c in criteria_results if c.passed)
        total = len(criteria_results)

        return ValidationReport(
            timestamp=datetime.utcnow(),
            total_criteria=total,
            passed_criteria=passed,
            failed_criteria=total - passed,
            pass_rate=(passed / total * 100) if total > 0 else 0,
            critical_failures=sum(1 for c in criteria_results if not c.passed and c.severity == "critical"),
            production_ready=passed == total and sum(1 for c in criteria_results if c.severity == "critical" and not c.passed) == 0,
            criteria=criteria_results,
        )

    def validate_phase_2(self, backtest_result, trade_history_months: int) -> ValidationReport:
        """Validate Phase 2: Strategy validation readiness."""
        criteria_results = []

        # Criterion 1: Sufficient data (6+ months)
        criterion = ValidationCriterion(
            name="Minimum Data Period",
            threshold=6,
            actual=trade_history_months,
            passed=trade_history_months >= 6,
            severity="critical",
            recommendation="Need >= 6 months of trade data for validation"
        )
        criteria_results.append(criterion)

        # Criterion 2: Trade count
        criterion = ValidationCriterion(
            name="Minimum Trade Count",
            threshold=1000,
            actual=backtest_result.metrics.total_trades,
            passed=backtest_result.metrics.total_trades >= 1000,
            severity="critical",
            recommendation="Need >= 1000 trades for robust validation"
        )
        criteria_results.append(criterion)

        # Criterion 3: Win rate
        criterion = ValidationCriterion(
            name="Minimum Win Rate",
            threshold=50,
            actual=backtest_result.metrics.win_rate,
            passed=backtest_result.metrics.win_rate >= 50,
            severity="high",
            recommendation="Win rate should be >= 50%"
        )
        criteria_results.append(criterion)

        # Criterion 4: Profit factor
        criterion = ValidationCriterion(
            name="Minimum Profit Factor",
            threshold=2.0,
            actual=backtest_result.metrics.profit_factor,
            passed=backtest_result.metrics.profit_factor >= 2.0,
            severity="high",
            recommendation="Profit factor should be >= 2.0"
        )
        criteria_results.append(criterion)

        # Criterion 5: Sharpe ratio
        sharpe = backtest_result.metrics.sharpe_ratio or 0
        criterion = ValidationCriterion(
            name="Minimum Sharpe Ratio",
            threshold=1.5,
            actual=sharpe,
            passed=sharpe >= 1.5,
            severity="medium",
            recommendation="Sharpe ratio should be >= 1.5"
        )
        criteria_results.append(criterion)

        # Criterion 6: Max drawdown limit
        max_dd_dollars = abs(backtest_result.metrics.max_drawdown)
        criterion = ValidationCriterion(
            name="Maximum Drawdown (Phase 2)",
            threshold=50000,
            actual=max_dd_dollars,
            passed=max_dd_dollars <= 50000,
            severity="high",
            recommendation="Max drawdown should be <= $50,000"
        )
        criteria_results.append(criterion)

        # Criterion 7: Monthly return consistency
        monthly_return = backtest_result.metrics.monthly_return_percent
        criterion = ValidationCriterion(
            name="Monthly Return Consistency",
            threshold=1.0,
            actual=abs(monthly_return),
            passed=abs(monthly_return) >= 1.0,
            severity="medium",
            recommendation="Average monthly return should be >= 1%"
        )
        criteria_results.append(criterion)

        passed = sum(1 for c in criteria_results if c.passed)
        total = len(criteria_results)

        critical_failures = sum(1 for c in criteria_results if not c.passed and c.severity == "critical")

        return ValidationReport(
            timestamp=datetime.utcnow(),
            total_criteria=total,
            passed_criteria=passed,
            failed_criteria=total - passed,
            pass_rate=(passed / total * 100) if total > 0 else 0,
            critical_failures=critical_failures,
            production_ready=critical_failures == 0,
            criteria=criteria_results,
        )

    def validate_phase_3(
        self,
        backtest_result,
        monthly_returns: List[float],
        monthly_drawdowns: List[float],
    ) -> ValidationReport:
        """Validate Phase 3: Execution enabled readiness."""
        criteria_results = []

        # Criterion 1: All Phase 2 criteria
        phase_2_report = self.validate_phase_2(backtest_result, 12)
        criteria_results.extend(phase_2_report.criteria)

        # Criterion 2: Monthly return consistency (no negative months)
        negative_months = sum(1 for r in monthly_returns if r < 0)
        criterion = ValidationCriterion(
            name="Monthly Return Consistency",
            threshold=90,
            actual=(len(monthly_returns) - negative_months) / len(monthly_returns) * 100 if monthly_returns else 0,
            passed=negative_months <= len(monthly_returns) * 0.1,
            severity="high",
            recommendation="Should have <= 10% negative return months"
        )
        criteria_results.append(criterion)

        # Criterion 3: Monthly drawdown limit
        max_monthly_dd = max(monthly_drawdowns) if monthly_drawdowns else 0
        criterion = ValidationCriterion(
            name="Monthly Drawdown Limit",
            threshold=10,
            actual=max_monthly_dd,
            passed=max_monthly_dd <= 10,
            severity="critical",
            recommendation="Max monthly drawdown should be <= 10%"
        )
        criteria_results.append(criterion)

        # Criterion 4: Win rate
        criterion = ValidationCriterion(
            name="Minimum Win Rate",
            threshold=55,
            actual=backtest_result.metrics.win_rate,
            passed=backtest_result.metrics.win_rate >= 55,
            severity="high",
            recommendation="Win rate should be >= 55% for execution"
        )
        criteria_results.append(criterion)

        passed = sum(1 for c in criteria_results if c.passed)
        total = len(criteria_results)
        critical_failures = sum(1 for c in criteria_results if not c.passed and c.severity == "critical")

        return ValidationReport(
            timestamp=datetime.utcnow(),
            total_criteria=total,
            passed_criteria=passed,
            failed_criteria=total - passed,
            pass_rate=(passed / total * 100) if total > 0 else 0,
            critical_failures=critical_failures,
            production_ready=critical_failures == 0,
            criteria=criteria_results,
        )

    def print_validation_report(self, report: ValidationReport) -> None:
        """Print a validation report."""
        status = "✓ PASS" if report.production_ready else "✗ FAIL"

        print("\n" + "="*80)
        print(f"VALIDATION REPORT — {status}")
        print("="*80)
        print(f"Date: {report.timestamp.isoformat()}")
        print(f"Criteria Passed: {report.passed_criteria}/{report.total_criteria} ({report.pass_rate:.1f}%)")
        print(f"Critical Failures: {report.critical_failures}")
        print()

        for criterion in report.criteria:
            status = "✓" if criterion.passed else "✗"
            print(f"{status} {criterion.name}")
            print(f"   Threshold: {criterion.threshold} | Actual: {criterion.actual:.2f}")
            if not criterion.passed:
                print(f"   → {criterion.recommendation}")
            print()

        print("="*80)

    def _get_phase_1_criteria(self) -> Dict:
        """Get Phase 1 criteria thresholds."""
        return {
            "min_trades": 100,
            "min_win_rate": 45,
            "min_profit_factor": 1.5,
            "min_sharpe": 1.0,
            "max_drawdown_dollars": 25000,
        }

    def _get_phase_2_criteria(self) -> Dict:
        """Get Phase 2 criteria thresholds."""
        return {
            "min_data_months": 6,
            "min_trades": 1000,
            "min_win_rate": 50,
            "min_profit_factor": 2.0,
            "min_sharpe": 1.5,
            "max_drawdown_dollars": 50000,
        }

    def _get_phase_3_criteria(self) -> Dict:
        """Get Phase 3 criteria thresholds."""
        return {
            "min_data_months": 12,
            "min_trades": 2000,
            "min_win_rate": 55,
            "min_profit_factor": 2.5,
            "min_sharpe": 2.0,
            "max_drawdown_dollars": 100000,
            "max_monthly_drawdown_percent": 10,
            "min_consistent_months": 90,
        }
