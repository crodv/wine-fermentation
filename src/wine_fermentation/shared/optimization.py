
from pathlib import Path
import json,time
import numpy as np
from scipy.optimize import least_squares
from .. import model as current
from .simulation import simulate

def fit(root,name,batches):
    root=Path(root);config=json.loads((root/f'configs/models/{name}/calibration.json').read_text())
    start=current.normalize_parameters(json.loads((root/'configs/theta/theta_full.json').read_text()))
    start.update(config['extra_initial']);names=list(config['bounds'])
    lo=np.array([config['bounds'][k][0] for k in names]);hi=np.array([config['bounds'][k][1] for k in names])
    exact=np.array([start[k] for k in names]);x0=np.clip(exact,lo+1e-10,hi-1e-10)
    support=[]
    for b in batches:
        for state in current.STATE_NAMES:
            obs=b.observations[state];mask=np.isfinite(obs)&(b.time>0)
            support.append((b,state,mask,obs[mask],current.sigma_for_state(state,obs[mask])))
    nres=sum(len(z[3]) for z in support);calls=0;begin=time.monotonic()
    def residual(x):
        nonlocal calls
        calls+=1;p={**start,**dict(zip(names,np.exp(x)))}
        try:pred={b.batch:simulate(name,b,p) for b in batches}
        except (RuntimeError,ValueError,FloatingPointError):return np.full(nres,1e4)
        return np.concatenate([(pred[b.batch][state].to_numpy()[mask]-obs)/sigma for b,state,mask,obs,sigma in support])
    initial=residual(np.log(x0))
    sol=least_squares(residual,np.log(x0),bounds=(np.log(lo),np.log(hi)),max_nfev=config['max_nfev'],diff_step=1e-3,
                      ftol=2e-5,xtol=2e-5,gtol=2e-5)
    result=dict(model=name,parameters={**start,**dict(zip(names,np.exp(sol.x)))},
       success=bool(sol.success),message=sol.message,initial_objective=float(np.mean(initial**2)),
       final_objective=float(np.mean(sol.fun**2)),calls=calls,seconds=time.monotonic()-begin,
       initialization_changes={k:dict(theta_full=float(a),feasible_start=float(b)) for k,a,b in zip(names,exact,x0) if a!=b},
       free=names,training_labs=[b.batch for b in batches],solubility_status=config['solubility_status'])
    (root/f'configs/models/{name}/fit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(name,result['success'],result['final_objective'],round(result['seconds'],1),flush=True)
    return result
