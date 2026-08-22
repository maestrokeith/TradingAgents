"""Fail-closed gateway for human-confirmed live execution.

The gateway contains no broker implementation. A broker adapter must be
injected and receives an order only after all local checks and explicit human
confirmation have succeeded.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .models import Confirmation, ExecutionResult, LiveOrderIntent


class BrokerAdapter:
    """Minimal protocol-like base for an application-specific broker adapter."""

    def submit(self, intent: LiveOrderIntent) -> str:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class HumanConfirmedGateway:
    broker: BrokerAdapter
    max_risk_amount: Decimal
    enabled: bool = False

    def prepare(self, intent: LiveOrderIntent) -> dict[str, str]:
        """Create a human-readable confirmation challenge; never submits."""
        if not self.enabled:
            raise RuntimeError("live execution is disabled")
        if intent.risk_amount > self.max_risk_amount:
            raise ValueError("intent exceeds gateway risk limit")
        return {
            "intent_id": intent.intent_id,
            "symbol": intent.symbol,
            "side": intent.side.value,
            "quantity": str(intent.quantity),
            "risk_amount": str(intent.risk_amount),
            "confirmation_required": "true",
        }

    def execute(self, intent: LiveOrderIntent, confirmation: Confirmation) -> ExecutionResult:
        """Submit only when the confirmation exactly matches the intent."""
        if not self.enabled:
            return ExecutionResult(intent.intent_id, False, None, "DISABLED", "live execution disabled")
        if confirmation.intent_id != intent.intent_id:
            return ExecutionResult(intent.intent_id, False, None, "REJECTED", "confirmation does not match intent")
        if not confirmation.confirmation_code.strip():
            return ExecutionResult(intent.intent_id, False, None, "REJECTED", "confirmation code required")
        if not confirmation.confirmed_by.strip():
            return ExecutionResult(intent.intent_id, False, None, "REJECTED", "confirming identity required")
        if intent.risk_amount > self.max_risk_amount:
            return ExecutionResult(intent.intent_id, False, None, "REJECTED", "risk limit exceeded")

        broker_order_id = self.broker.submit(intent)
        return ExecutionResult(intent.intent_id, True, broker_order_id, "SUBMITTED", "human confirmation accepted")
