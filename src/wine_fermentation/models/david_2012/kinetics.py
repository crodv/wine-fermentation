"""David 2012 structure without Zenteno kinetics or a gas-transfer layer.

All empirical functions are REQUIRED inputs. No hidden defaults reconstruct
unpublished thermal curves or nitrogen-allocation curves. Concentrations g/L,
time h, temperature Celsius passed to the empirical functions.

The article assumes E0=CO20=0. Measured nonzero E0 can be supplied as a boundary
condition; CO2 remains newly produced CO2. Thus E-E0=CO2-CO20.
"""
from dataclasses import dataclass
from typing import Callable, Mapping
import numpy as np
from scipy.integrate import solve_ivp
import pandas as pd

STATES=('X','Nx','Ntr','Tr','S','E','CO2')
THERMAL_NAMES=('mu_max','eta_max','beta_max_1','beta_max_2','KS','KE','phi')

@dataclass(frozen=True)
class Parameters:
    Kx: float
    k1: float
    Ktr: float
    thermal: Callable[[float], Mapping[str,float]]
    initial_partition: Callable[[float],float]
    # progress -> alpha, rise_h, beta_max_3, phi2, Section III-A.
    nutrition: Callable[[float], Mapping[str,float]]
    k1_prime: float=.16
    k2: float=2.17


def initial(initials,p):
    n=float(initials['N']);nx=float(p.initial_partition(n))
    if not 0<=nx<=n:raise ValueError('Initial partition must give Nx in [0,N]')
    return np.array([initials['X'],nx,n-nx,0.,initials['S'],initials['E'],0.],float)


def rates(y,T,p,boost=None):
    X,Nx,Ntr,Tr,S,E,CO2=np.maximum(np.asarray(y,float),0.)
    a=p.thermal(float(T))
    if set(THERMAL_NAMES)-set(a):raise ValueError('Missing empirical thermal functions')
    if min(a.values())<0 or min(p.Kx,p.Ktr,p.k1,p.k1_prime,p.k2)<=0:
        raise ValueError('Invalid physical parameters')
    f=Nx/(p.Kx*X+Nx) if p.Kx*X+Nx>0 else 0.
    dx=a['mu_max']*f*X
    dtr=a['eta_max']*Ntr/(p.Ktr+Ntr)*X
    activity=a['beta_max_1']*f+a['beta_max_2']*a['KE']/(a['KE']+E)
    phi=a['phi']
    if boost is not None:
        activity+=boost['beta_max_3']*Ntr/(p.Ktr+Ntr)
        phi=boost['phi2']
    de=activity*S/(a['KS']+S)*X*(1+phi*Tr)
    return dx,dtr,de


def rhs(t,y,T,p,boost=None,feed=0.):
    dx,dtr,de=rates(y,T,p,boost)
    alpha=boost['alpha'] if boost is not None else 0.
    return np.array([dx,-p.k1*dx+alpha*feed,
        -p.k1_prime*dtr+(1-alpha)*feed,dtr,-p.k2*de,de,de])


def simulate(time,temperature_c,initials,events,p,rtol=2e-7,atol=2e-9):
    time=np.asarray(time,float);temperature_c=np.asarray(temperature_c,float)
    if len(time)<2 or not np.all(np.diff(time)>0) or len(time)!=len(temperature_c):
        raise ValueError('Strictly increasing time and a matching log-temperature profile required')
    if len(events)>1:
        raise ValueError('David 2012 identifies single additions; repeated-addition extension not assumed')
    y=initial(initials,p);start=float(time[0]);end=float(time[-1]);segments=[];boost=None
    event=events[0] if events else None
    boundaries=[float(event[0])] if event and start<float(event[0])<end else []
    finish_feed=None
    while start<end-1e-10:
        if event and abs(start-float(event[0]))<1e-8 and boost is None:
            progress=np.clip((initials['S']-y[4])/initials['S'],0.,1.)
            boost=dict(p.nutrition(float(progress)))
            if not 0<=boost['alpha']<=1 or boost['rise_h']<=0:
                raise ValueError('Nutrition requires alpha in [0,1] and a positive rise time')
            if min(boost['beta_max_3'],boost['phi2'])<0:raise ValueError('Negative activity')
            finish_feed=start+boost['rise_h']
        stop=min([end]+[b for b in boundaries if b>start+1e-9]+([finish_feed] if finish_feed and finish_feed>start+1e-9 else []))
        feed=float(event[1])/boost['rise_h'] if boost is not None and start<finish_feed-1e-9 else 0.
        sol=solve_ivp(lambda t,y:rhs(t,y,np.interp(t,time,temperature_c),p,boost,feed),
            (start,stop),y,method='LSODA',rtol=rtol,atol=atol,max_step=.5,dense_output=True)
        if not sol.success or not np.isfinite(sol.y).all() or sol.y.min()<-1e-5:
            raise RuntimeError('Invalid David integration')
        segments.append((start,stop,sol.sol,boost,feed));y=sol.y[:,-1];start=stop
    values=np.empty((len(time),len(STATES)));q=np.empty(len(time))
    for i,t in enumerate(time):
        a,b,solution,boost,feed=next(z for z in segments if z[0]-1e-9<=t<=z[1]+1e-9)
        values[i]=solution(t);q[i]=rates(values[i],np.interp(t,time,temperature_c),p,boost)[2]
    frame=pd.DataFrame(values,index=time,columns=STATES)
    frame['N']=frame.Nx+frame.Ntr;frame['qCO2']=q
    if not np.allclose(frame.E-initials['E'],frame.CO2,atol=1e-7):raise AssertionError('E/CO2 balance')
    if not np.allclose(frame.S+p.k2*(frame.E-initials['E']),initials['S'],atol=1e-6):raise AssertionError('Sugar balance')
    return frame
