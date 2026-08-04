"""Signal Ensemble (Tier 4) — Combine multiple signals for robust predictions."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class SignalVote:
    """A single signal vote in the ensemble."""
    signal_name: str
    signal_type: str  # "technical", "macro", "correlation", "sentiment", "regime"
    vote: str  # "strong_buy", "buy", "neutral", "sell", "strong_sell"
    confidence: float  # 0-100
    weight: float  # Importance of this signal
    reasoning: str


@dataclass
class EnsembleVote:
    """Result of ensemble voting."""
    timestamp: datetime
    final_signal: str  # "strong_buy", "buy", "neutral", "sell", "strong_sell"
    buy_votes: int
    sell_votes: int
    neutral_votes: int
    weighted_score: float  # -100 (sell) to +100 (buy)
    consensus_strength: float  # 0-100 (how unified are the votes)
    agreement_level: str  # "strong_consensus", "consensus", "divided", "conflicted"
    individual_votes: List[SignalVote]


class SignalEnsemble:
    """
    Tier 4: Advanced Analysis - Ensemble Signal Combining.

    Combines multiple independent signals for more robust decision making.
    Reduces false signals and improves robustness.
    """

    def __init__(self, config):
        self.config = config
        self.signal_weights = {
            "rsi": 0.15,
            "macd": 0.15,
            "ma_cross": 0.15,
            "macro_sentiment": 0.20,
            "correlation_regime": 0.15,
            "volatility_regime": 0.10,
            "news_sentiment": 0.10,
        }
        self.voting_history: List[EnsembleVote] = []
        self.max_history = 100

    def vote(
        self,
        technical_signals: Dict[str, tuple],  # {signal_name: (vote, confidence)}
        macro_signals: Dict[str, tuple],
        correlation_signals: Dict[str, tuple],
        sentiment_signals: Dict[str, tuple],
        regime_signals: Dict[str, tuple],
    ) -> EnsembleVote:
        """
        Combine all signals through ensemble voting.

        Args:
            technical_signals: Technical indicator signals
            macro_signals: Macro analysis signals
            correlation_signals: Asset correlation signals
            sentiment_signals: News sentiment and other sentiment
            regime_signals: Market regime signals

        Returns:
            EnsembleVote with final decision and reasoning
        """
        all_votes = []

        # Process technical signals
        for signal_name, (vote, confidence) in technical_signals.items():
            weight = self.signal_weights.get(signal_name, 0.10)
            all_votes.append(SignalVote(
                signal_name=signal_name,
                signal_type="technical",
                vote=vote,
                confidence=confidence,
                weight=weight,
                reasoning=f"Technical signal: {signal_name}",
            ))

        # Process macro signals
        for signal_name, (vote, confidence) in macro_signals.items():
            weight = self.signal_weights.get("macro_sentiment", 0.20)
            all_votes.append(SignalVote(
                signal_name=signal_name,
                signal_type="macro",
                vote=vote,
                confidence=confidence,
                weight=weight,
                reasoning=f"Macro signal: {signal_name}",
            ))

        # Process correlation signals
        for signal_name, (vote, confidence) in correlation_signals.items():
            weight = self.signal_weights.get("correlation_regime", 0.15)
            all_votes.append(SignalVote(
                signal_name=signal_name,
                signal_type="correlation",
                vote=vote,
                confidence=confidence,
                weight=weight,
                reasoning=f"Correlation: {signal_name}",
            ))

        # Process sentiment signals
        for signal_name, (vote, confidence) in sentiment_signals.items():
            weight = self.signal_weights.get("news_sentiment", 0.10)
            all_votes.append(SignalVote(
                signal_name=signal_name,
                signal_type="sentiment",
                vote=vote,
                confidence=confidence,
                weight=weight,
                reasoning=f"Sentiment: {signal_name}",
            ))

        # Process regime signals
        for signal_name, (vote, confidence) in regime_signals.items():
            weight = self.signal_weights.get("volatility_regime", 0.10)
            all_votes.append(SignalVote(
                signal_name=signal_name,
                signal_type="regime",
                vote=vote,
                confidence=confidence,
                weight=weight,
                reasoning=f"Regime: {signal_name}",
            ))

        # Calculate ensemble result
        buy_score = 0.0
        sell_score = 0.0
        neutral_score = 0.0
        total_weight = 0.0

        for vote in all_votes:
            total_weight += vote.weight

            if vote.vote == "strong_buy":
                buy_score += vote.weight * vote.confidence * 2.0
            elif vote.vote == "buy":
                buy_score += vote.weight * vote.confidence
            elif vote.vote == "neutral":
                neutral_score += vote.weight * vote.confidence
            elif vote.vote == "sell":
                sell_score += vote.weight * vote.confidence
            elif vote.vote == "strong_sell":
                sell_score += vote.weight * vote.confidence * 2.0

        # Normalize scores
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
            neutral_score /= total_weight

        # Determine final signal
        max_score = max(buy_score, sell_score, neutral_score)
        if buy_score == max_score and buy_score > sell_score + 10:
            if buy_score > 60:
                final_signal = "strong_buy"
            else:
                final_signal = "buy"
        elif sell_score == max_score and sell_score > buy_score + 10:
            if sell_score > 60:
                final_signal = "strong_sell"
            else:
                final_signal = "sell"
        else:
            final_signal = "neutral"

        # Count votes
        buy_votes = sum(1 for v in all_votes if v.vote in ["buy", "strong_buy"])
        sell_votes = sum(1 for v in all_votes if v.vote in ["sell", "strong_sell"])
        neutral_votes = sum(1 for v in all_votes if v.vote == "neutral")

        # Calculate consensus strength
        total_votes = len(all_votes)
        max_consensus = max(buy_votes, sell_votes, neutral_votes) / total_votes if total_votes > 0 else 0
        consensus_strength = max_consensus * 100

        # Determine agreement level
        if consensus_strength > 80:
            agreement_level = "strong_consensus"
        elif consensus_strength > 60:
            agreement_level = "consensus"
        elif consensus_strength > 40:
            agreement_level = "divided"
        else:
            agreement_level = "conflicted"

        # Calculate weighted score (-100 to +100)
        weighted_score = buy_score - sell_score
        weighted_score = max(-100, min(100, weighted_score))

        ensemble_vote = EnsembleVote(
            timestamp=datetime.utcnow(),
            final_signal=final_signal,
            buy_votes=buy_votes,
            sell_votes=sell_votes,
            neutral_votes=neutral_votes,
            weighted_score=weighted_score,
            consensus_strength=consensus_strength,
            agreement_level=agreement_level,
            individual_votes=all_votes,
        )

        # Store in history
        self.voting_history.append(ensemble_vote)
        if len(self.voting_history) > self.max_history:
            self.voting_history.pop(0)

        return ensemble_vote

    def get_signal_reliability(self, lookback: int = 20) -> Dict[str, float]:
        """
        Calculate reliability of each signal type over recent history.

        Returns:
            Dict mapping signal type to reliability (0-1)
        """
        recent_votes = self.voting_history[-lookback:]

        if not recent_votes:
            return {}

        reliability = {}

        # Aggregate by signal type
        signal_performance = {}

        for ensemble in recent_votes:
            for vote in ensemble.individual_votes:
                signal_type = vote.signal_type

                if signal_type not in signal_performance:
                    signal_performance[signal_type] = {"correct": 0, "total": 0}

                # Assume ensemble decision is correct
                if (ensemble.final_signal in ["buy", "strong_buy"] and vote.vote in ["buy", "strong_buy"]) or \
                   (ensemble.final_signal in ["sell", "strong_sell"] and vote.vote in ["sell", "strong_sell"]) or \
                   (ensemble.final_signal == "neutral" and vote.vote == "neutral"):
                    signal_performance[signal_type]["correct"] += 1

                signal_performance[signal_type]["total"] += 1

        # Calculate reliability
        for signal_type, perf in signal_performance.items():
            if perf["total"] > 0:
                reliability[signal_type] = perf["correct"] / perf["total"]
            else:
                reliability[signal_type] = 0.5

        return reliability

    def update_weights_from_performance(self) -> None:
        """Adjust signal weights based on recent performance."""
        reliability = self.get_signal_reliability()

        # Normalize weights to sum to 1.0
        total_reliability = sum(reliability.values()) if reliability else 1.0

        if total_reliability == 0:
            total_reliability = 1.0

        for signal_name, rel in reliability.items():
            # Convert reliability to weight (0.5 = 1x, 0.7 = 1.4x, 0.3 = 0.6x)
            adjusted_weight = rel * 2.0  # Scale so 0.5 reliability = 1.0 weight

            # Only update if we have a known signal
            if signal_name in self.signal_weights:
                self.signal_weights[signal_name] = adjusted_weight

    def get_status(self) -> dict:
        """Get ensemble status."""
        recent_votes = self.voting_history[-10:]
        buy_consensus = sum(1 for v in recent_votes if v.final_signal in ["buy", "strong_buy"])
        sell_consensus = sum(1 for v in recent_votes if v.final_signal in ["sell", "strong_sell"])

        return {
            "total_votes": len(self.voting_history),
            "recent_buy_signals": buy_consensus,
            "recent_sell_signals": sell_consensus,
            "recent_neutral_signals": 10 - buy_consensus - sell_consensus,
            "average_consensus": sum(v.consensus_strength for v in recent_votes) / len(recent_votes) if recent_votes else 0,
            "signal_weights": self.signal_weights,
        }
