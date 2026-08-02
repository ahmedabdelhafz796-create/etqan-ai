"""Feature Importance Analyzer (Tier 4) — Identify most predictive indicators."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import statistics


@dataclass
class FeatureImportance:
    """Importance score for a single feature."""
    feature_name: str
    importance_score: float  # 0-100 (higher = more important)
    correlation_with_outcome: float  # -1 to +1 (how predictive)
    prediction_accuracy: float  # % correct when this feature signals
    usage_frequency: int  # How often this feature is used
    value_rank: int  # Ranking compared to other features


@dataclass
class ImportanceReport:
    """Complete feature importance analysis."""
    timestamp: datetime
    total_features: int
    total_trades: int
    most_important: List[FeatureImportance]
    least_important: List[FeatureImportance]
    redundant_features: List[str]  # Features that are redundant with others


class FeatureImportanceAnalyzer:
    """
    Tier 4: Advanced Analysis - Feature Importance.

    Identifies which indicators and signals are most predictive of market moves.
    Helps optimize signal generation and identify redundant features.
    """

    def __init__(self, config):
        self.config = config
        self.feature_scores: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        self.max_trades = 500

    def analyze_feature_importance(
        self,
        trades: List[Dict],
    ) -> ImportanceReport:
        """
        Analyze which features (indicators) are most predictive.

        Args:
            trades: List of closed trades with entry features and outcome

        Returns:
            ImportanceReport with feature rankings
        """
        if len(trades) < 10:
            return ImportanceReport(
                timestamp=datetime.utcnow(),
                total_features=0,
                total_trades=0,
                most_important=[],
                least_important=[],
                redundant_features=[],
            )

        # Aggregate feature data
        feature_data = self._aggregate_feature_data(trades)

        # Calculate importance for each feature
        feature_importance_list = []

        for feature_name, data in feature_data.items():
            if data["usage_count"] == 0:
                continue

            # Calculate correlation with profitability
            correlation = self._calculate_correlation_with_pnl(
                data["values"],
                data["pnls"],
            )

            # Calculate prediction accuracy
            accuracy = data["correct_predictions"] / data["usage_count"] if data["usage_count"] > 0 else 0

            # Combine into importance score (0-100)
            importance_score = (
                abs(correlation) * 40 +  # Correlation strength (40%)
                accuracy * 40 +  # Prediction accuracy (40%)
                (data["usage_count"] / len(trades)) * 20  # Frequency (20%)
            )

            feature_importance_list.append(FeatureImportance(
                feature_name=feature_name,
                importance_score=importance_score,
                correlation_with_outcome=correlation,
                prediction_accuracy=accuracy * 100,
                usage_frequency=data["usage_count"],
                value_rank=0,  # Will be set later
            ))

        # Sort by importance
        feature_importance_list.sort(key=lambda x: x.importance_score, reverse=True)

        # Set ranks
        for i, fi in enumerate(feature_importance_list):
            fi.value_rank = i + 1

        # Identify redundant features
        redundant = self._identify_redundant_features(feature_importance_list)

        # Get top and bottom features
        most_important = feature_importance_list[:10]
        least_important = feature_importance_list[-5:] if len(feature_importance_list) > 5 else []

        return ImportanceReport(
            timestamp=datetime.utcnow(),
            total_features=len(feature_data),
            total_trades=len(trades),
            most_important=most_important,
            least_important=least_important,
            redundant_features=redundant,
        )

    def _aggregate_feature_data(self, trades: List[Dict]) -> Dict:
        """Aggregate feature data from trades."""
        feature_data = {}

        for trade in trades:
            features = trade.get("entry_features", {})
            pnl = trade.get("final_p_l", 0.0)
            was_profitable = pnl > 0

            for feature_name, feature_value in features.items():
                if feature_name not in feature_data:
                    feature_data[feature_name] = {
                        "values": [],
                        "pnls": [],
                        "usage_count": 0,
                        "correct_predictions": 0,
                    }

                feature_data[feature_name]["values"].append(feature_value)
                feature_data[feature_name]["pnls"].append(pnl)
                feature_data[feature_name]["usage_count"] += 1

                # Simple heuristic: if feature value is positive and trade was profitable,
                # or negative and trade lost, it was a correct prediction
                if (feature_value > 0 and was_profitable) or (feature_value < 0 and not was_profitable):
                    feature_data[feature_name]["correct_predictions"] += 1

        return feature_data

    @staticmethod
    def _calculate_correlation_with_pnl(values: List[float], pnls: List[float]) -> float:
        """Calculate Pearson correlation between feature and P&L."""
        if len(values) < 2 or len(pnls) < 2 or len(values) != len(pnls):
            return 0.0

        mean_val = statistics.mean(values)
        mean_pnl = statistics.mean(pnls)

        numerator = sum((values[i] - mean_val) * (pnls[i] - mean_pnl) for i in range(len(values)))
        denominator_val = sum((v - mean_val) ** 2 for v in values) ** 0.5
        denominator_pnl = sum((p - mean_pnl) ** 2 for p in pnls) ** 0.5

        if denominator_val == 0 or denominator_pnl == 0:
            return 0.0

        correlation = numerator / (denominator_val * denominator_pnl)
        return max(-1.0, min(1.0, correlation))

    def _identify_redundant_features(self, features: List[FeatureImportance]) -> List[str]:
        """Identify features that are redundant with higher-ranked features."""
        redundant = []

        # If importance gap between two features is large, lower-ranked might be redundant
        for i in range(1, len(features)):
            prev_importance = features[i-1].importance_score
            curr_importance = features[i].importance_score

            # If importance drops by >30%, current feature might be redundant
            if (prev_importance - curr_importance) / prev_importance > 0.3:
                # Check if correlation is similar to previous feature
                # For now, use a simple heuristic: keep only top features
                if curr_importance < 30:  # Arbitrary threshold
                    redundant.append(features[i].feature_name)

        return redundant

    def get_feature_recommendations(self, report: ImportanceReport) -> Dict[str, str]:
        """Get recommendations for feature optimization."""
        recommendations = {}

        if not report.most_important:
            return recommendations

        # Top feature
        top_feature = report.most_important[0]
        recommendations["top_feature"] = f"Focus on {top_feature.feature_name} (importance: {top_feature.importance_score:.1f})"

        # Features to remove
        if report.least_important:
            weak_features = [f.feature_name for f in report.least_important if f.importance_score < 20]
            if weak_features:
                recommendations["remove_features"] = f"Consider removing: {', '.join(weak_features)}"

        # Redundant features
        if report.redundant_features:
            recommendations["remove_redundant"] = f"Remove redundant features: {', '.join(report.redundant_features)}"

        # Feature coverage
        if len(report.most_important) < 3:
            recommendations["coverage"] = "Only a few high-importance features detected. Consider adding more indicators."

        return recommendations

    def print_importance_report(self, report: ImportanceReport) -> None:
        """Print feature importance report."""
        print("\n" + "="*80)
        print("FEATURE IMPORTANCE ANALYSIS")
        print("="*80)
        print(f"Date: {report.timestamp.isoformat()}")
        print(f"Total Features: {report.total_features}")
        print(f"Trades Analyzed: {report.total_trades}")
        print()

        print("MOST IMPORTANT FEATURES")
        print("-"*80)
        for fi in report.most_important:
            print(f"{fi.value_rank}. {fi.feature_name}")
            print(f"   Importance: {fi.importance_score:.1f}")
            print(f"   Correlation: {fi.correlation_with_outcome:.3f}")
            print(f"   Accuracy: {fi.prediction_accuracy:.1f}%")
            print()

        if report.redundant_features:
            print("REDUNDANT FEATURES (consider removing)")
            print("-"*80)
            for feature in report.redundant_features:
                print(f"- {feature}")
            print()

        print("="*80)
