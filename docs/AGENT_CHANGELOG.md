# Historial de modificaciones por agentes

### 2026-10-27 13:37 -03

- Archivos: `src/wine_fermentation/model.py`, `co2.py`, `data.py`, `notebooks/01_recalibration_theta_nv2.source.ipynb`, `01_recalibration_theta_nv2.executed.ipynb`, `02_co2_theta_nv2.source.ipynb`, `02_co2_theta_nv2.executed.ipynb`, `configs/theta/theta_nv2.json`, `results/recalibration_nv2/`, `README.md`, `docs/model.md`.
- Cambio: reducción a cinco estados conservando mortalidad y capa CO₂; recalibración desde theta_full con rendimientos de etanol restringidos y comparación con theta_new. Notebooks e implementación anteriores conservados en historical. Datos y repositorio pyomo-doe sin cambios; sin operaciones de escritura Git.

### 2026-10-27 15:02 -03:00

- Archivos: `notebooks/` (cuatro parejas SOURCE/EXECUTED, incluidas las de historical), `configs/co2_reference_parameters.csv`, `results/co2_fit_parameters.csv`, `README.md`.
- Cambio: limpieza de 64 archivos auxiliares y temporales de results; conservados los coeficientes de CO2 a precisión completa. Eliminadas las exportaciones automáticas de CSV/PNG auxiliares; referencia de comparación reubicada en configs. Verificadas las cuatro parejas y sus 36 figuras sin alterar outputs ni recalibrar. pyomo-doe sin modificaciones.
