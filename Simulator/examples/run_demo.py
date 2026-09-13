from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hydrosim.config import load_config
from hydrosim.inference import score_leak_candidates
from hydrosim.observables import compute_observables, save_observables_npz
from hydrosim.physics import PipeModel
from hydrosim.plotting import plot_result
from hydrosim.sensors import add_sensor_effects


# All experiment parameters are intentionally source-controlled here.
CONFIG_PATH = ROOT / "configs" / "industrial_horizontal_steel.json"
OUTPUT_DIR = ROOT / "outputs"
DURATION_S = 0.20
PULSE_AMPLITUDE_HEAD_M = 0.50
PULSE_CENTER_S = 0.018
PULSE_WIDTH_S = 0.002
RANDOM_SEED = 7


def pressure_pulse(t: float) -> float:
    return PULSE_AMPLITUDE_HEAD_M * np.exp(-0.5 * ((t - PULSE_CENTER_S) / PULSE_WIDTH_S) ** 2)


def main() -> None:
    config = load_config(CONFIG_PATH)
    truth_model = PipeModel(config)
    truth = truth_model.run(DURATION_S, pulse=pressure_pulse, leak_enabled=True)
    measured = add_sensor_effects(
        truth.sensor_pressure_pa,
        config.sensors.pressure_noise_pa,
        config.sensors.bias_random_walk_pa_per_sqrt_s,
        truth_model.dt_s,
        RANDOM_SEED,
    )
    observables = compute_observables(truth, truth_model, measured)
    save_observables_npz(observables, OUTPUT_DIR / "simulation_observables.npz")

    def candidate_model(location_m: float, area_m2: float) -> PipeModel:
        candidate_config = config.__class__(
            name=config.name,
            fluid=config.fluid,
            pipe=config.pipe,
            operating=config.operating,
            sensors=config.sensors,
            fault=config.fault.__class__(location_m, area_m2, config.fault.discharge_coefficient, config.fault.outside_head_m),
        )
        return PipeModel(candidate_config)

    locations = np.linspace(4.0, 26.0, 12)
    areas = np.array([0.5e-5, 1.0e-5, 1.5e-5, 2.0e-5])
    # Transparent baseline for validating the simulator, not a final choice
    # between least-squares, Fourier, or probabilistic inference.
    candidates = score_leak_candidates(
        candidate_model,
        measured,
        DURATION_S,
        locations,
        areas,
        pulse=pressure_pulse,
        method="least_squares",
    )
    best = candidates[0]
    print(f"Wave speed: {truth.wave_speed_m_s:.2f} m/s")
    print(f"True leak: location={config.fault.leak_location_m:.2f} m, area={config.fault.leak_area_m2:.3e} m^2")
    print(f"Best baseline candidate: location={best.location_m:.2f} m, area={best.area_m2:.3e} m^2")
    plot_result(truth, measured, OUTPUT_DIR)
    print(f"Plot written to {OUTPUT_DIR / 'transient_response.png'}")
    print(f"Saved {len(observables)} theoretical and sensor observables to simulation_observables.npz")


if __name__ == "__main__":
    main()
