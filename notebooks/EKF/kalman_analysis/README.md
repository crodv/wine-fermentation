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

## Measurement covariance R audit

Section 3R of the same notebook adds `r_assessment.py`: local manufacturer
specifications, logged 4--20 mA / 0--50 SCCM conversion, gas-factor assumptions,
volume-dependent propagation, correlated 30-minute means, clipping and
conditional uncertainty scenarios. It uses only LAB019--021. The `R_*` files
contain per-window results and documentary provenance.

Range 0--50 SCCM, air calibration and gas factor 0.74 were explicitly confirmed
by the user on 2026-11-05; see `../../../configs/co2_instrument.json`. Do not
request these facts again. Accuracy bounds are not specified
standard deviations. The rectangular Type-B distribution is an assumption.
The manual's +/-4% gas-conversion accuracy has an unspecified percentage basis;
reading-based and full-scale scenarios are kept separate. Persistent biases
must not be assumed independent between measurements or reduced by sqrt(n).

This addition does not reoptimize Q or overwrite earlier noise-search artifacts.
Earlier fitted R values are effective fitting parameters, not manufacturer-
certified measurement uncertainty. No new value is automatically adopted in
any estimator. No additional dependency or environment change is required.
