# Auditoría de parámetros: 03, 07 y 08

Revisión del código efectivo y resultados guardados al 31 de octubre de 2026. No se repitieron ajustes. El 03 es `notebooks/03_calibrate_models`, no diagnostics/03 (que sólo hace sensibilidad).

## Parámetros químicos libres y cotas

Los diez comunes son libres en ambos modelos del 03 y en las recalibraciones de transportadores de 07/08. Valores iniciales de 03 y del 08 definitivo: theta_full convertido a parámetros físicos. En 07 los arranques se describen más abajo.

| Parámetro | Significado | Inicio theta_full físico | Cota inferior | Cota superior |
|---|---|---:|---:|---:|
| `mu0` | Tasa máxima de crecimiento | 0.0787279167845 | 0.05 | 1 |
| `betaG0` | Tasa fermentativa de glucosa | 0.428878002997 | 0.1 | 10 |
| `betaF0` | Tasa fermentativa de fructosa | 3.44039917477 | 0.1 | 10 |
| `Kn0` | Semisaturación de YAN para crecimiento | 0.00899598968508 | 0.0001 | 0.5 |
| `Kig0` | Inhibición de consumo de fructosa por glucosa | 17.8452129277 | 5 | 1000 |
| `Kie0` | Inhibición por etanol | 24.8954757352 | 5 | 1000 |
| `Kd0` | Coeficiente de mortalidad | 0.000150249547897 | 1e-05 | 0.05 |
| `Yxn` | Rendimiento de biomasa por nitrógeno de crecimiento | 3.73465315687 | 1 | 100 |
| `Yeg` | Rendimiento etanol/glucosa | 0.25039485163 | 0.1 | 0.5114 |
| `Yef` | Rendimiento etanol/fructosa | 0.684926876791 | 0.1 | 0.5114 |

Yef inicial de theta_full=0.684926876791 supera la cota; se proyecta a 0.5113999999 antes del ajuste nominal. Esto es una corrección del inicio factible, no una ampliación de la cota.

| Modelo | Parámetro adicional libre | Inicio de configuración | Cotas |
|---|---|---:|---|
| without_transporters | `aN` | 0.3 | [1e-06, 5] |
| without_transporters | `KNa` | 0.03 | [0.0001, 1] |
| with_transporters | `eta0` | 0.01 | [1e-05, 0.3] |
| with_transporters | `KTr` | 0.03 | [0.0001, 1] |
| with_transporters | `aTr` | 1 | [0.01, 30] |
| with_transporters | `alpha` | 0.7 | [0.02, 0.98] |

Estos inicios adicionales son valores nominales de `extra_initial` en las configuraciones del modelo; no proceden de theta_full ni son valores experimentales identificados. Sin transportadores se ajustan 12 parámetros; con transportadores, 14.

## Parámetros químicos fijos

| Parámetro | Valor conservado | Procedencia |
|---|---:|---|
| `Kg0` | 4.40077541912327 | betaG0/sG de theta_full |
| `Kf0` | 19.2960835081187 | betaF0/sF de theta_full |
| `Yxg` | 0.966093555347787 | mu0/qXG de theta_full |
| `Yxf` | 1.10989585294856 | mu0/qXF de theta_full |
| `m0` | 0.0183385793928771 | m0 de theta_full, sin conversión |
| `YTrN` | 6.25 | Sólo transportadores: constante de `extra_initial`, conservada en 03/07/08; no pertenece a theta_full |

En 07 el bloque fijo se hereda del fit con transportadores guardado por 03; ese bloque proviene originalmente de theta_full, salvo YTrN. En 08 se reconstruye directamente desde theta_full + extra_initial. Los valores efectivos fijos son iguales en los tres.

Fijar Kg0/Kf0/Yxg/Yxf en notación física no significa conservar los antiguos sG/sF/qXG/qXF: al cambiar beta o mu, esos cocientes efectivos cambiarían. Kn0, a diferencia de la recalibración theta_nv2, aquí sí es libre.

## Diferencias de calibración y arranques

- **03:** dos modelos distintos, datos depurados LAB004–009, una optimización química por modelo desde theta_full + sus extras. En el SOURCE actual `REFIT_CHEMISTRY=False`: reutiliza los fit.json. Para repetir química se activa esa bandera; el gas sí se reajusta al ejecutar el notebook.
- **07 congelado:** todo el fit químico del 03 se conserva. Referencia B=1; escenario inicial reducido B0=.2, tau=8 h; escenario pérdida delta=.01 h^-1. También se conserva el gas del ajuste principal.
- **07 recalibrado:** referencia ajusta los 14 parámetros; capacidad reducida ajusta los 14 + B0/tau (16); pérdida ajusta los 14 + delta (15). No se congelan los 14 al liberar los extras. Usa los mismos datos depurados.
- **07 arranques de referencia:** primero fit del 03; segundo theta_full + extra_initial en los parámetros libres. El bloque fijo permanece el del fit del 03.
- **07 arranques de capacidad:** ambos usan como base el fit del 03, con B0/tau=.2/8 h y .8/2 h.
- **07 arranques de pérdida:** ambos usan como base el fit del 03, con delta=.01 y .002 h^-1.
- **08 definitivo:** modelo original con transportadores, sin B0/tau/delta. Ajusta otra vez los 14 originales. Inicio nominal theta_full + extra_initial; segundo inicio multiplica sólo los libres por una perturbación lognormal sigma=.2, semilla20261029. Ambos se proyectan a cotas. El fit del 03 es referencia de comparación, no semilla química de 08.
- **08 datos:** Excel original y sus 76 biomasas, sin correcciones/exclusiones de biomasa de la versión depurada. Sólo YAN tratado: <=20mg/L a0, LAB006122h=0 y observaciones posteriores al agotamiento+12h excluidas. No hay corte tardío de biomasa.289 observaciones químicas t>0.
- El 08 previo pasó por datos depurados tratados y por inicialización theta_multistart_07. Esas revisiones fueron reemplazadas dentro del mismo notebook; no describen el SOURCE vigente.

Extras del 07: B0[.01,1], tau[.25,48]h; delta[1e-7,.05]h^-1. Son cotas exploratorias del notebook. B0 controla capacidad basal inicial, tau su recuperación y delta la pérdida funcional de capacidad basal y Tr. Los casos se ensayan por separado.

## Valores químicos finales

Los valores de 03/08 se muestran con 12 cifras significativas; 07 conserva aquí la precisión de sus tablas guardadas, no cifras adicionales inferidas.

| Parámetro | 03 sin Tr | 03 con Tr | 07 referencia | 07 capacidad reducida | 07 pérdida | 08 definitivo |
|---|---:|---:|---:|---:|---:|---:|
| `mu0` | 0.291046236765 | 0.326718670001 | 0.325026 | 0.311560 | 3.240140e-01 | 0.464011956466 |
| `betaG0` | 0.29497518897 | 0.423987773107 | 0.431025 | 5.153652 | 4.253381e-01 | 0.535434399232 |
| `betaF0` | 0.43389867678 | 0.503605488364 | 0.505355 | 7.758160 | 5.121232e-01 | 0.96342859488 |
| `Kn0` | 0.499940797183 | 0.499414946874 | 0.499968 | 0.500000 | 4.997445e-01 | 0.439431279174 |
| `Kig0` | 45.4801853705 | 83.4193006941 | 80.497165 | 47.331431 | 8.142819e+01 | 41.8894646643 |
| `Kie0` | 326.60177767 | 217.578446888 | 217.332256 | 5.001428 | 2.183304e+02 | 35.8849772021 |
| `Kd0` | 0.000506194777807 | 0.000370364951174 | 0.000359 | 0.000260 | 3.885814e-04 | 0.00411446106098 |
| `Yxn` | 5.43842202596 | 5.70783381134 | 5.671089 | 5.513137 | 5.663313e+00 | 9.01489250998 |
| `Yeg` | 0.505341261553 | 0.489528670103 | 0.495905 | 0.493316 | 4.892722e-01 | 0.471046722969 |
| `Yef` | 0.461675663168 | 0.476609442424 | 0.470183 | 0.474001 | 4.780678e-01 | 0.507794143746 |
| `eta0` | — | 0.00224086118494 | 0.001041 | 0.000018 | 4.891932e-05 | 0.0295382248162 |
| `KTr` | — | 0.265047759275 | 0.325012 | 0.387543 | 9.847960e-02 | 0.00861000492831 |
| `aTr` | — | 0.703208397943 | 0.702922 | 2.164075 | 9.162609e-01 | 0.764900032095 |
| `alpha` | — | 0.932869310152 | 0.937053 | 0.943273 | 9.391755e-01 | 0.529508556893 |
| `aN` | 0.84251579982 | — | — | — | — | — |
| `KNa` | 0.0438836022435 | — | — | — | — | — |
| `B0` | — | — | — | 0.010000 | — | — |
| `tau` | — | — | — | 47.999999 | — | — |
| `delta` | — | — | — | — | 3.429474e-07 | — |

## Gas: ajuste separado de la química

En los modelos con/sin transportadores se ajustan sólo **kLa y gain** con la química recién ajustada ya congelada. La ley es qgas=kLa·max(Cd−Csat,0); observación predicha=gain·qgas. No se recalibra escala de Csat, O2, gate, actividad o M de la formulación histórica.

| Ensayo | Datos de gas | Arranques | Cotas |
|---|---|---|---|
|03 ambos modelos|Principal019–021 y también inversa016–018|kLa=1, gain=.7 para cada partición|kLa[.01,20]h^-1; gain[.05,3]|
|07 recalibrado, cada caso|Sólo019–021; holdout016–018|Gas guardado03 con Tr, y [1,.7]|Las mismas|
|08 nuevo ajuste|Sólo019–021; holdout016–018|Gas guardado03 con Tr, y [1,.7]|Las mismas|

07 congelado y referencia azul del08 mantienen kLa=19.999971437134683 y gain=.604172081169656 del ajuste principal03 con transportadores.

| Resultado gas | kLa | gain |
|---|---:|---:|
|03 without_transporters, train_019_021|19.99999962|0.624818271968|
|03 without_transporters, train_016_018|0.221364864604|0.654560329978|
|03 with_transporters, train_019_021|19.9999714371|0.60417208117|
|03 with_transporters, train_016_018|0.431455209921|0.664574656743|
|07 referencia recalibrada|20|.603227|
|07 capacidad recalibrada|20|.624757|
|07 pérdida recalibrada|20|.602894|
|08 nuevo|20|.603073261463|

La fuente de gas de estas formulaciones es [mu/12.72+(betaG+betaF)/1.05]X:12.72 y1.05 son constantes conservadas. La correlación provisional Csat=1.69exp[-.032(T−20)+.0016E−.0012(G+F)] no se reajusta. Cd0=.907/.730/.829g/L para019/020/021, último provisional, y0 en016–018.

Química: residuos X,N,G,F,E t>0 de004–009, con errores históricos fijos. Gas: medianas horarias RAW, MSE ordinario e igual peso por LAB; no objetivo censurado de diagnostics05/06v2/09.019–021 es validación química y entrenamiento de gas, no holdout conjunto.

## Otras cantidades conservadas

Constantes térmicas y leyes de mortalidad/mantenimiento heredadas de model.py: R=8.314; Eac=59453, Eafe=11000; EaKn/EaKg/EaKf/EaKig/EaKie=46055; Eam=37681; Cde=.0415; Etd=130000. Umbral de atenuación del mantenimiento por azúcar=1g/L. En transportadores, síntesis usa la misma dependencia térmica del crecimiento, sin calibrar otra energía.

Temperatura, horarios y dosis de nutrición, condiciones iniciales medidas/normalizadas y errores de observación no son variables libres de estos ajustes. En08 las iniciales químicas se vuelven a tomar del Excel original. Excepción conceptual: alpha es libre y cambia Nx0=alpha·N0, Ntr0=(1−alpha)·N0 y el reparto de cada dosis; Tr0=0 es fijo. Por tanto, N0 total es entrada, pero su reparto interno no está congelado.

En03/07 los datos químicos depurados proceden de natural_batches.08 sustituye observaciones e iniciales por originales, conservando temperatura de logs y calendario/dosis del cargador.08 consolida LAB017 en un pulso.28g/L para ambos casos;07 conserva los eventos del lector.

## Fuentes locales

- [Configuración sin transportadores](../configs/models/without_transporters/calibration.json)
- [Configuración con transportadores](../configs/models/with_transporters/calibration.json)
- [Conversión de theta_full](../src/wine_fermentation/model.py)
- [Optimizador del03](../src/wine_fermentation/shared/optimization.py)
- [03 SOURCE](../notebooks/03_calibrate_models.source.ipynb)
- [07 SOURCE](../notebooks/diagnostics/07_transporter_capacity_functional_loss.source.ipynb)
- [07 EXECUTED](../notebooks/diagnostics/07_transporter_capacity_functional_loss.executed.ipynb)
- [08 SOURCE](../notebooks/diagnostics/08_transporter_legacy_data_treatment.source.ipynb)
- [08 EXECUTED](../notebooks/diagnostics/08_transporter_legacy_data_treatment.executed.ipynb)

Los ajustes03 están guardados en configs/models; los nuevos07/08 se conservan dentro de sus EXECUTED y no reemplazan esos fit.json.
