# Wine fermentation

Modelo de mosto natural con cinco estados: biomasa viable X, YAN N, glucosa G, fructosa F y etanol E.
La mortalidad se conserva en X. Se eliminaron los estados de biomasa muerta y glicerol, y los dos parámetros de producción de glicerol.
La capa de CO₂ conserva su formulación histórica v3 completa.

## Notebooks y referencias

| Ensayo | SOURCE (sin resultados) | EXECUTED (resultados y figuras) |
|---|---|---|
| Calibración de las tres formulaciones (experimental) | [Código](notebooks/03_calibrate_models.source.ipynb) | [Resultados](notebooks/03_calibrate_models.executed.ipynb) |
| Comparación de las tres formulaciones (experimental) | [Código](notebooks/04_compare_models.source.ipynb) | [Resultados](notebooks/04_compare_models.executed.ipynb) |
| Recalibración química LAB004–009 | [Código](notebooks/historical/01_recalibration_theta_nv2.source.ipynb) | [Resultados](notebooks/historical/01_recalibration_theta_nv2.executed.ipynb) |
| Evaluación química LAB019–021 y CO₂ LAB016–021 | [Código](notebooks/historical/02_co2_theta_nv2.source.ipynb) | [Resultados](notebooks/historical/02_co2_theta_nv2.executed.ipynb) |
| Balance de CO₂: etanol y crecimiento, completo y por tramos | [Código](notebooks/diagnostics/01_co2_mass_balance.source.ipynb) | [Resultados](notebooks/diagnostics/01_co2_mass_balance.executed.ipynb) |

Ejecutar SOURCE desde un kernel limpio del entorno Conda oficial `fermentation`, activado completamente con sus scripts de `activate.d`.
Los notebooks localizan la raíz y leen `src/`; no requieren instalar el paquete ni leer `pyomo-doe`.
Los SOURCE y EXECUTED contienen las mismas celdas. Los SOURCE de recalibración vuelven a ejecutar sus ajustes; el diagnóstico solo evalúa los datos y los theta existentes. Para consultar curvas abrir EXECUTED.

## Parámetros y recalibración

`configs/theta/theta_full.json` y `theta_new.json` son copias históricas intactas en la parametrización efectiva anterior.
El cargador las convierte de forma algebraica a parámetros físicos, sin corregir sus valores.
`theta_nv2.json` contiene los 15 parámetros físicos del modelo reducido; **no es intercambiable directamente con un vector antiguo de 17 parámetros**.
`theta_defaults.json` queda como referencia de los notebooks históricos.

La optimización parte exactamente de theta_full. Como su Y_E/F excede 0.5114, SLSQP admite ese inicio no factible;
después se refina mediante mínimos cuadrados acotados. Ambos rendimientos de etanol están limitados a 0.5114 g/g.
Se ajustan mu0, Yxn, betaG0, betaF0, Yeg, Yef, Kig0, Kie0 y Kd0.
Se mantienen Kn0, Kg0, Kf0, Yxg, Yxf y m0 en theta_full. Fijar magnitudes físicas difiere de fijar sus antiguos cocientes s/q.
El objetivo usa muestras posteriores a la inicial de X, N, G, F y E de LAB004–009 depurados, con los errores de medición históricos.
No se ajustan iniciales, horarios de nutrición, temperatura ni leyes térmicas. Intentos de integración con estados negativos sustanciales se rechazan.
Las cotas operativas y el inicio exacto se registran en el notebook y los resultados. No se afirma óptimo global ni identificabilidad.

En CO₂ se comparan primero los tres theta con los mismos coeficientes de capa congelados del ensayo anterior.
Después Z1 ajusta ganancia y Z2 liberación, escala de saturación y ganancia, conservando la fuente, oxígeno y nutrición.
LAB019–021 no participa en la recalibración química. Si se usa para calibrar gas, es entrenamiento de gas;
la transferencia de gas se evalúa por separado en LAB016–018 y en sentido inverso. `all_six` es descriptivo.

## Organización

- `src/wine_fermentation/model.py`: cinco estados y parámetros físicos.
- `src/wine_fermentation/co2.py`: funciones históricas de CO₂ conectadas a cinco estados.
- `src/wine_fermentation/data.py`: preparación común LAB004–009.
- `notebooks/`: los dos ensayos activos, cada uno SOURCE/EXECUTED.
- `notebooks/historical/`: los cuatro notebooks de comprobación anteriores, con sus resultados retenidos y sus imports actualizados.
- `src/wine_fermentation/historical/`: implementación de siete estados que permite ejecutar esas comprobaciones sin usar el modelo nuevo.
- `configs/recalibration_nv2.json`: selección de parámetros, convergencia y objetivo químico.
- `results/co2_fit_parameters.csv`: único resultado externo, con los coeficientes Z1/Z2 de CO₂ del ensayo nuevo a precisión completa.
- `configs/co2_reference_parameters.csv`: coeficientes anteriores, congelados para la comparación; no se sobrescriben al ejecutar los notebooks históricos.
- `data/original/` y `data/cleaned/`: fuentes originales y depuradas **separadas e intactas**.
- `data/compatibility/`: entradas derivadas mínimas y referencias de las pruebas ya copiadas; no sustituyen los archivos experimentales originales.
- `data/sources.csv`: inventario y hashes de la copia inicial.
- `docs/model.md`: ecuaciones activas y alcance de la reducción.
- `docs/memoria/`: documento de titulación y archivos asociados, conservados sin cambios.
- `docs/reference/`: auditoría temporal conservada por solicitud del usuario.

Los horarios propuestos de nutrición LAB004–009 siguen siendo supuestos, no registros confirmados.
Se conserva la diferencia entre iniciales medidas, homologadas o estimadas de los ensayos anteriores.
La reproducción numérica no valida por sí misma los mecanismos históricos de CO₂.

## Política de resultados

Las figuras, tablas y comprobaciones se consultan en los EXECUTED sin ejecutar ni leer `results/`. Los notebooks activos y archivados no exportan PNG, trayectorias, métricas, trazas ni checkpoints auxiliares. El notebook químico conserva theta_nv2 y su registro en `configs/`; el de CO₂ guarda únicamente `results/co2_fit_parameters.csv`. Para recalcular o actualizar un ajuste se ejecuta su SOURCE. Las ejecuciones antiguas de los EXECUTED se conservaron; la limpieza no repitió optimizaciones.

El diagnóstico CO₂ guarda un único CSV convertido en data/processed/co2_mass_balance_lab016_021_g_l_h.csv y lo relee antes de integrar. El EXECUTED muestra áreas sombreadas de las señales cruda y filtrada GUI, con límites, unidades y cobertura. En LAB019–021 usa el volumen remanente: 2 L cargados menos las seis retiradas de 50 mL, incluida m1; las nutriciones no añaden volumen. Al inocular quedan 1.95 L y antes/después de m12 quedan 1.75/1.70 L. LAB016–018 conservan 2 L. El factor histórico 0.74 sigue siendo un supuesto. La integral principal usa ahora la señal cruda nativa; Hampel/cero/offline quedan como sensibilidad.

## Comparación de formulaciones experimentales

Los paquetes models/historical, models/without_transporters y models/with_transporters separan la referencia actual de cinco estados y las dos hipótesis de nutrición. La antigua carpeta historical conserva por separado el modelo de siete estados. Los modelos actuales model.py y co2.py permanecen intactos.

Ejecutar notebooks/03_calibrate_models.source.ipynb para los ajustes químicos y de gas; notebooks/04_compare_models.source.ipynb carga esos parámetros y compara las tres variantes sin optimizar. Las parejas EXECUTED conservan figuras y tablas. Los parámetros nuevos se guardan exclusivamente en configs/models/. Solubilidad aún provisional: consultar docs/model_comparison.md; los resultados no validan una ley de Henry.

Los ensayos anteriores 01_recalibration_theta_nv2 y 02_co2_theta_nv2 se archivaron sin cambiar su contenido en notebooks/historical/. Para el estudio nuevo usar 03_calibrate_models y 04_compare_models. Los notebooks de diagnostics y data_graphics permanecen en sus carpetas.

La partición principal de CO₂ calibra LAB019–021 y reserva LAB016–018 como holdout; también se ejecuta la inversa. Cada gas_fit.json conserva ambas particiones. El histórico conserva ecuaciones y química, reajustando sólo los tres coeficientes de CO₂ al mismo objetivo de los modelos nuevos. La química se mantiene calibrada con LAB004–009; no cambia al invertir la partición de gas.
