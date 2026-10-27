"""Current v3 gas-source and transfer equations, connected to the five-state model."""
from dataclasses import replace
from types import SimpleNamespace
import math
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from . import model as base
CONFIG=dict(rtol=2e-9,atol=2e-11,max_step_h=.5,grid_h=.25)
CO2_G_PER_G_ETHANOL=(2*44.01)/(2.*46.07)
joint=SimpleNamespace(CO2_G_PER_G_ETHANOL=CO2_G_PER_G_ETHANOL)

def o2_saturation_mg_l(temp_c: float, ethanol_g_l: float, glucose_g_l: float, fructose_g_l: float, sat_scale: float = 1.0) -> float:
    """Working air-saturated dissolved oxygen concentration in wine-like must."""
    temp_factor = math.exp(-0.024 * (float(temp_c) - 20.0))
    ethanol_factor = math.exp(-0.0020 * max(float(ethanol_g_l), 0.0))
    sugar_factor = math.exp(-0.0010 * max(float(glucose_g_l) + float(fructose_g_l), 0.0))
    return max(float(sat_scale) * 8.6 * temp_factor * ethanol_factor * sugar_factor, 1e-6)
co2_cross=SimpleNamespace(O2_K_MG_L=.25,O2_ANA_K_MG_L=.75,O2_ANA_HILL=2.,
    O2_CRABTREE_FLOOR=.08,co2_model=SimpleNamespace(o2_saturation_mg_l=o2_saturation_mg_l))
def integrate_core(batch, theta, time):
    """Five-state integration; the gas source and transfer equations are unchanged."""
    return base.integrate(batch, theta, time, rtol=CONFIG['rtol'], atol=CONFIG['atol'], max_step=CONFIG['max_step_h'])

def production(theta, batch, core):
    out = []
    for t, row in core.iterrows():
        terms = base.kinetic_terms(theta, base.temperature_at(batch, t),
            row.X, row.N, row.G, row.F, row.E)
        out.append(joint.CO2_G_PER_G_ETHANOL * (terms['beta_g']+terms['beta_f']) * row.X)
    return np.asarray(out)

def csat(batch, core, params):
    temp = np.interp(core.index, batch.time, batch.temperature_c)
    return (params['CO2sat_scale'] * 1.69 * np.exp(-.032*(temp-20.))
            * np.exp(.0016*core.E.to_numpy())
            * np.exp(-.0012*(core.G+core.F).to_numpy()))

def release(cd, saturation, params):
    return params['kCO2_release_h'] * cd * (.05+.95*cd/max(cd+saturation, 1e-12))

def finish(batch, theta, core, core0, params, gate, ramp, multiplier, cd0, oxygen0):
    time = core.index.to_numpy(float)
    qn, q0 = production(theta, batch, core), production(theta, batch, core0)
    biomass = np.maximum(core0.X.to_numpy()+ramp*(core.X-core0.X).to_numpy(), 0.)
    oxygen = np.zeros(len(time))
    oxygen[0] = oxygen0
    for i, dt in enumerate(np.diff(time)):
        uptake = params['O2_qmax_mg_gdw_h']*biomass[i]*oxygen[i]/(co2_cross.O2_K_MG_L+oxygen[i])
        oxygen[i+1] = max(oxygen[i]-dt*uptake, 0.)
    k, h = co2_cross.O2_ANA_K_MG_L, co2_cross.O2_ANA_HILL
    phi = k**h/(k**h+oxygen**h)
    fferm = co2_cross.O2_CRABTREE_FLOOR+(1.-co2_cross.O2_CRABTREE_FLOOR)*phi
    activity = 1.+(params['pulse_activity_gain']-1.)*ramp
    qbio = multiplier*np.maximum(activity*q0+ramp*(qn-q0), 0.)
    qprod = gate*fferm*qbio  # Same simplified structure as co2_local_observability.
    saturation = csat(batch, core, params)
    cd, qout = np.zeros(len(time)), np.zeros(len(time))
    cd[0] = cd0
    qout[0] = release(cd0, saturation[0], params)
    for i, dt in enumerate(np.diff(time), 1):
        qout[i] = min(release(cd[i-1], saturation[i], params), cd[i-1]/dt+qprod[i-1])
        cd[i] = max(cd[i-1]+dt*(qprod[i-1]-qout[i]), 0.)
    mass_error = float(np.max(np.abs(np.diff(cd)-np.diff(time)*(qprod[:-1]-qout[1:]))))
    assert mass_error < 1e-10 and np.isfinite(cd).all()
    out = core.copy()
    out['GF'] = out.G+out.F
    out['Cd'], out['O2'] = cd, oxygen
    out['predicted'] = params['matrix_gain']*qout
    out['qprod'], out['qgas'], out['qbio'] = qprod, qout, qbio
    out['gate'], out['ramp'], out['multiplier'] = gate, ramp, multiplier
    out['csat'], out['temperature_C'] = saturation, np.interp(time, batch.time, batch.temperature_c)
    out.attrs['mass_error'] = mass_error
    return out
