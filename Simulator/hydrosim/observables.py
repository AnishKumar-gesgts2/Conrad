"""Derived state and diagnostic quantities from a transient simulation."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .physics import PipeModel, SimulationResult


def compute_observables(
    result: SimulationResult,
    model: PipeModel,
    measured_sensor_pressure_pa: np.ndarray | None = None,
) -> dict[str, np.ndarray | float]:
    """Compute theoretical, sensor-level, and numerical-quality observables."""
    rho = model.config.fluid.density_kg_m3
    g = 9.80665
    A = model.area_m2
    D = model.config.pipe.diameter_m
    f = model.config.pipe.darcy_friction_factor
    H = result.head_m
    Q = result.flow_m3_s
    z = result.elevation_m[None, :]
    pressure_head = H - z
    pressure_pa = rho * g * pressure_head
    velocity = Q / A
    dt = result.time_s[1] - result.time_s[0]
    dx = result.position_m[1] - result.position_m[0]

    dH_dt = np.gradient(H, dt, axis=0)
    dQ_dt = np.gradient(Q, dt, axis=0)
    dH_dx = np.gradient(H, dx, axis=1)
    dQ_dx = np.gradient(Q, dx, axis=1)
    dV_dt = np.gradient(velocity, dt, axis=0)
    dV_dx = np.gradient(velocity, dx, axis=1)
    B = model.B

    inlet_flow = Q[:, 0]
    leakage_fraction = result.leak_flow_m3_s / np.maximum(np.abs(inlet_flow), 1e-12)
    residual_continuity = dH_dt + (result.wave_speed_m_s**2 / (g * A)) * dQ_dx
    residual_momentum = dQ_dt + g * A * dH_dx + f / (2 * D * A) * Q * np.abs(Q)

    values: dict[str, np.ndarray | float] = {
        "time_s": result.time_s,
        "position_m": result.position_m,
        "elevation_m": result.elevation_m,
        "hydraulic_head_m": H,
        "pressure_head_m": pressure_head,
        "pressure_pa": pressure_pa,
        "flow_m3_s": Q,
        "velocity_m_s": velocity,
        "head_time_derivative_m_s": dH_dt,
        "flow_time_derivative_m3_s2": dQ_dt,
        "head_space_derivative": dH_dx,
        "flow_space_derivative_m2_s": dQ_dx,
        "velocity_time_derivative_m_s2": dV_dt,
        "velocity_space_derivative_s1": dV_dx,
        "material_acceleration_m_s2": dV_dt + velocity * dV_dx,
        "velocity_head_m": velocity**2 / (2 * g),
        "total_energy_head_m": H + velocity**2 / (2 * g),
        "hydraulic_power_w": rho * g * Q * H,
        "dynamic_pressure_pa": 0.5 * rho * velocity**2,
        "wave_impedance_pa_s_m3": rho * result.wave_speed_m_s / A,
        "wave_head_deviation_m": H - H[0:1, :],
        "wave_energy_proxy_head2": 0.5 * (H - H[0:1, :]) ** 2 + 0.5 * (B * Q) ** 2,
        "characteristic_plus_head_m": H + B * Q,
        "characteristic_minus_head_m": H - B * Q,
        "leak_flow_m3_s": result.leak_flow_m3_s,
        "leakage_fraction": leakage_fraction,
        "continuity_equation_residual": residual_continuity,
        "momentum_equation_residual": residual_momentum,
        "wave_speed_m_s": float(result.wave_speed_m_s),
        "pipe_area_m2": float(A),
        "pipe_volume_m3": float(A * model.config.pipe.length_m),
    }

    if measured_sensor_pressure_pa is not None:
        residual = measured_sensor_pressure_pa - result.sensor_pressure_pa
        sigma = model.config.sensors.pressure_noise_pa
        values["sensor_predicted_pressure_pa"] = result.sensor_pressure_pa
        values["sensor_measured_pressure_pa"] = measured_sensor_pressure_pa
        values["sensor_residual_pa"] = residual
        values["sensor_residual_zscore"] = residual / max(sigma, 1e-12)
        values["sensor_residual_rms_pa"] = np.sqrt(np.mean(residual**2, axis=0))

    return values


def save_observables_npz(observables: dict[str, np.ndarray | float], path: str | Path) -> None:
    np.savez_compressed(path, **observables)


def observable_catalog() -> list[str]:
    return [
        "hydraulic_head_m", "pressure_head_m", "pressure_pa", "flow_m3_s", "velocity_m_s",
        "head_time_derivative_m_s", "flow_time_derivative_m3_s2", "head_space_derivative",
        "flow_space_derivative_m2_s", "velocity_time_derivative_m_s2", "velocity_space_derivative_s1",
        "material_acceleration_m_s2", "velocity_head_m", "total_energy_head_m", "hydraulic_power_w",
        "dynamic_pressure_pa", "wave_impedance_pa_s_m3", "wave_head_deviation_m", "wave_energy_proxy_head2",
        "characteristic_plus_head_m", "characteristic_minus_head_m", "leak_flow_m3_s", "leakage_fraction",
        "continuity_equation_residual", "momentum_equation_residual", "sensor_predicted_pressure_pa",
        "sensor_measured_pressure_pa", "sensor_residual_pa", "sensor_residual_zscore",
    ]
