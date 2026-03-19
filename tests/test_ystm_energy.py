from __future__ import annotations

from dataclasses import replace

import pytest

from tonesoul.ystm.energy import (
    EnergyConfig,
    apply_energy_totals,
    compute_raw_total,
    normalize_totals,
)
from tonesoul.ystm.representation import EmbeddingConfig, build_nodes


def test_compute_raw_total_combines_weighted_components() -> None:
    config = EnergyConfig(alpha=1.0, beta=2.0, gamma=3.0, normalize=False)

    assert compute_raw_total(1.0, 2.0, 3.0, config) == 14.0


def test_normalize_totals_supports_passthrough_scaling_zero_floor_and_empty() -> None:
    assert normalize_totals([1.0, 2.0], EnergyConfig(normalize=False)) == [1.0, 2.0]
    assert normalize_totals([2.0, 1.0], EnergyConfig(normalize=True)) == [1.0, 0.5]
    assert normalize_totals([0.0, -1.0], EnergyConfig(normalize=True)) == [0.0, 0.0]
    assert normalize_totals([], EnergyConfig(normalize=True)) == []


def test_apply_energy_totals_treats_none_components_as_zero() -> None:
    nodes = build_nodes(
        [
            {"text": "alpha", "mode": "analysis", "domain": "governance"},
            {"text": "beta", "mode": "risk", "domain": "safety"},
        ],
        config=EmbeddingConfig(dims=4),
    )
    nodes[0] = replace(
        nodes[0],
        scalar=replace(nodes[0].scalar, E_energy=None, E_srsp=None, E_risk=None, E_total=0.0),
    )
    nodes[1] = replace(
        nodes[1],
        scalar=replace(nodes[1].scalar, E_energy=2.0, E_srsp=1.0, E_risk=0.5, E_total=0.0),
    )

    updated = apply_energy_totals(nodes, EnergyConfig(alpha=2.0, beta=1.0, gamma=1.0))

    assert nodes[0].scalar.E_total == 0.0
    assert nodes[1].scalar.E_total == 0.0
    assert updated[0].scalar.E_total == 0.0
    assert updated[1].scalar.E_total == pytest.approx(1.0)
