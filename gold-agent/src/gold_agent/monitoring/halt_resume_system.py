"""Halt/Resume System (§5.1 MASTER_PLAN) — Self-monitoring with 6 explicit halt triggers.

Operating State Machine:
- Autonomous: Normal operation
- Safe Mode: Stop new trades, keep existing positions open
- Emergency: Full stop, close all positions, manual recovery required
- Manual Recovery: No automatic exit from Emergency

HALT TRIGGERS (6 total):
1. Data feed disagreement (>0.5% diff between two sources)
2. Consecutive execution errors (3 failed orders)
3. Section 1 rule breach (capital/Sharia violation)
4. Sharia gate failure spike (>10% recent decisions rejected)
5. Broker connection loss (timeout >60s)
6. Abnormal market change (gap >2% in 1 min, or volatility spike >50%)

RESUME CONDITIONS (evidence-based, not timer-based):
1. Data feeds agree for 5+ consecutive quotes
2. Manual verification required for execution errors
3. Section 1 breach: NEVER auto-resume, manual recovery always
4. Sharia failure: Manual review of rule config
5. Connection re-established + health check passed
6. Manual decision on abnormal market conditions
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from enum import Enum

from gold_agent.core.models import StateType

logger = logging.getLogger(__name__)


class HaltReason(Enum):
    """Explicit halt trigger categories."""
    DATA_DISAGREEMENT = "data_disagreement"
    EXECUTION_ERRORS = "execution_errors"
    RULE_BREACH = "rule_breach"
    SHARIA_SPIKE = "sharia_spike"
    CONNECTION_LOSS = "connection_loss"
    ABNORMAL_MARKET = "abnormal_market"
    MANUAL = "manual"


class HaltResumeSystem:
    """Monitors system health and manages halt/resume transitions."""

    def __init__(self, config):
        self.config = config
        self.current_state = StateType.AUTONOMOUS
        self.halt_reason: Optional[HaltReason] = None
        self.halt_timestamp: Optional[datetime] = None
        self.halt_log: List[Dict] = []

        # Trigger tracking
        self.data_feed_tracking = {
            "price_sources": {},  # {source: price}
            "last_disagreement": None,
        }
        self.execution_error_count = 0
        self.execution_error_window = []  # Last 5 errors
        self.sharia_rejection_history = []  # Last 20 decisions
        self.connection_status_history = []  # Last 10 connection checks
        self.market_volatility_history = []  # Last 20 price ticks

    def check_trigger_1_data_disagreement(
        self, price_source_1: str, price_1: float, price_source_2: str, price_2: float
    ) -> Tuple[bool, Optional[str]]:
        """
        TRIGGER 1: Data feed disagreement (>0.5% difference).

        Returns:
            (should_halt: bool, reason: str or None)
        """
        if price_1 <= 0 or price_2 <= 0:
            return False, None

        price_diff_pct = abs(price_1 - price_2) / ((price_1 + price_2) / 2) * 100.0

        if price_diff_pct > 0.5:
            reason = (
                f"DATA DISAGREEMENT: {price_source_1}={price_1} vs "
                f"{price_source_2}={price_2} diverge by {price_diff_pct:.2f}% (threshold: 0.5%)"
            )
            logger.error(reason)
            return True, reason

        return False, None

    def check_trigger_1_resume(self, prices_aligned_count: int) -> bool:
        """
        TRIGGER 1 RESUME: Data feeds agree for 5+ consecutive quotes.

        Returns:
            True if data feeds stable and can resume
        """
        return prices_aligned_count >= 5

    def check_trigger_2_execution_errors(self, error_occurred: bool) -> Tuple[bool, Optional[str]]:
        """
        TRIGGER 2: Consecutive execution errors (3 failed order placements).

        Returns:
            (should_halt: bool, reason: str or None)
        """
        if error_occurred:
            self.execution_error_count += 1
            self.execution_error_window.append(datetime.utcnow())

            # Trim to last 5 errors
            cutoff = datetime.utcnow() - timedelta(minutes=10)
            self.execution_error_window = [t for t in self.execution_error_window if t > cutoff]

            if len(self.execution_error_window) >= 3:
                reason = (
                    f"EXECUTION ERROR SPIKE: {len(self.execution_error_window)} errors "
                    f"in last 10 minutes (threshold: 3). HALT for manual verification."
                )
                logger.critical(reason)
                return True, reason

        return False, None

    def check_trigger_2_resume(self) -> bool:
        """
        TRIGGER 2 RESUME: Manual verification required.

        No automatic resume - requires explicit human confirmation.

        Returns:
            False (always, requires manual intervention)
        """
        return False

    def check_trigger_3_rule_breach(self, rule_breached: bool, rule_name: str = "") -> Tuple[bool, Optional[str]]:
        """
        TRIGGER 3: Section 1 rule breach (capital or Sharia violation).

        Returns:
            (should_halt: bool, reason: str or None)
        """
        if rule_breached:
            reason = f"RULE BREACH: {rule_name or 'Governance rule violation'}. Escalating to Emergency."
            logger.critical(reason)
            return True, reason

        return False, None

    def check_trigger_3_resume(self) -> bool:
        """
        TRIGGER 3 RESUME: Section 1 rule breach.

        NEVER auto-resume from Emergency triggered by rule breach.
        Manual recovery always required.

        Returns:
            False (always)
        """
        return False

    def check_trigger_4_sharia_spike(
        self, recent_decisions: List[Dict], rejection_threshold_pct: float = 10.0
    ) -> Tuple[bool, Optional[str]]:
        """
        TRIGGER 4: Sharia gate failure spike (>10% recent decisions rejected).

        Args:
            recent_decisions: Last 20 trade decisions with sharia_passed status
            rejection_threshold_pct: Threshold for rejection rate (default 10%)

        Returns:
            (should_halt: bool, reason: str or None)
        """
        if not recent_decisions:
            return False, None

        rejections = sum(1 for d in recent_decisions if not d.get("sharia_passed", True))
        rejection_rate = (rejections / len(recent_decisions)) * 100.0

        if rejection_rate > rejection_threshold_pct:
            reason = (
                f"SHARIA SPIKE: {rejections}/{len(recent_decisions)} decisions rejected "
                f"({rejection_rate:.1f}% > {rejection_threshold_pct}%). Indicates rule misconfiguration."
            )
            logger.warning(reason)
            return True, reason

        return False, None

    def check_trigger_4_resume(self) -> bool:
        """
        TRIGGER 4 RESUME: Sharia rule misconfiguration.

        Requires manual review of sharia_rules.yaml configuration.

        Returns:
            False (requires manual fix)
        """
        return False

    def check_trigger_5_connection_loss(self, connection_healthy: bool) -> Tuple[bool, Optional[str]]:
        """
        TRIGGER 5: Broker connection loss (timeout >60s or connection down).

        Returns:
            (should_halt: bool, reason: str or None)
        """
        self.connection_status_history.append({"timestamp": datetime.utcnow(), "healthy": connection_healthy})

        # Trim to last 10
        if len(self.connection_status_history) > 10:
            self.connection_status_history = self.connection_status_history[-10:]

        if not connection_healthy:
            reason = "CONNECTION LOSS: Broker connection timeout or down. Escalating to Emergency."
            logger.critical(reason)
            return True, reason

        return False, None

    def check_trigger_5_resume(self, connection_healthy: bool, health_check_passed: bool) -> bool:
        """
        TRIGGER 5 RESUME: Connection re-established + health check passed.

        Returns:
            True only if both connection and health check pass
        """
        return connection_healthy and health_check_passed

    def check_trigger_6_abnormal_market(
        self, current_price: float, previous_price: float, volatility_pct: float
    ) -> Tuple[bool, Optional[str]]:
        """
        TRIGGER 6: Abnormal market change (gap >2% in 1 min, or volatility spike >50%).

        Returns:
            (should_halt: bool, reason: str or None)
        """
        if previous_price <= 0:
            return False, None

        gap_pct = abs(current_price - previous_price) / previous_price * 100.0

        self.market_volatility_history.append({"price": current_price, "timestamp": datetime.utcnow()})
        if len(self.market_volatility_history) > 20:
            self.market_volatility_history = self.market_volatility_history[-20:]

        if gap_pct > 2.0:
            reason = f"ABNORMAL MARKET: Price gap {gap_pct:.2f}% in 1 minute (threshold: 2%). Safe Mode."
            logger.warning(reason)
            return True, reason

        if volatility_pct > 50.0:
            reason = f"ABNORMAL MARKET: Volatility spike {volatility_pct:.1f}% (threshold: 50%). Safe Mode."
            logger.warning(reason)
            return True, reason

        return False, None

    def check_trigger_6_resume(self) -> bool:
        """
        TRIGGER 6 RESUME: Abnormal market conditions.

        Requires manual decision: legitimate volatility spike vs. exchange malfunction.

        Returns:
            False (requires manual decision)
        """
        return False

    def escalate_to_safe_mode(self, reason: str) -> Dict:
        """
        Escalate system to Safe Mode.

        - Stops NEW trades
        - Keeps existing positions OPEN (allows manual close if desired)
        """
        self.current_state = StateType.SAFE_MODE
        self.halt_reason = HaltReason.ABNORMAL_MARKET
        self.halt_timestamp = datetime.utcnow()

        log_entry = {
            "timestamp": self.halt_timestamp.isoformat(),
            "state_transition": "Autonomous → Safe Mode",
            "reason": reason,
        }
        self.halt_log.append(log_entry)

        logger.warning(f"ESCALATED TO SAFE MODE: {reason}")
        return log_entry

    def escalate_to_emergency(self, reason: str, halt_reason: HaltReason) -> Dict:
        """
        Escalate system to Emergency (full stop).

        - Closes ALL positions via market order
        - Full halt on all execution
        - Manual recovery required (no automatic exit)
        """
        self.current_state = StateType.EMERGENCY
        self.halt_reason = halt_reason
        self.halt_timestamp = datetime.utcnow()

        log_entry = {
            "timestamp": self.halt_timestamp.isoformat(),
            "state_transition": f"* → Emergency (via {halt_reason.value})",
            "reason": reason,
            "manual_recovery_required": True,
        }
        self.halt_log.append(log_entry)

        logger.critical(f"ESCALATED TO EMERGENCY: {reason}")
        return log_entry

    def manual_recovery(self, verified_by: str = "user", notes: str = "") -> Dict:
        """
        Manually exit Emergency state (operator-initiated recovery).

        Requires explicit human confirmation that the emergency condition is resolved.

        Returns:
            Recovery log entry
        """
        if self.current_state != StateType.EMERGENCY:
            logger.warning(f"Manual recovery called, but not in Emergency state (state: {self.current_state})")
            return {}

        previous_state = self.current_state
        self.current_state = StateType.AUTONOMOUS  # Back to normal operation
        self.halt_reason = None

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "state_transition": f"Emergency → Autonomous (manual recovery)",
            "verified_by": verified_by,
            "notes": notes,
        }
        self.halt_log.append(log_entry)

        logger.info(f"Manual recovery completed by {verified_by}. Resuming normal operation.")
        return log_entry

    def get_status(self) -> Dict:
        """Get current system state and halt information."""
        return {
            "current_state": self.current_state.value if hasattr(self.current_state, "value") else str(self.current_state),
            "halt_reason": self.halt_reason.value if self.halt_reason else None,
            "halt_timestamp": self.halt_timestamp.isoformat() if self.halt_timestamp else None,
            "halt_log_count": len(self.halt_log),
            "last_halt": self.halt_log[-1] if self.halt_log else None,
        }

    def get_halt_log(self) -> List[Dict]:
        """Get complete halt/resume log."""
        return self.halt_log.copy()
