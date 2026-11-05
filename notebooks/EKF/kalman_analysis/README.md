# EKF G/F: analysis of noise sources and amplitudes

Open `01_gf_variable_solubility_noise_analysis.executed.ipynb` to inspect the
completed study, or execute the matching `.source.ipynb` to reproduce it.

Only LAB019–021 enter fitting, internal validation, source comparisons, initial
search points and diagnostics. Existing estimators and calibrations are never
overwritten. Shared CSVs are filtered to those three laboratories immediately.
No LAB016–018 raw files are opened and no holdout estimator is run.

The notebook uses `analysis_core.py` (data isolation, physical model, EKF,
calibration and optimization) and `analysis_plots.py` (figures). These are local
helpers, not changes to the production model. `validate_analysis.py` checks the
six source columns against finite perturbations of the balances.

Dependencies: Python, numpy, pandas, scipy, matplotlib, nbformat, IPython, numba.
The delivered execution uses the existing Anaconda base environment, where
numba is available; it is not installed in the existing `fermentation`
environment. Select a kernel with these dependencies. No environment or kernel
installation is performed by this notebook.

`results/` contains gas fits, multistart noise searches, numerical diagnostics,
parameter sweeps, decision tables and compressed development trajectories.
Caches are checked against the analysis code and the *filtered training arrays*
before reuse. Delete the local `results/` directory or change inputs to recompute.
The first execution includes JIT compilation; optimization is substantially
longer than viewing the executed notebook.

The gas refits use the causal 30-minute operator and EKF initial conditions;
they differ deliberately from the archived hourly offline-temperature gas fit.
In each internal fold, both gas fitting and noise fitting exclude the validation
laboratory. These internal comparisons are not a final independent validation.

Bounds, local Gaussian approximations, clipping, data-dependent update screening,
unknown analytical uncertainty and only three fermentations limit inference.
Noise amplitudes at a bound or sensitive to initialization must not be presented
as precisely identified physical constants. The CO2-score leader is a candidate,
not an automatically approved estimator or source structure.
