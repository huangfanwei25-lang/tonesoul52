from typing import Dict, List, Sequence, Tuple

import numpy as np

from .schema import Node


def compute_pca_positions(
    nodes: Sequence[Node],
) -> Tuple[List[Tuple[float, float]], Dict[str, object]]:
    if not nodes:
        return [], {
            "mean": [],
            "components": [],
            "explained_variance": [],
            "explained_variance_ratio": [],
        }

    matrix = np.array([node.what.v_sem for node in nodes], dtype=float)
    mean = matrix.mean(axis=0)
    centered = matrix - mean

    if centered.size == 0:
        return [], {
            "mean": [],
            "components": [],
            "explained_variance": [],
            "explained_variance_ratio": [],
        }

    _, s, vt = np.linalg.svd(centered, full_matrices=False)
    components = vt[:2]
    if components.shape[0] < 2:
        padding = np.zeros((2 - components.shape[0], components.shape[1]))
        components = np.vstack([components, padding])

    projected = centered @ components.T
    points = [(float(point[0]), float(point[1])) for point in projected]

    denom = max(len(nodes) - 1, 1)
    variance = (s**2) / denom
    if variance.shape[0] < 2:
        variance = np.pad(variance, (0, 2 - variance.shape[0]))
    total = float(np.sum(variance)) if float(np.sum(variance)) > 0 else 1.0
    ratio = (variance / total).tolist()

    metadata = {
        "mean": mean.tolist(),
        "components": components.tolist(),
        "explained_variance": variance[:2].tolist(),
        "explained_variance_ratio": ratio[:2],
        "note": "P2 projection is observational; do not write back to governance.",
    }
    return points, metadata
