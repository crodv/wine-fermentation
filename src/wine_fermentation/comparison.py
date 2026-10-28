"""Matched CO2 calibration in both directions; chemical parameters remain fixed."""
import importlib
import json
from pathlib import Path
from dataclasses import replace
import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from .models.historical.calibration import load, release_forward, GAS_NAMES, GAS_BOUNDS
from .shared.simulation import simulate

NAMES=('historical','without_transporters','with_transporters')
LABS=tuple(f'LAB{i:03}' for i in range(16,22))
PRIMARY_TRAINING='train_019_021'
PARTITIONS={PRIMARY_TRAINING:LABS[3:], 'train_016_018':LABS[:3]}

def partition(training):
    if training not in PARTITIONS:
        raise ValueError(f'Unknown CO2 partition: {training}')
    train=PARTITIONS[training]
    holdout=tuple(lab for lab in LABS if lab not in train)
    return train,holdout

def observations(data):
    result={}
    for lab in LABS:
        frame=data[(data.lab==lab)&(data.time_h>=0)&(data.record_kind=='native')].copy()
        frame['bin']=np.floor(frame.time_h).astype(int)
        result[lab]=frame.groupby('bin')[['time_h','co2_raw_g_l_h']].median().dropna()
    return result

def fit_prediction(predict,observed,training_labs,start,bounds,max_nfev=100):
    """Only training_labs may enter the optimizer, including its objective."""
    def residual(x):
        parts=[]
        for lab in training_labs:
            f=predict(lab,np.exp(x))
            obs=observed[lab]
            obs=obs[obs.time_h.between(f.index.min(),f.index.max())]
            if obs.empty:raise ValueError(f'No covered training observations: {lab}')
            error=np.interp(obs.time_h,f.index,f.qpred)-obs.co2_raw_g_l_h.to_numpy()
            parts.append(error/np.sqrt(len(error)))
        return np.concatenate(parts)
    lo,hi=np.asarray(bounds,float).T
    return least_squares(residual,np.log(start),bounds=(np.log(lo),np.log(hi)),
                         max_nfev=max_nfev,ftol=1e-7,xtol=1e-7,gtol=1e-7)

def prepare(root):
    root=Path(root);V=load(root);V.prepare_all()
    data=pd.read_csv(root/'data/processed/co2_mass_balance_lab016_021_g_l_h.csv',
        usecols=['lab','time_h','record_kind','remaining_volume_L','co2_raw_g_l_h'])
    chemical={('historical',lab):V.cores['theta_nv2',lab] for lab in LABS}
    contexts={}
    for name in NAMES[1:]:
        p=json.loads((root/f'configs/models/{name}/fit.json').read_text(encoding='utf-8'))['parameters']
        contexts[name]={}
        for lab,batch in V.batches.items():
            events=data[(data.lab==lab)&(data.record_kind=='withdrawal_after')].sort_values('time_h')
            et=events.time_h.to_numpy();ev=events.remaining_volume_L.to_numpy()
            def volume(t,et=et,ev=ev):
                return np.r_[2.,ev][np.searchsorted(et,np.asarray(t,float),side='right')]
            if lab in LABS[3:]:
                batch=replace(batch,pulses={**batch.pulses,'N':tuple((t,d*2/float(volume(t))) for t,d in batch.pulses['N'])})
            core=simulate(name,batch,p);chemical[name,lab]=core
            contexts[name][lab]=(batch,p,core,volume)
    return dict(V=V,data=data,observations=observations(data),chemical=chemical,contexts=contexts)

def predictor(name,prepared):
    V=prepared['V']
    if name=='historical':
        def predict(lab,values):
            physical,cd,qout=release_forward(V.cache['theta_nv2',lab],dict(zip(GAS_NAMES,values)))
            return pd.DataFrame({'qpred':physical,'Cd':cd,'qgas':qout},index=V.cache['theta_nv2',lab]['time'])
        return predict
    module=importlib.import_module('wine_fermentation.models.'+name+'.co2')
    def predict(lab,values):
        batch,p,core,volume=prepared['contexts'][name][lab]
        cd={'LAB019':.907,'LAB020':.730,'LAB021':.829}.get(lab,0.)
        return module.simulate(batch,p,core,dict(kLa=values[0],gain=values[1],Cd0=cd),volume)
    return predict

def fit_path(root,name):return Path(root)/f'configs/models/{name}/gas_fit.json'

def save_fit(root,name,training,fit):
    path=fit_path(root,name)
    stored=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    if 'experiments' not in stored:
        # Preserve the first completed experiment as provenance, not an active fit.
        stored={'previous_single_partition_fit':stored} if stored else {}
        stored['experiments']={}
    stored.update(primary_training=PRIMARY_TRAINING,comparison_target='hourly_median_raw_g_l_h')
    stored['experiments'][training]=fit
    path.write_text(json.dumps(stored,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def run(root,fit_gas=False,training=PRIMARY_TRAINING,prepared=None):
    train,holdout=partition(training)
    root=Path(root);prepared=prepare(root) if prepared is None else prepared
    curves={};fits={};metrics=[]
    for name in NAMES:
        predict=predictor(name,prepared)
        keys=GAS_NAMES if name=='historical' else ('kLa','gain')
        start=(.4,1.,.7) if name=='historical' else (1.,.7)
        bounds=GAS_BOUNDS if name=='historical' else ((.01,20.),(.05,3.))
        if fit_gas:
            sol=fit_prediction(predict,prepared['observations'],train,start,bounds)
            values=np.exp(sol.x)
            fit={**dict(zip(keys,map(float,values))), 'success':bool(sol.success),'message':str(sol.message),
                 'training':training,'training_labs':list(train),'holdout_labs':list(holdout),
                 'objective':float(sol.fun@sol.fun),'nfev':int(sol.nfev),'optimality':float(sol.optimality),
                 'active_bounds':[key for key,a in zip(keys,sol.active_mask) if a],
                 'initial_parameters':dict(zip(keys,start)),
                 'parameter_bounds':{key:list(b) for key,b in zip(keys,bounds)},
                 'target':'hourly_median_raw_g_l_h','weighting':'equal_lab_mean_squared_error',
                 'chemical_parameters':'theta_nv2' if name=='historical' else 'unchanged chemical fit.json',
                 'historical_equations_unchanged':name=='historical',
                 'solubility_status':'historical_unchanged' if name=='historical' else 'provisional_inherited_correlation',
                 'Cd0_unmeasured':'0 assumed for LAB016-018'}
            save_fit(root,name,training,fit)
            print(name,training,'objective',round(fit['objective'],6),'success',fit['success'],flush=True)
        else:
            stored=json.loads(fit_path(root,name).read_text(encoding='utf-8'))
            if training not in stored.get('experiments',{}):
                raise ValueError(f'Missing CO2 fit {name}/{training}; execute calibration notebook first')
            fit=stored['experiments'][training]
            if fit['training_labs']!=list(train) or fit['holdout_labs']!=list(holdout):
                raise ValueError(f'Partition metadata mismatch: {name}/{training}')
            values=np.array([fit[key] for key in keys])
        fits[name]=fit
        for lab in LABS:
            f=predict(lab,values);curves[name,lab]=f
            obs=prepared['observations'][lab]
            obs=obs[obs.time_h.between(f.index.min(),f.index.max())]
            error=np.interp(obs.time_h,f.index,f.qpred)-obs.co2_raw_g_l_h.to_numpy()
            metrics.append(dict(model=name,training=training,lab=lab,n=len(obs),
                split='gas_training' if lab in train else 'gas_validation',
                RMSE=float(np.sqrt(np.mean(error**2))),bias=float(error.mean())))
    chemical_metrics=[]
    for (name,lab),f in prepared['chemical'].items():
        if lab not in LABS[3:]:continue
        samples=prepared['V'].chem.query('lab==@lab and is_NUT==False and t_h>0').copy()
        samples['GF_g_l']=samples.G_g_l+samples.F_g_l
        for state,col in dict(X='X_viable_g_l',N='N_kg_m3',G='G_g_l',F='F_g_l',E='E_g_l',GF='GF_g_l').items():
            obs=samples[['t_h',col]].dropna();obs=obs[obs.t_h<=f.index.max()]
            prediction=f.G+f.F if state=='GF' else f[state]
            error=np.interp(obs.t_h,f.index,prediction)-obs[col].to_numpy()
            if len(error):chemical_metrics.append(dict(model=name,lab=lab,state=state,n=len(error),
                RMSE=float(np.sqrt(np.mean(error**2))),bias=float(error.mean())))
    return dict(curves=curves,chemical=prepared['chemical'],metrics=pd.DataFrame(metrics),
        chemical_metrics=pd.DataFrame(chemical_metrics),gas_fits=fits,data=prepared['data'],V=prepared['V'],
        training=training,training_labs=train,holdout_labs=holdout)

def run_both(root,fit_gas=False):
    prepared=prepare(root)
    return {key:run(root,fit_gas=fit_gas,training=key,prepared=prepared) for key in PARTITIONS}
