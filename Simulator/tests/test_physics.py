from pathlib import Path

import numpy as np

from hydrosim.config import load_config
from hydrosim.physics import PipeModel
from hydrosim.observables import compute_observables


def test_wave_speed_is_physically_reasonable():
    config = load_config(Path(__file__).parents[1] / "configs" / "industrial_horizontal_steel.json")
    model = PipeModel(config)
    assert 100.0 < model.wave_speed_m_s < 1500.0


def test_leak_removes_flow():
    config = load_config(Path(__file__).parents[1] / "configs" / "industrial_horizontal_steel.json")
    model = PipeModel(config)
    result = model.run(0.05, leak_enabled=True)
    assert np.max(result.leak_flow_m3_s) > 0.0


def test_no_leak_has_zero_leak_flow():
    config = load_config(Path(__file__).parents[1] / "configs" / "industrial_horizontal_steel.json")
    model = PipeModel(config)
    result = model.run(0.05, leak_enabled=False)
    assert np.all(result.leak_flow_m3_s == 0.0)


def test_observables_cover_full_state():
    config = load_config(Path(__file__).parents[1] / "configs" / "industrial_horizontal_steel.json")
    model = PipeModel(config)
    result = model.run(0.02)
    values = compute_observables(result, model)
    for key in ["pressure_pa", "flow_m3_s", "velocity_m_s", "material_acceleration_m_s2", "wave_impedance_pa_s_m3", "continuity_equation_residual"]:
        assert key in values
    assert values["pressure_pa"].shape == result.head_m.shape
