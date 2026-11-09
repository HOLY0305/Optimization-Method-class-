"""Shared exact-capacity Lloyd routines used by the manuscript experiments."""

from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import norm


K = 3
MAX_ITERATIONS = 100


def population_shape() -> np.ndarray:
    """Return the equal-third Gaussian population fixed shape, centered."""
    q = norm.ppf(2.0 / 3.0)
    outer_centroid = 3.0 * norm.pdf(q)
    return np.array([[-outer_centroid, 0.0], [0.0, 0.0], [outer_centroid, 0.0]])


def balanced_assignment(data: np.ndarray, centers: np.ndarray) -> np.ndarray:
    """Solve the exact equal-capacity assignment by duplicating center slots."""
    n = data.shape[0]
    capacity = n // K
    slot_labels = np.repeat(np.arange(K), capacity)
    slots = centers[slot_labels]
    cost = np.sum((data[:, None, :] - slots[None, :, :]) ** 2, axis=2)
    rows, columns = linear_sum_assignment(cost)
    labels = np.empty(n, dtype=np.int64)
    labels[rows] = slot_labels[columns]
    return labels


def lloyd(
    data: np.ndarray,
    initial_centers: np.ndarray,
    trace: list[np.ndarray] | None = None,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Run exact balanced assignment and centroid updates to a fixed partition."""
    centers = np.asarray(initial_centers, dtype=float).copy()
    previous_labels: np.ndarray | None = None
    for iteration in range(1, MAX_ITERATIONS + 1):
        labels = balanced_assignment(data, centers)
        updated = np.vstack([data[labels == j].mean(axis=0) for j in range(K)])
        if trace is not None:
            trace.append(updated.copy())
        if previous_labels is not None and np.array_equal(labels, previous_labels):
            return updated, labels, iteration
        previous_labels = labels
        centers = updated
    raise RuntimeError(f"Balanced Lloyd did not stabilize within {MAX_ITERATIONS} iterations")


def normalized_center_shape(centers: np.ndarray) -> np.ndarray:
    centered = centers - centers.mean(axis=0, keepdims=True)
    return centered / np.linalg.norm(centered)


def generate_data(n: int, tau: float, rng: np.random.Generator) -> np.ndarray:
    data = rng.normal(size=(n, 2))
    data[:, 1] *= np.sqrt(tau)
    return data - data.mean(axis=0, keepdims=True)
