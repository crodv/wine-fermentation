# Revisión de diagnostics 02–15

Revisión del estado local al 31 de octubre de 2026. Se contrastaron celdas de código, explicaciones, resultados guardados, módulos/configuraciones utilizados y `AGENT_CHANGELOG.md`. No se volvieron a ejecutar optimizaciones ni se modificaron notebooks, datos o parámetros. Los resultados numéricos siguientes proceden de los EXECUTED presentes.

Existen **15 parejas SOURCE/EXECUTED** en este intervalo: 02–11 y 13–15, más las v2 de 05 y 06. Los 15 pares tienen las mismas celdas y código; los SOURCE están sin resultados, los EXECUTED no contienen errores guardados y reúnen 187 figuras. Eso comprueba coherencia de los archivos, no una nueva reproducción numérica. El 12 fue creado y después eliminado por solicitud del usuario.

## 1. El recorrido y sus ramas

No son quince calibraciones sucesivas del mismo modelo. Hay tres líneas principales:

1. **02–04: localizar el origen de la discrepancia.** Separar producción y transferencia, explorar sensibilidad química y comparar una transferencia inspirada en Zenteno.
2. **05/06 y sus v2: simplificar la fuente histórica de CO₂.** Primero cambiar cómo se usan las trayectorias con/sin nutrición; después recalibrar sólo el gas. En paralelo, **07–08** revisan otra familia: el modelo con transportadores y sus datos de calibración.
3. **09–15: usar una sola simulación química nutrida.** Recalibrar inicialmente el gas (09), después hacer sensibilidades de amplitud, liberación, O₂ y tiempos (10/11/13), y finalmente revisar las entradas experimentales: dosis (14), accidente de mezcla/volumen y biomasa inicial (15).

La rama reciente es **09 E1 → 10 → 11 → 13 → 14 → 15**. No hereda la química recalibrada de 07/08 ni el ajuste E2 de 09. Tampoco conserva todos los escenarios intermedios: 11 fija A=0; 13 vuelve a A=0.3 como referencia para estudiar el transitorio; 14/15 conservan A=0.3.

## 2. Qué significa cada pieza

- **Core químico:** integración de X, N, G, F y E: biomasa viable, YAN, glucosa, fructosa y etanol. El histórico reducido conserva mortalidad, mantenimiento y dependencias térmicas; no integra biomasa muerta ni glicerol.
- **qN / q0:** producción fermentativa calculada usando, respectivamente, la trayectoria química con pulsos de N y una trayectoria auxiliar sin esos pulsos. Antes de modulaciones, q=(44.01/46.07)(betaG+betaF)X.
- **r(t):** rampa que comienza en el primer pulso; **a(t)=1+(gN−1)r(t)**, factor de actividad cuyo valor final de referencia es gN=0.25. No es A.
- **M(t):** multiplicador transitorio posterior al pulso: 1+A·suma[(dosis/0.14)·kernel normalizado]. Referencia A=0.3, tiempo de subida 4 h y de decaimiento 12 h. Su amplitud depende linealmente de la dosis.
- **gate:** activación gaseosa al consumir entre 2 y 10 g/L de azúcar predicho. En la rama 09–15 permanece fija; el onset manual del 02 no se incorpora.
- **fO₂:** atenuación empírica de la fuente mientras queda oxígeno. No constituye retroalimentación del gas a la química.
- **Cd / Csat:** CO₂ disuelto y escala de saturación provisional. **Ganancia** transforma emisión física en predicción del sensor; no pertenece al balance del depósito.

La fuente histórica combina `max[a*q0+r*(qN−q0),0]`, multiplicada por gate, fO₂ y M. La fuente de un core, desde el 09, utiliza `gate*a*M*qN`, sin O₂ en 09/10 y con la opción O₂ en 11 y los ensayos posteriores.

## 3. Diferencias notebook por notebook

Los enlaces apuntan a EXECUTED, que contienen las tablas y figuras. Sus SOURCE son los homónimos terminados en `.source.ipynb`.

| Notebook | Pregunta y cambio efectivo | Qué se ajusta | Qué se conserva |
|---|---|---|---|
| [02 · Producción/transferencia](../notebooks/diagnostics/02_co2_production_transfer.executed.ipynb) | Factorial de dos producciones y dos transferencias; después sensibilidad de Csat, coeficientes antiguos y onset manual | Transferencia y ganancia por combinación y partición; también se repiten esos ajustes para escalas Csat prefijadas | Química theta_nv2; modulaciones de producción histórica; Cd0=0 en todos; Csat de escala 1 en el principal |
| [03 · Sensibilidad theta_nv2](../notebooks/diagnostics/03_theta_nv2_parameter_sensitivity.executed.ipynb) | Un cambio químico por escenario: KIE, KIG o betaG/betaF | Nada: valores ensayados, sin optimización | Rendimientos, resto de theta, coeficientes antiguos de gas, iniciales/temperatura/pulsos |
| [04 · Transferencia Zenteno](../notebooks/diagnostics/04_co2_zenteno_transfer.executed.ipynb) | Transferencia por sobresaturación frente a acumulación tipo Zenteno adaptada | Nada | Química **sin transportadores**, producción común, kLa=0.07, Csat=1.5 constante, Cd0=0 y misma ganancia |
| [05 · Fuente única](../notebooks/diagnostics/05_historical_single_trajectory.executed.ipynb) | Sustituye el corchete histórico completo por qN o q0; retira también a(t) | Nada | theta_nv2, transferencia y coeficientes guardados, gate/O₂/M/Csat históricos |
| [05 v2](../notebooks/diagnostics/05_historical_single_trajectory_v2.executed.ipynb) | Mismas fuentes únicas del 05, todavía sin a(t), ahora reajustadas | Liberación, escala Csat y ganancia, por fuente; 3 arranques | Química, O₂, activación y respuesta nutricional |
| [06 · Actividad conservada](../notebooks/diagnostics/06_historical_single_trajectory_fixed_activity.executed.ipynb) | Sustituye el corchete por a·qN o a·q0 | Nada | Misma actividad y demás auxiliares históricos |
| [06 v2](../notebooks/diagnostics/06_historical_single_trajectory_fixed_activity_v2.executed.ipynb) | Mismas fuentes del 06 con reajuste independiente | Liberación, escala Csat y ganancia; 3 arranques por fuente | Química y todos los factores nutricionales/de activación/O₂ |
| [07 · Capacidad/pérdida](../notebooks/diagnostics/07_transporter_capacity_functional_loss.executed.ipynb) | Sobre transportadores de 04: recuperación de capacidad basal inicial o pérdida funcional | Química de referencia y variantes; B0/tau o delta según caso; después kLa/ganancia | Estructura X,Nx,Ntr,Tr,G,F,E, reparto de N y política de datos del comparador |
| [08 · Originales + YAN tratado](../notebooks/diagnostics/08_transporter_legacy_data_treatment.executed.ipynb) | Modelo original con transportadores; cambia el conjunto de observaciones de entrenamiento | 14 parámetros químicos desde theta_full y perturbación; después kLa/ganancia | Sin mecanismos B0/tau/delta del 07; iniciales y leyes térmicas no se optimizan |
| [09 · Un core](../notebooks/diagnostics/09_historical_single_core.executed.ipynb) | Histórico con dos cores y O₂ frente a un core nutrido **sin O₂** | E1: 3 coeficientes de gas. E2: esos 3 más 5 nutricionales; independiente por formulación | theta_nv2; misma salida química nutrida; Cd0=0, gate y datos comunes |
| [10 · A](../notebooks/diagnostics/10_single_core_A_sensitivity.executed.ipynb) | E1 de un core del 09: A=0.3/0.2/0.1/0 | Nada | Sin O₂, k=2.348168, resto de parámetros E1 y química |
| [11 · Liberación/O₂](../notebooks/diagnostics/11_single_core_release_O2.executed.ipynb) | k original, mitad o cuarta parte, cada uno con/sin O₂ | Nada | A=0, theta_nv2, ganancia/escala Csat/actividad/tiempos |
| 12 · Liberación transitoria | Se probó k(t)=k0[1+B·h(t)] y se descartó; archivos eliminados | Sólo B había sido ajustado | No forma parte de la rama conservada |
| [13 · M original](../notebooks/diagnostics/13_single_core_original_M_sensitivity.executed.ipynb) | Sensibilidades individuales de A, tiempo de subida y decaimiento | Nada | Un core, O₂ activo, k=0.587042, theta_nv2. Referencia A=.3/4 h/12 h |
| [14 · Dosis](../notebooks/diagnostics/14_single_core_nutrition_dose.executed.ipynb) | Dosis 100/75/50%: cambia el salto de N químico **y** la dosis de M | Nada | O₂ activo, k=.587042, A=.3/4 h/12 h, theta_nv2, iniciales y horarios |
| [15 · Reconstrucción](../notebooks/diagnostics/15_single_core_reconstructed_dose_volume.executed.ipynb) | Pulso nominal frente a mezcla/volumen reconstruidos de LAB016–018; versión actual X0=.20 en ambos | Nada | Parámetros del 14, LAB019–021 intactos; mismo RHS después de los saltos |

### 02: qué se separó y qué salió

Cuatro combinaciones: A producción/transferencia históricas; B producción histórica y transferencia nueva; C producción ligada a crecimiento+etanol y transferencia histórica; D producción y transferencia nuevas. La fuente nueva es `(mu/12.72+(betaG+betaF)/1.05)*X`, distinta de la fuente fermentativa histórica modulada.

La transferencia histórica es `k*Cd*(.05+.95*Cd/(Cd+Csat))`; puede emitir por debajo de Csat. La nueva es `kLa*max(Cd−Csat,0)`. Sus coeficientes no son físicamente intercambiables.

Se prueban ambas particiones de gas. Con entrenamiento 019–021, RMSE medio holdout 016–018: A=.12365, B=.12966, C=.14247 y D=.14000. A es también la mejor media en la partición inversa (.13313 en 019–021). Dentro de estas condiciones, cambiar sólo la transferencia no resuelve la discrepancia de producción.

Escalas Csat .5/1/2/4 son sensibilidades separadas. El bloque de onset usa horas manuales 24.2491/22.2981/22.6475/28/32/24 para 016–021, sin ajuste de coeficientes: mejora varios arranques, empeora LAB021 y **no se convierte en política general**. El bloque de coeficientes antiguos lee la fila compartida theta_full/Z2: k=2.000835, escala=.999955, ganancia=1.054708; no es el Z2 específico de theta_nv2.

### 03: sensibilidad química, no theta nuevo

Referencia KIE=286.579410, KIG=122.553899, betaG=.412766 y betaF=.447244. Se ensayan KIE=122.206/24.895; KIG=17.845; betaG y betaF ±20%, una modificación por escenario. Se conservan Yeg=.482075 y Yef=.483728 y todos los demás rendimientos. No se retoca la ganancia del gas para compensar.

Reducir KIE aumenta inhibición por etanol y puede bajar el gas, pero frena el consumo y deja más azúcar. Reducir KIG aumenta la inhibición de fructosa por glucosa: mejora algunos errores gaseosos a costa de fructosa/azúcar residual. Ningún escenario fue guardado como nueva calibración aceptada. Este notebook no incorpora todavía las comparaciones posteriores con G+F por densidad de 016–018.

### 04: una prueba de transferencia con otra química

No usa theta_nv2 como química común: carga el ajuste **sin transportadores**. E0=9.8 g/L para 016–018; kLa=.07, Cd0=0 y Csat=1.5 constante para ambas leyes. El modelo tipo Zenteno calcula acumulación hacia saturación y emite producción menos acumulación; se limita acumulación a producción disponible y se usa tolerancia .001 g/L para declarar saturación. Son adaptaciones expresas, no reproducción literal de todo Zenteno.

RMSE medio de los seis LAB: .18504 → .15605. Mejora cinco LAB; LAB019 empeora .10896 → .11579. Persisten arranque adelantado y déficit del máximo previo a nutrición.

### 05 frente a 06, y v1 frente a v2

Esta es la diferencia conceptual más importante de los primeros ensayos:

| Fuente alternativa | 05 / 05 v2 | 06 / 06 v2 |
|---|---|---|
| Nutrida | qN | a(t)·qN |
| Sin pulso en la fuente | q0 | a(t)·q0 |

Sin recalibrar, RMSE medio holdout: histórica .12004; q0 del 05 .14033; q0 del 06 .10747. El 05 confundía eliminar la mezcla con eliminar a(t); el 06 muestra que mantenerlo cambia la conclusión.

Las v2 sí ajustan por fuente k, escala Csat y ganancia, sólo con 019–021 y tres arranques por caso. Usan objetivo censurado y soporte temporal recortado; los errores v1/v2 no son directamente comparables.

| Caso reajustado | RMSE calibración | RMSE holdout |
|---|---:|---:|
| Histórica, ambas v2 | .13347 | .12290 |
| 05 v2 · qN sin a | .14768 | .14178 |
| 05 v2 · q0 sin a | .16065 | .12163 |
| 06 v2 · a·qN | .12979 | .15701 |
| 06 v2 · a·q0 | .13126 | .11530 |

En 05 v2 las fuentes únicas llevan k a 25 y escala a.35, sus límites. En 06 v2, q0 conserva menor error que la histórica reajustada; aun así, su resultado congelado sobre ese mismo soporte era mejor (.10978 frente a.11530).

**“Sólo sin nutrición” identifica la fuente gaseosa, no la predicción química.** Las figuras químicas definitivas de ambas v2 conservan los pulsos reales y son idénticas entre los casos azul/verde. En 05/06 siguen existiendo auxiliares históricos que proceden de las dos trayectorias. No son todavía modelos completos de un solo core.

### 07: mecanismos nuevos sobre transportadores

La capacidad fermentativa original `1+aTr*Tr` pasa a `B+aTr*Tr`:

- Recuperación inicial: `B=1−(1−B0)*exp(−t/tau)`; síntesis/pérdida de Tr originales.
- Pérdida funcional: `B=exp(−delta*t)` y `dTr=vTr−(kd+delta)*Tr`. Se pierde capacidad basal y adicional.

Son hipótesis separadas, no una combinación. Se evalúan congeladas y recalibradas. Química sólo 004–009 depurados; gas 019–021; química 019–021 reservada; gas 016–018 reservado.

Recuperación: objetivo químico 4.46907→3.60061, pero B0≈.01 y tau=48 h en límites; betaG/betaF compensan la baja capacidad. CO₂ holdout .14731→.16265, peor. Pérdida: delta≈3.43e−7 h⁻¹, prácticamente nula; no aporta mejora útil. Todos mantienen kLa≈20 h⁻¹ en el límite.

### 08: versión definitiva y versiones reemplazadas

El mismo archivo se rehízo varias veces. El nombre “legacy_data_treatment” no describe por completo su contenido final.

1. Primer ensayo: datos depurados con umbral YAN, corte YAN +12 h y biomasa +24 h; generó `observations_legacy_treatment_v1.csv`.
2. Revisión intermedia: inicio/fijos desde `theta_multistart_07` del repositorio anterior.
3. **Versión conservada:** Excel original, sus 76 biomasas, sin las tres correcciones/seis exclusiones ni cortes tardíos de biomasa; sólo YAN tratado. Inicio y bloque fijo desde theta_full, más adicionales originales de transportadores. Dos arranques derivados de ese mismo inicio. El CSV final es `observations_original_yan_treated_v1.csv`.

Tratamiento final: YAN≤20 mg/L→0; exclusión con t>agotamiento+12 h; LAB006 agotamiento manual 122 h, punto 122 h=0 y corte posterior 134 h. No se borran filas ni se aplica el corte biomasa +24 h. Se ajustan 289 observaciones químicas posteriores al inicio. El Yef inicial no factible de theta_full se proyecta a .5114; finales Yeg=.471047 y Yef=.507794.

Parámetros libres: mu0,betaG0,betaF0,Kn0,Kig0,Kie0,Kd0,Yxn,Yeg,Yef,eta0,KTr,aTr,alpha. Fijos químicos Kg0,Kf0,Yxg,Yxf,m0 desde theta_full; YTrN=6.25. No incorpora recuperación/pérdida del 07.

Resultados mixtos: en 019–021 mejoran YAN39.28→35.63 mg/L y etanol8.72→7.80 g/L; empeoran biomasa .557→.586 g/L y G+F16.17→16.39 g/L. Gas holdout .147027→.158070, peor; kLa vuelve a 20. Los CSV de revisiones anteriores permanecen, pero no son el objetivo final del 08.

### 09: eliminación efectiva del segundo core

La propuesta integra sólo la química con pulsos reales; no contiene q0/core 0. También elimina O₂, de modo que la comparación con la histórica cambia dos elementos estructurales. No cambia theta_nv2 ni la salida química entre ambas formulaciones.

E1 ajusta liberación, escala Csat y ganancia. E2 libera además actividad final, duración de rampa, A, tau de subida y tau de decaimiento. Se conservan gate2–10 g/L, iniciales, temperatura, Cd0=0 y parámetros específicos de O₂ histórico.

| Etapa/formulación | RMSE gas 019–021 | RMSE gas 016–018 |
|---|---:|---:|
| E1 histórica | .133468 | .122912 |
| E1 un core sin O₂ | .130951 | .157588 |
| E2 histórica | .127371 | .214679 |
| E2 un core sin O₂ | .129549 | .195681 |

E2 reduce el objetivo de ajuste, pero empeora holdout. La propuesta E2 tiene A=1.129288 y tau de subida=.25 h en límite; la histórica E2 llega a varios límites. No se adoptó E2 para las sensibilidades siguientes: éstas parten de **E1 de un core**.

En 09–15 LAB017 se consolida como **un pulso de.28 g/L**, no dos pulsos. No se vuelve a dividir la dosis019–021 por volumen remanente: se usan.08 g/L del lector. Ésta es una diferencia de entradas respecto de 02/03 y 07/08.

### 10–13: separar amplitud, almacenamiento, O₂ y tiempos

10 conserva la liberación E1 k=2.348168, sin O₂. A=.3→0 baja el RMSE holdout completo.157588→.132837 y el de ventana de pico.225380→.089476; la cola empeora ligeramente.087116→.090054. En 019–021 el error completo empeora.130951→.134424; LAB021 ya tenía déficit de pico.

11 fija A=0. Compara k=2.348168/1.174084/.587042 con y sin O₂. Holdout completo con O₂: .124829/.118432/.108247. Menor k sostiene cola; O₂ beneficia principalmente arranque. El O₂ atenúa producción, mientras bajar k redistribuye emisión mediante Cd: no son el mismo mecanismo.

12 probó liberación transitoria con B ajustado≈.898533. Se eliminó; no se utiliza después. Su existencia/eliminación queda documentada en el changelog del 30 de octubre.

13 conserva O₂ y k=.587042, **restaura A=.3** y examina un parámetro por vez: A=0/.1/.2; subida 1/2/8 h; decaimiento 4/8/24 h, frente a referencia.3/4 h/12 h. RMSE holdout de referencia.137399; A=0 da.108247; decaimiento 4 h da.112187. Decaimiento24 h mejora cola.069878→.062539, pero empeora registro.150777 y pico.269447. El máximo del kernel se renormaliza: variar tiempos cambia cronología y área, aunque el máximo normalizado permanezca1.

### 14: el cambio ya afecta la química

Usa O₂, k=.587042 y M=.3/4 h/12 h. No reduce YAN inicial. Reduce sólo pulsos posteriores, tanto en el balance químico como en M. Por eso ya cambian X/N/G/F/E: no equivale a bajar A con química congelada.

| Dosis | RMSE019–021 completo | RMSE016–018 completo | Pico016–018 | Cola016–018 |
|---|---:|---:|---:|---:|
| 100% | .128003 | .137399 | .227531 | .069878 |
| 75% | .127174 | .115330 | .147250 | .066131 |
| 50% | .129504 | .099856 | .066410 | .061646 |

Dosis nominales del lector: 80 mg/L en 004–009 y 019–021;140/280/140 mg/L en 016/017/018. Se documenta discrepancia entre80 mg/L del workbook y 140 mg/L calculados históricamente suponiendo20% de YAN para ambos productos. Receta nominal1 g SFX+.4 g FDA no demuestra equivalencia de aporte YAN ni confirma las masas reales de016–018. El50% es una sensibilidad hipotética, no una corrección experimental demostrada.

### 15: estado actual, después de la revisión de X0

Reconstruye el accidente016–018 con pulmón inicial 500 mL en agua, objetivo140 mg/L sobre 2 L previos, retorno017 durante 140 s y caudales100 mL en 230/235/245s.016/018 completan100 mL;017 recibe200 mL después. Se balancean X,N,G,F,E,Cd,O₂ y un trazador separado de YAN externo.

Resultados hidráulicos: retorno59.574 mL; volumen final2.1/2.140426/2.1 L; aportes externos expresados por 2 L128.408/246.678/128.097 mg/L. No confundir esas dosis de referencia con concentraciones finales: el salto químico usa masas, YAN residual y volumen final. Con X0 actual, N postmezcla≈122.293/230.494/121.997 mg/L.

**Versión vigente:** X0=.20 g/L sólo 016–018, tanto nominal como reconstruido; antes era.39.019–021 conserva X0=.283162/.153342/.136153 y sus demás entradas. .20 g/L equivale a 6.67 millones viables/mL usando30 pg/célula; es una sensibilidad, no una nueva medición.

| Tramo016–018 | Nominal X0=.20 | Reconstruido X0=.20 |
|---|---:|---:|
| Completo | .143358 | .134295 |
| Primeras24 h postpulso | .195200 | .165350 |
| Cola desde 32 h postpulso | .050257 | .045988 |

Los dos casos y las observaciones se expresan al mismo volumen reconstruido; el nominal también se convierte desde su caudal másico referido a 2 L. Por tanto, no comparar estos errores directamente con 14 como si unidades/entradas fueran idénticas.

El reconstruido previo X0=.39 tenía errores.122861/.180820/.064964. La revisión a.20 mejora ventanas de pico/cola y empeora el completo. Las figuras actuales **no** comparan.39 frente a.20: ambos casos usan.20.

La operación de715 s se aproxima por un salto al horario nominal. Se ignoran reacción/desgasificación del pulmón durante esos minutos y se supone agua sin Cd/O₂. Las muestras disponibles016–018 son pre-pulso; no validan directamente la química postmezcla.019–021 queda idéntico entre nominal/reconstruido, con RMSE medio completo.128003.

## 4. Qué sigue fijo y qué no es común a todos

### Química y parámetros

Theta_nv2 tiene15 parámetros físicos y fue calibrado previamente sólo con química 004–009 depurada. Se ajustaron mu0,Yxn,betaG0,betaF0,Yeg,Yef,Kig0,Kie0,Kd0; se fijaron Kn0,Kg0,Kf0,Yxg,Yxf,m0 desde theta_full. Rendimientos Yeg/Yef limitados a .5114.

02,05/06,09–15 mantienen ese theta;03 hace perturbaciones sin aceptarlas como ajuste.04 usa la química calibrada sin transportadores.07/08 sí recalibran química de transportadores. Cambiar dosis/X0 en 14/15 mantiene theta, pero cambia trayectorias.

### Observaciones, particiones y objetivo

El gas se compara normalmente con medianas horarias RAW convertidas, sin filtrar la predicción. La señal GUI filtrada no es el objetivo de estos ensayos. En 019–021 la conversión base descuenta muestras:1.95 L al inicio después dem1 y 1.70 L final; la nutrición directa no añade volumen.016–018 usa 2 L hasta la reconstrucción15, que corrige en memoria.

Cuando se calibra gas, la partición principal es019–021→016–018;02 ejecuta también la inversa. Química004–009→019–021.019–021 puede ser validación química y entrenamiento de gas simultáneamente: no es validación conjunta.

02,05v2,06v2 y 09 usan pérdida censurada: si observado<.05, residuo=max(predicho−.05,0); en otro caso predicho−observado. Cada LAB tiene igual peso.07/08 conservan MSE ordinario/cobertura del comparador04.05/06v1 no optimizan y muestran la métrica censurada como información adicional. Las sensibilidades10–15 no hacen una nueva calibración.

02 tiene política propia de corte compartido;05/06v1 conservan cobertura disponible; sus v2 y 09–15 utilizan horizontes del lector histórico. En09 son151.10/141/141 h para016–018 y 166/172.333/166 h para019–021. La última muestra química 019–021 es166 h. No confundir cobertura observada, horizonte y confirmación de final.

### Iniciales, dosis y transferencia

- Cd0=0 en 02/03/04,05/06 y 09–15.07/08 conservan.907/.730/.829 g/L en 019–021, última provisional, y cero016–018.
- E0=9.8 g/L en 016–018 se ensayó en 04_compare_models_v2 y diagnostics 04.09–15 vuelve a las iniciales del lector: E0=0 en 016–018;019–021≈12.075/11.918/11.760 g/L.
- X0=.39 g/L en 016–018 para 09–14; sólo 15 vigente usa.20. No se cambia el archivo de iniciales original.
-02/03 y 07/08 corrigen concentración de dosis019–021 por volumen remanente.09–15 conserva.08 g/L del lector sin otra renormalización.08 y 09–15 consolidan017 como un solo pulso doble;02 conserva los eventos originales del lector.
- kLa de sobresaturación no equivale al k de liberación histórica. El.07 del 04 y el.587042 de 11–15 actúan en leyes distintas. El.587042 es la cuarta parte del ajuste E1 de un core 09, una sensibilidad; no un nuevo coeficiente identificado experimentalmente.
- La correlación Csat histórica sigue siendo provisional.04 usa1.5 constante; la extensión David disuelta usa otra función térmica. Ninguna de estas pruebas convirtió automáticamente la solubilidad histórica en una medición validada.

## 5. Configuración efectiva de la rama final

| Elemento | 15 vigente |
|---|---|
| Modelo químico | Histórico reducido, X,N,G,F,E; una trayectoria nutrida por caso/LAB |
| Parámetros químicos | theta_nv2 sin recalibrar |
| Fuente | gate·a(t)·fO₂·M·(44.01/46.07)(betaG+betaF)X |
| Activación | Consumo predicho2–10 g/L, sin onset manual |
| Actividad | Final.25; rampa 64.658703746 h |
| Transitorio M | A=.3, subida 4 h, decaimiento 12 h; Nref=.14 g/L |
| Oxígeno | Activo; consume según X de esa misma química; qmax=.15, escala inicial.19539966565 |
| Transferencia | Histórica, k=.5870419885002788 h⁻¹ constante |
| Escala Csat / ganancia |2.5 / .77428737694085 |
| Cd inicial |0 |
| Entradas 016–018 | X0=.20 en ambos; nominal frente a reconstrucción de dosis, mezcla y volumen |
| Entradas 019–021 | Sin cambios respecto 14; idénticas en ambos casos |
| Optimización nueva | Ninguna |
| Procedencia de gas | E1 un core 09, con reducción manual de k a ¼ y reintroducción O₂ |

10,11,13,14 y 15 leen los parámetros E1 a precisión completa desde la salida JSON del **09 EXECUTED**. No basta conservar sus SOURCE para esa dependencia. Los ajustes exploratorios de diagnostics no reemplazan configs de los modelos; 08 sí conserva una nueva tabla de datos separada. No hay un nuevo ajuste global definitivo guardado a partir del 15.

## 6. Otros notebooks recientes para situar el contexto

- [03_calibrate_models](../notebooks/03_calibrate_models.executed.ipynb) calibra la comparación base: histórico fijo químicamente, respuesta directa al YAN sin transportadores y respuesta con transportadores. Los nuevos usan fuente crecimiento+fermentación y depósito por sobresaturación; no contienen la combinación histórica ni su gate/O₂/M.
- [04_compare_models](../notebooks/04_compare_models.executed.ipynb) carga los ajustes, no optimiza; presenta ambas particiones, G+F medido conjuntamente y YAN NUT numérico. Es la referencia de 07/08.
- [04_compare_models_v2](../notebooks/04_compare_models_v2.executed.ipynb) fija kLa=.07 sólo en los nuevos y reajusta ganancias; ensaya E0=9.8 en 016–018. No añade adaptación fisiológica.
- [05_david_2012](../notebooks/05_david_2012.executed.ipynb) es una familia distinta: Contois, Nx/Ntr/Tr, azúcar total S y disponibilidad nutricional distribuida. Reconstruye funciones empíricas no publicadas; calibra sólo química 004–009. No ajusta gas ni usa la fuente modulada histórica. Gas 019–021 RMSE≈.232/.232/.241.
- [06_david_2012_dissolved_co2](../notebooks/06_david_2012_dissolved_co2.executed.ipynb) conserva David y agrega depósito/saturación térmica; compara kLa=.07/2/20 sin ajustar. No elimina exceso de área: para kLa=2 predice≈71–73 g/L frente≈36–40 g/L observados.
- [preparing_data](../notebooks/preparing_data/preparing_data.executed.ipynb) audita observaciones/temperaturas/procedencia; no calibra. Distingue reglas del prototipo, theta_full y theta_new. Mostrar una regla aquí no demuestra que haya sido aplicada a cada ajuste.
- [Primer EKF LAB019](../notebooks/EKF/lab019_first_ekf_full_batch.executed.ipynb) reproduce un prototipo con theta_full y memoria contrafactual y theta_full; no usa theta_nv2 ni el modelo de un core 15. Contrasta libre/CO₂/CO₂+GF/YAN a 22 y 40 h. Procesamiento causal de 30 min y restricciones originales: no es un EKF ya actualizado con las últimas hipótesis.
- [Histórico02_co2_theta_nv2](../notebooks/historical/02_co2_theta_nv2.executed.ipynb) añadió comparación de onset manual para los tres theta con coeficientes compartidos. No confundirlo con diagnostics 02, que hace el factorial producción/transferencia.

## 7. Lectura para retomar

Para retomar la línea más reciente: **09 E1 → 11 → 13 → 14 → 15**. 10 documenta por qué se aisló A; 12 está descartado. Para entender por qué no bastó sustituir una fuente, volver a 06 y 06 v2. Para la alternativa de transportadores, leer 07 y la versión final 08 como rama separada.

Lo que falta decidir científicamente sigue visible: forma/tiempo del arranque, compromiso pico-cola, comportamiento distinto de LAB021, conversión producto→YAN, inicial X de 016–018 y validez física de solubilidad/transferencia. El holdout 016–018 se ha examinado repetidamente durante estas sensibilidades; sirve para comparación exploratoria, pero ya no constituye una nueva prueba independiente de selección final.

No aparece en los resultados una mejora uniforme que cierre esas decisiones. La secuencia más reciente pasó de ajustar parámetros de gas a comprobar si las entradas nutricionales, hidráulicas e iniciales explican las diferencias.

## Auditoría ampliada de parámetros

[Detalle exacto de libres, fijos, inicializaciones y resultados del 03/07/08](transporters_parameter_audit_03_07_08.md). El 03 actual reutiliza la química guardada salvo que se active REFIT_CHEMISTRY; sí recalibra el gas. El 07 conserva los eventos originales de LAB017; el 08 los consolida en un pulso doble.
