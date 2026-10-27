# Wine fermentation

Proyecto independiente para revisar los datos y reconstruir el modelo de fermentación de mosto natural.

## Pruebas de compatibilidad disponibles

| Prueba | SOURCE | EXECUTED |
|---|---|---|
| Estados LAB004–009, tres theta | [Código](notebooks/01_current_model_theta_comparison.source.ipynb) | [Resultados y figuras](notebooks/01_current_model_theta_comparison.executed.ipynb) |
| Química y CO₂ LAB016–021, formulación principal v3 | [Código](notebooks/02_current_co2_v3_comparison.source.ipynb) | [Resultados y figuras](notebooks/02_current_co2_v3_comparison.executed.ipynb) |

Estas pruebas conservan el modelo actual de siete estados, incluyendo biomasa muerta, glicerol, mortalidad y mantenimiento atenuado. La capa de CO₂ conserva oxígeno, activación, trayectorias con/sin nutrición, multiplicador transitorio y reservorio implícito. Constituyen una referencia de migración; todavía no aplican las simplificaciones discutidas para el modelo nuevo.

## Parámetros

Los tres vectores de diecisiete parámetros están en `configs/theta/`:

- `theta_full.json`: vector natural completo histórico.
- `theta_new.json`: reajuste de la rama `recalibration`; no es el ajuste con rendimientos restringidos.
- `theta_defaults.json`: definición utilizada por los notebooks históricos y v3: `theta_full` con **solo seis** parámetros heredados (`sN`, `qXG`, `qXF`, `sG`, `sF`, `m0`) sustituidos por sus defaults. No es el vector completo `DEFAULT_THETA`.

La comparación de estados no recalibra ningún theta. En CO₂ los theta también permanecen congelados: Z1 ajusta únicamente `matrix_gain`; Z2 ajusta `kCO2_release_h`, `CO2sat_scale` y `matrix_gain`. Se presentan ajuste conjunto descriptivo y transferencias entre LAB019–021 y LAB016–018. Las mezclas positivas exploratorias de v3 no se incluyen porque cambian la formulación.

## Ejecución

Usar el entorno oficial Conda `fermentation`, activado con sus scripts de `activate.d`. Abrir un SOURCE con ese kernel y ejecutar todas sus celdas desde un kernel limpio. El notebook localiza la raíz del proyecto y carga las funciones de `src/`; no requiere instalación editable. No se ha instalado ni actualizado ningún paquete.

Los SOURCE se conservan sin outputs ni contadores. Los EXECUTED contienen las mismas celdas de código y Markdown, ejecutadas sin errores. Todas las figuras permanecen inline; los CSV numéricos están en `results/compatibility_states/` y `results/compatibility_co2_v3/`.

## Organización y datos

- `data/original/`: fuentes conservadas, sin sobrescribirlas. `CO2_FILT` identifica exportaciones previamente filtradas. La ubicación de un libro como fuente no convierte sus valores heredados u homologados en mediciones directas.
- `data/cleaned/`: datos depurados separados. LAB004–012 tiene Excel original y depurado independientes. LAB019–021 conserva su CSV YAN corregido y el Excel original separado; todavía no se ha creado otro Excel depurado.
- `data/processed/`: reservado para la preparación nueva.
- `data/sources.csv`: inventario de la copia inicial y sus hashes.
- `data/compatibility/`: entradas derivadas mínimas y referencias archivadas necesarias **solo para estas pruebas autorizadas**. No sustituyen las fuentes originales ni definen el futuro procedimiento de preparación.
- `configs/compatibility_provenance.json`: procedencia y hashes de las funciones, vectores y entradas de compatibilidad.
- `src/wine_fermentation/current_model.py`: ecuaciones, integrador y preparación mínima actuales; funciones extraídas estáticamente y verificadas sin cambiar sus cuerpos.
- `src/wine_fermentation/current_co2.py`: funciones compartidas de fuente y simulación utilizadas por la prueba v3. Las funciones específicas de filtrado y ajuste están dentro de su SOURCE.
- `tests/reference/original_core_predictions.npz`: referencias del RHS y del integrador para comprobar el traslado.
- `references/Zenteno_2010.pdf`: fuente bibliográfica.
- `docs/reference/temporal_audit_lab001_018_2026-09-09.md`: auditoría histórica conservada sin editar. Sus rutas y conclusiones corresponden a su contexto original; no es la especificación del modelo nuevo.

El Excel natural original procede de `main`, commit `3b1d20d99c08e7186b14802b37db964571de0ca3`; el depurado y `theta_new`, de `recalibration`, commit `16a8500ac3ca79260e0ba59f9657f82724a2f2de`. Los datos completos de CO₂ y temperatura LAB019–021 son archivos reales materializados desde los objetos LFS. Los notebooks nuevos no leen ni importan archivos desde `pyomo-doe` o su `.git`.

## Verificaciones y alcance

`results/notebook_execution_checks.json` registra identidad SOURCE/EXECUTED, figuras, errores, paridad y conservación de fuentes. El RHS y las trayectorias de comprobación coinciden con las referencias originales; también se comparan las observaciones procesadas y las curvas v3 con parámetros congelados.

Las referencias CSV de comparación se leen con `float_precision='round_trip'`: redondear tiempos casi coincidentes con un pulso puede alterar la comparación puntual del flujo. Esta precisión de lectura no cambia las ecuaciones ni deduplica la malla histórica.

`results/compatibility_co2_v3/refit_vs_archived.csv` muestra por separado los nuevos reajustes Z1/Z2 frente a los archivados. La equivalencia de ecuaciones se comprueba con parámetros congelados; un reajuste local puede terminar en un mínimo numérico distinto. No se afirma unicidad ni óptimo global.

Las condiciones iniciales y nutriciones se mantienen según cada prueba histórica. Los horarios propuestos de LAB004–009 siguen siendo supuestos, no registros confirmados. Que las pruebas se ejecuten y reproduzcan referencias no valida todos los mecanismos ni resuelve los rendimientos físicos históricos.

Git no está inicializado y no se modificó el repositorio anterior. La especificación del modelo definitivo y cualquier simplificación se desarrollarán por separado.
