"""Conservative supersaturation reservoir downstream of fixed David chemistry.

Temperature dependence from the empirical Henry relation reproduced in
Liger-Belair et al. 2023, DOI 10.1021/acsomega.3c01812, Eq.1.
At fixed ethanol a=12.5 vol% and sugar b=0, the thermal coefficient is
7e-5*a-0.02905=-0.028175 / Celsius. Anchor at 1.5 g/L/bar, 20 C.
This is a reference-wine approximation, not measured must solubility.
The supersaturation transfer law and assumed constant pCO2 are modeling
choices; neither belongs to David's original model nor follows from Henry alone.
"""
import numpy as np
import pandas as pd

def saturation(temperature_c,pco2_bar=1.,reference_g_l_bar=1.5):
    if pco2_bar<=0 or reference_g_l_bar<=0:raise ValueError('Positive pressure/reference required')
    return reference_g_l_bar*np.exp(-.028175*(np.asarray(temperature_c)-20.))*pco2_bar


def simulate(core,temperature_time,temperature_c,volume,kLa=2.,Cd0=0.,step=.025,pco2_bar=1.):
    if kLa<=0 or Cd0<0 or step<=0:raise ValueError('Invalid transfer parameters')
    t0=float(core.index[0]);tf=float(core.index[-1])
    grid=np.unique(np.r_[np.arange(t0,tf,step),tf,core.index,np.asarray(getattr(volume,"knots",[]))])
    # Remove near-duplicate floating times; avoid cancellation at nominal common knots.
    grid=grid[(grid>=t0)&(grid<=tf)]
    grid=grid[np.r_[True,np.diff(grid)>1e-9]]
    T=np.interp(grid,temperature_time,temperature_c);sat=saturation(T,pco2_bar)
    source=np.interp(grid,core.index,core.qCO2)
    cd=np.zeros(len(grid));cd[0]=Cd0;q=np.zeros(len(grid));q[0]=kLa*max(Cd0-sat[0],0)
    for i,h in enumerate(np.diff(grid),1):
        inventory=cd[i-1]+h*source[i-1]
        cd[i]=inventory if inventory<=sat[i] else (inventory+h*kLa*sat[i])/(1+h*kLa)
        q[i]=kLa*max(cd[i]-sat[i],0.)
    residual=np.diff(cd)-np.diff(grid)*(source[:-1]-q[1:])
    if np.max(abs(residual))>1e-9:raise AssertionError('Concentration balance')
    if min(cd.min(),q.min())<-1e-12:raise AssertionError('Negative concentration/flow')
    V=volume(grid)
    result=pd.DataFrame(dict(T=T,Csat=sat,Cd=cd,V=V,Md=V*cd,qprod=source,qgas=q),index=grid)
    result.attrs.update(kLa=kLa,Cd0=Cd0,pCO2_bar=pco2_bar,step_h=step,max_balance_error=float(np.max(abs(residual))))
    return result
