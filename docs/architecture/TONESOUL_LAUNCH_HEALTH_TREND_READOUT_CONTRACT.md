# ToneSoul Launch Health Trend Readout Contract

> Purpose: define how ToneSoul should separate present-tense launch posture from future trend or forecast surfaces.
> Last Updated: 2026-04-06
> Authority: bounded readout contract. Does not create predictive numbers or override current launch truth.

---

## Why This Exists

ToneSoul already exposes:

- `launch_claim_posture`
- `coordination_mode`
- `evidence_readout_posture`

What readers still overdo is:

- treating current tier as if it were a forecast
- treating one validation snapshot as if it were a trend
- treating descriptive confidence as if it were predictive operations truth

This contract exists to keep those layers separate.

## Compressed Thesis

Launch health should be split into:

- `descriptive_only`
- `trendable`
- `forecast_later`

ToneSoul today should expose only the first two honestly, and keep the third non-numeric.

## Current Metric Classes

### Descriptive Only

Examples:

- `current_launch_tier`
- `public_launch_ready_flag`

Meaning:

- present-tense posture only
- not a success probability
- not a trend line

### Trendable

Examples:

- `coordination_backend_alignment`
- `collaborator_beta_validation_health`

Meaning:

- worth tracking across time later
- still only a bounded snapshot today
- should not be restated as forecast confidence

### Forecast Later

Examples:

- `public_launch_forecast`

Meaning:

- a future possible surface
- not yet numeric
- blocked until trendable inputs are collected over time and calibrated separately from current descriptive confidence

## Receiver Rule

Use launch-health readouts as:

- current honesty posture
- future trend-lane preparation

Do not use them as:

- a substitute for current launch claim posture
- a replacement for readiness
- a predictive probability layer

## Non-Goals

This contract is not:

- a TimesFM integration
- a public-launch forecast
- a new council confidence system

It is only the boundary that keeps those things from collapsing together.
