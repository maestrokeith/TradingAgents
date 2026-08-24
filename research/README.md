# AURA-GOLD Research Layer

Research-only integration for studying XAUUSD observations from TradingView.

## Components

- `aura_gold_research.pine` — Pine Script v6 indicator that evaluates higher-timeframe context, EMA structure, RSI, liquidity sweeps, displacement, session context, and a configurable research score.
- `webhook/app.py` — FastAPI receiver that validates an optional shared secret and stores TradingView observations in SQLite.
- `webhook/requirements.txt` — minimal gateway dependencies.

## Safety boundary

This layer is intentionally research-only. It does not contain broker credentials, order-placement code, execution APIs, position sizing, or live-money execution logic. Webhook payloads are persisted as observations for later analysis.

## TradingView setup

1. Open the Pine Editor and paste `aura_gold_research.pine`.
2. Add the indicator to an XAUUSD chart.
3. Create a TradingView alert using `Any alert() function call`.
4. Point the webhook URL at the deployed `/webhook` endpoint.
5. Configure the same value in `AURA_RESEARCH_WEBHOOK_SECRET` and send it as `X-Aura-Secret` if your webhook relay supports custom headers.

TradingView creates and runs alerts from the chart UI; Pine code defines the alert events but does not itself create a running alert. See the official TradingView alert documentation for current alert behavior.

## Local gateway

```bash
cd research/webhook
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export AURA_RESEARCH_WEBHOOK_SECRET='change-me'
uvicorn app:app --host 0.0.0.0 --port 8000
```

Health check: `GET /health`

Recent observations: `GET /observations?limit=100`

## Next research phase

Use the stored observations to evaluate signal frequency, regime stability, false-positive rate, session effects, and out-of-sample performance. Do not treat the score as a guarantee or as a substitute for independent validation.
