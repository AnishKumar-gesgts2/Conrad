# Product Description and Project Plan
## Adaptive pressure-wave leak detection for water pipes

### Simple summary

**What we are building.** A system that helps an operator find a leak in a water pipe without opening the pipe along its entire length. A small set of pressure sensors records how water pressure changes. Software compares those recordings with a computer model of the pipe to identify whether a leak is likely and where it might be. When ordinary measurements are unclear, the proposed system can choose a controlled pressure change and examine the resulting echoes.

**Our goal.** Deliver a working, repeatable laboratory prototype for the Conrad Challenge: a physical pipe setup, synchronized sensors, a calibrated simulator, and software that reports a leak decision, an estimated location, and how certain or uncertain that estimate is. The initial product covers one pressurized pipe with one possible leak. A city-wide water network is a later goal.

**Why this approach could be different.** Pressure waves and computer models have already been used to find leaks. Our proposed distinction is the combination of an affordable sensor setup, a model calibrated to the actual pipe, and an adaptive test: the software chooses a useful follow-up pressure change when several explanations fit the measurements. We will test whether this combination improves accuracy or reduces the number of tests compared with a fixed pressure pulse and simpler detection methods. This is a proposed advantage, not yet a proven invention or a demonstrated cost saving.

**How we plan to achieve it.** First verify the simulator, then build and measure a small pipe setup. Fit the model using healthy-pipe data, collect controlled leak and non-leak trials, and compare several detection methods on recordings they have not seen before. Finally, add a small library of permitted pressure tests and a rule for selecting the most useful next test.

**What is missing today.** We have simulation code, synthetic sensor measurements, plots, and a basic comparison of possible leaks. We still need verified numerical physics, real sensor acquisition, a physical prototype, calibration, a reliable no-leak decision, meaningful uncertainty estimates, adaptive test selection, and independent experimental results. Our current software is a research starting point; it is not a finished leak detector.

**Competition target.** The prototype evidence and submission materials must be ready before the **2026–2027 Conrad Challenge Innovation Stage submission deadline: January 7, 2027**. The official submission includes an Innovation Brief, a 3–5 minute Innovation Video, and a website. This deadline is our planning constraint; the laboratory acceptance targets below are our team's proposed goals, not Conrad requirements. See [the official Innovation Stage page](https://conrad.spacecenter.org/the-challenge/innovation-stage/).

## 1. Product and intended users

The first intended users are maintenance teams responsible for accessible, pressurized water-pipe sections in buildings, campuses, or small facilities. We need to interview these users before choosing a first commercial market.

The proposed package contains:

- A few pressure sensors and synchronized data recording.
- A measured description of the pipe: length, diameter, material, elevation, connections, sensor positions, and normal operating conditions.
- A calibrated transient simulator: a computer model that predicts how pressure changes travel through that pipe.
- Detection software that compares measurements with healthy and faulty explanations.
- A permitted pressure-test mechanism, such as a controlled valve operation.
- A report showing the measured and predicted pressure traces, leak decision, estimated location, uncertainty, and any reason the result is inconclusive.

The initial operator workflow is: describe and calibrate the pipe, record a test, inspect the diagnosis, and perform a suggested follow-up test if necessary. The output should help an operator choose where to inspect. Automated repair and autonomous operation of a public water network are outside the first prototype.

**Finished laboratory product:** another team member can set up the documented system, record an unknown trial, and reproduce its diagnosis without editing solver code or entering the true leak location.

**Later commercial product:** installation and calibration procedures, reliable hardware, operator trials, maintenance support, and evidence of economic value. A successful Conrad prototype alone will not establish field readiness.

## 2. What is implemented, and what remains

Repository reviewed on October 3, 2026, at commit `a297543c63bb2f0ef161e707640e46f38092c829`. These are findings from reading the code, not results of running a new validation study.

| Component | Current implementation | Work still needed |
| --- | --- | --- |
| Pipe simulation | One-dimensional, single-pipe water-hammer model; fixed-head inlet; prescribed outlet flow; adjustable inlet pulse; fluid compressibility, elastic pipe-wall wave speed, elevation, and a configured friction factor. | Verify travel times, boundary reflections, numerical convergence, and steady initial conditions. Add more complex components only when measurements require them. |
| Leak representation | One configurable orifice leak, applied as a localized head update. | Check that the implementation conserves mass and represents the junction flow correctly. Validate its pressure and reflection behavior before relying on leak estimates. |
| Configuration | JSON presets for horizontal steel, vertical steel, and horizontal PVC. | Measure the actual apparatus and calibrate it. PVC presets do not establish that time-dependent plastic-wall behavior is modeled accurately. |
| Sensors | Pressure samples at configured simulated locations, with added random noise and drifting bias. | Physical sensors, bandwidth measurements, timestamp synchronization, calibration, data import, and acquisition controls. |
| Diagnosis baseline | A grid of candidate leak locations and areas ranked by mean squared pressure mismatch. A normalized waveform-similarity option also exists. | Explicit healthy-pipe and non-leak alternatives, thresholds, independent benchmarks, and uncertainty. The similarity option does not currently search time delays. |
| Probabilistic method | The option named `probabilistic` computes one-half of the mean squared mismatch. | It currently produces the same candidate ranking as least squares. It is not a complete probabilistic estimator: no explicit uncertainty model, prior, posterior, or calibrated confidence interval is implemented. |
| Observables | Pressure, flow, velocity, head, derivatives, impedance, characteristic components, leak flow, sensor residuals, and other diagnostics can be exported to NPZ. | Validate derived quantities and select useful outputs. The wave-energy quantity is a proxy, not energy in joules. Exported diagnostics do not prove physical accuracy. |
| Verification | Four basic tests check a broad wave-speed range, positive leak flow, zero leak flow when disabled, and selected output fields. | Quantitative checks against known solutions and measured recordings. These tests do not establish detection performance. |
| Adaptive testing and network support | No adaptive test selector or network junction solver in the reviewed implementation. | Implement bounded follow-up tests for the single-pipe prototype. Branches, multiple leaks, pumps, obstructions, and full networks are later extensions. |

Two issues deserve early attention. The current solver advances characteristic information across neighboring grid locations while its timestep is set to 0.90 times the grid travel time. We must check travel-time accuracy and make the discretization consistent, rather than assuming this setting validates the solver. The initial head and flow are also uniform; with friction and an enabled leak, this can create a startup transient. Calibration tests must distinguish that settling behavior from the deliberate diagnostic pulse.

The demonstration generates its measurements and candidate predictions using the same model. This is useful for debugging, but success in that demonstration cannot establish performance on real pipes.

## 3. Proposed differentiation and how to prove it

Transient reflection and inverse transient analysis are established approaches. For example, [Duan and colleagues' 2010 study](https://www.iahr.org/library/infor?pid=4823) investigates the role of reflected signals in transient leak detection. We should not claim that sending a pressure pulse, interpreting echoes, or comparing measurements with a simulation is new.

| Proposed product advantage | Evidence we need |
| --- | --- |
| A small, affordable sensor setup can locate a leak in the supported pipe geometry. | Compare one-, two-, and three-sensor arrangements on the same trials; report hardware cost and the accuracy lost when reducing sensors. |
| Calibration helps separate leaks from ordinary differences between the model and apparatus. | Compare uncalibrated and calibrated predictions on recordings excluded from calibration; include demand changes and sensor offsets. |
| An adaptive follow-up test gives more useful information than a fixed test. | Use the same pressure limits and test budget for both approaches; compare localization error, ambiguity, and number of tests. |
| A useful diagnosis includes uncertainty and an inconclusive result. | Measure how often reported location intervals contain the true leak and how often non-leak trials trigger an alarm. |

Review at least five relevant research papers and three commercial alternatives. Record what they already do and identify the exact combination or implementation we improve. Adaptive excitation and digital-twin methods may also have prior art; their combination alone does not prove novelty. If our measurements show no advantage, revise the differentiation claim rather than overstating the results.

## 4. Simple project plan with measurable completion steps

Complete these steps in order where they depend on earlier evidence. For every step, fill in an **owner, result, evidence link, and remaining issue**. All numerical targets are provisional laboratory goals. Freeze the final test protocol before collecting the blind evaluation data.

### Step 1 — Define the first product and its claim

- [ ] Choose one pipe geometry, one material, one operating-pressure range, and a range of single-leak sizes.
- [ ] Review five research papers and three commercial alternatives using the comparison above.
- [ ] Interview at least three potential users about current inspection methods, installation constraints, and costs.
- [ ] Produce a one-page scope and a comparison table stating the proposed advantage we will actually test.

**Complete when:** the team can state the user, supported pipe conditions, measurable advantage, and excluded cases without relying on a claim of unproven novelty.

### Step 2 — Verify the simulator

- [ ] Check pressure-wave travel time against length divided by wave speed and pressure change against the Joukowsky relation.
- [ ] Check inlet and outlet reflections, a settled healthy state, leak continuity, and leak flow against the orifice relation.
- [ ] Repeat at three grid resolutions. Resolve the characteristic timestep issue and check that key results converge.
- [ ] Save plots and a verification table. Initial target: under 5% error in analytical travel time and pressure-jump cases within the model's assumptions; under 5% change in selected outputs between the two finest grids.

**Complete when:** known reference cases pass and any remaining model approximation is documented. Do not tune detection methods to compensate for a solver error.

### Step 3 — Build and characterize the physical apparatus

- [ ] Assemble one measured water-pipe setup with a controllable leak outlet and a repeatable pressure-test mechanism.
- [ ] Install at least two pressure sensors; document component ratings, pressure limits, sensor positions, and the bill of materials.
- [ ] Measure sensor bandwidth, noise, offset, sample rate, and relative timing. Aim for at least ten samples across the shortest pressure feature used for diagnosis.
- [ ] Record at least ten repeatable healthy-pipe tests and independently measure discharged leak water over a known time to obtain a reference flow.

**Complete when:** the setup produces repeatable, timestamped recordings and known leak conditions. Pressure limits constrain every subsequent test.

### Step 4 — Calibrate and validate the healthy-pipe model

- [ ] Use healthy recordings to estimate effective wave speed, friction, sensor offsets, and actual excitation timing or waveform.
- [ ] Keep a separate set of recordings for validation. Do not use leak truth to calibrate the healthy model.
- [ ] Compare arrival times and pressure-change amplitudes. Initial targets: under 5% arrival-time error and under 10% amplitude error for the chosen operating range.
- [ ] If those targets fail, investigate timing, connections, trapped air, wall behavior, and model assumptions; narrow the scope or add the necessary physics.

**Complete when:** the model predicts withheld healthy tests within the agreed tolerances, with remaining mismatch recorded.

### Step 5 — Establish detection baselines

- [ ] Implement an explicit healthy-pipe candidate and a detection threshold.
- [ ] Compare a simple pressure-change threshold, least-squares candidate fitting, and one reflection-timing or waveform-matching method.
- [ ] Include Fourier analysis only if frequency features help; choose a probabilistic method only if uncertainty modeling justifies the additional work.
- [ ] Separate calibration/tuning data from evaluation data. Record detection rate, false-alarm rate, localization error, and processing time.

**Complete when:** at least two practical methods have been compared on the same withheld recordings and the initial method has been selected using measured results.

### Step 6 — Run a blind physical evaluation

- [ ] Collect at least 100 evaluation trials: five leak locations × three measurable leak sizes × five repeats = 75 leak trials, plus 25 non-leak trials.
- [ ] Include ordinary flow changes, sensor offsets, and repeated healthy tests among the non-leak conditions.
- [ ] Randomize trials and hide the true condition from the person running the detector. Recalibrate only under the frozen protocol.
- [ ] Initial goals: detect at least 90% of leaks in the declared size range; false alarms in at most 10% of non-leak trials; median location error at most 5% of pipe length among correctly detected leaks.
- [ ] Report counts, error distributions, missed leaks, and all inconclusive results. State the smallest reliably detected measured leak flow.

**Complete when:** the full dataset and evaluation report are reproducible. Report goals that were missed; do not describe these targets as achieved performance.

### Step 7 — Add useful uncertainty and diagnosis limits

- [ ] Produce a location interval using repeated-data resampling or a justified probabilistic model.
- [ ] Test interval coverage on withheld leak trials; nominal 90% intervals should contain the true location roughly 90% of the time, with sampling uncertainty reported.
- [ ] Define an inconclusive result for ambiguous signals, insufficient signal strength, or substantial model mismatch.
- [ ] Report effective leak area or leak flow only if independently validated. Effective area depends on the assumed discharge coefficient and is not automatically the physical hole size.

**Complete when:** the operator sees an uncertainty range and understandable reasons for an inconclusive diagnosis, rather than an unsupported confidence score.

### Step 8 — Demonstrate adaptive follow-up testing

- [ ] Define at least three repeatable pressure tests within the apparatus limits.
- [ ] Implement a first selector that chooses the test whose simulated responses best separate the remaining plausible explanations.
- [ ] Compare adaptive selection with a fixed-test strategy over at least 20 paired ambiguous cases, using equal pressure limits and maximum test counts.
- [ ] Measure whether adaptation reduces localization error, the inconclusive fraction, or tests needed. A provisional improvement goal is 20% in one preselected metric without worsening false alarms.

**Complete when:** the selection works on the apparatus and its benefit or failure is documented. If adaptation adds no benefit, it cannot be the central claim in our submission.

### Step 9 — Package the prototype and evaluate value

- [ ] Provide one documented command or workflow to import recordings, run diagnosis, and save a readable report.
- [ ] Have a teammate reproduce at least five trial diagnoses without access to the hidden truth.
- [ ] Record hardware cost, setup time, calibration time, test duration, and processing time.
- [ ] Use interview findings to estimate the cost of a first pilot and a plausible business model. Separate measured figures from assumptions.

**Complete when:** the prototype is independently usable and the pitch explains who would buy it and what evidence supports its value.

### Step 10 — Prepare the Conrad submission

- [ ] Finish the Innovation Brief, required 3–5 minute Innovation Video, and website before the official submission deadline.
- [ ] Show a measured leak demonstration, a non-leak trial, the hardware, and the software report.
- [ ] Present the prior-art comparison, blind evaluation results, cost estimate, limitations, and next development steps.
- [ ] Check every performance and novelty claim against an evidence file.

**Complete when:** the submission is complete and its claims match the prototype's demonstrated capabilities.

## 5. Math and physics: what to learn and why

These difficulty ratings are planning judgments, not fixed course requirements. “Moderate” means focused study and exercises; “high” usually means additional prerequisites and substantial debugging. With AP Physics C mechanics and calculus, the basic wave and energy ideas should be accessible. Fluid transients, numerical PDEs, and statistical inference will require new study.

| Topic | Purpose in this project, in plain language | Math/physics level | Learning difficulty and priority |
| --- | --- | --- | --- |
| Conservation of mass and momentum; hydraulic head | Track where water goes and how pressure forces accelerate it. Head expresses pressure and elevation in equivalent heights of water. | Introductory college mechanics, fluid mechanics, algebra, and calculus. | Moderate. Essential first: understand pressure versus head, flow versus velocity, and boundary conditions. |
| Water hammer and the Joukowsky relation | Explain why changing water speed creates a pressure wave; estimate its initial size. | College waves and fluids; algebra for the simple relation, differential equations for a full derivation. | Moderate with AP Physics C. Learn early; useful for validating both the model and test limits. |
| Water-hammer partial differential equations (PDEs) | Describe pressure and flow changing across both distance and time. These are the simulator's governing equations. | Multivariable calculus, ordinary differential equations, introductory PDEs. | High from scratch. Learn the assumptions and meaning first; full derivations become worthwhile when modifying the solver. |
| Method of Characteristics (MOC) and numerical consistency | Follow the paths along which wave information travels and turn the equations into computer updates. | Differential equations, PDEs, numerical analysis. | High from scratch; moderate-to-high with calculus and programming. Essential for whoever verifies the solver. A timestep rule alone does not prove correctness. |
| Darcy–Weisbach friction and orifice flow | Estimate pressure loss along the pipe and how much water leaves a leak. | College fluids; mostly algebra and square roots in the initial implementation. | Low-to-moderate. High value early. Calibrate coefficients rather than treating every default as measured. |
| Wave reflection, impedance, and time of flight | Explain echoes at leaks, ends, and connections, and use their timing to estimate distance. | College waves, algebra, basic calculus. | Moderate. Essential for interpreting traces; overlapping echoes can make location ambiguous. |
| Sampling theory, bandwidth, and synchronization | Ensure sensors capture a wave without losing fast features or confusing clock errors with distance. | Introductory signals; algebra, frequencies, basic calculus. | Moderate. Essential before purchasing or selecting acquisition hardware. |
| Least squares, inverse problems, and identifiability | Find model settings that best explain recordings; determine whether different leaks or pipe parameters look indistinguishable. | Linear algebra, calculus, numerical optimization. | Moderate for grid search; high for sophisticated optimization. Learn the simple method first and examine ambiguous candidates. |
| Cross-correlation and matched filtering | Compare a recording with an expected shape and, when implemented, search for its arrival delay. | Introductory signal processing, sums, vectors. | Moderate. A practical early alternative to exhaustive candidate fitting. |
| Fourier analysis and the FFT | Separate a pressure trace into frequency components to study resonances or patterns. It is a representation of data, not a complete detector by itself. | Trigonometry, complex numbers, college signals. | Moderate. Optional until evidence shows frequency features improve results. |
| Bayesian inference and uncertainty estimation | Combine a measurement-noise model with prior information to express which explanations remain plausible. Resampling is another way to estimate variability. | Probability, statistics, calculus; numerical methods for advanced implementations. | Moderate for a finite candidate grid or basic resampling; high for advanced samplers. Worth learning after the baseline and noise measurements work. |
| Experimental design and information gain | Choose the next pressure test that is expected to reduce ambiguity. | Basic optimization for response separation; probability and information theory for formal information gain. | Moderate for a simple selector, high for a full probabilistic design method. Needed to test our adaptive distinction, but formal information theory can wait. |
| EKF/UKF and particle filtering | Continually update an estimated hidden pipe state from incoming measurements. | Linear algebra, probability, nonlinear dynamics, control theory. | High. Defer unless continuous tracking becomes necessary; these are not required for the first recorded-test prototype. |
| Viscoelasticity and unsteady friction | Model plastic walls that deform over time and flow resistance that depends on recent motion. | Advanced fluids, mechanics, differential equations. | High. Add only if measured behavior demands it; PVC may require these effects earlier than steel. |

**Suggested learning order:** head and flow → water hammer and reflections → friction and leaks → sampling and sensor timing → MOC verification → least-squares diagnosis → uncertainty → adaptive selection. Team members can divide these topics; everyone does not need to derive every equation. Machine learning, full network simulation, and advanced state estimators should wait until the physical baseline demonstrates a need.

## 6. Evidence and progress tracker

For each milestone, copy and fill out this line:

**Step:** ___ | **Owner:** ___ | **Status:** ___ | **Measured result:** ___ | **Evidence path/link:** ___ | **Remaining issue:** ___

Keep apparatus measurements, configuration versions, raw recordings, calibration data, evaluation labels, analysis scripts, and plots together. Label each result as simulated or physical. Report performance within the tested material, geometry, leak-size, and operating range; do not extrapolate a small laboratory success to an entire distribution network.

## References

- [Current simulator documentation](Simulator/README.md), [physics implementation](Simulator/hydrosim/physics.py), [candidate scoring](Simulator/hydrosim/inference.py), and [existing tests](Simulator/tests/test_physics.py).
- Duan, H.-F., Lee, P. J., Ghidaoui, M. S., and Tung, Y.-K. (2010), [Essential system response information for transient-based leak detection methods](https://www.iahr.org/library/infor?pid=4823), DOI: 10.1080/00221686.2010.507014. Prior art establishing that reflection-based transient leak detection predates this project.
- [Conrad Challenge: 2026–2027 Innovation Stage](https://conrad.spacecenter.org/the-challenge/innovation-stage/). Deadline and submission deliverables checked October 3, 2026.

