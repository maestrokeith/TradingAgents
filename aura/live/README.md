# Human-confirmed live execution boundary

This package provides the final application boundary between AURA's validated
trade intent and a broker adapter.

## Safety invariant

**The model cannot submit a live order.** TradingAgents/AURA produces an
`LiveOrderIntent`. The application presents that intent to an authenticated
human operator. Only a matching `Confirmation` can authorize the injected
broker adapter.

The gateway is fail-closed when `enabled=False`.

## Required production controls

Before enabling a real broker adapter, the application owner must add:

- secret storage outside source control;
- broker-specific authentication and account/environment separation;
- idempotency and duplicate-order protection;
- server-side position reconciliation;
- market-hours and instrument validation;
- price/slippage bounds;
- order/partial-fill/cancel state machines;
- durable audit logging;
- operator authentication and authorization;
- independent kill switch;
- daily loss and exposure limits;
- monitoring and alerting;
- integration tests against the broker's official sandbox;
- explicit production configuration review.

No credentials are included in this repository and no concrete broker is
selected by this package.
