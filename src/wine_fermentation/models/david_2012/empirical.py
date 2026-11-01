"""Explicit reconstructed empirical functions for David 2012, not original code.
Thermal shapes: linear interpolation of Table I endpoints at 18/30 Celsius,
with shared calibrated amplitudes. Nutrition and initial partition are calibrated
bounded two-knot functions. These choices reconstruct missing functions; all
David biological equations remain in kinetics.py. No Zenteno laws are used.
"""
import numpy as np
from .kinetics import Parameters
THERMAL=dict(mu_max=(.0996,.3034),eta_max=(.0799,.2257),
 beta_max_1=(.1963,.3759),beta_max_2=(.3318,.9205),
 KS=(7.656,2.9011),KE=(47.744,26.3585),phi=(.3887,.4727))
NAMES=tuple(THERMAL)+('Kx','k1','Ktr','nx_fraction_071','nx_fraction_570',
 'rise_0','rise_1','alpha_0','alpha_1','beta3_0','beta3_1','phi2_0','phi2_1')
START=[1.]*7+[.0127,.0528,.3134,.95,.5,3.,20.,.9,.1,.1,.3,.45,.9]
BOUNDS=[(.15,6.)]*7+[(.001,.5),(.01,.2),(.01,2.),(.02,.999),(.02,.999),
 (.5,60.),(.5,60.),(.001,.999),(.001,.999),(.0001,3.),(.0001,3.),(.01,5.),(.01,5.)]

def build(values):
 d=dict(zip(NAMES,map(float,values)))
 def thermal(T):
  # Boundary holding is explicit: no unsupported extrapolation beyond 18-30C.
  return {key:d[key]*np.interp(T,[18.,30.],ab) for key,ab in THERMAL.items()}
 def partition(n):return n*np.interp(n,[.071,.57],[d['nx_fraction_071'],d['nx_fraction_570']])
 def nutrition(progress):
  return {name:float(np.interp(progress,[0.,1.],[d[key+'_0'],d[key+'_1']]))
   for name,key in [('rise_h','rise'),('alpha','alpha'),('beta_max_3','beta3'),('phi2','phi2')]}
 return Parameters(d['Kx'],d['k1'],d['Ktr'],thermal,partition,nutrition)
