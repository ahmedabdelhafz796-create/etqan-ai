#!/usr/bin/env python3
"""
Run Gold Trading Analysis Agent once.

Usage:
    python scripts/run_once.py

This script runs one complete analysis cycle without any scheduling.
It fetches market data, calculates indicators, analyzes, and produces
a decision with confidence and explanation.

Expected output:
- Decision: BUY/SELL/WAIT
- Confidence: X%
- Reason: explanation
- Audit log: saved to database

No API keys required; mock data is used by default.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gold_agent.main import GoldTradingAgent


async def main():
    """Run one analysis cycle."""
    try:
        print("=" * 60)
        print("Gold Trading Analysis Agent — Run Once")
        print("=" * 60)
        print()

        # Initialize
        print("Initializing agent...")
        agent = GoldTradingAgent()
        print("✓ Agent initialized")
        print()

        # Run cycle
        print("Running analysis cycle...")
        success = await agent.run_once()

        if success:
            print("✓ Analysis cycle completed successfully")
            print()

            # Print decision if available
            if agent.pipeline.last_decision:
                decision = agent.pipeline.last_decision
                print("=" * 60)
                print("DECISION")
                print("=" * 60)
                print(f"Action:     {decision.action.value}")
                print(f"Confidence: {decision.confidence:.1f}%")
                print(f"Reason:     {decision.reason}")
                print(f"State:      {decision.state.value}")
                print()

                if decision.risk_gate_verdict:
                    print(f"Risk Gate:  {'✓ PASSED' if decision.risk_gate_verdict.passed else '✗ BLOCKED'}")
                if decision.sharia_gate_verdict:
                    print(f"Sharia Gate:{'✓ PASSED' if decision.sharia_gate_verdict.passed else '✗ BLOCKED'}")
                print()

            # Print status
            print("=" * 60)
            print("STATUS")
            print("=" * 60)
            await agent.print_status()
            print()

            # Print report
            print("=" * 60)
            print("REPORT")
            print("=" * 60)
            agent.print_report()

            return 0
        else:
            print("✗ Analysis cycle failed")
            print()
            agent.print_report()
            return 1

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
