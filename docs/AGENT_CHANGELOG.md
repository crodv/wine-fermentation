# Historial de modificaciones por agentes

### 2026-10-27 13:37 -03

- Archivos: `src/wine_fermentation/model.py`, `co2.py`, `data.py`, `notebooks/01_recalibration_theta_nv2.source.ipynb`, `01_recalibration_theta_nv2.executed.ipynb`, `02_co2_theta_nv2.source.ipynb`, `02_co2_theta_nv2.executed.ipynb`, `configs/theta/theta_nv2.json`, `results/recalibration_nv2/`, `README.md`, `docs/model.md`.
- Cambio: reducción a cinco estados conservando mortalidad y capa CO₂; recalibración desde theta_full con rendimientos de etanol restringidos y comparación con theta_new. Notebooks e implementación anteriores conservados en historical. Datos y repositorio pyomo-doe sin cambios; sin operaciones de escritura Git.

### 2026-10-27 15:02 -03:00

- Archivos: `notebooks/` (cuatro parejas SOURCE/EXECUTED, incluidas las de historical), `configs/co2_reference_parameters.csv`, `results/co2_fit_parameters.csv`, `README.md`.
- Cambio: limpieza de 64 archivos auxiliares y temporales de results; conservados los coeficientes de CO2 a precisión completa. Eliminadas las exportaciones automáticas de CSV/PNG auxiliares; referencia de comparación reubicada en configs. Verificadas las cuatro parejas y sus 36 figuras sin alterar outputs ni recalibrar. pyomo-doe sin modificaciones.

### 2026-10-27 16:06 -03:00

- Archivos: `notebooks/diagnostics/01_co2_mass_balance.source.ipynb`, `notebooks/diagnostics/01_co2_mass_balance.executed.ipynb`, `README.md`.
- Cambio: diagnóstico de CO2 acumulado desde inoculación y por tramos, comparando etanol solo y crecimiento más etanol de Zenteno. Incluye referencias experimentales LAB019–021, cobertura LAB016–021, sensibilidad de conversión y cinco figuras inline. Ejecutado sin errores, sin recalibración ni exportaciones en results; modelos, parámetros y pyomo-doe sin cambios.

### 2026-10-27 16:49 -03:00

- Archivos: `notebooks/diagnostics/01_co2_mass_balance.source.ipynb`, `notebooks/diagnostics/01_co2_mass_balance.executed.ipynb`.
- Cambio: incorporado CO2 disuelto inicial de carbodoseur con temperaturas confirmadas del log: 0.907, 0.730 y 0.829 g/L; LAB021 y sus cálculos derivados permanecen provisionales. Reejecutado el diagnóstico con inventario final requerido, escenario final cero y figura adicional; conservadas las inconsistencias negativas como diagnóstico. Sin recalibración, exportaciones en results ni cambios en pyomo-doe.
