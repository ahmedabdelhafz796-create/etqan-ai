"""Operating State Machine (§5.1 MASTER_PLAN) — Event-driven human oversight."""

from datetime import datetime
from typing import Callable, Dict, List, Optional

from gold_agent.core.models import StateType


class StateTransition:
    """A state transition with conditions."""

    def __init__(
        self,
        from_state: StateType,
        to_state: StateType,
        trigger: str,
        condition: Optional[Callable[..., bool]] = None,
    ):
        self.from_state = from_state
        self.to_state = to_state
        self.trigger = trigger
        self.condition = condition or (lambda **kwargs: True)

    def can_transition(self, **kwargs) -> bool:
        """Check if transition can occur."""
        return self.condition(**kwargs)


class StateMachine:
    """
    4-state Operating State Machine.

    States (§5.1):
    - AUTONOMOUS: Normal operation, decisions acted on
    - SAFE_MODE: New trades blocked; existing managed; requires human review
    - EMERGENCY: Full stop + notification; connection loss/drawdown/bug
    - MANUAL_RECOVERY: Full stop until human review; NO automatic exit

    Escalation Triggers:
    - Data quality < 95% → Safe Mode
    - Model conflict (confidence divergence) → Safe Mode
    - Drawdown > 15% → Emergency
    - Connection loss > 5 min → Emergency
    - Market anomaly (VIX spike > 30%) → Emergency
    - Bug detected → Emergency

    Key Features:
    - Event-driven transitions (not trade-driven)
    - Kill switch mandatory (execution OFF by default)
    - No automatic exit from Emergency
    - All transitions audited
    """

    def __init__(self, initial_state = StateType.AUTONOMOUS):
        # Handle both string and enum inputs (config passes strings)
        if isinstance(initial_state, str):
            self.current_state = StateType(initial_state)
        else:
            self.current_state = initial_state
        self.previous_state = self.current_state
        self.transitions: List[StateTransition] = []
        self.transition_history: List[Dict] = []
        self.kill_switch_armed = True  # Armed = stopped; disarmed = ready
        self._setup_default_transitions()

    def _setup_default_transitions(self):
        """Set up default transition rules from config (§5.1)."""
        # Autonomous → Safe Mode
        self.add_transition(
            StateType.AUTONOMOUS,
            StateType.SAFE_MODE,
            "data_quality_degradation",
            lambda data_quality=1.0: data_quality < 0.95,
        )
        self.add_transition(
            StateType.AUTONOMOUS,
            StateType.SAFE_MODE,
            "model_conflict",
            lambda confidence_divergence=0: confidence_divergence > 0.60,
        )

        # Autonomous → Emergency
        self.add_transition(
            StateType.AUTONOMOUS,
            StateType.EMERGENCY,
            "critical_drawdown",
            lambda drawdown=0: drawdown > 0.15,
        )
        self.add_transition(
            StateType.AUTONOMOUS,
            StateType.EMERGENCY,
            "connection_loss",
            lambda timeout_seconds=0: timeout_seconds > 300,
        )
        self.add_transition(
            StateType.AUTONOMOUS,
            StateType.EMERGENCY,
            "market_anomaly",
            lambda vix_spike=0: vix_spike > 30,
        )
        self.add_transition(
            StateType.AUTONOMOUS,
            StateType.EMERGENCY,
            "bug_detected",
            lambda error=False: error is True,
        )

        # Safe Mode → Autonomous (manual review required)
        self.add_transition(
            StateType.SAFE_MODE,
            StateType.AUTONOMOUS,
            "manual_review_approved",
            lambda manual_approval=False: manual_approval is True,
        )

        # Safe Mode → Emergency (escalation)
        self.add_transition(
            StateType.SAFE_MODE,
            StateType.EMERGENCY,
            "escalate_to_emergency",
            lambda: True,
        )

        # Emergency → Manual Recovery (automatic escalation)
        # Note: NO automatic exit from Emergency
        self.add_transition(
            StateType.EMERGENCY,
            StateType.MANUAL_RECOVERY,
            "manual_recovery_initiated",
            lambda: True,
        )

        # Manual Recovery → Autonomous (manual approval only)
        self.add_transition(
            StateType.MANUAL_RECOVERY,
            StateType.AUTONOMOUS,
            "recovery_complete",
            lambda manual_approval=False: manual_approval is True,
        )

    def add_transition(
        self,
        from_state: StateType,
        to_state: StateType,
        trigger: str,
        condition: Optional[Callable[..., bool]] = None,
    ) -> None:
        """Add a state transition."""
        transition = StateTransition(from_state, to_state, trigger, condition)
        self.transitions.append(transition)

    def trigger(self, trigger_name: str, **kwargs) -> bool:
        """
        Trigger a state transition with optional conditions.

        Args:
            trigger_name: Name of the trigger
            **kwargs: Conditions for the transition

        Returns:
            bool: True if transition occurred, False otherwise
        """
        applicable = [
            t
            for t in self.transitions
            if t.from_state == self.current_state and t.trigger == trigger_name
        ]

        for transition in applicable:
            if transition.can_transition(**kwargs):
                self._execute_transition(transition, trigger_name, kwargs)
                return True

        return False

    def _execute_transition(
        self, transition: StateTransition, trigger: str, context: Dict
    ) -> None:
        """Execute a state transition and log it."""
        self.previous_state = self.current_state
        self.current_state = transition.to_state

        # Log transition
        self.transition_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "from_state": self.previous_state.value,
                "to_state": self.current_state.value,
                "trigger": trigger,
                "context": context,
            }
        )

    def can_trade(self) -> bool:
        """Check if trading is allowed in current state."""
        return self.current_state == StateType.AUTONOMOUS

    def can_execute(self) -> bool:
        """Check if execution is allowed (state + kill switch)."""
        return self.can_trade() and not self.kill_switch_armed

    def arm_kill_switch(self) -> None:
        """Arm kill switch (stop trading)."""
        self.kill_switch_armed = True
        self.transition_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event": "kill_switch_armed",
            }
        )

    def disarm_kill_switch(self) -> None:
        """Disarm kill switch (enable trading). Requires explicit activation."""
        self.kill_switch_armed = False
        self.transition_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event": "kill_switch_disarmed",
            }
        )

    def get_status(self) -> Dict:
        """Get current state and status."""
        return {
            "current_state": self.current_state.value,
            "previous_state": self.previous_state.value,
            "can_trade": self.can_trade(),
            "can_execute": self.can_execute(),
            "kill_switch_armed": self.kill_switch_armed,
            "transition_history_length": len(self.transition_history),
        }

    def reset(self, state: StateType = StateType.AUTONOMOUS) -> None:
        """Reset to a specific state (manual recovery only)."""
        if self.current_state == StateType.MANUAL_RECOVERY:
            self.current_state = state
            self.transition_history.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "event": "manual_reset",
                    "new_state": state.value,
                }
            )
        else:
            raise RuntimeError("Can only reset from MANUAL_RECOVERY state")

    def get_transition_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get transition history."""
        if limit:
            return self.transition_history[-limit:]
        return self.transition_history
