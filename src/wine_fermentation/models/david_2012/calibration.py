"""Chemical-only calibration. No LAB019-021 or CO2 observations read here."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from ...data import natural_batches
from .kinetics import simulate
from .empirical import NAMES,START,BOUNDS,build
LABS=tuple(f'LAB{i:03}' for i in range(4,10))
COLUMNS=dict(X='X_viable_kg_m3',N='N_kg_m3',S='S_observed_g_l',E='E_g_l')
SCALES=dict(X=.25,N=.03,S=5.,E=3.)
WEIGHTS=dict(X=2.,N=2.,S=1.,E=1.)

def prepare(root):
 data,batches,profiles=natural_batches(root)
 data=data[data.batch.isin(LABS)].copy()
 assert set(data.batch)==set(LABS)
 tasks=[]
 for b in batches:
  raw=data[data.batch==b.batch]
  initial=dict(X=b.initials['X'],N=b.initials['N'],S=b.initials['G']+b.initials['F'],E=b.initials['E'])
  # Prefer the measured combined initial sugar over a sum of separately cleaned assays.
  initial_s=raw.loc[raw.time_h.eq(0),COLUMNS['S']].dropna()
  if len(initial_s):initial['S']=float(initial_s.iloc[0])
  t=np.unique(np.r_[np.arange(0,b.time[-1],.5),b.time,raw.time_h.to_numpy()])
  t=t[(t>=0)&(t<=b.time[-1])]
  support={}
  for state,col in COLUMNS.items():
   o=raw.dropna(subset=['time_h',col]);o=o[o.time_h.gt(0)&o.time_h.le(t[-1])]
   support[state]=(o.time_h.to_numpy(float),o[col].to_numpy(float))
  tasks.append(dict(lab=b.batch,time=t,temp=np.interp(t,b.time,b.temperature_c),initial=initial,events=b.pulses['N'],support=support))
 return tasks,data,profiles

def fit(tasks,max_nfev=45):
 lower,upper=np.array(BOUNDS).T
 size=sum(len(y) for z in tasks for t,y in z['support'].values())
 assert set(z['lab'] for z in tasks)==set(LABS)
 calls=0
 def residual(logvalues):
  nonlocal calls
  calls+=1;parts=[]
  try:
   p=build(np.exp(logvalues))
   for z in tasks:
    f=simulate(z['time'],z['temp'],z['initial'],z['events'],p)
    for state,(t,y) in z['support'].items():
     if len(y):parts.extend(np.sqrt(WEIGHTS[state]/len(y))*(np.interp(t,f.index,f[state])-y)/SCALES[state])
  except (RuntimeError,ValueError,FloatingPointError):return np.full(size,1e4)
  return np.asarray(parts)
 initial=np.array(START,float);initial_error=float(np.sum(residual(np.log(initial))**2))
 runs=[]
 for number,start in enumerate([initial,initial*np.r_[np.full(7,.8),np.ones(len(initial)-7)]]):
  sol=least_squares(residual,np.log(np.clip(start,lower+1e-7,upper-1e-7)),bounds=(np.log(lower),np.log(upper)),
   max_nfev=max_nfev,diff_step=.002,ftol=3e-4,xtol=3e-4,gtol=3e-4)
  runs.append(sol)
  print('Start',number+1,'objective',sol.fun@sol.fun,'success',sol.success,'nfev',sol.nfev,flush=True)
 best=min(runs,key=lambda s:s.fun@s.fun);values=np.exp(best.x)
 singular=np.linalg.svd(best.jac,compute_uv=False)
 result=dict(parameters=dict(zip(NAMES,map(float,values))),success=bool(best.success),message=best.message,
 objective=float(best.fun@best.fun),initial_objective=initial_error,calls=calls,
 training_labs=list(LABS),training_variables=list(COLUMNS),CO2_in_objective=False,
 validation_labs=['LAB019','LAB020','LAB021'],scales=SCALES,weights=WEIGHTS,
 bounds=dict(zip(NAMES,[list(x) for x in BOUNDS])),singular_values=singular.tolist(),
 active_bounds=[name for name,x,lo,hi in zip(NAMES,values,lower,upper) if min((x-lo)/(hi-lo),(hi-x)/(hi-lo))<.001],
 empirical_functions='Reconstructed linear thermal Table I shapes; fitted two-knot nutrition and initial Nx partition. Not author source code.',
 runs=[dict(objective=float(s.fun@s.fun),success=bool(s.success),nfev=s.nfev) for s in runs])
 return build(values),result
