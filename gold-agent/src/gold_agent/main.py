"""Main entry point for Gold Trading Analysis Agent."""

import asyncio
import sys
from pathlib import Path

from src.gold_agent.analysis.indicators import IndicatorEngine
from src.gold_agent.analysis.scoring import ScoringEngine
from src.gold_agent.audit.db import get_audit_log
from src.gold_agent.brain.llm_brain import get_brain
from src.gold_agent.config import load_config, load_sharia_rules
from src.gold_agent.core.pipeline import Pipeline
from src.gold_agent.data.market import get_market_provider
from src.gold_agent.data.news import get_news_provider
from src.gold_agent.decision.decision_engine import DecisionEngine
from src.gold_agent.execution.placeholder import ExecutionEngine
from src.gold_agent.monitoring.health import Monitor
from src.gold_agent.notification.telegram import get_notifier
from src.gold_agent.risk.risk_gate import RiskGate
from src.gold_agent.sharia.sharia_gate import ShariGate
from src.gold_agent.state_machine import StateMachine


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
            api_key=self.config.data.market.provider,
        )
        self.news = get_news_provider(
            self.config.data.news_provider,
            api_key=self.config.data.news.provider,
        )

        # Indicators & Scoring
        self.indicators = IndicatorEngine(self.config)
        self.scoring = ScoringEngine(self.config)

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

        # Execution
        self.execution = ExecutionEngine(self.config)

        # Monitoring
        self.monitor = Monitor(self.config)

        # Pipeline
        self.pipeline = Pipeline(
            market_data_provider=self.market_data,
            news_provider=self.news,
            indicator_engine=self.indicators,
            scoring_engine=self.scoring,
            brain_engine=self.brain,
            decision_engine=self.decision,
            risk_gate=self.risk_gate,
            sharia_gate=self.sharia_gate,
            notifier=self.notifier,
            audit_log=self.audit_log,
            state_machine=self.state_machine,
            config=self.config,
        )

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
        print(f"\nExecution: {status['execution']}")
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
