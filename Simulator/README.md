# Adaptive Hydraulic Leak Simulator

An extensible Python proof-of-concept for simulating transient pressure waves in pressurized pipes and studying leak diagnosis through a digital-twin control loop.

The project follows the hydraulic-network concept from the Conrad Challenge document:

```text
physical pipe → imperfect sensors → digital twin → residuals
             → fault hypotheses → optional pressure interrogation
```

The repository deliberately does **not** commit to one interrogation or inference method. Fourier/spectral analysis, deterministic inverse modeling, probabilistic inference, correlation methods, and later machine-learning methods can be implemented behind the same interfaces. The current code provides a physically motivated transient solver, configurable faults and sensors, plotting, and a baseline candidate-scoring interface for comparison experiments. The demo uses least-squares mismatch only as a transparent validation baseline; it does not select the final inference method.

## Quick start

```bash
python -m pip install -r requirements.txt
python examples/run_demo.py
```

The demo writes figures to `outputs/` and prints the inferred leak candidate. All experiment parameters are in `examples/run_demo.py`; there is no interactive input.

## Configuration

The simulator already reads pipe/material presets from JSON. The default industrial steel configuration is:

```text
configs/industrial_horizontal_steel.json
```

Additional starting presets are provided for vertical steel and horizontal PVC pipes. A future measurement package can write a JSON file containing measured lengths, elevations, diameters, wall thicknesses, material, sensor locations, and fault modules. The solver can then load that file without changing the physics code.

## Current physics

The transient model uses the one-dimensional water-hammer equations:

\[
\frac{\partial H}{\partial t} + \frac{a^2}{gA}\frac{\partial Q}{\partial x}=0,
\qquad
\frac{\partial Q}{\partial t}+gA\frac{\partial H}{\partial x}
 + \frac{f}{2DA}Q|Q|=0.
\]

The Method of Characteristics advances the pressure head \(H\) and flow \(Q\). The model includes:

- fluid and pipe-wall-dependent wave speed;
- Darcy–Weisbach friction;
- a controllable inlet pressure pulse;
- a controllable outlet demand/flow boundary;
- an orifice leak model;
- pressure sensors with noise and slowly varying bias;
- candidate leak scoring against simulated sensor traces.

This is a research simulator, not a safety-certified hydraulic design tool.

## Tracked observables

Every run can export a compressed `.npz` archive containing the full simulated state and derived quantities, including pressure head, total hydraulic head, pressure, flow, velocity, temporal and spatial derivatives, material acceleration, velocity head, total energy head, hydraulic power, dynamic pressure, wave impedance, wave-energy proxy, right- and left-traveling characteristic components, leak flow, leakage fraction, continuity and momentum-equation residuals, sensor predictions, sensor residuals, and residual z-scores. Some are directly measurable; others are theoretical state variables or model diagnostics that may be useful for calibration and future estimator design.

## Planned extensions

1. Graph-based junctions and branched networks.
2. Pump and valve component models.
3. Explicit reservoir, blockage, and sensor-failure hypotheses.
4. EKF/UKF, particle-filter, Fourier, and probabilistic inference modules.
5. Information-gain-based active test selection.
6. Experimental comparison against a physical tubing loop.

## Repository layout

```text
hydrosim/       reusable physics, sensors, inference, plotting, and configuration code
configs/        editable JSON pipe/material presets
examples/       source-controlled demonstrations
tests/          physics regression tests
outputs/        generated plots; ignored by Git except for a placeholder
```
