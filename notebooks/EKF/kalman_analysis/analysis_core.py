"""Training-only EKF noise analysis. No holdout simulations or model-file writes.

All numerical results are exploratory. Q amplitudes are flux diffusion amplitudes,
not kinetic parameters. Native process temperatures are treated as known inputs.
"""
from pathlib import Path
import ast
import hashlib
import json
import math
import numpy as np
import pandas as pd
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import chi2
from numba import njit

LABS = ('LAB019', 'LAB020', 'LAB021')
STATES = ('X', 'N', 'G', 'F', 'E', 'Cd', 'I')
SOURCE_NAMES = ('Growth', 'Glucose fermentation', 'Fructose fermentation',
                'Additional CO2', 'Mortality', 'Maintenance')
THETA = dict(mu0=.09403147367985473, betaG0=.42243676903335664,
             betaF0=.6236552480900203, Kn0=.008257860224319971,
             Kg0=4.400775419123265, Kf0=19.296083508118652,
             Kig0=65.01993873457147, Kie0=96.26516563486751,
             Kd0=.00044, Yxn=6.456225797038313, Yxg=.9660935553477866,
             Yxf=1.1098958529485594, Yeg=.4684585383875136,
             Yef=.5113278649826252, m0=.0183385793928771)
PARS = np.array(list(THETA.values()))
SCALE = np.array([.3,.25,80.,80.,15.,.2,1.])
BASE_SIGMA = np.array([.003,.08,.08,.01,0.,0.])
ARCHIVED_GAS = np.array([.15007991020720535,.6460643588058115])
CHEM_COLS = dict(X='X_viable_g_l', N='N_kg_m3', G='G_g_l', F='F_g_l',
                 GF='GF_g_l', E='E_g_l')
# Bounds are sensitivity/search constraints, not measured confidence intervals.
LOG_BOUNDS = dict(growth=(-2.,1.), fermentation=(-2.,1.), gas=(-2.,1.),
                  mortality=(-5.,-1.), maintenance=(-4.,0.), R=(-3.,-.7))
STRUCTURES = {
    'Current': ('growth','fermentation','gas','R'),
    '+ mortality': ('growth','fermentation','gas','mortality','R'),
    '+ maintenance': ('growth','fermentation','gas','maintenance','R'),
    '+ both': ('growth','fermentation','gas','mortality','maintenance','R'),
    'Separate G/F': ('growth','ferm_G','ferm_F','gas','R'),
    'No extra CO2': ('growth','fermentation','R'),
}

def filtered_csv(path, **kwargs):
    """Discard every nondevelopment row immediately, before any analysis."""
    chunks = pd.read_csv(path, chunksize=100000, **kwargs)
    return pd.concat([c.loc[c.lab.isin(LABS)].copy() for c in chunks], ignore_index=True)

def recent_raw(path, columns):
    parts=[]
    for c in pd.read_csv(path, usecols=columns, chunksize=200000):
        c=c.loc[c.timestamp.ge('2026-09-21 11:00:00')].copy()
        if len(c): parts.append(c)
    frame=pd.concat(parts,ignore_index=True)
    stamp=pd.DatetimeIndex(pd.to_datetime(frame.timestamp)).tz_localize('America/Santiago',ambiguous='raise',nonexistent='raise').tz_convert('UTC')
    origin=pd.Timestamp('2026-09-21 17:00:00',tz='America/Santiago').tz_convert('UTC')
    frame['t_h']=(stamp-origin).total_seconds()/3600
    return frame

def prepare(root):
    root=Path(root)
    initials=filtered_csv(root/'data/compatibility/co2_v3/initial_conditions_v2.csv').set_index('lab')
    chem=filtered_csv(root/'data/compatibility/co2_v3/chemistry_v2.csv')
    coverage=filtered_csv(root/'data/compatibility/co2_v3/reference/coverage.csv').set_index('lab')
    volumes=filtered_csv(root/'data/processed/co2_mass_balance_lab016_021_g_l_h.csv',usecols=['lab','time_h','record_kind','remaining_volume_L'])
    base=root/'data/original/natural/lab019_021'
    raw=recent_raw(base/'backup_global_co2_completo.csv',['timestamp','fermentador','flow_sccm'])
    temp=recent_raw(base/'backup_global_temperatura_completo.csv',['timestamp','fermentador','T'])
    assert set(initials.index)==set(LABS) and set(chem.lab)==set(LABS)
    data={}; audit=[]; raw_audit=[]
    for i,lab in enumerate(LABS):
        horizon=float(coverage.loc[lab,'cut_h'])
        v=volumes.loc[volumes.lab.eq(lab)&volumes.record_kind.eq('withdrawal_after')].sort_values('time_h')
        et=v.time_h.to_numpy(); vv=v.remaining_volume_L.to_numpy()
        def volume(t): return np.r_[2.,vv][np.searchsorted(et,np.asarray(t),side='right')]
        rg=raw.loc[raw.fermentador.eq('F'+str(i+1))].sort_values('t_h').dropna(subset=['flow_sccm']).copy()
        rg['bin']=np.ceil(rg.t_h/.5-1e-10).astype(int)
        rows=[]
        for end in np.arange(.5,horizon+1e-9,.5):
            d=rg.loc[rg.bin.eq(round(end/.5))]
            gaps=np.diff(np.r_[end-.5,d.t_h.to_numpy(),end])
            y=d.flow_sccm.to_numpy()*(44.0095*60*.74/(1000*24.16))/volume(d.t_h.to_numpy())
            rows.append((end,np.mean(y) if len(y) else np.nan,len(d)>=30 and gaps.max()<=2/60))
            if len(y)>=30:
                # Split-window contrast is descriptive, NOT a pure sensor-noise estimator.
                halves=[y[d.t_h.to_numpy()<=end-.25],y[d.t_h.to_numpy()>end-.25]]
                raw_audit.append(dict(LAB=lab,t_h=end,n=len(y),raw_SD=float(np.std(y,ddof=1)),
                    naive_SE=float(np.std(y,ddof=1)/np.sqrt(len(y))),
                    lag1=float(pd.Series(y).autocorr()) if np.std(y)>0 else np.nan,
                    half_difference=float(np.mean(halves[1])-np.mean(halves[0])) if all(map(len,halves)) else np.nan))
        sensor=pd.DataFrame(rows,columns=['t_h','measured','valid'])
        sensor['assimilate']=sensor.valid&sensor.measured.ge(.05)&sensor.valid.shift(fill_value=False)&sensor.measured.shift().ge(.05)
        rt=temp.loc[temp.fermentador.eq('F'+str(i+1))].sort_values('t_h').copy()
        rt['minute']=np.floor(rt.t_h*60).astype(int)
        tm=rt.groupby('minute').T.median().dropna()
        available=(tm.index.to_numpy()+1)/60; temperatures=tm.to_numpy(float)
        events=ast.literal_eval(initials.loc[lab,'N_events'])
        events=np.array([(round(t,10),dose*2/float(volume(t))) for t,dose in events],float)
        ini=np.array([float(initials.loc[lab,k]) for k in STATES[:5]]+[0.,0.])
        ini[4]=10.010194
        if lab=='LAB021': ini[0]=.27
        P0=np.diag([max(.03,.2*ini[0])**2,.015**2,12.5,37.5,4.,0.,0.]);P0[2,3]=P0[3,2]=-12.5
        grid=np.unique(np.round(np.r_[np.arange(0,horizon,1/12),sensor.t_h,horizon,events[:,0]],10))
        doses=np.zeros(len(grid));obs=np.full(len(grid),np.nan);valid=np.zeros(len(grid),bool);update=np.zeros(len(grid),bool)
        for t,dose in events: doses[np.argmin(abs(grid-t))]+=dose
        for row in sensor.itertuples():
            j=np.argmin(abs(grid-row.t_h));assert abs(grid[j]-row.t_h)<1e-8
            obs[j]=row.measured;valid[j]=row.valid;update[j]=row.assimilate
        d=dict(grid=grid,doses=doses,y=obs,valid=valid,update=update,initial=ini,P0=P0,
               available=available,temperature=temperatures,S0=ini[2]+ini[3],sensor=sensor,horizon=horizon)
        data[lab]=d
        audit.append(dict(LAB=lab,horizon_h=horizon,windows=len(sensor),updates=int(sensor.assimilate.sum()),
                          X0=ini[0],N0=ini[1],G0=ini[2],F0=ini[3],E0=ini[4],pulse_h=events[0,0],dose_g_L=events[0,1]))
    assert tuple(data)==LABS
    return data,chem,pd.DataFrame(audit),pd.DataFrame(raw_audit)

@njit(cache=True)
def temperature_at(t,available,values):
    j=np.searchsorted(available,t+1e-12,side='right')-1
    if j<0: raise ValueError('No causal temperature')
    return values[j]

@njit(cache=True)
def scalar_terms(x,n,g,f,e,T,S0):
    tk=T+273.15;R=8.314
    p=PARS
    am=np.exp(59453*(tk-300)/(300*R*tk));ab=np.exp(11000*(tk-296.15)/(296.15*R*tk));ak=np.exp(46055*(tk-293.15)/(293.15*R*tk))
    mu=p[0]*am*n/(n+p[3]*ak+1e-8)
    if g<=0 or f<=0:mu=0.
    bg=p[1]*ab*g/(g+p[4]*ak+1e-8)/(1+e/(p[7]*(ak+1e-8)))
    bf=p[2]*ab*f/(f+p[5]*ak+1e-8)/(1+g/(p[6]*(ak+1e-8)))/(1+e/(p[7]*(ak+1e-8)))
    td=-.0001*e**3+.0049*e**2-.1279*e+315.89
    kd=p[8]*np.exp(.0415*e+130000*(tk-305.65)/(305.65*R*tk)) if tk>=td else 0.
    m=p[14]*np.exp(37681*(tk-293.3)/(293.3*R*tk))*(g+f+1e-8)/(g+f+1+1e-8)
    z=min(max((S0-g-f-5)/5,0.),1.);A=z*z*(3-2*z)
    a=e/7.8924;cs=3.295*np.exp((7e-5*a-.02905)*T-.0179*a-.00111*(g+f))
    return mu,bg,bf,kd,m,A,cs

@njit(cache=True)
def terms(w,T,S0):
    return scalar_terms(max(w[0],0.),max(w[1],0.),max(w[2],0.),max(w[3],0.),max(w[4],0.),T,S0)

@njit(cache=True)
def rhs_fill(w,T,S0,kla,gain,out):
    p=PARS
    for j in range(w.shape[0]):
        x=max(w[j,0],0.);n=max(w[j,1],0.);g=max(w[j,2],0.);f=max(w[j,3],0.);e=max(w[j,4],0.);cd=max(w[j,5],0.)
        mu,bg,bf,kd,m,A,cs=scalar_terms(x,n,g,f,e,T,S0)
        qp=A*(mu/12.72+(bg+bf)/1.05)*x
        acc=min(qp,kla*max(cs-cd,0.))-kla*max(cd-cs,0.)
        out[j,0]=(mu-kd)*x;out[j,1]=-mu*x/p[9]
        out[j,2]=-(mu/p[10]+bg/p[12]+m*g/(g+f+1e-8))*x
        out[j,3]=-(mu/p[11]+bf/p[13]+m*f/(g+f+1e-8))*x
        out[j,4]=(bg+bf)*x;out[j,5]=acc;out[j,6]=gain*(qp-acc)

@njit(cache=True)
def batch_transition(points,start,end,available,temps,S0,kla,gain,step):
    w=points*SCALE;k1=np.empty_like(w);k2=np.empty_like(w);k3=np.empty_like(w);k4=np.empty_like(w);work=np.empty_like(w)
    n=max(1,int(np.ceil((end-start)/step-1e-7)));dt=(end-start)/n
    for j in range(n):
        t=start+j*dt;T0=temperature_at(t,available,temps);Tm=temperature_at(t+dt/2,available,temps);T1=temperature_at(t+dt,available,temps)
        rhs_fill(w,T0,S0,kla,gain,k1)
        for a in range(len(w)):
            for b in range(7):work[a,b]=w[a,b]+dt*k1[a,b]/2
        rhs_fill(work,Tm,S0,kla,gain,k2)
        for a in range(len(w)):
            for b in range(7):work[a,b]=w[a,b]+dt*k2[a,b]/2
        rhs_fill(work,Tm,S0,kla,gain,k3)
        for a in range(len(w)):
            for b in range(7):work[a,b]=w[a,b]+dt*k3[a,b]
        rhs_fill(work,T1,S0,kla,gain,k4)
        for a in range(len(w)):
            for b in range(7):w[a,b]=max(w[a,b]+dt*(k1[a,b]+2*k2[a,b]+2*k3[a,b]+k4[a,b])/6,0.)
    return w/SCALE

@njit(cache=True)
def rhs(w,T,S0,kla,gain):
    x,n,g,f,e,cd=np.maximum(w[:6],0.);mu,bg,bf,kd,m,A,cs=terms(w,T,S0);p=PARS
    qp=A*(mu/12.72+(bg+bf)/1.05)*x
    acc=min(qp,kla*max(cs-cd,0.))-kla*max(cd-cs,0.)
    return np.array([(mu-kd)*x,-mu*x/p[9],-(mu/p[10]+bg/p[12]+m*g/(g+f+1e-8))*x,
                     -(mu/p[11]+bf/p[13]+m*f/(g+f+1e-8))*x,(bg+bf)*x,acc,gain*(qp-acc)])

@njit(cache=True)
def transition(z,start,end,available,temps,S0,kla,gain,step=1/60):
    w=z*SCALE;n=max(1,int(np.ceil((end-start)/step-1e-7)));dt=(end-start)/n
    for j in range(n):
        t=start+j*dt;T0=temperature_at(t,available,temps);Tm=temperature_at(t+dt/2,available,temps);T1=temperature_at(t+dt,available,temps)
        k1=rhs(w,T0,S0,kla,gain);k2=rhs(w+dt*k1/2,Tm,S0,kla,gain)
        k3=rhs(w+dt*k2/2,Tm,S0,kla,gain);k4=rhs(w+dt*k3,T1,S0,kla,gain)
        w=np.maximum(w+dt*(k1+2*k2+2*k3+k4)/6,0.)
    return w/SCALE

@njit(cache=True)
def jacobian(z,start,end,available,temps,S0,kla,gain,step):
    points=np.empty((15,7));points[0]=z;J=np.zeros((7,7));eps=1e-5;den=np.empty(7)
    for j in range(7):
        points[j+1]=z;points[j+8]=z;points[j+1,j]+=eps;den[j]=eps
        if z[j]>=eps:points[j+8,j]-=eps;den[j]=2*eps
    out=batch_transition(points,start,end,available,temps,S0,kla,gain,step)
    for j in range(7):J[:,j]=(out[j+1]-out[j+8])/den[j]
    return out[0],J

@njit(cache=True)
def noise_L(w,T,S0,kla,gain):
    x,n,g,f,e,cd=np.maximum(w[:6],0.);mu,bg,bf,kd,m,A,cs=terms(w,T,S0);p=PARS
    qp=A*(mu/12.72+(bg+bf)/1.05)*x;branch=1. if qp<kla*max(cs-cd,0.) else 0.
    L=np.zeros((7,6));L[:5,0]=np.array([1.,-1/p[9],-1/p[10],-1/p[11],0.])
    L[2,1]=-1.;L[4,1]=p[12];L[3,2]=-1.;L[4,2]=p[13]
    prod=A*np.array([1/12.72,p[12]/1.05,p[13]/1.05,1.])
    L[5,:4]=branch*prod;L[6,:4]=gain*(1-branch)*prod
    L[0,4]=-1.;L[2,5]=-g/(g+f+1e-8);L[3,5]=-f/(g+f+1e-8)
    return L

@njit(cache=True,nogil=True)
def replay(grid,doses,y,valid,update,initial,P0,available,temps,S0,kla,gain,sigma,Rsd,correct=True,step=1/60):
    z=initial/SCALE;P=P0/np.outer(SCALE,SCALE);N=len(grid)
    frames=np.zeros((N,7));covs=np.zeros((N,7,7));diag=np.full((N,7),np.nan)
    for i in range(N):
        t=grid[i]
        if i:
            start=grid[i-1];dt=t-start;before=z.copy()
            if correct:
                z,J=jacobian(z,start,t,available,temps,S0,kla,gain,step)
                L=noise_L(before*SCALE,temperature_at(start,available,temps),S0,kla,gain)
                Q=(L@np.diag(sigma*sigma)@L.T)/np.outer(SCALE,SCALE)
                P=J@P@J.T+Q*dt;P=(P+P.T)/2
            else:z=transition(z,start,t,available,temps,S0,kla,gain,step)
        z[1]+=doses[i]/SCALE[1]
        if t>0 and abs(t/.5-round(t/.5))<1e-8:
            R=Rsd[i]*Rsd[i]
            prediction=z[6]/.5;innovation=y[i]-prediction;S=4*P[6,6]+R
            clips=0
            if update[i] and correct:
                K=2*P[:,6]/S;updated=z+K*innovation;clips=np.sum(updated[:6]<0)
                B=np.eye(7);B[:,6]-=2*K
                P=B@P@B.T+np.outer(K,K)*R;P=(P+P.T)/2;z=np.maximum(updated,0.)
            diag[i]=np.array([prediction,innovation,S,innovation*innovation/S,float(clips),1. if update[i] else 0.,1. if valid[i] else 0.])
            z[6]=0.;P[6,:]=0.;P[:,6]=0.
        if not np.all(np.isfinite(z)) or not np.all(np.isfinite(P)):raise ValueError('Nonfinite filter')
        frames[i]=z*SCALE;covs[i]=P*np.outer(SCALE,SCALE)
    return frames,covs,diag

def run(d,gas=ARCHIVED_GAS,sigma=BASE_SIGMA,Rsd=.04,correct=True,step=1/60):
    """Run with a scalar observation SD or an SD vector aligned to the grid."""
    observation_sd=np.asarray(Rsd,dtype=float)
    if observation_sd.ndim==0:
        observation_sd=np.full(d['grid'].shape,observation_sd.item())
    if (observation_sd.shape!=d['grid'].shape or not np.all(np.isfinite(observation_sd))
            or np.any(observation_sd<=0)):
        raise ValueError('Rsd must be positive, finite, and scalar or aligned to the grid')
    return replay(d['grid'],d['doses'],d['y'],d['valid'],d['update'],d['initial'],d['P0'],
                  d['available'],d['temperature'],d['S0'],float(gas[0]),float(gas[1]),np.asarray(sigma,float),observation_sd,correct,step)

def gas_fit(data,labs):
    """Training-only refit using the causal 30-min operator and EKF initials.

    Gain is analytic; kLa profile + bounded refinement. This deliberately differs
    from the archived hourly, offline-temperature gas calibration.
    """
    assert labs and set(labs)<=set(LABS)
    def evaluate(logk,details=False):
        k=np.exp(logk);pairs=[];xx=xy=0.
        for lab in labs:
            d=data[lab];a=run(d,np.array([k,1.]),correct=False)[2];m=d['valid']&np.isfinite(a[:,0])&np.isfinite(d['y'])
            x=a[m,0];y=d['y'][m];xx+=np.mean(x*x);xy+=np.mean(x*y);pairs.append((x,y))
        g=np.clip(xy/max(xx,1e-20),.05,3.);loss=np.mean([np.mean((g*x-y)**2) for x,y in pairs])
        return (loss,k,g) if details else loss
    grid=np.linspace(np.log(.001),np.log(20),33);scores=np.array([evaluate(k) for k in grid]);candidates=[evaluate(grid[0],True),evaluate(grid[-1],True)]
    for j in range(1,len(grid)-1):
        if scores[j]<=scores[j-1] and scores[j]<=scores[j+1]:
            opt=minimize_scalar(evaluate,bounds=(grid[j-1],grid[j+1]),method='bounded',options={'xatol':1e-5})
            candidates.append(evaluate(opt.x,True))
    loss,k,g=min(candidates)
    return np.array([k,g]),pd.DataFrame(dict(kLa=np.exp(grid),MSE=scores)),float(loss)

def decode(x,names):
    v=dict(zip(names,10.**np.asarray(x)))
    sigma=np.zeros(6);sigma[0]=.003*v.get('growth',1.)
    sigma[1]=.08*v.get('fermentation',v.get('ferm_G',1.));sigma[2]=.08*v.get('fermentation',v.get('ferm_F',1.))
    sigma[3]=.01*v['gas'] if 'gas' in v else 0.
    sigma[4]=v.get('mortality',0.);sigma[5]=v.get('maintenance',0.)
    return sigma,v.get('R',.04)

def bounds_for(names):
    return [LOG_BOUNDS.get(n,LOG_BOUNDS['fermentation']) for n in names]

def initial_for(names):
    return np.array([np.log10(.04) if n=='R' else (-3. if n=='mortality' else (-2. if n=='maintenance' else 0.)) for n in names])

def objective(x,names,data,labs,gas,details=False):
    sigma,Rsd=decode(x,names);scores=[];predictions=[]
    try:
        for lab in labs:
            f,P,dg=run(data[lab],gas,sigma,Rsd)
            m=data[lab]['update'];nu=dg[m,1];S=dg[m,2]
            if np.any(S<=0) or not np.all(np.isfinite(S)):return 1e12
            # Equal LAB weights; objective is a screened Gaussian quasi-score.
            scores.append(.5*np.mean(np.log(2*np.pi*S)+nu*nu/S))
            predictions.extend(dg[m,0].tolist())
        value=float(np.mean(scores))
    except (ValueError,OverflowError,np.linalg.LinAlgError):return 1e12
    return (value,np.array(predictions)) if details else value

def fit_noise(data,labs,gas,structure,starts=2,maxiter=220):
    names=STRUCTURES[structure];bounds=bounds_for(names);base=initial_for(names)
    starts_x=[base]
    rng=np.random.default_rng(23021)
    for _ in range(starts-1):starts_x.append(np.clip(base+rng.normal(0,.45,len(base)),np.array(bounds)[:,0],np.array(bounds)[:,1]))
    runs=[];best=None
    for i,start in enumerate(starts_x):
        simplex=np.tile(start,(len(start)+1,1))
        for j in range(len(start)):simplex[j+1,j]=np.clip(start[j]+(.3 if start[j]+.3<=bounds[j][1] else -.3),*bounds[j])
        opt=minimize(objective,start,args=(names,data,labs,gas),method='Nelder-Mead',bounds=bounds,
                     options={'maxiter':maxiter,'xatol':.025,'fatol':1e-4,'adaptive':True,'initial_simplex':simplex})
        row=dict(start=i,score=float(opt.fun),success=bool(opt.success),nfev=int(opt.nfev),message=str(opt.message),x=opt.x.tolist())
        runs.append(row)
        if best is None or opt.fun<best.fun:best=opt
    if not best.success:
        opt=minimize(objective,best.x,args=(names,data,labs,gas),method='Nelder-Mead',bounds=bounds,
                     options={'maxiter':200,'xatol':.025,'fatol':1e-4,'adaptive':True})
        runs.append(dict(start='refinement',score=float(opt.fun),success=bool(opt.success),nfev=int(opt.nfev),message=str(opt.message),x=opt.x.tolist()))
        if opt.fun<=best.fun:best=opt
    sigma,Rsd=decode(best.x,names)
    return dict(structure=structure,names=list(names),x=best.x.tolist(),sigma=sigma.tolist(),Rsd=float(Rsd),
                score=float(best.fun),runs=runs,at_bound=[n for n,a,b in zip(names,best.x,bounds) if min(a-b[0],b[1]-a)<.05])

def diagnostics(data,chem,lab,result):
    f,P,dg=result;d=data[lab];rows=[]
    m=d['valid']&np.isfinite(dg[:,0]);error=dg[m,0]-d['y'][m]
    rows.append(dict(LAB=lab,variable='CO2',unit='g/(L h)',n=int(m.sum()),RMSE=float(np.sqrt(np.mean(error**2))),MAE=float(np.mean(abs(error))),coverage95=np.nan))
    for state,col in CHEM_COLS.items():
        o=chem.loc[chem.lab.eq(lab)&chem.t_h.gt(0)&chem.t_h.le(d['horizon'])].dropna(subset=[col]).copy()
        if state=='GF':o=o.loc[~o.GF_zero_substitution.astype(str).str.lower().eq('true')]
        if not len(o):continue
        pred=f[:,2]+f[:,3] if state=='GF' else f[:,STATES.index(state)]
        var=P[:,2,2]+P[:,3,3]+2*P[:,2,3] if state=='GF' else P[:,STATES.index(state),STATES.index(state)]
        estimate=np.interp(o.t_h,d['grid'],pred);variance=np.maximum(np.interp(o.t_h,d['grid'],var),0.)
        factor=1000 if state=='N' else 1.;err=(estimate-o[col].to_numpy())*factor
        coverage=float(np.mean(abs(estimate-o[col].to_numpy())<=1.96*np.sqrt(variance)))
        rows.append(dict(LAB=lab,variable=state,unit='mg/L' if state=='N' else 'g/L',n=len(o),RMSE=float(np.sqrt(np.mean(err**2))),MAE=float(np.mean(abs(err))),coverage95=coverage))
    m=d['update'];z=dg[m,1]/np.sqrt(dg[m,2]);N=len(z);acf=[]
    # Do not join across gaps in the correction sequence.
    idx=np.flatnonzero(np.isfinite(dg[:,0]));zz=np.full(len(idx),np.nan);ok=d['update'][idx];zz[ok]=dg[idx[ok],1]/np.sqrt(dg[idx[ok],2])
    for lag in range(1,11):
        good=np.isfinite(zz[lag:])&np.isfinite(zz[:-lag])
        acf.append(float(np.corrcoef(zz[lag:][good],zz[:-lag][good])[0,1]) if good.sum()>5 else np.nan)
    info=dict(LAB=lab,updates=N,standardized_bias=float(np.mean(z)),mean_NIS=float(np.mean(z*z)),innovation_coverage95=float(np.mean(abs(z)<=1.96)),
              lag1=acf[0],clips=int(np.nansum(dg[:,4])),min_eigenvalue=float(min(np.linalg.eigvalsh(p).min() for p in P)))
    return pd.DataFrame(rows),info,np.array(acf)

def protected_hashes(root):
    root=Path(root);out={}
    for folder in ('notebooks','src','configs'):
        for p in (root/folder).rglob('*'):
            if p.is_file() and 'kalman_analysis' not in p.parts and '__pycache__' not in p.parts:
                out[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
    return out

def verify_protected(root,manifest):
    assert all(hashlib.sha256((Path(root)/p).read_bytes()).hexdigest()==h for p,h in manifest.items())

def study_fingerprint(data,chem):
    h=hashlib.sha256(Path(__file__).read_bytes())
    for lab in LABS:
        h.update(lab.encode())
        for key in ('grid','doses','y','valid','update','initial','P0','available','temperature'):
            h.update(np.ascontiguousarray(data[lab][key]).tobytes())
    h.update(chem.to_csv(index=False).encode())
    h.update(b'two-starts-220iter-refine200-v1')
    return h.hexdigest()

def perform_study(data,chem,out,workers=3):
    from concurrent.futures import ThreadPoolExecutor,as_completed
    out=Path(out);out.mkdir(exist_ok=True);fingerprint=study_fingerprint(data,chem)
    # Compile before threads: all subsequent runs use identical numerical kernels.
    run(data[LABS[0]])
    gas_fits={};gas_rows=[]
    folds={'All development':LABS,**{f'Leave {lab} out':tuple(x for x in LABS if x!=lab) for lab in LABS}}
    for fold,training in folds.items():
        path=out/('gas_'+fold.replace(' ','_')+'.json')
        stored=json.loads(path.read_text()) if path.exists() else {}
        if stored.get('fingerprint')==fingerprint:gas=np.array(stored['gas']);loss=stored['loss']
        else:
            gas,profile,loss=gas_fit(data,training);profile.to_csv(path.with_suffix('.csv'),index=False)
            path.write_text(json.dumps(dict(fingerprint=fingerprint,training=training,gas=gas.tolist(),loss=loss),indent=2))
        gas_fits[fold]=gas
        gas_rows.append(dict(fold=fold,training=', '.join(training),kLa=gas[0],gain=gas[1],MSE=loss))
        print('Gas calibration:',fold,gas,flush=True)
    def task(fold,training,structure):
        path=out/('fit_'+fold.replace(' ','_')+'_'+structure.replace(' ','_').replace('+','plus').replace('/','_')+'.json')
        stored=json.loads(path.read_text()) if path.exists() else {}
        if stored.get('fingerprint')==fingerprint:return fold,structure,stored['fit']
        fit=fit_noise(data,training,gas_fits[fold],structure)
        path.write_text(json.dumps(dict(fingerprint=fingerprint,fold=fold,training=training,fit=fit),indent=2))
        print('Noise fit:',fold,structure,'score',round(fit['score'],4),'bounds',fit['at_bound'],flush=True)
        return fold,structure,fit
    fits={}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        tasks=[pool.submit(task,fold,training,structure) for fold,training in folds.items() for structure in STRUCTURES]
        for job in as_completed(tasks):
            fold,structure,fit=job.result();fits[fold,structure]=fit
    metrics=[];checks=[];records={};score_rows=[]
    for fold,training in folds.items():
        validation=LABS if fold=='All development' else tuple(x for x in LABS if x not in training)
        for structure in STRUCTURES:
            fit=fits[fold,structure];sigma=np.array(fit['sigma']);rsd=fit['Rsd']
            score=objective(np.array(fit['x']),fit['names'],data,validation,gas_fits[fold])
            score_rows.append(dict(fold=fold,structure=structure,score=score,training_score=fit['score'],parameters=len(fit['names']),
                                   Rsd=rsd,at_bound=', '.join(fit['at_bound']),converged=any(x['success'] and abs(x['score']-fit['score'])<1e-10 for x in fit['runs'])))
            for lab in validation:
                result=run(data[lab],gas_fits[fold],sigma,rsd)
                m,info,acf=diagnostics(data,chem,lab,result)
                m['fold']=fold;m['structure']=structure;metrics.extend(m.to_dict('records'))
                info.update(fold=fold,structure=structure,acf=acf.tolist());checks.append(info)
                if fold=='All development':records[structure,lab]=result
    # Same refitted gas and original noise: isolates the Q/R adjustment.
    for lab in LABS:
        result=run(data[lab],gas_fits['All development']);records['Original noise',lab]=result
        m,info,acf=diagnostics(data,chem,lab,result);m['fold']='All development';m['structure']='Original noise';metrics.extend(m.to_dict('records'))
        info.update(fold='All development',structure='Original noise',acf=acf.tolist());checks.append(info)
    scores=pd.DataFrame(score_rows);cv=scores.loc[scores.fold.ne('All development')].groupby('structure').score.mean().sort_values()
    # A CO2-score leader is a diagnostic candidate, never automatically an approved filter.
    leader=str(cv.index[0]);profiles=[];sensitivities={};fit=fits['All development',leader]
    names=fit['names'];x=np.array(fit['x']);gas=gas_fits['All development']
    def signature(xx):
        sig,rr=decode(xx,names);parts=[]
        for lab in LABS:
            dg=run(data[lab],gas,sig,rr)[2];m=data[lab]['update']
            parts.extend((dg[m,0]/.04).tolist());parts.extend(np.log(np.maximum(dg[m,2],1e-20)).tolist())
        return np.array(parts)
    J=[];bounds=bounds_for(names)
    for j,name in enumerate(names):
        hi=x.copy();lo=x.copy();hi[j]=min(x[j]+.05,bounds[j][1]);lo[j]=max(x[j]-.05,bounds[j][0])
        J.append((signature(hi)-signature(lo))/(hi[j]-lo[j]))
        grid=np.unique(np.r_[np.linspace(*bounds[j],7),x[j]])
        for value in grid:
            xx=x.copy();xx[j]=value
            profiles.append(dict(parameter=name,log10_value=value,value=10**value,score=objective(xx,names,data,LABS,gas),fit_value=10**x[j]))
    J=np.array(J).T;singular=np.linalg.svd(J,compute_uv=False)
    sensitivities=dict(names=names,singular_values=singular.tolist(),column_norms=np.linalg.norm(J,axis=0).tolist(),
                       normalized_gram=(J.T@J/np.maximum(np.outer(np.linalg.norm(J,axis=0),np.linalg.norm(J,axis=0)),1e-30)).tolist())
    payload=dict(fingerprint=fingerprint,allowed_labs=LABS,gas=gas_rows,metrics=metrics,checks=checks,scores=score_rows,
                 fits=[dict(fold=k[0],**v) for k,v in fits.items()],leader=leader,
                 conditional_profiles=profiles,sensitivity=sensitivities)
    (out/'study.json').write_text(json.dumps(payload,indent=2,allow_nan=True))
    pd.DataFrame(metrics).to_csv(out/'metrics.csv',index=False);scores.to_csv(out/'noise_scores.csv',index=False)
    pd.DataFrame(gas_rows).to_csv(out/'gas_fits.csv',index=False)
    pd.DataFrame(profiles).to_csv(out/'conditional_profiles.csv',index=False)
    packed={}
    for (structure,lab),(f,P,dg) in records.items():
        key=structure.replace(' ','_').replace('+','plus').replace('/','_')+'__'+lab
        for suffix,array in [('frame',f),('covariance',P),('diagnostics',dg)]:packed[key+'__'+suffix]=array
    np.savez_compressed(out/'development_trajectories.npz',**packed)
    return payload,records
