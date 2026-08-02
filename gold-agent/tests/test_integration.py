"""Integration tests — full pipeline with mock data."""

import asyncio
import sys
from pathlib import Path
import pytest
from datetime import datetime

# Add gold-agent/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gold_agent.analysis.indicators import IndicatorEngine
from gold_agent.analysis.scoring import ScoringEngine
from gold_agent.core.models import MarketData, ActionType, StateType
from gold_agent.data.market import MockMarketDataProvider
from gold_agent.data.news import MockNewsProvider
from gold_agent.decision.decision_engine import DecisionEngine
from gold_agent.risk.risk_gate import RiskGate
from gold_agent.sharia.sharia_gate import ShariGate
from gold_agent.config import Config, load_config


class TestIntegration:
    """Integration tests."""

    @pytest.fixture
    def config(self):
        """Load test config."""
        try:
            return load_config("config/config.yaml")
        except:
            # Fallback config
            return Config()

    @pytest.mark.asyncio
    async def test_market_data_fetch(self):
        """Test market data provider."""
        provider = MockMarketDataProvider()
        data = await provider.fetch()

        assert data is not None
        assert data.xau_usd > 0
        assert data.dxy > 0
        assert data.data_quality == 1.0

    @pytest.mark.asyncio
    async def test_news_fetch(self):
        """Test news provider."""
        provider = MockNewsProvider()
        news = await provider.fetch()

        assert isinstance(news, list)
        assert len(news) > 0
        assert news[0].title is not None

    def test_indicators(self, config):
        """Test indicator calculations."""
        engine = IndicatorEngine(config)

        # Add some data points
        for i in range(200):
            price = 2050 + i * 0.1
            engine.add_price(
                MarketData(
                    timestamp=datetime.utcnow(),
                    xau_usd=price,
                    dxy=104.0,
                )
            )

        # Calculate
        market_data = MarketData(
            timestamp=datetime.utcnow(),
            xau_usd=2070.0,
            dxy=104.0,
        )
        indicators = engine.calculate(market_data)

        assert indicators.rsi >= 0 and indicators.rsi <= 100
        assert indicators.ma_short > 0
        assert indicators.ma_long > 0

    def test_scoring(self, config):
        """Test scoring engine."""
        scorer = ScoringEngine(config)

        market_data = MarketData(
            timestamp=datetime.utcnow(),
            xau_usd=2050.0,
            dxy=104.0,
            bond_yield_10y=4.5,
            vix=15.0,
        )

        # Create indicators
        from gold_agent.core.models import IndicatorValues
        indicators = IndicatorValues(
            timestamp=datetime.utcnow(),
            rsi=35.0,  # Oversold
            macd=0.5,  # Positive
            macd_signal=0.3,
            macd_histogram=0.2,
            ma_short=2050.0,
            ma_long=2048.0,
        )

        score = scorer.score(
            indicators=indicators,
            news=[],
            market_data=market_data,
        )

        assert score.combined_score >= 0 and score.combined_score <= 100
        assert score.rsi_score > 0
        assert score.macd_score > 0

    def test_decision_engine(self, config):
        """Test decision generation."""
        decision_engine = DecisionEngine(config)

        from gold_agent.core.models import IndicatorValues, Score
        indicators = IndicatorValues(
            timestamp=datetime.utcnow(),
            rsi=25.0,
            macd=1.0,
            macd_signal=0.5,
            macd_histogram=0.5,
            ma_short=2050.0,
            ma_long=2048.0,
        )

        score = Score(
            timestamp=datetime.utcnow(),
            rsi_score=80.0,
            macd_score=75.0,
            ma_score=70.0,
            combined_score=75.0,
        )

        market_data = MarketData(
            timestamp=datetime.utcnow(),
            xau_usd=2050.0,
            dxy=104.0,
        )

        action, confidence, reason = decision_engine.decide(
            score=score,
            brain_result=None,
            market_data=market_data,
        )

        assert action in [ActionType.BUY, ActionType.SELL, ActionType.WAIT]
        assert confidence >= 0 and confidence <= 100
        assert reason is not None

    def test_risk_gate(self, config):
        """Test risk gate."""
        gate = RiskGate(config)

        market_data = MarketData(
            timestamp=datetime.utcnow(),
            xau_usd=2050.0,
            dxy=104.0,
            vix=15.0,
            data_quality=1.0,
        )

        from gold_agent.core.models import Score
        score = Score(
            timestamp=datetime.utcnow(),
            rsi_score=70.0,
            macd_score=70.0,
            ma_score=70.0,
            combined_score=70.0,
        )

        verdict = gate.check(ActionType.BUY, market_data, score)

        assert verdict.passed
        assert verdict.verdict.value == "passed"

    def test_sharia_gate(self, config):
        """Test Sharia gate."""
        gate = ShariGate(config)

        market_data = MarketData(
            timestamp=datetime.utcnow(),
            xau_usd=2050.0,
            dxy=104.0,
        )

        verdict = gate.check(ActionType.BUY, market_data)

        # Should pass with default mock rules
        assert verdict.passed

    def test_state_machine(self):
        """Test state machine."""
        from gold_agent.state_machine import StateMachine

        sm = StateMachine(StateType.AUTONOMOUS)

        assert sm.current_state == StateType.AUTONOMOUS
        assert sm.can_trade()
        assert not sm.can_execute()  # Kill switch armed

        # Trigger transition
        success = sm.trigger("data_quality_degradation", data_quality=0.9)
        assert success
        assert sm.current_state == StateType.SAFE_MODE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
