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

### 2026-10-27 23:44 -03:00

- Archivos: `notebooks/diagnostics/01_co2_mass_balance.source.ipynb`, `01_co2_mass_balance.executed.ipynb`, `data/processed/co2_mass_balance_lab016_021_g_l_h.csv`, `README.md`.
- Cambio: conversión y guardado de caudales crudos y filtrados GUI antes de integrar; el balance relee el CSV y utiliza la señal cruda nativa como referencia. Añadidas cinco figuras con 48 áreas sombreadas, límites, unidades y cobertura; verificada su igualdad con las integrales y ejecución sin errores. Conservados 2 L y factor 0.74 como supuestos; sin cambios en modelos, parámetros, results ni pyomo-doe.

### 2026-10-27 23:52 -03:00

- Archivos: `notebooks/diagnostics/01_co2_mass_balance.source.ipynb`, `notebooks/diagnostics/01_co2_mass_balance.executed.ipynb`.
- Cambio: sustituido el sombreado de trapecios individuales por relleno continuo de cada bloque válido para eliminar franjas de renderizado. Regenerado EXECUTED y verificados los 48 rellenos contra sus integrales, conservando valores y huecos de datos; modelos y parámetros sin cambios.

### 2026-10-28 00:19 -03:00

- Archivos: `data/processed/co2_mass_balance_lab016_021_g_l_h.csv`, `notebooks/diagnostics/01_co2_mass_balance.source.ipynb`, `notebooks/diagnostics/01_co2_mass_balance.executed.ipynb`, `README.md`.
- Cambio: normalización por volumen remanente en LAB019–021 para señales cruda y filtrada, descontando las seis retiradas de 50 mL incluida m1 y sin aporte líquido por nutrición. CSV con volumen por lectura y límites antes/después de cada retirada; actualizadas tablas, balances y figuras. EXECUTED regenerado sin errores; verificados 1.95 L al inocular, 1.75/1.70 L antes/después de m12, conservación del caudal másico y áreas sombreadas. LAB016–018, modelos, parámetros, results y pyomo-doe sin cambios.

### 2026-10-28 13:15 -03:00

- Archivos: `src/wine_fermentation/models/`, `src/wine_fermentation/shared/`, `src/wine_fermentation/comparison.py`, `configs/models/`, `notebooks/03_calibrate_models.source.ipynb`, `notebooks/03_calibrate_models.executed.ipynb`, `notebooks/04_compare_models.source.ipynb`, `notebooks/04_compare_models.executed.ipynb`, `notebooks/historical/`, `tests/test_model_variants.py`, `docs/model_comparison.md`, `README.md`.
- Cambio: implementadas tres formulaciones separadas: referencia histórica congelada, respuesta directa al YAN y transportadores. Recalibrados los dos modelos nuevos desde theta_full con cotas de rendimiento y evaluación independiente; CO2 sin modulación O2, con depósito y volumen remanente. Solubilidad heredada identificada expresamente como provisional. Archivados los cuatro notebooks anteriores sin alterar su contenido. Verificados cuatro tests, ambos pares SOURCE/EXECUTED y siete figuras; originales históricos y results conservados, sin cambios en pyomo-doe.
### 2026-10-28 14:19 -03:00

- Archivos: `notebooks/04_compare_models.source.ipynb`, `notebooks/04_compare_models.executed.ipynb`.
- Cambio: títulos explícitos para calibración de CO2, holdout químico y diagnóstico de depósito/transferencia; leyendas superiores con título y nombres de modelos en español. Aclarados datos medidos, curvas calculadas y ganancia de observación. EXECUTED regenerado sin recalibración; verificadas siete figuras, ausencia de errores e igualdad de fuentes. Sin cambios en modelos, parámetros ni pyomo-doe.
### 2026-10-28 14:27 -03:00

- Archivos: `notebooks/04_compare_models.source.ipynb`, `notebooks/04_compare_models.executed.ipynb`.
- Cambio: añadidas figuras de glucosa más fructosa para calibración química LAB004–009 y holdout LAB019–021, comparando las tres formulaciones. Sumas experimentales sólo con G y F de la misma muestra; condiciones iniciales diferenciadas. Títulos y leyendas superiores verificados visualmente. EXECUTED regenerado sin recalibrar; nueve figuras sin errores y fuentes coherentes. Sin cambios en modelos, parámetros ni pyomo-doe.
### 2026-10-28 14:38 -03:00

- Archivos: `src/wine_fermentation/comparison.py`, `configs/models/*/gas_fit.json`, `configs/models/*/calibration.json`, `configs/models/historical/reference.json`, `notebooks/03_calibrate_models.source.ipynb`, `notebooks/03_calibrate_models.executed.ipynb`, `notebooks/04_compare_models.source.ipynb`, `notebooks/04_compare_models.executed.ipynb`, `tests/test_model_variants.py`, `docs/model_comparison.md`, `README.md`.
- Cambio: corregida la partición principal de CO2 a calibración LAB019–021 y holdout LAB016–018; ejecutada también la inversa. Reajustados los coeficientes de CO2 de las tres formulaciones al mismo objetivo de medianas horarias crudas, conservando ecuaciones, química y ajustes originales. Parámetros agrupados por partición; tablas pareadas y figuras con roles explícitos, conservando G+F. Documentados parámetros en cota y supuestos de Cd inicial/solubilidad. Verificados seis ajustes convergentes, seis tests, once figuras y ambos pares SOURCE/EXECUTED; results y pyomo-doe sin cambios.
### 2026-10-28 15:08 -03:00

- Archivos: `notebooks/04_compare_models.source.ipynb`, `notebooks/04_compare_models.executed.ipynb`.
- Cambio: retiradas las etiquetas de ensayo principal/inverso de los títulos de las dos primeras figuras de CO2 emitido; conservada la identificación de laboratorios de calibración y holdout. Ejes Y limitados a 0–1.2 g/(L·h). EXECUTED regenerado sin optimizar y verificadas once figuras, fuentes coherentes y ausencia de errores. Modelos, parámetros y pyomo-doe sin cambios.