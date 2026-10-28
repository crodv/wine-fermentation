
import importlib
import numpy as np
import pandas as pd
from .solubility import saturation,STATUS
from .. import model as current

def simulate(name,batch,p,core,gas_parameters,volume):
    model=importlib.import_module('wine_fermentation.models.'+name+'.kinetics')
    # Conservative concentration reservoir; homogeneous withdrawals preserve Cd.
    grid=np.unique(np.r_[np.arange(0.,core.index[-1],.1),core.index[-1],core.index])
    values=np.column_stack([np.interp(grid,core.index,core[k]) for k in model.STATES])
    rate=[]
    for ti,yi in zip(grid,values):
        q=model.terms(ti,yi,p,batch)
        rate.append((q['mu']/12.72+(q['beta_g']+q['beta_f'])/1.05)*yi[0])
    rate=np.array(rate)
    T=np.interp(grid,batch.time,batch.temperature_c)
    E=values[:,model.STATES.index('E')];G=values[:,model.STATES.index('G')];F=values[:,model.STATES.index('F')]
    sat=saturation(T,E,G,F)
    cd=np.zeros(len(grid));cd[0]=gas_parameters['Cd0']
    released=np.zeros(len(grid))
    k=gas_parameters['kLa']
    for i,dt in enumerate(np.diff(grid),1):
        inventory=cd[i-1]+dt*rate[i-1]
        # Implicit positive-part transfer: no release below saturation.
        cd[i]=inventory if inventory<=sat[i] else (inventory+dt*k*sat[i])/(1+dt*k)
        released[i]=(inventory-cd[i])/dt
    qgas=np.r_[k*max(cd[0]-sat[0],0),released[1:]]
    residual=np.diff(cd)-np.diff(grid)*(rate[:-1]-released[1:])
    assert np.max(abs(residual))<1e-9
    V=volume(grid)
    f=pd.DataFrame(dict(X=np.interp(grid,core.index,core.X),qprod=rate,Cd=cd,Md=V*cd,V=V,
        qgas=qgas,qpred=gas_parameters['gain']*qgas,Csat=sat),index=grid)
    f.attrs['solubility_status']=STATUS
    return f
