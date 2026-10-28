# Tres formulaciones

Histórico: ecuaciones químicas y CO₂ v3 congeladas en models/historical; theta_nv2 fijo. Para la comparación por particiones se reajustan solamente sus tres coeficientes de CO₂; los ajustes originales siguen intactos.
Sin transportadores: respuesta directa al YAN, aN y KNa.
Con transportadores: dos destinos de YAN, Tr funcional, síntesis eta0/KTr y efecto aTr; pérdida por mortalidad. Adaptación propuesta, no copia literal de David.

Los modelos nuevos usan el mismo depósito y transferencia positiva kLa max(Cd-Csat,0), y ganancia de observación. Volumen remanente se aplica a Md=V Cd; una retirada homogénea no cambia Cd.

Punto aún provisional: se conserva de forma explícita la correlación de solubilidad heredada para poder ejecutar los ensayos. No se presenta como Henry validado; su sustitución requiere seleccionar correlación y presión parcial de contacto. No se ajustan sus coeficientes.

La síntesis de Tr se modela como capacidad funcional adicional y consumo separado de YAN; no es un modelo de conservación elemental completo. YTrN se fija en 6.25; no se ajusta junto con todos los parámetros de escala de Tr.

La inicialización deriva de theta_full; los rendimientos fuera de cota se proyectan y se registran explícitamente. Los fits no reemplazan theta_full, theta_new ni theta_nv2.

## Implementación y supuestos

- Ambos modelos nuevos conservan los cinco balances actuales de X,G,F,E y la mortalidad/mantenimiento. Sin transportadores, betaG y betaF se multiplican por 1+aN*N/(KNa+N); dN=-mu*X/Yxn.
- Con transportadores: N observado=Nx+Ntr; mu usa Nx. vTr=eta0*a_mu(T)*Ntr/(KTr+Ntr)*X; dNx=-mu*X/Yxn; dNtr=-vTr/YTrN; dTr=vTr-kd*Tr. Las tasas betaG y betaF se multiplican por 1+aTr*Tr. Tr(0)=0; Nx(0)=alpha*N(0); Ntr(0)=(1-alpha)*N(0). Las dosis se reparten con la misma alpha. El Yxn reajustado representa crecimiento separado de la síntesis de Tr. Esta representación requiere validación e identificabilidad.
- La dependencia térmica de síntesis de transportadores se toma igual a la del crecimiento como hipótesis fija; no se ha copiado una ley térmica identificada de David.
- qprod=(mu/12.72+(betaG+betaF)/1.05)*X; dCd=qprod-qgas; qgas=kLa*max(Cd-Csat,0); qpred=gain*qgas. Integración implícita conservativa. No hay modulación O2, activación artificial, mezclas contrafactuales ni pulsos adicionales en el CO2 de los modelos nuevos.
- Md=V*Cd. Muestreos homogéneos mantienen Cd y reducen Md; V viene del CSV corregido. LAB019–021: las nutriciones no agregan volumen; la dosis previamente expresada por 2 L nominales se transforma a masa y se divide por V al aplicarse.
- Cd inicial: 0.907/0.730/0.829 g/L en LAB019–021 (último provisional). Sin medida de LAB016–018 se asume cero, explícitamente.
- La solubilidad provisional es exactamente la correlación heredada 1.69*exp(-0.032*(T-20))*exp(0.0016*E)*exp(-0.0012*(G+F)). No es una correlación de Henry validada. No se ajusta su escala; se reserva la sustitución de esta función para una elección documentada de solubilidad y presión parcial.
- Ajuste químico: residuos estandarizados de X,N,G,F,E posteriores a la inicial de LAB004–009; sin priors ni ajuste de iniciales. Cotas y parámetros libres constan en cada calibration.json. Partida theta_full con proyección explícita de rendimientos no factibles, registrada en fit.json.
- CO₂ principal: calibrar con LAB019–021, evaluar holdout LAB016–018. Prueba inversa: calibrar con LAB016–018, evaluar holdout LAB019–021. Las tres formulaciones usan medianas horarias crudas, cobertura del modelo y suma de errores cuadrados medios por fermentación; ningún dato de holdout entra al optimizador. Mismos puntos iniciales y cotas por modelo en ambas particiones. Cd0 y correlación de saturación fijos. Son ajustes locales; se registran convergencia y cotas activas.
- El histórico conserva fuente, ecuaciones y theta_nv2; ajusta kCO2_release_h, CO2sat_scale y matrix_gain al mismo objetivo crudo usado para los modelos nuevos. Sus coeficientes previos no se sobrescriben. Los nuevos ajustan kLa y gain. Cada gas_fit.json agrupa ambos experimentos y declara train_019_021 como principal. La química no se recalibra al invertir la partición de CO₂; LAB019–021 sigue siendo holdout químico y no es holdout conjunto cuando calibra CO₂.
- Los nuevos fits son resultados locales; revisar convergencia, cotas y validación. La mejor curva por sí sola no prueba que los transportadores estén identificados.

Tolerancia cerca de cero: los modelos nuevos registran mínimos internos y sólo proyectan salidas negativas de G/F hasta 1e-4 g/L (0.1 mg/L), y otros estados hasta 1e-6 g/L. Valores más negativos rechazan la integración. La referencia histórica conserva sus tolerancias originales.

Condición de frontera de los dos modelos nuevos: como el crecimiento consume ambos azúcares en los balances elegidos, mu se anula al agotarse G o F. La fermentación del azúcar restante puede continuar. No se añade un factor suave ni un parámetro; la referencia histórica no se modifica. Esta condición evita consumo de un sustrato ausente y debe distinguirse de la respuesta al nitrógeno.


## Lectura de la comparación en ambos sentidos

El histórico conserva también su inicialización original Cd(0)=0 en los seis ensayos; las mediciones iniciales recientes sólo se aplican a los modelos nuevos. Por tanto la igualdad del objetivo no elimina las diferencias estructurales y de inicialización entre formulaciones.

En los ajustes actuales, los dos modelos nuevos llevan kLa hasta 20 h^-1 o muy cerca de esa cota al calibrar LAB019–021; al calibrar LAB016–018 quedan aproximadamente en 0.22 y 0.43 h^-1. El histórico alcanza una cota de CO2sat_scale en ambos sentidos. Convergencia numérica no equivale a identificación física. Las tablas de cada EXECUTED contienen las cotas activas y los parámetros completos.

La tabla pareada compara cada LAB bajo los dos ajustes e indica su rol en el principal. Al invertir las particiones cambia también el conjunto de holdout; las medias de RMSE de ambos holdouts no son un efecto causal aislado de elegir un entrenamiento. Para comparar modelos dentro de una partición, usar los mismos laboratorios y la misma columna de holdout. La selección del mecanismo sigue siendo exploratoria, con sólo dos grupos de tres ensayos y solubilidad provisional.
