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
### 2026-10-28 15:41 -03:00

- Archivos: `notebooks/diagnostics/02_co2_production_transfer.source.ipynb`, `notebooks/diagnostics/02_co2_production_transfer.executed.ipynb`, `notebooks/04_compare_models.source.ipynb`, `notebooks/04_compare_models.executed.ipynb`.
- Cambio: añadido diagnóstico factorial de producción/transferencia con química theta_nv2 común, ambas particiones de CO2, perfiles y sensibilidad separada de saturación. Ajustes sólo en memoria; condiciones iniciales, volumen y saturación compartidos. Verificadas leyes de transferencia, balances con retiradas, exclusión de holdout e integridad de src/configs/results. Figuras actuales sustituyen RAW densa por medianas horarias del objetivo. Regenerados ambos EXECUTED, con siete y once figuras, fuentes coherentes y sin errores; modelos, parámetros guardados y pyomo-doe intactos.
### 2026-10-28 16:14 -03:00

- Archivos: `notebooks/04_compare_models.source.ipynb`, `notebooks/04_compare_models.executed.ipynb`, `notebooks/diagnostics/02_co2_production_transfer.source.ipynb`, `notebooks/diagnostics/02_co2_production_transfer.executed.ipynb`.
- Cambio: medianas horarias experimentales de CO2 representadas como líneas sin marcadores; retirado el máximo fijo de 1.2 g/(L·h) y ajustada la escala Y según las curvas de cada panel. Actualizados textos de presentación y regenerados ambos EXECUTED. Verificadas fuentes coherentes, once y siete figuras sin errores e integridad de modelos y parámetros; pyomo-doe intacto.
### 2026-10-28 16:41 -03:00

- Archivos: `notebooks/diagnostics/02_co2_production_transfer.source.ipynb`, `notebooks/diagnostics/02_co2_production_transfer.executed.ipynb`.
- Cambio: Cd inicial fijado en cero para todos los LAB y combinaciones; restaurada pérdida con umbral de detección 0.05 g/(L·h), distinguiéndola del RMSE descriptivo. Política común de final mediante 2 h ≤0.02, cobertura suficiente, última muestra offline incluida y ausencia de actividad posterior detectable; registros sin confirmación marcados como censurados. Regenerado EXECUTED con siete figuras. Verificados casos de política y pérdida, balances, emisiones iniciales cero e integridad de modelos/configs/results; predicciones sin filtrar y pyomo-doe intacto.
### 2026-10-28 18:06 -03:00

- Archivos: `notebooks/diagnostics/02_co2_production_transfer.source.ipynb`, `notebooks/diagnostics/02_co2_production_transfer.executed.ipynb`.
- Cambio: añadida figura de theta_nv2 con el conjunto compartido de CO2 del notebook antiguo, comparado con A y cambios aislados de ganancia/liberación. Parámetros antiguos leídos a precisión completa; condiciones del diagnóstico y predicción sin filtrar comunes. Incluidas tablas de coeficientes, error y efecto de escala de saturación. Regenerado EXECUTED con ocho figuras; verificadas identidad de A reconstruida, proporcionalidad de ganancia, fuentes coherentes e integridad de modelos/configs/results; pyomo-doe intacto.
### 2026-10-28 18:36 -03:00

- Archivos: `src/wine_fermentation/comparison.py`, `tests/test_model_variants.py`, `notebooks/04_compare_models.source.ipynb`, `notebooks/04_compare_models.executed.ipynb`, `notebooks/diagnostics/02_co2_production_transfer.source.ipynb`, `notebooks/diagnostics/02_co2_production_transfer.executed.ipynb`.
- Cambio: corregida la selección común para gráficos y métricas químicas: G+F usa su medición conjunta y YAN incluye NUT, recuperando trece valores de G+F y tres de YAN. Añadidos controles de conteos y dos pruebas de regresión. Incorporada comparación de onset manual histórico con theta_nv2 y coeficientes antiguos/A fijos, modificando sólo la activación y reintegrando el depósito. Regenerados ambos EXECUTED; ocho tests aprobados, once y nueve figuras verificadas. Modelos, parámetros guardados, datos de compatibilidad y pyomo-doe intactos.
### 2026-10-28 19:08 -03:00

- Archivos: `notebooks/diagnostics/03_theta_nv2_parameter_sensitivity.source.ipynb`, `notebooks/diagnostics/03_theta_nv2_parameter_sensitivity.executed.ipynb`.
- Cambio: añadido ensayo de sensibilidad exclusivamente de theta_nv2 con cambios individuales de KIE, KIG y tasas betaG0/betaF0 ±20%; rendimientos y coeficientes históricos de CO2 fijos. Comparadas predicciones de CO2, etanol, glucosa, fructosa y G+F en LAB016–021, con métricas y caída previa a nutrición. Verificadas 48 simulaciones sin fallos, cinco figuras, muestras G+F y fuentes SOURCE/EXECUTED coherentes; modelos, parámetros guardados, results, datos de compatibilidad y pyomo-doe intactos. Sin exportar CSV ni PNG al repositorio.

### 2026-10-28 19:25 -03:00

- Archivos: `notebooks/historical/02_co2_theta_nv2.source.ipynb`, `notebooks/historical/02_co2_theta_nv2.executed.ipynb`.
- Cambio: añadida figura y métricas de onset manual histórico para los tres theta con los coeficientes compartidos del notebook, sin recalibrar. Comparadas activación por azúcar y manual reintegrando el depósito, con Cd inicial cero y predicciones nuevas sin filtro. Conservadas todas las salidas anteriores; ejecutadas sólo dependencias de lectura/simulación y sección nueva, omitiendo optimizaciones y exportaciones. Verificadas 18 parejas, identidad de referencia física, balance, once figuras totales y fuentes coherentes; src/configs/results/datos de compatibilidad y pyomo-doe intactos.

### 2026-10-28 19:32 -03:00

- Archivos: `notebooks/historical/02_co2_theta_nv2.source.ipynb`, `notebooks/historical/02_co2_theta_nv2.executed.ipynb`.
- Cambio: retiradas las curvas sin onset manual de la figura adicional; conserva sólo las tres curvas manuales y la señal experimental, con colores/estilos por theta y leyenda superior. Actualizada la salida de esa sección, preservando las restantes figuras. Verificados SOURCE/EXECUTED coherentes, ausencia de errores y presentación visual; modelos, parámetros y results intactos.

### 2026-10-28 23:25 -03:00

- Archivos: `notebooks/04_compare_models_v2.source.ipynb`, `notebooks/04_compare_models_v2.executed.ipynb`, `notebooks/EKF/lab019_first_ekf_full_batch.source.ipynb`, `notebooks/EKF/lab019_first_ekf_full_batch.executed.ipynb`, `notebooks/EKF/diagrams/ekf_general_block_diagram.source.ipynb`, `notebooks/EKF/diagrams/ekf_general_block_diagram.executed.ipynb`, `notebooks/EKF/diagrams/ekf_general_block_diagram.pdf`.
- Cambio: añadida comparación v2 con kLa=0.07 h-1 en los dos modelos nuevos, ganancias ajustadas sólo en memoria y ambas particiones de gas; probado E0=9.8 g/L en LAB016–018 y separado su efecto frente a E0=0. Conservadas química, correlación de saturación e iniciales de Cd del comparador. Verificadas dieciséis figuras, balances, muestras y fuentes coherentes; documentada la ausencia de adaptación fisiológica sin introducirla.
- Cambio: trasladado el primer EKF LAB019 con instantáneas internas de los parámetros y datos químicos originales, lectura causal de registros del nuevo repositorio y formulación, covarianzas, restricciones y ganancias explícitas. Conservada la reducción global de ganancia original, sin incorporar proyección restringida ni parámetros v2. Verificadas seis figuras y paridad exacta de ambas tablas de resultados a la precisión archivada. Trasladados códigos de tres diagramas a SOURCE/EXECUTED y PDF multipágina, revisado visualmente. Sin CSV/PNG externos; modelos, configuraciones, resultados previos, 04 original y pyomo-doe intactos.

### 2026-10-29 00:04-03:00

- Archivos: `notebooks/diagnostics/04_co2_zenteno_transfer.source.ipynb`, `notebooks/diagnostics/04_co2_zenteno_transfer.executed.ipynb`.
- Cambio: comparación sin recalibración de transferencia actual y Zenteno con acumulación limitada por producción y tolerancia de saturación; misma química sin transportadores, ganancia, Cd inicial cero y saturación constante. Verificadas tres figuras, paridad SOURCE/EXECUTED, conservación con retiradas, positividad y sensibilidad numérica; src/configs y pyomo-doe intactos, sin CSV ni PNG exportados al repositorio.

### 2026-10-29 00:13 -03:00

- Archivos: `notebooks/diagnostics/04_co2_zenteno_transfer.source.ipynb`, `notebooks/diagnostics/04_co2_zenteno_transfer.executed.ipynb`.
- Cambio: añadidas seis figuras químicas separadas (biomasa viable, YAN, glucosa, fructosa, G+F y etanol) con mediciones offline, entradas iniciales, nutrición y métricas por laboratorio. Conservadas muestras numéricas NUT y medición conjunta G+F; indicada ausencia de muestras LAB016–018. Regenerado EXECUTED y verificadas nueve figuras, paridad de fuentes, conteos y modelos/configuraciones intactos; revisión visual de G+F y YAN. Sin CSV/PNG exportados al repositorio ni cambios en pyomo-doe.

### 2026-10-29 01:23 -03:00

- Archivos: `src/wine_fermentation/models/david_2012/__init__.py`, `src/wine_fermentation/models/david_2012/kinetics.py`, `src/wine_fermentation/models/david_2012/empirical.py`, `src/wine_fermentation/models/david_2012/calibration.py`, `configs/models/david_2012/fit.json`, `notebooks/05_david_2012.source.ipynb`, `notebooks/05_david_2012.executed.ipynb`.
- Cambio: implementadas ecuaciones de David 2012 y extensión nutricional con funciones empíricas reconstruidas y calibradas con autorización explícita; sin cinética de Zenteno, transferencia, ganancia ni activación añadida. Ajuste exclusivo de química depurada LAB004–009 con dos inicios convergentes; validación de X, YAN, S, etanol y CO2 en LAB019–021 sin reajuste. Documentados parámetros, reconstrucciones, normalización, límites e identificación débil.
- Verificación: balances de nitrógeno/azúcar/etanol/CO2, positividad y ensayo con/sin nutrición; diferencia máxima 0.000073 g/L en LAB004 al estrechar tolerancias. Nueve figuras, SOURCE limpio, paridad de fuentes y revisión visual; hashes de modelos/configuraciones anteriores intactos. Sin CSV/PNG exportados al repositorio, cambios en pyomo-doe, commit ni push.

### 2026-10-29 01:51-03:00

- Archivos: `src/wine_fermentation/models/david_2012_dissolved/__init__.py`, `src/wine_fermentation/models/david_2012_dissolved/co2.py`, `notebooks/06_david_2012_dissolved_co2.source.ipynb`, `notebooks/06_david_2012_dissolved_co2.executed.ipynb`.
- Cambio: extensión independiente de David calibrado fijo con depósito conservativo, Csat térmica anclada a referencia de literatura y presión parcial asumida; comparación sin reajuste para kLa 0.07/2/20 en figuras separadas. Mostrados Cd/Csat, acumulados, métricas y balances con volumen remanente y retiradas.
- Verificación: cinco figuras, SOURCE limpio, paridad de fuentes, revisión visual, positividad, conservación, monotonía térmica y refinamiento temporal. Hashes de modelos/configuraciones/notebooks originales intactos; sin CSV/PNG exportados al repositorio, cambios en pyomo-doe ni operaciones Git.

### 2026-10-29 11:23-03:00

- Archivos: `notebooks/diagnostics/05_historical_single_trajectory.source.ipynb`, `notebooks/diagnostics/05_historical_single_trajectory.executed.ipynb`.
- Cambio: ablación sin recalibración de la combinación histórica frente a qN y q0 por separado, conservando activación, O2, multiplicador transitorio, saturación, transferencia y coeficientes. Documentada la sustitución del corchete completo y eliminación del factor de actividad interno. Comparados LAB019–021 y holdout LAB016–018 con medianas horarias RAW, áreas, fuente y Cd.
- Verificación: referencia y objetivo guardado reproducidos exactamente; coincidencia previa a nutrición y balances verificados; cuatro figuras, SOURCE limpio, paridad SOURCE/EXECUTED y revisión visual. Hashes de modelos, parámetros, resultados y notebooks anteriores intactos; sin CSV/PNG exportados al repositorio ni cambios en pyomo-doe.

### 2026-10-29 11:33-03:00

- Archivos: `notebooks/diagnostics/06_historical_single_trajectory_fixed_activity.source.ipynb`, `notebooks/diagnostics/06_historical_single_trajectory_fixed_activity.executed.ipynb`.
- Cambio: repetida en otro notebook la comparación histórica/qN/q0 conservando expresamente a(t)=1+(pulse_activity_gain-1)r en ambas fuentes únicas. Resto de factores, estados auxiliares, transferencia y parámetros congelados; sin recalibración. Documentados resultados corregidos respecto al ensayo 05 y alcance del aislamiento de fuente.
- Verificación: referencia y objetivo históricos exactos, igualdad previa a nutrición, conservación, cuatro figuras, SOURCE limpio y paridad de fuentes; revisión visual. Hashes de modelos, parámetros, resultados y notebooks anteriores intactos; sin CSV/PNG exportados al repositorio ni cambios en pyomo-doe.

### 2026-10-29 11:55-03:00

- Archivos: `notebooks/diagnostics/05_historical_single_trajectory_v2.source.ipynb`, `notebooks/diagnostics/05_historical_single_trajectory_v2.executed.ipynb`, `notebooks/diagnostics/06_historical_single_trajectory_fixed_activity_v2.source.ipynb`, `notebooks/diagnostics/06_historical_single_trajectory_fixed_activity_v2.executed.ipynb`.
- Cambio: creadas v2 de 05/06 con recalibración independiente de liberación, escala Csat y ganancia para histórica/qN/q0, preservando las distintas políticas de actividad. Química y respuesta nutricional fijas. Ajuste exclusivo LAB019–021; holdout LAB016–018 sin reajuste. Objetivo censurado bajo 0.05, igual peso por LAB y cortes del lector histórico; tablas de parámetros, límites, tres inicios y congelado/reajustado.
- Verificación: seis ajustes convergentes, dieciocho arranques, balances y separación de datos; ocho figuras, SOURCE limpios y paridad con EXECUTED, revisión visual. Modelos/configuraciones/resultados/notebooks anteriores protegidos por hashes; sin CSV/PNG externos al notebook en el repositorio, parámetros sobrescritos, cambios en pyomo-doe ni operaciones Git.

### 2026-10-29 17:35 -03:00

- Archivos: `notebooks/diagnostics/05_historical_single_trajectory_v2.source.ipynb`, `notebooks/diagnostics/05_historical_single_trajectory_v2.executed.ipynb`, `notebooks/diagnostics/06_historical_single_trajectory_fixed_activity_v2.source.ipynb`, `notebooks/diagnostics/06_historical_single_trajectory_fixed_activity_v2.executed.ipynb`.
- Cambio: agregadas seis figuras químicas separadas (etanol, glucosa, fructosa, G+F, biomasa viable y YAN) con/sin adiciones posteriores de nitrógeno, y tabla de diferencias máximas/finales en LAB016–021. Theta_nv2, temperatura e iniciales fijos; YAN inicial conservado.
- Verificación: ejecutada la sección química común, comprobadas iniciales y biomasa sin pulso contra la trayectoria original, seis figuras por notebook y paridad SOURCE/EXECUTED; revisión visual de G+F. Salidas previas de CO2 conservadas sin repetir ajustes; modelos/configuraciones/resultados protegidos por hashes. Sin CSV/PNG en el repositorio ni cambios en pyomo-doe.

### 2026-10-29 18:01 -03:00

- Archivos: `notebooks/diagnostics/05_historical_single_trajectory_v2.source.ipynb`, `notebooks/diagnostics/05_historical_single_trajectory_v2.executed.ipynb`, `notebooks/diagnostics/06_historical_single_trajectory_fixed_activity_v2.source.ipynb`, `notebooks/diagnostics/06_historical_single_trajectory_fixed_activity_v2.executed.ipynb`.
- Cambio: superpuestas muestras químicas de LAB019–021, incluidas iniciales y NUT numéricas, a las seis comparaciones con/sin nutrición. Añadidos G+F por densidad (2.5*(rho-1000)) y biomasa viable experimental de LAB016–018; identificados paneles sin datos y tabla de conteos por variable/LAB.
- Verificación: sección química ejecutada y salidas actualizadas en ambos EXECUTED, seis figuras por notebook sin errores, paridad de fuentes y revisión visual de G+F/biomasa. Salidas previas de CO2 idénticas y parámetros/modelos preservados; sin CSV/PNG en el repositorio ni cambios en pyomo-doe.

### 2026-10-29 18:08 -03:00

- Archivos: `notebooks/diagnostics/05_historical_single_trajectory_v2.source.ipynb`, `notebooks/diagnostics/05_historical_single_trajectory_v2.executed.ipynb`, `notebooks/diagnostics/06_historical_single_trajectory_fixed_activity_v2.source.ipynb`, `notebooks/diagnostics/06_historical_single_trajectory_fixed_activity_v2.executed.ipynb`.
- Cambio: corregidas las figuras químicas para comparar los mismos casos que CO2: Histórica actual (azul) y Sólo sin nutrición (verde). Se muestra explícitamente su química idéntica con pulsos reales; sustituido el contrafactual anterior que retiraba pulsos de la química. Muestras experimentales, biomasa y G+F por densidad conservados.
- Verificación: seis figuras por notebook, diferencias químicas nulas, fuentes SOURCE/EXECUTED coincidentes y revisión visual; salidas previas de CO2 intactas y sin recalibración ni cambios en modelos/parámetros o pyomo-doe.

### 2026-10-29 19:28 -03:00

- Archivos: notebooks/diagnostics/07_transporter_capacity_functional_loss.source.ipynb, notebooks/diagnostics/07_transporter_capacity_functional_loss.executed.ipynb.
- Cambio: ensayo separado de capacidad inicial reducida y pérdida funcional frente al modelo con transportadores de 04, congelado y recalibrado. Química LAB004–009 y gas LAB019–021; validación química LAB019–021 y holdout gas LAB016–018. Ecuaciones explícitas, muestras por variable, biomasa y G+F por densidad, límites, convergencia, parámetros y conclusiones dentro del notebook, sin exportar ajustes.
- Verificación: seis ajustes químicos convergentes, referencia gas reproducida en seis LAB y casos nulos comprobados; 16 figuras y revisión visual de CO2/G+F, SOURCE limpio, paridad SOURCE/EXECUTED y cero errores. 92 archivos originales protegidos por hashes; sin cambios en módulos, configuraciones, pyomo-doe ni operaciones Git.

### 2026-10-29 19:51 -03:00

- Archivos: notebooks/preparing_data/preparing_data.source.ipynb, notebooks/preparing_data/preparing_data.executed.ipynb.
- Cambio: adaptado preparing_data desde recalibration de pyomo-doe a las rutas existentes de wine-fermentation; naturales depurados y sintéticos normalizados en memoria con funciones mínimas incorporadas, calendario/reloj/logs locales. Conservadas 14 matrices químicas y dos térmicas. Añadida auditoría de reglas del prototipo temprano frente a rutas theta_full/theta_new/actual, horarios/dosis y exclusiones Oculyze.
- Verificación: ejecución completa sin errores; 16 experimentos, 70 biomasas naturales, 16 figuras, SOURCE limpio y paridad con EXECUTED, revisión visual YAN y hashes de entradas. Sin duplicar datos, CSV/PNG auxiliares, modificaciones en modelos/ajustes ni escrituras en pyomo-doe; sin commit/push.

### 2026-10-29 20:37 -03:00

- Archivos: data/cleaned/natural/lab004_009/observations_legacy_treatment_v1.csv, notebooks/diagnostics/08_transporter_legacy_data_treatment.source.ipynb, notebooks/diagnostics/08_transporter_legacy_data_treatment.executed.ipynb.
- Cambio: nueva versión de observaciones con YAN<=20mg/L a0, agotamiento manual LAB006122h y ese dato a0, cortes estrictos YAN+12h/X+24h; conservadas filas y demás sustancias. Recalibrado el modelo original con transportadores sólo con química LAB004–009 y después gas LAB019–021; comparación y validación reservada. LAB017 consolidado en un pulso0.28g/L en memoria para ambos modelos, sin editar fuentes.
- Verificación: dos arranques químicos convergentes, restricciones de rendimientos, campos/unidades y cortes comprobados;13 figuras con muestras conservadas/transformadas/excluidas, revisión visual YAN, SOURCE limpio, paridad y cero errores. Reinicio documentado con límite20000 evaluaciones RHS (un rechazo numérico). Hashes originales intactos; sin modificar modelos/ajustes ni pyomo-doe, sin commit/push.

### 2026-10-29 22:05 -03:00

- Archivos: notebooks/diagnostics/08_transporter_legacy_data_treatment.source.ipynb, notebooks/diagnostics/08_transporter_legacy_data_treatment.executed.ipynb.
- Cambio: rehecho el mismo08 con la MISMA tabla tratada lab004–009 (umbral/cortes/LAB006122h), sin modificar datos. Inicialización nominal theta_multistart_07 y perturbación del mismo vector; bloque fijo también procedente de07, parámetros de transportadores explícitos. Vector efectivo y procedencia incorporados al SOURCE, sin dependencia de ejecución de pyomo-doe. Química y gas recalibrados con particiones originales; parámetros nuevos completos impresos en JSON dentro del EXECUTED y tabla de residuo YAN Nx/Ntr.
- Verificación: dos arranques convergentes, límites de rendimiento y hashes de originales/tabla intactos; cero rechazos numéricos.13 figuras, revisión visual CO2, SOURCE limpio, paridad SOURCE/EXECUTED y cero errores. Sin nuevos notebooks/datos/configuraciones ni cambios en pyomo-doe; sin commit/push.

### 2026-10-29 22:44 -03:00

- Archivos: notebooks/diagnostics/08_transporter_legacy_data_treatment.source.ipynb, notebooks/diagnostics/08_transporter_legacy_data_treatment.executed.ipynb, data/cleaned/natural/lab004_009/observations_original_yan_treated_v1.csv.
- Cambio: rehecho el mismo08 desde theta_full nominal y una perturbación derivada, con Excel original LAB004–009 y sus76 biomasas sin correcciones ni cortes de biomasa. Nueva tabla separada con sólo YAN<=20mg/L a0, exclusiones tardías YAN+12h y LAB006122h=0/corte posterior134h. Química recalibrada con LAB004–009; gas reajustado sólo LAB019–021 y holdout LAB016–018. Leyendas explícitas Referencia transportadores de04/Nueva recalibración datos originales+YAN tratado.
- Verificación: ejecución completa del SOURCE definitivo, dos arranques terminados por xtol, rendimientos restringidos (Yef inicial proyectado al límite factible), cero rechazos numéricos;13 figuras con muestras y tabla final Nx/Ntr, revisión visual, paridad SOURCE/EXECUTED y cero errores. Documentado empeoramiento de CO2 holdout y kLa en límite20h^-1. Hashes originales y datos previos intactos, sin modificar módulos/configuraciones ni pyomo-doe; sin commit/push.

### 2026-10-29 23:02 -03:00

- Archivos: notebooks/diagnostics/09_historical_single_core.source.ipynb, notebooks/diagnostics/09_historical_single_core.executed.ipynb.
- Cambio: comparación histórica de dos cores frente a propuesta de un core nutrido sin O2, con theta_nv2 congelado. Recalibración separada sólo CO2 LAB019–021, holdout LAB016–018: etapa de tres coeficientes y etapa ampliada con cinco parámetros nutricionales, tres arranques por caso/etapa. Medianas RAW por volumen remanente, objetivo censurado y horizontes comunes; LAB017 un pulso0.28g/L para ambos. Ecuaciones, entradas, cotas, parámetros y resultados completos dentro del notebook.
- Verificación:12 arranques convergentes; propuesta integra una sola química por LAB y no accede a core0. Igualdad exacta de química, rendimientos restringidos, fuente histórica contrastada con código original y balance del depósito comprobados.12 figuras con muestras químicas/biomasa/G+F por densidad y medianas CO2; revisión visual, SOURCE limpio, paridad y cero errores. Documentado empeoramiento holdout al liberar nutrición y parámetros en cotas. Hashes previos intactos; sin modificar módulos, parámetros ni pyomo-doe; sin CSV/PNG de resultados, commit ni push.

### 2026-10-29 23:28 -03:00

- Archivos: notebooks/diagnostics/10_single_core_A_sensitivity.source.ipynb, notebooks/diagnostics/10_single_core_A_sensitivity.executed.ipynb.
- Cambio: sensibilidad exclusiva de A=0.3/0.2/0.1/0 en propuesta de un core sin O2, partiendo del E1 del09 a precisión completa; theta_nv2 y demás parámetros congelados, sin optimización. Comparaciones separadas por alternativa con registro completo, pico posterior24h, cola desde32h y Cd, medianas medidas y métricas por LAB.
- Verificación: referencia reproduce09, seis integraciones y ningún core0, restricciones de rendimiento, balance y hashes previos intactos.12 figuras revisadas, SOURCE limpio, paridad y cero errores. Documentado menor pico del holdout y cola ligeramente peor, además de deterioro del pico de LAB021. Sin cambios en modelos/ajustes originales, sin CSV/PNG externos al proyecto, sin commit/push ni escrituras en pyomo-doe.

### 2026-10-30 00:32 -03:00

- Archivos: notebooks/diagnostics/11_single_core_release_O2.source.ipynb, notebooks/diagnostics/11_single_core_release_O2.executed.ipynb.
- Cambio: seis escenarios de un core con A=0: liberación histórica2.348168/1.174084/0.587042h^-1 con/sin O2, theta_nv2 y demás parámetros fijos. O2 usa únicamente biomasa nutrida; sin optimización ni core0. Comparaciones por pares con medianas medidas, arranque, pico24h, cola desde32h, depósito y factorO2, métricas completas por LAB.
- Verificación: referencia reproduce10; seis integraciones químicas, rendimientos y balance comprobados, hashes originales intactos.26 figuras, revisión visual, paridad SOURCE/EXECUTED, SOURCE limpio y cero errores. Documentado beneficio medio de liberación menor en cola y de O2 en arranque, con compromisos del pico y limitaciones LAB021. Sin modificaciones en modelos/ajustes/datos anteriores ni pyomo-doe, sin CSV/PNG externos al proyecto, commit ni push.

### 2026-10-30 01:01 -03:00

- Archivos: notebooks/diagnostics/12_single_core_transient_release.source.ipynb, notebooks/diagnostics/12_single_core_transient_release.executed.ipynb.
- Cambio: ensayo de k(t)=k0[1+B h(t)], k0=0.587042h^-1 y tiempos4/12h fijos, un core, A=0, O2 activo y theta_nv2 congelado. Sólo B común ajustado con LAB019–021 mediante barrido/refinamiento acotado0–3; holdout LAB016–018. Comparación B=0 con mediciones, arranque/pico/cola, Cd y k(t).
- Verificación: B=0 reproduce11, B ajustado0.898533, fuente idéntica, balance del depósito y gas adicional/inventario comprobados, seis integraciones y ningún core0. Seis figuras revisadas, SOURCE limpio, paridad y cero errores; hashes previos intactos. Documentadas mejora pequeña del holdout, cola peor y máximos demasiado adelantados. Sin cambios en modelos/ajustes/datos anteriores ni pyomo-doe, sin CSV/PNG de resultados, commit ni push.

### 2026-10-30 01:06 -03:00

- Archivos: notebooks/diagnostics/12_single_core_transient_release.source.ipynb, notebooks/diagnostics/12_single_core_transient_release.executed.ipynb.
- Cambio: eliminados ambos notebooks del ensayo12 de liberación transitoria por solicitud explícita del usuario; descartada esta variante. No se modifican otros notebooks, modelos, datos o parámetros, ni pyomo-doe.
- Verificación: comprobadas rutas absolutas y ausencia de ambos archivos tras eliminación; conservado el historial previo.

### 2026-10-30 01:17 -03:00

- Archivos: notebooks/diagnostics/13_single_core_original_M_sensitivity.source.ipynb, notebooks/diagnostics/13_single_core_original_M_sensitivity.executed.ipynb.
- Cambio: completada sensibilidad del M original, un core y theta_nv2 fijos, O2 activo y transferencia constante k0.587042h^-1. Variaciones independientes A0/0.1/0.2, tau_r1/2/8h y tau_d4/8/24h frente a referencia A0.3/4h/12h; sin optimización. Se distingue del10 (sólo A y otra transferencia) y del09 (ajuste conjunto).
- Verificación: seis integraciones, sin core0; un único parámetro cambia por escenario, balance y rendimientos comprobados, A0 reproduce11.27 figuras por pares con mediciones/registro/pico/cola, revisión visual, SOURCE limpio, paridad y cero errores. Hashes previos intactos; sin cambios en modelos/ajustes/datos anteriores ni pyomo-doe, sin CSV/PNG externos al proyecto, commit ni push.

### 2026-10-30 02:19 -03:00

- Archivos: notebooks/diagnostics/14_single_core_nutrition_dose.source.ipynb, notebooks/diagnostics/14_single_core_nutrition_dose.executed.ipynb.
- Cambio: sensibilidad de pulsos al100/75/50% en una química nutrida y en M, theta_nv2 y todos los coeficientes fijos, O2 activo, sin recalibración. Auditoría de masas SFX/FDA en Excel originales y de discrepancia80/140mg/L de YAN; sin corregir registros ni asumir masas verificadas para016–018. Comparación CO2 y seis estados con mediciones.
- Verificación:18 integraciones, ningún core0, referencia reproduce13, balance y hashes originales comprobados.18 figuras por pares, revisión visual, SOURCE limpio, paridad y cero errores. Documentada mejora media CO2 holdout y contrapartidas químicas; sin CSV/PNG externos al proyecto, modificaciones de Excel/modelos/ajustes previos o pyomo-doe, commit ni push.

### 2026-10-30 02:58 -03:00

- Archivos: notebooks/diagnostics/15_single_core_reconstructed_dose_volume.source.ipynb, notebooks/diagnostics/15_single_core_reconstructed_dose_volume.executed.ipynb.
- Cambio: reconstrucción del accidente nutricional016–018 con500mL en agua, retorno140s, caudales230/235/245s por100mL, posterior200mL a017. Balance de pulmón para X,N,G,F,E,Cd,O2 y trazadorYAN externo; aplicación como salto de masa/volumen, conforme al modelo previo. Comparación con nominal100% del14, theta_nv2 y todos los parámetros fijos, O2 activo;019–021 idénticos. Volumen final2.1/2.140426/2.1L y aportes128.408/246.678/128.097mg/L por2L.
- Verificación: balances globales/depósito, reproducción de referencia14 antes de conversión de unidades, observaciones/predicciones normalizadas al mismo volumen, muestras químicas completas.12 figuras revisadas, SOURCE limpio, paridad y cero errores; hashes previos intactos. Documentadas aproximación instantánea, supuestos del agua/pulmón y falta de muestras químicas postpulso016–018. Sin optimización, core0, CSV/PNG externos al proyecto, cambios de originales/pyomo-doe, commit ni push.

### 2026-10-30 03:08 -03:00

- Archivos: notebooks/diagnostics/15_single_core_reconstructed_dose_volume.source.ipynb, notebooks/diagnostics/15_single_core_reconstructed_dose_volume.executed.ipynb.
- Cambio: rehecho el mismo15 con X0=0.20g/L (6.67 millones viables/mL redondeados) sólo016–018, en ambos casos nominal/reconstruido. Recalculadas química, O2, Cd y composición retornada; mantenidos019–021, theta_nv2, reconstrucción hidráulica, parámetros y datos. Reemplazadas conclusiones anteriores con nuevos resultados y contexto numérico de X0=0.39.
- Verificación: sólo inicialX cambia en016–018,019–021 reproducen resultados previos; balances y hashes restantes intactos, sin optimización ni core0.12 figuras con muestras revisadas, SOURCE limpio, paridad y cero errores. Documentado resultado mixto: mejor ventana de pico/cola reconstruida, peor registro completo frente aX0=0.39. Sin nuevos notebooks ni CSV/PNG de resultados, sin cambios en datos/modelos/ajustes o pyomo-doe, commit ni push.

### 2026-11-01 20:38 -0300

- Archivos: `notebooks/diagnostics/16_zenteno_recalibration_legacy_treatment.source.ipynb`, `notebooks/diagnostics/16_zenteno_recalibration_legacy_treatment.executed.ipynb`.
- Cambio: recalibración química histórica de cinco estados con LAB004–009 depurados, YAN<=20mg/L a0, cortes agotamiento+12h y LAB006122h=0; biomasa sin cortes adicionales y sigmaX=.50g/L estimada desde réplicas. Nutrición causal suavizada3h, sin pulso inicial ni aN/KNa. Ajuste propio kLa/ganancia con019–021 y holdout016–018, muestras usadas/transformadas/excluidas y química reservada con biomasa/G+F por densidad. Frontera de crecimiento al agotarse G/F, igual que los modelos actuales, documentada explícitamente; tolerancias por estado y mínimos registrados.
- Verificación: dos arranques químicos convergentes, dosis y balances del depósito/retiradas, prueba de frontera y equivalencia de dinámica histórica en dominio positivo;13 figuras con revisión visual, SOURCE limpio, paridad con EXECUTED y cero errores. Datos, módulos, configuraciones y notebooks anteriores intactos por hashes; sin exportaciones de resultados, commit ni push.

### 2026-11-01 21:08 -0300

- Archivos: `notebooks/diagnostics/16_zenteno_recalibration_legacy_treatment.source.ipynb`, `notebooks/diagnostics/16_zenteno_recalibration_legacy_treatment.executed.ipynb`.
- Cambio: rehecho el mismo notebook fijando Kn de Zenteno a0.01g/L a23C, equivalente Kn0=0.00825786022432g/L a20C mediante la ley térmica existente. Nueve parámetros químicos libres y reajuste propio de kLa/ganancia; mismos datos depurados, tratamientos YAN, ponderación biomasa, nutrición3h y holdout016–018, sin escenarios adicionales.
- Verificación: dos arranques convergentes, Kn excluido del optimizador y referencia térmica comprobada; kLa=0.1159583841h^-1, ganancia=0.6200676664. RMSE medio gas calibración0.1439781 y holdout0.1368005g/(L.h); MSE químico ponderado3.9745241. Trece figuras revisadas, validación nbformat, SOURCE limpio, paridad y cero errores; balances y hashes de archivos previos intactos. Sin nuevos notebooks, modificaciones de datos/configuraciones/modelos ni exportaciones de resultados.

### 2026-11-01 21:41 -0300

- Archivos: `notebooks/diagnostics/16_zenteno_recalibration_legacy_treatment.source.ipynb`, `notebooks/diagnostics/16_zenteno_recalibration_legacy_treatment.executed.ipynb`.
- Cambio: mismo notebook recalibrado con Kd0=0.00044h^-1 de Zenteno y Kn previamente fijo; ocho parámetros químicos libres, kLa/ganancia reajustados. Mismos datos, iniciales, tratamientos YAN, sigmaX, nutrición3h y holdout016–018; mortalidad por umbral conservada.
- Verificación: dos arranques convergentes y cero rechazos; ambos parámetros excluidos del optimizador y comprobados al terminar. MSE químico4.0022431, Yxn7.0772948, kLa0.1163346671h^-1, ganancia0.6196888692; RMSE gas medio calibración0.1450434 y holdout0.1362914g/(L.h). Trece figuras, revisión visual, validación nbformat, SOURCE limpio, paridad y cero errores; balances y hashes previos intactos. La caída tardía se atenúa, persiste sobreestimación de biomasa. Sin nuevos notebooks ni cambios de datos/configuraciones/modelos.

### 2026-11-01 21:56 -0300

- Archivos: `notebooks/diagnostics/16_zenteno_recalibration_legacy_treatment.source.ipynb`, `notebooks/diagnostics/16_zenteno_recalibration_legacy_treatment.executed.ipynb`.
- Cambio: eliminado aporte suavizado3h; nutrición aplicada como salto instantáneo de YAN, dosis y horarios intactos, muestra previa al salto en coincidencias. Recalibrados ocho parámetros químicos y kLa/ganancia, manteniendo Kn/Kd0 de Zenteno, datos depurados, tratamientos YAN, ponderación biomasa y holdout016–018. Saltos pre/post visibles y usados al interpolar la fuente de gas.
- Verificación: ambos arranques convergen sin rechazos; comprobación de cada dosis y ausencia de cambios instantáneos de X/G/F/E; tabla de saltos incluida. MSE químico4.0453035, Yxn7.0802129, kLa0.1155842472h^-1, ganancia0.6204348696; RMSE medio gas calibración0.1442769 y holdout0.1359746g/(L.h). Trece figuras revisadas, nbformat válido, SOURCE limpio, paridad y cero errores; balances y hashes previos intactos. Sin nuevos notebooks ni cambios de datos/configuraciones/modelos.
