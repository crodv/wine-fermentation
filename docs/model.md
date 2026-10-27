# Modelo activo de cinco estados

Implementación: `src/wine_fermentation/model.py`. Se conservan las ecuaciones históricas de X, N, G, F y E,
incluidas sus adaptaciones previas; no se afirma que todas sean transcripción literal del artículo de Zenteno.
La única reducción de estados elimina dXd/dt y dGly/dt. La conversión de cocientes a rendimientos y constantes físicas es algebraica.

## Temperatura y cinéticas

Entrada T en °C; para Arrhenius se usa TK=T+273.15, R=8.314 J/(mol K):

\[
a_\mu=e^{59453(TK-300)/(300R TK)},\quad
a_\beta=e^{11000(TK-296.15)/(296.15R TK)},
\]
\[
a_K=e^{46055(TK-293.15)/(293.15R TK)},\quad
a_m=e^{37681(TK-293.3)/(293.3R TK)}.
\]

\(\mu_{max}=\mu_0a_\mu\), \(\beta_{Gmax}=\beta_{G0}a_\beta\), \(\beta_{Fmax}=\beta_{F0}a_\beta\).
\(K_N=K_{N0}a_K\), \(K_G=K_{G0}a_K\), \(K_F=K_{F0}a_K\).
Para preservar exactamente la regularización anterior, \(K_{IG}=K_{IG0}(a_K+\varepsilon)\) y
\(K_{IE}=K_{IE0}(a_K+\varepsilon)\), con \(\varepsilon=10^{-8}\).

\[
\mu=\mu_{max}\frac{N}{N+K_N+\varepsilon},\quad
\beta_G=\beta_{Gmax}\frac{G}{G+K_G+\varepsilon}\frac{K_{IE}}{E+K_{IE}},
\]
\[
\beta_F=\beta_{Fmax}\frac{F}{F+K_F+\varepsilon}\frac{K_{IG}}{G+K_{IG}}\frac{K_{IE}}{E+K_{IE}}.
\]

\(S_\varepsilon=G+F+\varepsilon\), \(m_{ef}=m_0a_m S_\varepsilon/(S_\varepsilon+1)\).
La atenuación de mantenimiento por azúcar se conserva como adaptación histórica.

\[
T_d(E)=-0.0001E^3+0.0049E^2-0.1279E+315.89\ \mathrm{K},
\]
\[
k_d=\begin{cases}K_{d0}\exp\left[0.0415E+\frac{130000(TK-305.65)}{305.65R TK}\right],&TK\geq T_d(E),\\0,&TK<T_d(E).\end{cases}
\]

## Balances

X es biomasa viable; las concentraciones usan g/L (equivalente numérico a kg/m³), N en g N/L y tiempo en horas.

\[
\frac{dX}{dt}=(\mu-k_d)X,\qquad \frac{dN}{dt}=-\frac{\mu}{Y_{X/N}}X,
\]
\[
\frac{dG}{dt}=-\left(\frac{\mu}{Y_{X/G}}+\frac{\beta_G}{Y_{E/G}}+m_{ef}\frac{G}{S_\varepsilon}\right)X,
\]
\[
\frac{dF}{dt}=-\left(\frac{\mu}{Y_{X/F}}+\frac{\beta_F}{Y_{E/F}}+m_{ef}\frac{F}{S_\varepsilon}\right)X,
\qquad \frac{dE}{dt}=(\beta_G+\beta_F)X.
\]

Los rendimientos son constantes en cada theta. El ajuste nuevo impone \(0<Y_{E/G},Y_{E/F}\leq0.5114\).
Nutriciones: \(N(t_p^+)=N(t_p^-)+\Delta N_p\), muestra antes del salto si coinciden.
El RHS evalúa cinéticas con concentraciones no negativas, como el anterior. Integraciones con estados <−10⁻⁶ se rechazan;
esto no corrige la limitación estructural de que el término de crecimiento puede consumir un azúcar agotado.

## Conexión CO₂ conservada

La fuente fermentativa de cada trayectoria es \(q_{ferm}=(44.01/46.07)(\beta_G+\beta_F)X\).
La capa histórica calcula trayectorias con y sin nutrición y conserva la rampa, multiplicador transitorio,
activación por azúcar consumido y modulación por oxígeno. No se simplificaron en esta tarea.
Con b=`pulse_activity_gain`, r la rampa y M el multiplicador:

\[
q_{prod}=\operatorname{gate}\,f_{ferm}(O_2)\,M\,
\max\{[1+(b-1)r]q_{sin\ N}+r(q_{con\ N}-q_{sin\ N}),0\}.
\]

La solubilidad y la liberación histórica son:
\[
C_{sat}=\mathrm{scale}\,1.69e^{-0.032(T-20)}e^{0.0016E}e^{-0.0012(G+F)},
\]
\[
q_{gas}=kC_d\left(0.05+0.95\frac{C_d}{C_d+C_{sat}}\right),\qquad
\frac{dC_d}{dt}=q_{prod}-q_{gas}.
\]

El notebook conserva el reservorio implícito de raíz positiva y el operador offline de observación v3.
La ganancia `matrix_gain` multiplica la liberación para compararla con el sensor; no es un rendimiento químico.
El auxiliar `finish` conserva su integrador histórico de referencia para preparar oxígeno y fuente;
el ajuste principal usa `release_forward` implícito, igual que el notebook anterior.
Los detalles ejecutables de rampas, filtrado y ajustes están en el SOURCE de CO₂.
La capa no realimenta las cinco ecuaciones químicas. La ecuación histórica de fuente no constituye un balance de carbono cerrado.
