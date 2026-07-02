# Calibration Score Eval

Deterministic check of the confidence-calibration primitive (Brier / ECE / reliability).
Not a real-forecaster benchmark; it verifies the scorer labels calibrated /
overconfident / underconfident / insufficient correctly. It scores only; it does
NOT persist, surface, or bind (binding is owner-gated).

- scenarios: **5**
- verdict mismatches (failures): **0**

| scenario | category | expected | actual | n | brier | ece | weighted_gap |
|---|---|---|---|---:|---|---|---|
| perfectly_calibrated | baseline | calibrated | calibrated | 30 | 0.180 | 0.000 | 0.000 |
| systematic_overconfidence | kalshibench-shaped | overconfident | overconfident | 100 | 0.770 | 0.850 | 0.850 |
| systematic_underconfidence | boundary | underconfident | underconfident | 100 | 0.340 | 0.500 | -0.500 |
| canceling_miscalibration | ece-catches-what-net-bias-hides | miscalibrated | miscalibrated | 200 | 0.410 | 0.400 | 0.000 |
| insufficient_sample | small-sample-honesty | insufficient | insufficient | 3 | - | - | - |
