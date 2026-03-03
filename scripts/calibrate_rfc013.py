"""RFC-013 calibration sweep for DynamicVarianceCompressor.

Generates a 240-row matrix:
5 work categories x 4 semantic zones x 4 lambda states x 3 trend states.

Output columns:
category, zone, lambda, trend, gamma_eff, compression_ratio
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.nonlinear_predictor import PredictionResult  # noqa: E402
from tonesoul.semantic_control import LambdaState, SemanticZone  # noqa: E402
from tonesoul.variance_compressor import DynamicVarianceCompressor  # noqa: E402
from tonesoul.work_classifier import WorkCategory  # noqa: E402

EXPECTED_ROWS = 5 * 4 * 4 * 3


@dataclass(frozen=True)
class MatrixRow:
    category: str
    zone: str
    lambda_state: str
    trend: str
    gamma_eff: float
    compression_ratio: float


def _prediction_for(trend: str) -> PredictionResult:
    return PredictionResult(
        predicted_delta_sigma=0.5,
        prediction_confidence=0.8,
        trend=trend,
        lyapunov_exponent=0.0,
        horizon_steps=3,
        acceleration=0.0,
        ewma=0.5,
    )


def _build_matrix(
    *,
    signal_variance: float,
    sigma_scale: float,
    trends: tuple[str, ...],
) -> list[MatrixRow]:
    compressor = DynamicVarianceCompressor(sigma_scale=sigma_scale)
    rows: list[MatrixRow] = []

    for category in WorkCategory:
        for zone in SemanticZone:
            for lambda_state in LambdaState:
                for trend in trends:
                    result = compressor.compress(
                        signal_variance=signal_variance,
                        prediction=_prediction_for(trend),
                        zone=zone,
                        lambda_state=lambda_state,
                        work_category=category,
                    )
                    rows.append(
                        MatrixRow(
                            category=category.value,
                            zone=zone.value,
                            lambda_state=lambda_state.value,
                            trend=trend,
                            gamma_eff=result.gamma_effective,
                            compression_ratio=result.compression_ratio,
                        )
                    )
    return rows


def _write_csv(path: Path, rows: list[MatrixRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["category", "zone", "lambda", "trend", "gamma_eff", "compression_ratio"])
        for row in rows:
            writer.writerow(
                [
                    row.category,
                    row.zone,
                    row.lambda_state,
                    row.trend,
                    f"{row.gamma_eff:.6f}",
                    f"{row.compression_ratio:.6f}",
                ]
            )


def _find_ratio(
    rows: list[MatrixRow],
    *,
    category: str,
    zone: str,
    lambda_state: str,
    trend: str,
) -> float:
    for row in rows:
        if (
            row.category == category
            and row.zone == zone
            and row.lambda_state == lambda_state
            and row.trend == trend
        ):
            return row.compression_ratio
    raise RuntimeError(
        f"missing matrix row for category={category}, zone={zone}, lambda={lambda_state}, trend={trend}"
    )


def _evaluate(
    rows: list[MatrixRow],
    *,
    min_ratio: float,
    max_ratio: float,
    freeform_min_target: float,
    severe_max_target: float,
) -> tuple[bool, list[str]]:
    issues: list[str] = []

    if len(rows) != EXPECTED_ROWS:
        issues.append(f"row_count={len(rows)} expected={EXPECTED_ROWS}")

    out_of_bounds = [row for row in rows if not (min_ratio <= row.compression_ratio <= max_ratio)]
    if out_of_bounds:
        issues.append(
            "ratio_out_of_bounds="
            f"{len(out_of_bounds)} (expected all within [{min_ratio:.2f}, {max_ratio:.2f}])"
        )

    freeform_baseline = _find_ratio(
        rows,
        category=WorkCategory.FREEFORM.value,
        zone=SemanticZone.SAFE.value,
        lambda_state=LambdaState.CONVERGENT.value,
        trend="stable",
    )
    if freeform_baseline < freeform_min_target:
        issues.append(
            "freeform_baseline_too_low="
            f"{freeform_baseline:.4f} < target {freeform_min_target:.2f}"
        )

    severe_case = _find_ratio(
        rows,
        category=WorkCategory.DEBUG.value,
        zone=SemanticZone.DANGER.value,
        lambda_state=LambdaState.CHAOTIC.value,
        trend="chaotic",
    )
    if severe_case > severe_max_target:
        issues.append("severe_case_too_high=" f"{severe_case:.4f} > target {severe_max_target:.2f}")

    return (len(issues) == 0), issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RFC-013 calibration sweep and emit CSV.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/status/rfc013_calibration.csv"),
        help="CSV output path.",
    )
    parser.add_argument(
        "--signal-variance",
        type=float,
        default=0.3,
        help="Signal variance used for every matrix entry.",
    )
    parser.add_argument(
        "--sigma-scale",
        type=float,
        default=1.0,
        help="DynamicVarianceCompressor sigma_scale (runtime default is 1.0).",
    )
    parser.add_argument(
        "--freeform-min-target",
        type=float,
        default=0.85,
        help="Validation target for freeform/safe/convergent/stable ratio.",
    )
    parser.add_argument(
        "--severe-max-target",
        type=float,
        default=0.35,
        help="Validation target for debug/danger/chaotic/chaotic ratio.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when validation targets are not met.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    trends = ("stable", "diverging", "chaotic")
    rows = _build_matrix(
        signal_variance=args.signal_variance,
        sigma_scale=args.sigma_scale,
        trends=trends,
    )
    _write_csv(args.output, rows)

    ok, issues = _evaluate(
        rows,
        min_ratio=0.35,
        max_ratio=1.0,
        freeform_min_target=args.freeform_min_target,
        severe_max_target=args.severe_max_target,
    )

    min_ratio = min(row.compression_ratio for row in rows)
    max_ratio = max(row.compression_ratio for row in rows)
    print(f"wrote: {args.output.as_posix()}")
    print(f"rows: {len(rows)} (expected {EXPECTED_ROWS})")
    print(f"ratio_range: min={min_ratio:.4f} max={max_ratio:.4f}")
    print(f"targets_ok: {ok}")
    if issues:
        print("issues:")
        for item in issues:
            print(f"- {item}")

    if args.strict and not ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
