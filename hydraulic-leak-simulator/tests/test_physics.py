from pathlib import Path

import numpy as np

from hydrosim.config import load_config
from hydrosim.physics import PipeModel


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
