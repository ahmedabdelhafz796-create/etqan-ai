"""Main entry point for Gold Trading Analysis Agent."""

import asyncio
import sys
from pathlib import Path

from gold_agent.analysis.indicators import IndicatorEngine
from gold_agent.analysis.scoring import ScoringEngine
from gold_agent.analysis.macro import MacroAgent
from gold_agent.analysis.correlations import CorrelationAgent
from gold_agent.analysis.volatility_adjuster import VolatilityAdjuster
from gold_agent.analysis.regime_detector import RegimeDetector
from gold_agent.analysis.signal_ensemble import SignalEnsemble
from gold_agent.analysis.feature_importance import FeatureImportanceAnalyzer
from gold_agent.audit.db import get_audit_log
from gold_agent.brain.llm_brain import get_brain
from gold_agent.config import load_config, load_sharia_rules
from gold_agent.core.pipeline import Pipeline
from gold_agent.data.market import get_market_provider
from gold_agent.data.news import get_news_provider
from gold_agent.decision.decision_engine import DecisionEngine
from gold_agent.execution.engine import ExecutionEngine
from gold_agent.execution.brokers.mock import MockBrokerAdapter
from gold_agent.execution.order_manager import OrderManager
from gold_agent.execution.position_manager import PositionManager
from gold_agent.execution.capital_manager import CapitalManager
from gold_agent.execution.trade_lifecycle_manager import TradeLifecycleManager
from gold_agent.learning.learning_engine import LearningEngine
from gold_agent.validation.backtester import Backtester
from gold_agent.validation.performance_validator import PerformanceValidator
from gold_agent.monitoring.health import Monitor
from gold_agent.notification.telegram import get_notifier
from gold_agent.risk.risk_gate import RiskGate
from gold_agent.sharia.sharia_gate import ShariGate
from gold_agent.state_machine import StateMachine
from gold_agent.self_management.config_tuner import ConfigurationTuner
from gold_agent.self_management.adaptive_strategy_selector import AdaptiveStrategySelector
from gold_agent.self_management.risk_adjuster import RiskAdjuster
from gold_agent.self_management.performance_monitor import PerformanceMonitor
from gold_agent.self_management.parameter_optimizer import ParameterOptimizer


class GoldTradingAgent:
    """Main application orchestrator."""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.sharia_rules = load_sharia_rules()
        self._initialize_components()

    def _initialize_components(self):
        """Initialize all system components."""
        # State Machine
        self.state_machine = StateMachine(self.config.state_machine.initial_state)

        # Data Providers
        self.market_data = get_market_provider(
            self.config.data.market_provider,
        )
        self.news = get_news_provider(
            self.config.data.news_provider,
        )

        # Indicators & Scoring
        self.indicators = IndicatorEngine(self.config)
        self.scoring = ScoringEngine(self.config)

        # Phase 2: Macro & Correlation Analysis
        self.macro_agent = MacroAgent(self.config)
        self.correlation_agent = CorrelationAgent(self.config)

        # Tier 4: Advanced Analysis
        self.volatility_adjuster = VolatilityAdjuster(self.config)
        self.regime_detector = RegimeDetector(self.config)
        self.signal_ensemble = SignalEnsemble(self.config)
        self.feature_importance = FeatureImportanceAnalyzer(self.config)

        # Brain
        self.brain = get_brain(self.config.brain.provider, self.config)

        # Decision
        self.decision = DecisionEngine(self.config)

        # Gates
        self.risk_gate = RiskGate(self.config)
        self.sharia_gate = ShariGate(self.config, self.sharia_rules)

        # Notification
        self.notifier = get_notifier(self.config)

        # Audit
        self.audit_log = get_audit_log(self.config)

        # Tier 1 Execution Architecture
        # Initialize broker adapter (mock by default, or real broker if configured)
        broker_type = self.config.execution.broker_type
        if broker_type == "mock":
            self.broker = MockBrokerAdapter(self.config)
        elif broker_type == "mt5":
            from gold_agent.execution.brokers.mt5 import MT5BrokerAdapter
            self.broker = MT5BrokerAdapter(self.config)
        elif broker_type == "oanda":
            from gold_agent.execution.brokers.oanda import OANDABrokerAdapter
            self.broker = OANDABrokerAdapter(self.config)
        else:
            self.broker = MockBrokerAdapter(self.config)

        # Execution engine
        self.execution = ExecutionEngine(self.broker, self.config)

        # Execution subsystems
        self.order_manager = OrderManager(self.config)
        self.position_manager = PositionManager(self.config)
        self.capital_manager = CapitalManager(self.config, initial_capital=100000.0)
        self.trade_lifecycle = TradeLifecycleManager(
            self.position_manager,
            self.capital_manager,
            self.config
        )

        # Tier 2: Learning & Memory
        self.learning_engine = LearningEngine(self.config, self.audit_log)

        # Monitoring
        self.monitor = Monitor(self.config)

        # Pipeline (must be created before backtester which references it)
        self.pipeline = Pipeline(
            market_data_provider=self.market_data,
            news_provider=self.news,
            indicator_engine=self.indicators,
            scoring_engine=self.scoring,
            macro_agent=self.macro_agent,
            correlation_agent=self.correlation_agent,
            brain_engine=self.brain,
            decision_engine=self.decision,
            risk_gate=self.risk_gate,
            sharia_gate=self.sharia_gate,
            notifier=self.notifier,
            audit_log=self.audit_log,
            state_machine=self.state_machine,
            config=self.config,
        )

        # Tier 3: Validation & Testing (after pipeline)
        self.backtester = Backtester(self.config, self.pipeline)
        self.performance_validator = PerformanceValidator(self.config)

        # Tier 5: Self-Management
        self.config_tuner = ConfigurationTuner(self.config)
        self.strategy_selector = AdaptiveStrategySelector(self.config)
        self.risk_adjuster = RiskAdjuster(self.config)
        self.performance_monitor = PerformanceMonitor(self.config)
        self.parameter_optimizer = ParameterOptimizer(self.config)

    async def run_once(self) -> bool:
        """Run one complete analysis cycle."""
        try:
            # Check health
            health = await self.monitor.check_data_health(self.pipeline)
            if health and health.requires_intervention:
                await self.notifier.notify_state_change(
                    health.state.value,
                    health.reason or "Unknown reason"
                )

            # Run pipeline
            decision = await self.pipeline.run_once()

            # Record metrics
            if decision:
                gate_block = None
                if decision.risk_gate_verdict and not decision.risk_gate_verdict.passed:
                    gate_block = "Risk Gate"
                elif decision.sharia_gate_verdict and not decision.sharia_gate_verdict.passed:
                    gate_block = "Sharia Gate"

                self.monitor.record_decision(decision.action.value, gate_block)

            return decision is not None

        except Exception as e:
            print(f"Pipeline error: {e}")
            self.monitor.record_error()
            await self.notifier.notify_emergency(f"Pipeline error: {str(e)}")
            return False

    async def run_continuous(self, interval_minutes: int = 60):
        """Run continuously on a schedule."""
        print(f"Starting continuous run (interval: {interval_minutes}m)")
        import time

        while True:
            success = await self.run_once()
            if success:
                print("✓ Cycle complete")
            else:
                print("✗ Cycle failed")

            # Sleep until next cycle
            await asyncio.sleep(interval_minutes * 60)

    def get_status(self) -> dict:
        """Get current system status."""
        return {
            "state_machine": self.state_machine.get_status(),
            "health": self.monitor.get_status(),
            "performance": self.monitor.get_performance(),
            "execution": self.execution.get_status(),
            "orders": self.order_manager.get_status(),
            "positions": self.position_manager.get_status(),
            "capital": self.capital_manager.get_status(),
            "trades": self.trade_lifecycle.get_status(),
            "learning": self.learning_engine.get_status(),
            "volatility": self.volatility_adjuster.get_status(),
            "regime": self.regime_detector.get_status(),
            "ensemble": self.signal_ensemble.get_status(),
            "config_tuner": self.config_tuner.get_status(),
            "strategy_selector": self.strategy_selector.get_status(),
            "risk_adjuster": self.risk_adjuster.get_status(),
            "performance_monitor": self.performance_monitor.get_status(),
            "parameter_optimizer": self.parameter_optimizer.get_status(),
            "sharia": self.sharia_gate.get_compliance_status(),
        }

    async def print_status(self):
        """Print current system status."""
        status = self.get_status()
        print("\n=== SYSTEM STATUS ===")
        print(f"State: {status['state_machine']['current_state']}")
        print(f"Can Trade: {status['state_machine']['can_trade']}")
        print(f"Kill Switch: {'ARMED' if status['state_machine']['kill_switch_armed'] else 'DISARMED'}")
        print(f"\nHealth: {status['health']}")
        print(f"\nPerformance: {status['performance']}")
        print(f"\nExecution Engine: {status['execution']}")
        print(f"\nOrders: {status['orders']}")
        print(f"\nPositions: {status['positions']}")
        print(f"\nCapital: {status['capital']}")
        print(f"\nTrades: {status['trades']}")
        print(f"\nLearning: {status['learning']}")
        print(f"\nVolatility: {status['volatility']}")
        print(f"\nRegime: {status['regime']}")
        print(f"\nEnsemble: {status['ensemble']}")
        print(f"\nConfiguration Tuner: {status['config_tuner']}")
        print(f"\nStrategy Selector: {status['strategy_selector']}")
        print(f"\nRisk Adjuster: {status['risk_adjuster']}")
        print(f"\nPerformance Monitor: {status['performance_monitor']}")
        print(f"\nParameter Optimizer: {status['parameter_optimizer']}")
        print(f"\nSharia Compliance: {status['sharia']}")

    def print_report(self):
        """Print monitoring report."""
        print(self.monitor.generate_report())


async def main():
    """Main entry point."""
    # Ensure data directory exists
    Path("data").mkdir(exist_ok=True)

    # Initialize agent
    agent = GoldTradingAgent()

    # Run once
    print("Starting Gold Trading Analysis Agent...")
    print(f"Config: {agent.config.data.market_provider} market provider")
    print(f"State: {agent.state_machine.current_state.value}")
    print()

    success = await agent.run_once()

    # Print status
    await agent.print_status()
    agent.print_report()

    if success:
        print("\n✓ Analysis cycle completed successfully")
        return 0
    else:
        print("\n✗ Analysis cycle failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
