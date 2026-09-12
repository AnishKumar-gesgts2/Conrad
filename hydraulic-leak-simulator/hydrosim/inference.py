from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from .physics import PipeModel


InferenceMethod = Literal["least_squares", "cross_correlation", "probabilistic"]


@dataclass(frozen=True)
class LeakCandidate:
    location_m: float
    area_m2: float
    score: float


def score_leak_candidates(
    model_factory,
    measured_pressure_pa: np.ndarray,
    duration_s: float,
    candidate_locations_m: np.ndarray,
    candidate_areas_m2: np.ndarray,
    pulse=None,
    method: InferenceMethod = "least_squares",
) -> list[LeakCandidate]:
    """Score candidate faults while keeping the inference method replaceable.

    The current baseline is least-squares trace mismatch. The method argument
    deliberately exposes alternatives rather than declaring one method to be
    the final approach for the project.
    """
    if method not in {"least_squares", "cross_correlation", "probabilistic"}:
        raise ValueError(f"Unknown inference method: {method}")
    results = []
    for location in candidate_locations_m:
        for area in candidate_areas_m2:
            model: PipeModel = model_factory(float(location), float(area))
            prediction = model.run(duration_s, pulse=pulse).sensor_pressure_pa
            if method == "least_squares":
                score = float(np.mean((prediction - measured_pressure_pa) ** 2))
            elif method == "cross_correlation":
                centered_a = prediction - prediction.mean(axis=0)
                centered_b = measured_pressure_pa - measured_pressure_pa.mean(axis=0)
                corr = np.sum(centered_a * centered_b) / (np.linalg.norm(centered_a) * np.linalg.norm(centered_b) + 1e-12)
                score = float(-corr)
            else:
                residual = prediction - measured_pressure_pa
                score = float(0.5 * np.mean(residual**2))
            results.append(LeakCandidate(float(location), float(area), score))
    return sorted(results, key=lambda candidate: candidate.score)
