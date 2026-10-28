
from dataclasses import replace
import importlib
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from .. import model as current

def simulate(name,batch,parameters):
    model=importlib.import_module('wine_fermentation.models.'+name+'.kinetics')
    if name=='historical':return model.integrate(batch,parameters)
    t=np.asarray(batch.time,float);y=model.initial(batch,parameters);out={float(t[0]):y.copy()}
    events=dict(batch.pulses.get('N',()))
    now=float(t[0])
    for end in sorted(set([float(t[-1])]+[float(x) for x in events if now<x<=t[-1]])):
        requested=t[(t>now)&(t<=end)]
        sol=solve_ivp(lambda ti,yi:model.rhs(ti,yi,parameters,batch),(now,end),y,
            t_eval=np.unique(np.r_[requested,end]),method='LSODA',rtol=2e-6,atol=2e-8,max_step=.75)
        tolerance=np.full(len(model.STATES),1e-6)
        for species in ('G','F'):tolerance[model.STATES.index(species)]=1e-4
        if not sol.success or not np.isfinite(sol.y).all() or np.any(sol.y.min(axis=1)<-tolerance):
            raise RuntimeError('Invalid integration: '+str(dict(zip(model.STATES,sol.y.min(axis=1).tolist()))))
        out.update({float(ti):yi.copy() for ti,yi in zip(sol.t,sol.y.T)})
        y=sol.y[:,-1].copy();now=end
        if end in events:y=model.nutrition(y,float(events[end]),parameters)
    values=np.vstack([out[float(ti)] for ti in t])
    f=pd.DataFrame(np.maximum(values,0),index=t,columns=model.STATES)
    f.attrs['minimum_integrated_states']=dict(zip(model.STATES,values.min(axis=0).tolist()))
    f.attrs['roundoff_policy']='G/F down to -1e-4 g/L; other states -1e-6 g/L; report minima and project outputs to zero'
    if name=='with_transporters':f['N']=f.Nx+f.Ntr
    return f
