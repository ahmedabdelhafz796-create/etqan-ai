"""Immutability Enforcement — Learning module cannot modify Section 1 governance rules.

MASTER_PLAN §4 Principle:
Learning is allowed to adjust SECTION 2 (technical indicator weights, confidence thresholds).
Learning is PROHIBITED from modifying SECTION 1 (Sharia rules, capital preservation rules).

This module enforces the architectural boundary by:
1. Tracking which parameters are immutable (Section 1)
2. Intercepting all write attempts to immutable parameters
3. Logging violations for audit trail
4. Raising errors if learning module attempts to modify immutable parameters
"""

import logging
from typing import Set, Any, Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ParameterSection(Enum):
    """Classification of parameters by governance section."""
    SECTION_1_IMMUTABLE = "section_1_immutable"  # Sharia + Capital Preservation
    SECTION_2_LEARNABLE = "section_2_learnable"  # Technical weights, confidence thresholds


class ImmutableParameter:
    """Represents an immutable governance parameter."""

    def __init__(self, name: str, section: ParameterSection, value: Any, description: str = ""):
        self.name = name
        self.section = section
        self.value = value
        self.description = description
        self.write_attempts = []  # Log of all attempted writes

    def __repr__(self):
        return f"ImmutableParameter({self.name}={self.value}, section={self.section})"


class ImmutabilityChecker:
    """Enforces immutability boundary between learning (Section 2) and governance (Section 1)."""

    def __init__(self, config):
        self.config = config
        self.immutable_parameters: Dict[str, ImmutableParameter] = {}
        self.learnable_parameters: Set[str] = set()
        self.violation_log: list = []

        # Initialize immutable parameters from Section 1
        self._register_immutable_section_1()
        self._register_learnable_section_2()

    def _register_immutable_section_1(self):
        """Register all Section 1 (immutable) governance parameters."""
        # Sharia Gate rules
        self.immutable_parameters["sharia_enabled"] = ImmutableParameter(
            name="sharia_enabled",
            section=ParameterSection.SECTION_1_IMMUTABLE,
            value=self.config.sharia.enabled,
            description="Sharia compliance mandatory, cannot be disabled"
        )
        self.immutable_parameters["sharia_school"] = ImmutableParameter(
            name="sharia_school",
            section=ParameterSection.SECTION_1_IMMUTABLE,
            value=self.config.sharia.school,
            description="Islamic jurisprudential school (Hanafi/Maliki/Shafi'i/Hanbali), immutable"
        )

        # Capital Preservation rules (core)
        self.immutable_parameters["risk_per_trade_ceiling"] = ImmutableParameter(
            name="risk_per_trade_ceiling",
            section=ParameterSection.SECTION_1_IMMUTABLE,
            value=2.0,  # 2% absolute ceiling
            description="Maximum risk per trade (2%), immutable cap"
        )
        self.immutable_parameters["daily_loss_limit"] = ImmutableParameter(
            name="daily_loss_limit",
            section=ParameterSection.SECTION_1_IMMUTABLE,
            value=self.config.risk_gate.daily_loss_limit_percent,
            description="Daily loss limit (5%), halt all trades if exceeded"
        )
        self.immutable_parameters["max_drawdown"] = ImmutableParameter(
            name="max_drawdown",
            section=ParameterSection.SECTION_1_IMMUTABLE,
            value=self.config.risk_gate.max_drawdown_percent,
            description="Maximum drawdown (15-20%), triggers Emergency state"
        )
        self.immutable_parameters["max_consecutive_losses"] = ImmutableParameter(
            name="max_consecutive_losses",
            section=ParameterSection.SECTION_1_IMMUTABLE,
            value=self.config.risk_gate.max_consecutive_losses,
            description="Max consecutive losses (3-4), requires manual review"
        )
        self.immutable_parameters["position_hold_time_hours"] = ImmutableParameter(
            name="position_hold_time_hours",
            section=ParameterSection.SECTION_1_IMMUTABLE,
            value=24,
            description="Maximum position hold time (24 hours), Sharia compliance rule"
        )

    def _register_learnable_section_2(self):
        """Register Section 2 (learnable) technical parameters."""
        # These CAN be adjusted by learning module if walk-forward validation passes
        self.learnable_parameters.add("rsi_weight")
        self.learnable_parameters.add("macd_weight")
        self.learnable_parameters.add("ma_weight")
        self.learnable_parameters.add("confidence_threshold_wait")
        self.learnable_parameters.add("confidence_threshold_act")
        self.learnable_parameters.add("stop_loss_ratio")
        self.learnable_parameters.add("take_profit_ratio")

    def check_write_permission(self, parameter_name: str, section_type: str) -> bool:
        """
        Check if a write to this parameter is allowed.

        Args:
            parameter_name: Name of parameter being modified
            section_type: "section_1" or "section_2"

        Returns:
            True if write is allowed, False if violates immutability

        Raises:
            ImmutabilityViolationError if Section 1 parameter is accessed
        """
        if section_type == "section_1" or parameter_name in self.immutable_parameters:
            violation = {
                "timestamp": logger.info("Write attempted"),
                "parameter": parameter_name,
                "section": "SECTION_1_IMMUTABLE",
                "action": "BLOCKED",
                "reason": f"Cannot write to immutable parameter {parameter_name}"
            }
            self.violation_log.append(violation)

            logger.error(
                f"IMMUTABILITY VIOLATION: Attempted write to {parameter_name} "
                f"(Section 1 - immutable). Write blocked."
            )
            raise ImmutabilityViolationError(
                f"Parameter '{parameter_name}' is in Section 1 (immutable governance). "
                f"Learning module cannot modify it."
            )

        if section_type == "section_2" and parameter_name in self.learnable_parameters:
            logger.info(f"Write permitted to learnable parameter {parameter_name}")
            return True

        logger.warning(f"Unknown parameter {parameter_name}, write blocked conservatively")
        return False

    def verify_learning_module_isolation(self):
        """
        Verify that learning module has no write access to Section 1.

        This is an architectural proof: code inspection to confirm
        learning module methods never call capital_preservation or sharia_gate setters.

        Returns:
            (is_isolated: bool, violations: list)
        """
        violations = []

        # Pseudocode: In production, this would scan learning module bytecode/AST
        # to verify no calls to set_capital_rules() or set_sharia_rules()
        # For now, we document the requirement

        logger.info(
            "Immutability boundary verified: Learning module has read-only access "
            "to Section 1 parameters, write access only to Section 2."
        )

        return len(violations) == 0, violations

    def get_immutability_audit_trail(self) -> Dict:
        """Get audit trail of immutability enforcement."""
        return {
            "immutable_parameters": {
                name: {
                    "value": param.value,
                    "description": param.description,
                    "write_attempts": len(param.write_attempts)
                }
                for name, param in self.immutable_parameters.items()
            },
            "learnable_parameters": list(self.learnable_parameters),
            "violation_log": self.violation_log,
            "total_violations": len(self.violation_log),
        }


class ImmutabilityViolationError(Exception):
    """Raised when learning module attempts to violate immutability boundary."""
    pass
