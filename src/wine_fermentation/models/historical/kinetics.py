"""Five-state reduction of the current fermentation model, in physical parameters.

Only Xd and Gly and their two production parameters are removed. Mortality,
thermal laws, maintenance attenuation and numerical safeguards are retained.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

STATE_NAMES=('X','N','G','F','E')
INPUT_CHANNELS=('N','G','F','E','X')
PARAMETERS=('mu0','betaG0','betaF0','Kn0','Kg0','Kf0','Kig0','Kie0','Kd0','Yxn','Yxg','Yxf','Yeg','Yef','m0')
STATE_COLUMNS=dict(X='X_viable_kg_m3',N='N_kg_m3',G='G_g_l',F='F_g_l',E='E_g_l')
MEASUREMENT_ERROR_FLOOR=dict(X=.06,N=.012,G=2.5,F=2.5,E=2.)
MEASUREMENT_ERROR_REL=dict(X=.08,N=.08,G=.025,F=.025,E=.025)
FIXED_CONSTANTS=dict(Cde=.0415,Etd=130000.,R=8.314,Eac=59453.,Eafe=11000.,
    EaKn=46055.,EaKg=46055.,EaKf=46055.,EaKig=46055.,EaKie=46055.,Eam=37681.)
MAINTENANCE_SUGAR_CUTOFF_KG_M3=1.

@dataclass(frozen=True)
class BatchData:
    medium:str
    batch:str
    time:np.ndarray
    temperature_c:np.ndarray
    pulses:dict
    observations:dict
    initials:dict
    @property
    def label(self):return f'{self.medium}/{self.batch}'

def normalize_parameters(theta):
    """Convert a frozen legacy vector once; keep all values, not new bounds."""
    if 'qN' not in theta:
        return {name:float(theta[name]) for name in PARAMETERS}
    return dict(mu0=theta['mu0'],betaG0=theta['betaG0'],betaF0=theta['betaF0'],
        Kn0=theta['mu0']/theta['sN'],Kg0=theta['betaG0']/theta['sG'],Kf0=theta['betaF0']/theta['sF'],
        Kig0=1./theta['iG'],Kie0=1./theta['iE'],Kd0=theta['Kd0'],
        Yxn=theta['mu0']/theta['qN'],Yxg=theta['mu0']/theta['qXG'],Yxf=theta['mu0']/theta['qXF'],
        Yeg=theta['betaG0']/theta['qEG'],Yef=theta['betaF0']/theta['qEF'],m0=theta['m0'])

def to_legacy(theta):
    """Only for comparison tests against the archived seven-state implementation."""
    t=normalize_parameters(theta)
    return dict(mu0=t['mu0'],betaG0=t['betaG0'],betaF0=t['betaF0'],
        sN=t['mu0']/t['Kn0'],sG=t['betaG0']/t['Kg0'],sF=t['betaF0']/t['Kf0'],
        qN=t['mu0']/t['Yxn'],qXG=t['mu0']/t['Yxg'],qXF=t['mu0']/t['Yxf'],
        qEG=t['betaG0']/t['Yeg'],qEF=t['betaF0']/t['Yef'],iG=1./t['Kig0'],iE=1./t['Kie0'],
        Kd0=t['Kd0'],m0=t['m0'],gammaG0=0.,gammaF0=0.)

def temperature_at(batch,t):return float(np.interp(float(t),batch.time,batch.temperature_c))

def kinetic_terms(theta,temperature_c,x,n,g,f,e):
    x,n,g,f,e=(max(float(value),0.) for value in (x,n,g,f,e))
    tk=float(temperature_c)+273.15;eps=1e-8;R=FIXED_CONSTANTS['R']
    a_mu=math.exp(59453.*(tk-300.)/(300.*R*tk))
    a_beta=math.exp(11000.*(tk-296.15)/(296.15*R*tk))
    a_K=math.exp(46055.*(tk-293.15)/(293.15*R*tk))
    Kn=theta['Kn0']*a_K;Kg=theta['Kg0']*a_K;Kf=theta['Kf0']*a_K
    # Preserve the legacy +eps inside inverse thermal inhibition exactly.
    KIG=theta['Kig0']*(a_K+eps);KIE=theta['Kie0']*(a_K+eps)
    mu=theta['mu0']*a_mu*n/(n+Kn+eps)
    beta_g=theta['betaG0']*a_beta*g/(g+Kg+eps)*(KIE/(e+KIE))
    beta_f=theta['betaF0']*a_beta*f/(f+Kf+eps)*(KIG/(g+KIG))*(KIE/(e+KIE))
    maintenance=theta['m0']*math.exp(37681.*(tk-293.3)/(293.3*R*tk))
    td=-.0001*e**3+.0049*e**2-.1279*e+315.89
    kd=theta['Kd0']*math.exp(.0415*e+130000.*(tk-305.65)/(305.65*R*tk)) if tk>=td else 0.
    sugar_total=g+f+eps
    return dict(x=x,mu=mu,beta_g=beta_g,beta_f=beta_f,kd=kd,maintenance=maintenance,
        maintenance_availability=sugar_total/(sugar_total+MAINTENANCE_SUGAR_CUTOFF_KG_M3),sugar_total=sugar_total)

def rhs(t,y,theta,batch):
    x,n,g,f,e=(max(float(value),0.) for value in y)
    rates=kinetic_terms(theta,temperature_at(batch,t),x,n,g,f,e)
    mu,bg,bf=rates['mu'],rates['beta_g'],rates['beta_f']
    maintenance=rates['maintenance']*rates['maintenance_availability']
    return [(mu-rates['kd'])*x,-mu/theta['Yxn']*x,
        -(mu/theta['Yxg']+bg/theta['Yeg']+maintenance*g/rates['sugar_total'])*x,
        -(mu/theta['Yxf']+bf/theta['Yef']+maintenance*f/rates['sugar_total'])*x,(bg+bf)*x]

def initial_vector(batch):return np.array([batch.initials[state] for state in STATE_NAMES],float)

def _pulse_events(batch,t0,tf):
    events={};indices={state:i for i,state in enumerate(STATE_NAMES)}
    for channel in INPUT_CHANNELS:
        for event,dose in batch.pulses.get(channel,()):
            event,dose=float(event),float(dose)
            if not np.isfinite(event+dose) or dose<0:raise ValueError('Invalid event')
            if dose==0 or event<t0-1e-12 or event>tf+1e-12:continue
            delta=events.setdefault(event,np.zeros(5));delta[indices[channel]]+=dose
    return events

def integrate(batch,theta,time=None,*,rtol=2e-9,atol=2e-11,max_step=.5):
    time=np.asarray(batch.time if time is None else time,float)
    if len(time)==0 or np.any(np.diff(time)<=0):raise ValueError('Output times must be strictly increasing')
    if abs(time[0]-batch.time[0])>1e-9:raise ValueError('Initial output time differs from batch start')
    state=initial_vector(batch);events=_pulse_events(batch,time[0],time[-1])
    records={float(time[0]):state.copy()};current=float(time[0]);jump_error=0.
    if current in events:state+=events[current]
    for boundary in sorted({float(time[-1]),*[event for event in events if event>current]}):
        if boundary<=current:continue
        requested=time[(time>current)&(time<=boundary)]
        solution=solve_ivp(lambda t,y:rhs(t,y,theta,batch),(current,boundary),state,
            t_eval=np.unique(np.r_[requested,boundary]),method='LSODA',rtol=rtol,atol=atol,max_step=max_step)
        if not solution.success:raise RuntimeError(solution.message)
        records.update({float(t):value.copy() for t,value in zip(solution.t,solution.y.T)})
        state=solution.y[:,-1].copy();current=boundary
        if boundary in events:
            before=state.copy();state+=events[boundary]
            jump_error=max(jump_error,float(np.max(abs(state-before-events[boundary]))))
    values=np.vstack([records[float(t)] for t in time])
    if not np.isfinite(values).all() or values.min()<-1e-6:raise RuntimeError('Invalid integrated state')
    result=pd.DataFrame(np.maximum(values,0.),index=time,columns=STATE_NAMES)
    result.attrs['jump_error']=jump_error
    return result

def simulate(batch,theta,output_time=None):return integrate(batch,theta,output_time)

def sigma_for_state(state,observed):
    observed=np.asarray(observed,float)
    return np.maximum(MEASUREMENT_ERROR_FLOOR[state],MEASUREMENT_ERROR_REL[state]*np.maximum(abs(observed),MEASUREMENT_ERROR_FLOOR[state]))

def make_batches(data):
    defaults=dict(X=.45,N=.18,G=80.,F=80.,E=0.)
    batches=[]
    for (medium,lab),group in data.groupby(['medium','batch'],sort=True):
        group=group.sort_values('time_h').drop_duplicates('time_h')
        initials={}
        for state,col in STATE_COLUMNS.items():
            finite=pd.to_numeric(group[col],errors='coerce').dropna()
            initials[state]=float(finite.iloc[0]) if len(finite) else defaults[state]
        pulses=tuple((float(row.time_h),float(row.N_pulse_kg_m3)) for row in group.itertuples() if pd.notna(row.N_pulse_kg_m3) and row.N_pulse_kg_m3>0)
        batches.append(BatchData(medium,lab,group.time_h.to_numpy(float),
            group.temperature_c.interpolate(limit_direction='both').fillna(18.).to_numpy(float),
            {'N':pulses},{state:group[col].to_numpy(float) for state,col in STATE_COLUMNS.items()},initials))
    return batches
