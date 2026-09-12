from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .physics import SimulationResult


def plot_result(result: SimulationResult, measured_pressure_pa: np.ndarray, output_dir: str | Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(3, 1, figsize=(10, 11), constrained_layout=True)
    axes[0].plot(result.time_s, result.head_m[:, 0], label="inlet")
    axes[0].plot(result.time_s, result.head_m[:, result.head_m.shape[1] // 2], label="middle")
    axes[0].plot(result.time_s, result.head_m[:, -1], label="outlet")
    axes[0].set_ylabel("Hydraulic head [m]")
    axes[0].set_title("Transient pressure-wave response")
    axes[0].legend()
    for i in range(result.sensor_pressure_pa.shape[1]):
        axes[1].plot(result.time_s, result.sensor_pressure_pa[:, i] / 1000.0, label=f"sensor {i + 1} truth")
        axes[1].plot(result.time_s, measured_pressure_pa[:, i] / 1000.0, alpha=0.45, label=f"sensor {i + 1} measured")
    axes[1].set_ylabel("Pressure [kPa]")
    axes[1].set_title("Sensor truth and noisy measurements")
    axes[1].legend(ncol=2)
    axes[2].plot(result.position_m, result.head_m[0], label="initial")
    axes[2].plot(result.position_m, result.head_m[len(result.time_s) // 2], label="middle of run")
    axes[2].plot(result.position_m, result.head_m[-1], label="final")
    axes[2].set_xlabel("Distance along pipe [m]")
    axes[2].set_ylabel("Hydraulic head [m]")
    axes[2].set_title(f"Spatial state; estimated wave speed = {result.wave_speed_m_s:.1f} m/s")
    axes[2].legend()
    fig.savefig(output_dir / "transient_response.png", dpi=160)
    plt.close(fig)
