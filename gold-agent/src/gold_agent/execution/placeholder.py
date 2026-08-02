"""Execution Placeholder (§4, §5.1 MASTER_PLAN) — OFF by default.

Kill Switch is mandatory. Execution is designed to be able to run
automatically but is STOPPED by default until consciously activated
after real testing.
"""

from typing import Optional

from src.gold_agent.core.models import Decision


class ExecutionEngine:
    """
    Execution engine placeholder.

    Phase 1-2: Disabled (alerts only)
    Phase 4: Implemented with real broker integration
    """

    def __init__(self, config):
        self.config = config
        self.enabled = config.execution.enabled
        self.kill_switch_armed = config.execution.kill_switch_armed
        self.broker = None
        self.position_size = 0.0
        self.last_execution_price = None
        self.last_execution_time = None

    async def execute(self, decision: Decision) -> Optional[dict]:
        """
        Execute a decision (BUY/SELL).

        Returns:
            Execution details if successful, None if blocked.
        """
        # Safety check 1: Execution disabled
        if not self.enabled:
            return {
                "status": "BLOCKED",
                "reason": "Execution engine disabled (Phase 1 - alerts only)",
                "decision_action": decision.action.value,
                "confidence": decision.confidence,
            }

        # Safety check 2: Kill switch armed
        if self.kill_switch_armed:
            return {
                "status": "BLOCKED",
                "reason": "Kill switch ARMED - trading stopped",
                "decision_action": decision.action.value,
                "kill_switch_armed": True,
            }

        # Safety check 3: State machine check
        if not self._can_execute():
            return {
                "status": "BLOCKED",
                "reason": "State machine does not allow execution",
                "current_state": "to be added",
            }

        # Safety check 4: Confidence threshold
        if decision.confidence < self.config.scoring.confidence_threshold_act:
            return {
                "status": "BLOCKED",
                "reason": f"Confidence {decision.confidence:.0f}% below execution threshold",
                "confidence": decision.confidence,
            }

        # If all checks pass, execution would happen here in Phase 4
        # For now, just log
        return {
            "status": "WOULD_EXECUTE",
            "action": decision.action.value,
            "confidence": decision.confidence,
            "note": "Phase 1 - execution not implemented",
        }

    def _can_execute(self) -> bool:
        """Check if execution is allowed by state machine."""
        # TODO: Connect to state machine
        return False

    def arm_kill_switch(self) -> bool:
        """Arm kill switch (stop trading)."""
        self.kill_switch_armed = True
        return True

    def disarm_kill_switch(self, confirmation: str) -> bool:
        """
        Disarm kill switch (enable trading).

        Requires explicit string confirmation for safety.
        """
        if confirmation != "ACTIVATE_TRADING":
            return False

        self.kill_switch_armed = False
        return True

    def get_status(self) -> dict:
        """Get execution status."""
        return {
            "enabled": self.enabled,
            "kill_switch_armed": self.kill_switch_armed,
            "broker": self.config.execution.broker,
            "position_size": self.position_size,
            "phase": "1 (alerts only)",
        }


class MockBroker:
    """Mock broker for testing (Phase 1-2)."""

    def __init__(self):
        self.positions = {}
        self.balance = 100000.0  # Starting capital
        self.trades = []

    async def buy(self, symbol: str, quantity: float, price: float) -> bool:
        """Execute a buy order."""
        cost = quantity * price
        if cost > self.balance:
            return False

        self.balance -= cost
        self.positions[symbol] = quantity
        self.trades.append({
            "action": "BUY",
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
        })
        return True

    async def sell(self, symbol: str, quantity: float, price: float) -> bool:
        """Execute a sell order."""
        if symbol not in self.positions or self.positions[symbol] < quantity:
            return False

        proceeds = quantity * price
        self.balance += proceeds
        self.positions[symbol] -= quantity
        self.trades.append({
            "action": "SELL",
            "symbol": symbol,
            "quantity": quantity,
            "price": price,
        })
        return True

    def get_balance(self) -> float:
        """Get account balance."""
        return self.balance

    def get_positions(self) -> dict:
        """Get open positions."""
        return self.positions.copy()
