from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FluidConfig:
    density_kg_m3: float
    bulk_modulus_pa: float
    dynamic_viscosity_pa_s: float


@dataclass(frozen=True)
class PipeConfig:
    length_m: float
    diameter_m: float
    wall_thickness_m: float
    youngs_modulus_pa: float
    poissons_ratio: float
    elevation_start_m: float
    elevation_end_m: float
    darcy_friction_factor: float
    grid_cells: int


@dataclass(frozen=True)
class OperatingConfig:
    reference_head_m: float
    outlet_flow_m3_s: float


@dataclass(frozen=True)
class SensorConfig:
    pressure_locations_m: list[float]
    pressure_noise_pa: float
    bias_random_walk_pa_per_sqrt_s: float


@dataclass(frozen=True)
class FaultConfig:
    leak_location_m: float
    leak_area_m2: float
    discharge_coefficient: float
    outside_head_m: float


@dataclass(frozen=True)
class SimulationConfig:
    name: str
    fluid: FluidConfig
    pipe: PipeConfig
    operating: OperatingConfig
    sensors: SensorConfig
    fault: FaultConfig


def load_config(path: str | Path) -> SimulationConfig:
    data = json.loads(Path(path).read_text())
    return SimulationConfig(
        name=data["name"],
        fluid=FluidConfig(**data["fluid"]),
        pipe=PipeConfig(**data["pipe"]),
        operating=OperatingConfig(**data["operating"]),
        sensors=SensorConfig(**data["sensors"]),
        fault=FaultConfig(**data["fault"]),
    )
