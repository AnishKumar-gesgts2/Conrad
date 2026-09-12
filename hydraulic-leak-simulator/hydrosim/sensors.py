from __future__ import annotations

import numpy as np


def add_sensor_effects(
    pressure_pa: np.ndarray,
    noise_std_pa: float,
    bias_random_walk_pa_per_sqrt_s: float,
    dt_s: float,
    seed: int = 7,
) -> np.ndarray:
    """Return pressure measurements with independent noise and drifting bias."""
    rng = np.random.default_rng(seed)
    steps, sensors = pressure_pa.shape
    bias = np.zeros((steps, sensors))
    increments = rng.normal(
        0.0,
        bias_random_walk_pa_per_sqrt_s * np.sqrt(dt_s),
        size=(steps - 1, sensors),
    )
    bias[1:] = np.cumsum(increments, axis=0)
    return pressure_pa + bias + rng.normal(0.0, noise_std_pa, size=pressure_pa.shape)
