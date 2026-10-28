"""Proposed hybrid; additional nitrogen terms are hypotheses, not literal Zenteno equations."""
STATES=('X', 'N', 'G', 'F', 'E')

import numpy as np
from ... import model as current
def initial(batch,p):
    values=[batch.initials[k] for k in current.STATE_NAMES]
    if len(STATES)==5:return np.array(values,float)
    X,N,G,F,E=values
    return np.array([X,p['alpha']*N,(1-p['alpha'])*N,0.,G,F,E])
def nutrition(y,dose,p):
    y=y.copy()
    if len(STATES)==5:y[1]+=dose
    else:y[1]+=p['alpha']*dose;y[2]+=(1-p['alpha'])*dose
    return y
def terms(t,y,p,batch):
    T=current.temperature_at(batch,t)
    if len(STATES)==5:X,N,G,F,E=np.maximum(y,0);Tr=0.
    else:X,N,Ntr,Tr,G,F,E=np.maximum(y,0)
    q=current.kinetic_terms(p,T,X,N,G,F,E)
    if len(STATES)==5:
        multiplier=1.+p['aN']*N/(p['KNa']+N)
        vTr=0.
    else:
        multiplier=1.+p['aTr']*Tr
        a_mu=np.exp(59453*(T+273.15-300)/(300*8.314*(T+273.15)))
        vTr=p['eta0']*a_mu*Ntr/(p['KTr']+Ntr)*X
    # Growth stoichiometry consumes both sugars: stop growth at the exhausted-substrate boundary.
    # This is a boundary condition, not a new smooth empirical kinetic factor.
    if G<=0. or F<=0.:q['mu']=0.
    q['beta_g']*=multiplier;q['beta_f']*=multiplier
    q['vTr']=vTr
    return q
def rhs(t,y,p,batch):
    if len(STATES)==5:X,N,G,F,E=np.maximum(y,0)
    else:X,N,Ntr,Tr,G,F,E=np.maximum(y,0)
    q=terms(t,y,p,batch);mu=q['mu'];bg=q['beta_g'];bf=q['beta_f']
    m=q['maintenance']*q['maintenance_availability'];S=q['sugar_total']
    dx=(mu-q['kd'])*X;dn=-mu*X/p['Yxn']
    dg=-(mu/p['Yxg']+bg/p['Yeg']+m*G/S)*X
    df=-(mu/p['Yxf']+bf/p['Yef']+m*F/S)*X
    de=(bg+bf)*X
    if len(STATES)==5:return [dx,dn,dg,df,de]
    return [dx,dn,-q['vTr']/p['YTrN'],q['vTr']-q['kd']*Tr,dg,df,de]
