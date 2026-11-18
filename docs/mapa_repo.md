# Mapa del repositorio de fermentación

Abre el [mapa interactivo](mapa_repo.html) para buscar por tema, carpeta o calibración. Cada ficha tiene una línea sobre el ensayo, la procedencia de la química y del CO₂, y enlaces al código y a los resultados guardados.

**Punto de partida para retomar el trabajo.** [EKF 22](../notebooks/EKF/22_ekf_s_media_ganancia_azucar_lab016_024.executed.ipynb) es la referencia S más reciente. Usa la química del 17_2, la solubilidad variable del 17 y \(S_0\) por densidad. Mantiene el \(Q\) del EKF 20, asimila CO₂ sin umbral de flujo y reduce a la mitad la ganancia de \(S\) tras el primer agotamiento de YAN. La recalibración específica de la cola de S sigue pendiente.

## De dónde salen las calibraciones

| Rama | Notebook | Qué ajusta o carga |
|---|---|---|
| Histórica | [Recalibración theta_nv2](../notebooks/historical/01_recalibration_theta_nv2.executed.ipynb) y [CO₂ Z1/Z2](../notebooks/historical/02_co2_theta_nv2.executed.ipynb) | Química de cinco estados ajustada en LAB004–009. La capa histórica de gas se ajusta por separado. |
| Modelos comparativos | [03](../notebooks/03_calibrate_models.executed.ipynb) → [04](../notebooks/04_compare_models.executed.ipynb) → [04 v2](../notebooks/04_compare_models_v2.executed.ipynb) | Química y variantes de transportadores en `configs/models/`. El 03, en su configuración guardada, carga la química y ajusta gas. El 04 compara. El 04 v2 fija \(k_La\) y reajusta la ganancia de las variantes con y sin transportadores. |
| David | [05 David](../notebooks/05_david_2012.executed.ipynb) → [06 David con CO₂ disuelto](../notebooks/06_david_2012_dissolved_co2.executed.ipynb) | Química propia en `configs/models/david_2012/fit.json`. El 06 conserva esa química para probar el reservorio de CO₂. |
| Zenteno G/F | [Diagnóstico 16](../notebooks/diagnostics/16_zenteno_recalibration_legacy_treatment.executed.ipynb) → [16](../notebooks/16_zenteno_recalibration_legacy_treatment_variable_solubility.executed.ipynb) → [16_2](../notebooks/16_2_zenteno_recalibration_legacy_biomass_weight.executed.ipynb) | El 16 documenta la química archivada y ajusta gas variable. El 16_2 reajusta la química con la ponderación histórica de biomasa y usa el mismo gas. Los parámetros nuevos están en su salida **PARÁMETROS QUÍMICOS COMPLETOS**. |
| Zenteno S | [Diagnóstico 17](../notebooks/diagnostics/17_zenteno_single_sugar.executed.ipynb) → [17](../notebooks/17_zenteno_single_sugar_variable_solubility.executed.ipynb) → [17_2](../notebooks/17_2_zenteno_single_sugar_legacy_biomass_weight.executed.ipynb) | El diagnóstico 17 ajusta el modelo agregado a \(G+F\). El 17 usa química congelada y ajusta el gas variable. El 17_2 reajusta la química con la ponderación histórica de biomasa y conserva ese gas. Buscar **PARÁMETROS S 17_2** en su salida. |
| Zenteno S con temperatura causal | [Diagnóstico 25](../notebooks/diagnostics/25_zenteno_azucar_total_temperatura_causal.executed.ipynb) → [EKF 14](../notebooks/EKF/14_ekf_s_comparacion_ponderacion_biomasa.executed.ipynb) | El 25 ajusta dos vectores, offline y causal. El 14 los carga del bloque **TEMPERATURE_FIT_PARAMETERS_JSON**. |

La química principal de Zenteno se ajusta en **LAB004–009**. El gas variable de referencia se ajusta en **LAB019–021**. Los **LAB016–018** y **LAB022–024** se usan para comparar la transferencia de esos ajustes, según el ensayo.

## Ruta de los experimentos de EKF

| Notebook | Química | Qué se prueba |
|---|---|---|
| [EKF 09](../notebooks/EKF/09_ekf_lima_clean_figures.executed.ipynb) / [EKF 13](../notebooks/EKF/13_ekf_lima_validacion_lab022_024.executed.ipynb) | G/F 16 | Trayectorias con covarianza cinética; extensión a LAB022–024 y sensibilidad al hueco de CO₂. |
| [EKF 15](../notebooks/EKF/15_ekf_s_validacion_lab022_024.executed.ipynb) | S 17 | Protocolo de LAB022–024 con el modelo S del EKF 06. |
| [EKF 16](../notebooks/EKF/16_ekf_gf_crecimiento_azucar_disponible_lab016_024.executed.ipynb) → [EKF 17](../notebooks/EKF/17_ekf_gf_reparto_yan_azucar_residual_lab016_024.executed.ipynb) | G/F 16 | Crecimiento cuando queda uno de los azúcares; reparto del YAN del pulso según el azúcar residual. |
| [EKF 18](../notebooks/EKF/18_ekf_gf_reparto_yan_quimica_16_2_lab016_024.executed.ipynb) | G/F 16_2 | Repite la prueba de reparto con química recalibrada. |
| [EKF 19](../notebooks/EKF/19_ekf_s_calibracion_17_2_lab016_024.executed.ipynb) → [EKF 20](../notebooks/EKF/20_ekf_s_ruido_crecimiento_yan_lab022_024.executed.ipynb) | S 17 y S 17_2 → S 17_2 | Compara ambas calibraciones; luego condiciona el ruido de crecimiento de \(Q\). |
| [EKF 21](../notebooks/EKF/21_ekf_s_gf_sin_umbral_co2_lab016_024.executed.ipynb) | G/F 16_2 y S 17_2 | Prueba quitar el umbral de CO₂ en los dos modelos; S usa densidad para inicializar y graficar el azúcar. |
| [EKF 22](../notebooks/EKF/22_ekf_s_media_ganancia_azucar_lab016_024.executed.ipynb) | S 17_2 | Prueba media ganancia para \(S\) después del primer agotamiento de YAN. |

Los números se repiten entre carpetas. **Notebook 16** se refiere aquí a `notebooks/16_zenteno...`. **EKF 16** está en `notebooks/EKF/` y **Diagnóstico 16** en `notebooks/diagnostics/`.

## Dónde buscar

- `notebooks/` contiene las calibraciones y comparaciones de modelos. `historical/` conserva las reproducciones antiguas y `diagnostics/` documenta ajustes y pruebas específicas.
- `notebooks/EKF/` reúne las corridas de filtro. `kalman_analysis/` estudia \(Q\), \(R\) y las fuentes de ruido.
- `notebooks/preparing_data/` y `data_graphics/` reúnen la preparación y exploración de los datos. `data/` conserva datos originales, depurados, de compatibilidad y procesados.
- `configs/` contiene parámetros archivados y configuración. `src/wine_fermentation/` contiene las ecuaciones y lectores comunes. Algunos ajustes recientes viven en las salidas `.executed.ipynb`.

Abre `.executed.ipynb` para consultar curvas y tablas. Abre `.source.ipynb` para ver el código y reproducir. El mapa funciona al abrir el archivo directamente. Para usarlo por localhost, desde la raíz del repositorio ejecuta `python -m http.server 8765 --bind 127.0.0.1` y abre [el mapa en el navegador](http://127.0.0.1:8765/docs/mapa_repo.html).
