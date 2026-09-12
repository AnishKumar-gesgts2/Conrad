from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .config import SimulationConfig


@dataclass
class SimulationResult:
    time_s: np.ndarray
    position_m: np.ndarray
    head_m: np.ndarray
    flow_m3_s: np.ndarray
    sensor_pressure_pa: np.ndarray
    leak_flow_m3_s: np.ndarray
    wave_speed_m_s: float


class PipeModel:
    """One-dimensional Method-of-Characteristics water-hammer model.

    This is intentionally a transparent proof-of-concept. It models one pipe
    with a fixed-head inlet, a prescribed-flow outlet, and one optional leak.
    Network junctions are planned as a separate layer.
    """

    def __init__(self, config: SimulationConfig):
        self.config = config
        p = config.pipe
        f = config.fluid
        self.area_m2 = np.pi * p.diameter_m**2 / 4.0
        wall_factor = 1.0 + f.bulk_modulus_pa * p.diameter_m / (p.youngs_modulus_pa * p.wall_thickness_m)
        self.wave_speed_m_s = np.sqrt((f.bulk_modulus_pa / f.density_kg_m3) / wall_factor)
        self.position_m = np.linspace(0.0, p.length_m, p.grid_cells)
        self.elevation_m = np.linspace(p.elevation_start_m, p.elevation_end_m, p.grid_cells)
        self.dx_m = self.position_m[1] - self.position_m[0]
        self.dt_s = 0.90 * self.dx_m / self.wave_speed_m_s
        self.B = self.wave_speed_m_s / (9.80665 * self.area_m2)
        self.friction_R = p.darcy_friction_factor * self.dx_m / (2.0 * 9.80665 * p.diameter_m * self.area_m2**2)

    def leak_flow(self, head_m: float) -> float:
        fault = self.config.fault
        leak_index = int(np.argmin(np.abs(self.position_m - fault.leak_location_m)))
        pressure_head = max(head_m - self.elevation_m[leak_index] - fault.outside_head_m, 0.0)
        return fault.discharge_coefficient * fault.leak_area_m2 * np.sqrt(2.0 * 9.80665 * pressure_head)

    def run(
        self,
        duration_s: float,
        pulse: Callable[[float], float] | None = None,
        leak_enabled: bool = True,
        outlet_flow: Callable[[float], float] | None = None,
    ) -> SimulationResult:
        n_steps = int(np.ceil(duration_s / self.dt_s)) + 1
        n = self.config.pipe.grid_cells
        times = np.arange(n_steps) * self.dt_s
        heads = np.empty((n_steps, n))
        flows = np.empty((n_steps, n))
        leak_flows = np.zeros(n_steps)
        # H is total hydraulic head. The configured reference head is the
        # inlet pressure head, so initial total head includes elevation.
        h0 = self.config.operating.reference_head_m + self.elevation_m[0]
        q0 = self.config.operating.outlet_flow_m3_s
        H = np.full(n, h0, dtype=float)
        Q = np.full(n, q0, dtype=float)
        leak_index = int(np.argmin(np.abs(self.position_m - self.config.fault.leak_location_m)))

        for k, t in enumerate(times):
            heads[k] = H
            flows[k] = Q
            leak_flows[k] = self.leak_flow(H[leak_index]) if leak_enabled else 0.0
            if k == n_steps - 1:
                break

            Cp = H[:-2] + self.B * Q[:-2] - self.friction_R * Q[:-2] * np.abs(Q[:-2])
            Cm = H[2:] - self.B * Q[2:] + self.friction_R * Q[2:] * np.abs(Q[2:])
            H_new = H.copy()
            Q_new = Q.copy()
            H_new[1:-1] = 0.5 * (Cp + Cm)
            Q_new[1:-1] = (Cp - Cm) / (2.0 * self.B)

            if leak_enabled:
                q_leak = self.leak_flow(H_new[leak_index])
                H_new[leak_index] -= (self.wave_speed_m_s**2 * self.dt_s / (9.80665 * self.area_m2 * self.dx_m)) * q_leak

            inlet_head = h0 + (pulse(t) if pulse else 0.0)
            incoming_minus = H[1] - self.B * Q[1] + self.friction_R * Q[1] * abs(Q[1])
            H_new[0] = inlet_head
            Q_new[0] = (H_new[0] - incoming_minus) / self.B

            q_out = outlet_flow(t) if outlet_flow else q0
            outgoing_plus = H[-2] + self.B * Q[-2] - self.friction_R * Q[-2] * abs(Q[-2])
            Q_new[-1] = q_out
            H_new[-1] = outgoing_plus - self.B * q_out
            H, Q = H_new, Q_new

        sensor_indices = [int(np.argmin(np.abs(self.position_m - x))) for x in self.config.sensors.pressure_locations_m]
        pressure = self.config.fluid.density_kg_m3 * 9.80665 * (
            heads[:, sensor_indices] - self.elevation_m[sensor_indices]
        )
        return SimulationResult(times, self.position_m, heads, flows, pressure, leak_flows, self.wave_speed_m_s)
