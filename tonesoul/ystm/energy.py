from dataclasses import dataclass, replace
from typing import List, Sequence

from .schema import Node


@dataclass(frozen=True)
class EnergyConfig:
    alpha: float = 1.0
    beta: float = 0.0
    gamma: float = 0.0
    normalize: bool = True


def compute_raw_total(e_energy: float, e_srsp: float, e_risk: float, config: EnergyConfig) -> float:
    return (config.alpha * e_energy) + (config.beta * e_srsp) + (config.gamma * e_risk)


def normalize_totals(raw_totals: Sequence[float], config: EnergyConfig) -> List[float]:
    if not config.normalize:
        return list(raw_totals)
    max_val = max(raw_totals) if raw_totals else 0.0
    if max_val <= 0:
        return [0.0 for _ in raw_totals]
    return [value / max_val for value in raw_totals]


def apply_energy_totals(nodes: Sequence[Node], config: EnergyConfig) -> List[Node]:
    raw_totals = []
    for node in nodes:
        e_energy = node.scalar.E_energy or 0.0
        e_srsp = node.scalar.E_srsp or 0.0
        e_risk = node.scalar.E_risk or 0.0
        raw_totals.append(compute_raw_total(e_energy, e_srsp, e_risk, config))
    totals = normalize_totals(raw_totals, config)
    updated_nodes = []
    for node, total in zip(nodes, totals):
        new_scalar = replace(node.scalar, E_total=total)
        updated_nodes.append(replace(node, scalar=new_scalar))
    return updated_nodes
