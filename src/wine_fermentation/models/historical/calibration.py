from pathlib import Path
import sys,json,time,re,hashlib,ast
import numpy as np
import pandas as pd
from dataclasses import replace
from IPython.display import display
from . import kinetics as base
from . import co2 as gas
ROOT=Path(__file__).resolve().parents[4]
CASES=('theta_full','theta_new','theta_nv2')
from scipy.optimize import least_squares, minimize_scalar
from types import SimpleNamespace
from dataclasses import replace
import math, hashlib, ast
from . import co2 as gas
TRAIN=('LAB019','LAB020','LAB021')
HOLDOUT=('LAB016','LAB017','LAB018')
GAS_NAMES=('kCO2_release_h','CO2sat_scale','matrix_gain')
GAS_BOUNDS=((.03,25.),(.35,2.5),(.1,20.))
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def release_forward(c, p, max_step=None):
    """Conservative implicit reservoir, identical to v2 (positive root)."""
    k, scale, gain = (p[n] for n in GAS_NAMES)
    source, dt = c["source"], c["dt"]
    sat = c["sat_base"] * scale
    cd, out = np.zeros(len(source)), np.zeros(len(source))
    for i in range(1, len(source)):
        subdivisions = 1 if max_step is None else int(np.ceil(dt[i-1] / max_step))
        step = dt[i-1] / subdivisions
        inventory, released = cd[i-1], 0.
        for _ in range(subdivisions):
            a = inventory + step * source[i-1]
            aa = 1. + step * k
            b = sat[i] * (1. + .05 * step * k) - a
            root = np.sqrt(b*b + 4.*aa*a*sat[i])
            new = 2.*a*sat[i]/(root+b) if b >= 0. else (root-b)/(2.*aa)
            released += a - new
            inventory = new
        cd[i], out[i] = inventory, released/dt[i-1]
    return gain*out, cd, out

def features(t, y):
    t, y = np.asarray(t), np.asarray(y)
    peak = int(np.argmax(y))
    def run(mask, start=0):
        for i in range(max(2, start), len(t)):
            if mask[i-2:i+1].all() and np.allclose(np.diff(t[i-2:i+1]), 1.):
                return float(t[i])
        return np.nan
    return dict(peak_h=float(t[peak]), peak=float(y[peak]),
                onset_h=run(y >= .05), fall_h=run(y < .05, peak+2))

class Search:
    def prepare(self, name, theta, labs=TRAIN):
        self.theta_by_case[name] = theta.copy()
        for lab in labs:
            if (name, lab) in self.cache:
                continue
            bt = self.batches[lab]
            core = self.gas.integrate_core(bt, theta, bt.time)
            core0 = self.gas.integrate_core(replace(bt, pulses={**bt.pulses, "N": ()}), theta, bt.time)
            core["GF"] = core.G + core.F
            self.cores[name, lab] = core
            time = bt.time
            events = bt.pulses["N"]
            ramp, multiplier = self.histories(time, events, self.old)
            consumed = core.GF.iloc[0]-core.GF.to_numpy()
            z = np.clip((consumed-2.)/8., 0., 1.)
            gate = z*z*(3.-2.*z)
            ini = bt.initials
            oxygen0 = self.old["O2_initial_scale"]*self.cross.co2_model.o2_saturation_mg_l(
                bt.temperature_c[0], ini["E"], ini["G"], ini["F"], 1.)
            ref = self.gas.finish(bt, theta, core, core0, self.old, gate, ramp, multiplier, 0., oxygen0)
            qn, q0 = self.gas.production(theta, bt, core), self.gas.production(theta, bt, core0)
            d = self.obs[self.obs.lab.eq(lab)].sort_values("t_h")
            idx = np.searchsorted(time, d.t_h.to_numpy())-1
            w = (d.t_h.to_numpy()-time[idx]) / (time[idx+1]-time[idx])
            phi = .75**2/(.75**2+ref.O2.to_numpy()**2)
            self.cache[name, lab] = dict(
                time=time, dt=np.diff(time), source=ref.qprod.to_numpy(),
                sat_base=ref.csat.to_numpy()/self.old["CO2sat_scale"],
                qn=qn, q0=q0, ramp=ramp, multiplier=multiplier,
                gate=gate, fferm=.08+.92*phi, obs=d, idx=idx, w=w,
                events=events, core=core, reference=ref, core0_X=core0.X.to_numpy(),
                oxygen0=oxygen0, sugar_consumed=consumed)

    @staticmethod
    def histories(time, events, p):
        ramp = np.clip((time-events[0][0])/p["pulse_t_rise_h"], 0., 1.) if events else np.zeros(len(time))
        mult = np.ones(len(time))
        tr, td = p["tau_rise_h"], p["tau_decay_h"]
        up = tr*np.log1p(td/tr)
        peak = -np.expm1(-up/tr)*np.exp(-up/td)
        for event, dose in events:
            u = np.maximum(time-event, 0.)
            mult += p["A"]*dose/p["N_ref_g_l"]*(-np.expm1(-u/tr))*np.exp(-u/td)/peak
        return ramp, mult

    def source_cache(self, case, lab, p, mode="v2"):
        if mode != "v2":raise ValueError("Only the unchanged historical primary formulation is available")
        return self.cache[case, lab]

    def verify_protected(self):
        assert all(sha256(self.root/p) == h for p, h in self.protected.items())
        return len(self.protected)
import ast

import json

from dataclasses import replace

from pathlib import Path

import numpy as np

import pandas as pd

from numpy.lib.stride_tricks import sliding_window_view

from scipy import signal

from scipy.optimize import least_squares, minimize_scalar

LABS = tuple(f"LAB{i:03}" for i in range(16, 22))

FILTERS = {"offline_20min": 1200., "offline_30min": 1800., "offline_40min": 2400.}

PRIMARY = "offline_30min"

OBS_STEP_H = 1. / 6.

LOD = .05

QUIET = .02

FACTOR = 44.0095 * 60. * .74 / (1000. * 24.16 * 2.)

LOCAL_ZONE = "America/Santiago"

def local_to_utc(values):
    """Interpret logger/worksheet civil times, rejecting ambiguous/invalid times."""
    return pd.DatetimeIndex(pd.to_datetime(values)).tz_localize(
        LOCAL_ZONE, ambiguous="raise", nonexistent="raise").tz_convert("UTC")

def elapsed_civil_hours(hours, origin_local):
    """Convert legacy naive-clock offsets, not actual elapsed durations, to UTC."""
    wall = origin_local + pd.to_timedelta(np.asarray(hours, float), unit="h")
    return (local_to_utc(wall)-local_to_utc([origin_local])[0]).total_seconds()/3600.

def centered_hampel(values, dt_s, window_s=120., k=3.5, floor=.5):
    """Exact median/MAD of the same centered odd window, reflection at edges."""
    x = np.asarray(values, float)
    assert np.isfinite(x).all()
    half = max(1, int(round(window_s / (2. * dt_s))))
    padded = np.pad(x, (half, half), mode="reflect")
    windows = sliding_window_view(padded, 2 * half + 1)
    med = np.median(windows, axis=1)
    mad = np.median(abs(windows - med[:, None]), axis=1)
    flag = abs(x-med) > np.maximum(k * 1.4826 * mad, floor)
    return np.where(flag, med, x), flag

def runs(mask):
    edges = np.diff(np.r_[False, np.asarray(mask, bool), False].astype(int))
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))

def fill_short_gaps(series, max_samples):
    result = series.copy()
    candidate = series.interpolate(method="time", limit_area="inside")
    for a, b in runs(series.isna().to_numpy()):
        if b-a <= max_samples and a > 0 and b < len(series):
            result.iloc[a:b] = candidate.iloc[a:b]
    return result

def butter_sos(tau_s, dt_s, order=3):
    cutoff = 1. / (2. * np.pi * tau_s)
    return signal.butter(order, cutoff, fs=1. / dt_s, output="sos")

def zero_phase(values, tau_s, dt_s):
    # The default SciPy padding is too short for this very low cutoff.
    padlen = min(int(np.ceil(6. * tau_s / dt_s)), len(values)-2)
    assert padlen > 12 and len(values) > 24
    return signal.sosfiltfilt(butter_sos(tau_s, dt_s), values, padtype="odd", padlen=padlen)

def read_window(path, root, columns, start, end=None):
    content = Path(path)
    pieces = []
    for chunk in pd.read_csv(content, usecols=columns, chunksize=400000, low_memory=False):
        stamp = pd.to_datetime(chunk.timestamp, errors="coerce")
        keep = stamp.ge(start)
        if end is not None:
            keep &= stamp.le(end)
        if keep.any():
            part = chunk.loc[keep].copy()
            part["timestamp"] = stamp[keep]
            pieces.append(part)
    if not pieces:
        raise ValueError(f"No data in requested window: {path}")
    return pd.concat(pieces, ignore_index=True), content

class RecalibrationV3(Search):
    def __init__(self, root):
        self.root=Path(root)
        self.base=base
        self.gas=gas
        self.cross=gas.co2_cross
        self.v2=self.root/'data/compatibility/co2_v3'
        settings=json.loads((self.root/'configs/co2_v3_reference.json').read_text(encoding='utf-8'))
        self.old=settings['old_gas_start']
        self.gui=settings['gui']
        assert self.gui==dict(W_SPIKE_SECONDS=120.,K=3.5,MIN_ABS_SPIKE=.5,TAU_SECONDS=1200.,BUTTER_ORDER=3)
        self.thetas={name:base.normalize_parameters(json.loads((self.root/f'configs/theta/{name}.json').read_text())) for name in CASES}
        self.initials=pd.read_csv(self.v2/'initial_conditions_v2.csv').set_index('lab')
        self.chem=pd.read_csv(self.v2/'chemistry_v2.csv')
        self.density=pd.read_csv(self.v2/'density_v2.csv')
        self.biomass=pd.read_csv(self.v2/'biomass_v2.csv')
        self.previous_chemistry=pd.DataFrame(columns=['lab','t_h'])
        self.v2_initials=self.initials.copy()
        self.raw_co2,self.raw_temperature,self.t0,self.artifacts={},{},{},{}
        self.dense,self.temperature,self.observations={},{},{}
        self.filter_audit,self.coverage_rows,self.temp_audit=[],[],[]
        self.fit_runs,self.fit_table,self.v3_fits=[],[],{}
        self.saved_core_contexts={}
        self.clock_audit,self.elapsed_audit,self.nutrition_events=[],[],[]
        old_dir=self.root/'data/original/natural/lab016_018'
        book_path=old_dir/'LAB016-018-offline-measurements.xlsx'
        sheet=pd.read_excel(book_path,sheet_name='CondicionesIniciales').set_index('CodigoLab')
        recent_dir=self.root/'data/original/natural/lab019_021'
        recent_t0=pd.Timestamp('2026-09-21 17:00:00')
        recent_co2,_=read_window(recent_dir/'backup_global_co2_completo.csv',self.root,
            ['timestamp','fermentador','flow_sccm','flow_filt_sccm','status'],recent_t0-pd.Timedelta(hours=6))
        recent_temp,_=read_window(recent_dir/'backup_global_temperatura_completo.csv',self.root,
            ['timestamp','fermentador','T','SP','nutricion_activa'],recent_t0-pd.Timedelta(hours=6))
        for i, lab in enumerate(LABS):
            fermenter = f"F{i%3+1}"
            if i < 3:
                row = sheet.loc[lab]
                clock = row.Hora if hasattr(row.Hora, "hour") else pd.to_datetime(str(row.Hora)).time()
                t0 = pd.Timestamp.combine(pd.Timestamp(row.Fecha).date(), clock)
                raw_path = old_dir/f"CO2_F{i+1}_{lab}.csv"
                filt_path = old_dir/f"CO2_FILT_F{i+1}_{lab}.csv"
                temp_path = old_dir/({0:"Temp_F1_LAB016.csv",1:"Temp_F2_LAB017.csv",2:"Temp_F3._LAB018.csv"}[i])
                raw = pd.read_csv(raw_path, parse_dates=["timestamp"])
                recorded = pd.read_csv(filt_path, parse_dates=["timestamp"])
                raw = raw.merge(recorded[["timestamp", "flow_filt_sccm"]], on="timestamp", how="left", validate="one_to_one")
                tmp = pd.read_csv(temp_path, parse_dates=["timestamp"])
            else:
                t0 = recent_t0
                raw = recent_co2[recent_co2.fermentador.eq(fermenter)].copy()
                tmp = recent_temp[recent_temp.fermentador.eq(fermenter)].copy()
            origin_local = t0
            t0 = local_to_utc([origin_local])[0]
            for kind, frame in (("co2", raw), ("temperature", tmp)):
                wall = pd.DatetimeIndex(frame.timestamp)
                utc = local_to_utc(wall)
                local_dt = wall.to_series(index=np.arange(len(wall))).diff().dt.total_seconds().to_numpy()
                real_dt = utc.to_series(index=np.arange(len(utc))).diff().dt.total_seconds().to_numpy()
                jumps = np.flatnonzero(abs(local_dt-real_dt)>1.)
                for j in jumps:
                    self.clock_audit.append(dict(lab=lab,signal=kind,
                        previous_local=str(wall[j-1]),next_local=str(wall[j]),
                        previous_utc=str(utc[j-1]),next_utc=str(utc[j]),
                        civil_interval_seconds=float(local_dt[j]),elapsed_interval_seconds=float(real_dt[j])))
                frame["timestamp_local"] = frame.timestamp.astype(str)
                frame["timestamp"] = utc
            raw = raw[raw.timestamp.ge(t0-pd.Timedelta(hours=6))].sort_values("timestamp").copy()
            tmp = tmp[tmp.timestamp.ge(t0-pd.Timedelta(hours=6))].sort_values("timestamp").copy()
            assert raw.timestamp.is_unique and tmp.timestamp.is_unique
            raw["t_h"] = (raw.timestamp-t0).dt.total_seconds()/3600.
            tmp["t_h"] = (tmp.timestamp-t0).dt.total_seconds()/3600.
            self.t0[lab], self.raw_co2[lab], self.raw_temperature[lab] = t0, raw, tmp
            # Pump activation is nutrition, not evidence of a measurement artifact.
            # Keep its measured response; no bridges, recovery windows or guards.
            self.artifacts[lab] = []
            state = pd.to_numeric(tmp.nutricion_activa, errors="raise").eq(1)
            for a,b in runs(state):
                self.nutrition_events.append(dict(lab=lab,start_h=float(tmp.t_h.iloc[a]),
                    end_h=float(tmp.t_h.iloc[min(b,len(tmp)-1)]),excluded_from_fit=False))
            for name, frame in (("chemistry",self.chem),("density",self.density),
                                ("biomass",self.biomass),("previous_chemistry",self.previous_chemistry)):
                ids = frame.index[frame.lab.eq(lab)]
                if not len(ids):continue
                # t_h=0 may intentionally map a pre-inoculation sample to the
                # initial condition. Preserve that mapping and the measurement.
                old = frame.loc[ids,"t_h"].to_numpy(float)
                if name == "previous_chemistry":
                    # The legacy simulation includes artificial civil-clock
                    # grid points inside the skipped hour; they are not samples.
                    wall = origin_local+pd.to_timedelta(old,unit="h")
                    utc = pd.DatetimeIndex(wall).tz_localize(LOCAL_ZONE,
                        ambiguous="raise",nonexistent="NaT").tz_convert("UTC")
                    exists = ~utc.isna()
                    frame.drop(index=ids[~exists],inplace=True)
                    ids,old,utc = ids[exists],old[exists],utc[exists]
                    new = (utc-t0).total_seconds()/3600.
                else:
                    new = elapsed_civil_hours(old,origin_local)
                frame.loc[ids,"t_h"] = new
                for idx,before,after in zip(ids,old,new):
                    self.elapsed_audit.append(dict(lab=lab,table=name,row=int(idx),
                        civil_t_h=float(before),elapsed_t_h=float(after)))
            old_events = ast.literal_eval(self.initials.loc[lab,"N_events"])
            corrected_events = tuple((float(elapsed_civil_hours([h],origin_local)[0]),dose) for h,dose in old_events)
            self.initials.loc[lab,"N_events"] = repr(corrected_events)
            self.initials.loc[lab,"horizon_h"] = float(elapsed_civil_hours(
                [self.v2_initials.loc[lab,"horizon_h"]],origin_local)[0])

        self.protected={str(p.relative_to(self.root)):sha256(p) for p in self.v2.rglob('*') if p.is_file()}
        for p in (self.root/'configs').rglob('*.json'):
            self.protected[str(p.relative_to(self.root))]=sha256(p)
        self.cores,self.cache,self.theta_by_case={},{},{}
        self.runs=[]


    def process(self):
        for lab in LABS:
            self._process_temperature(lab)
            self._process_co2(lab)
        self.filter_audit = pd.DataFrame(self.filter_audit)
        self.temp_audit = pd.DataFrame(self.temp_audit)
        self._choose_horizons()
        self.coverage = pd.DataFrame(self.coverage_rows)
        # Use the same native ten-minute support for all smoothing sensitivities.
        for lab in LABS:
            dense = self.dense[lab]
            cut = self.horizons[lab]
            width = OBS_STEP_H
            bin_id = np.floor(dense.time_h/width+1e-10).astype(int)
            frame = dense.copy()
            valid = frame.valid_for_fit & frame.time_h.ge(0.) & frame.time_h.le(cut)
            frame["bin"] = bin_id
            agg = frame[valid].groupby("bin").agg(lo=("time_h", "min"),hi=("time_h", "max"),n=("time_h", "size"))
            dt = self.filter_blocks[lab][0]
            keep = (agg.hi-agg.lo >= .75*width) & agg.n.ge(.75*width*3600./dt) & (agg.index*width >= 0.) & ((agg.index+1)*width <= cut+1e-9)
            for a,b in self.fit_exclusions[lab]:
                keep &= ~((agg.index*width <= b)&((agg.index+1)*width >= a))
            bins = agg[keep].index
            for name in FILTERS:
                grouped = frame[valid].groupby("bin")[name].median().reindex(bins)
                points = pd.DataFrame(dict(lab=lab,bin=bins,t_h=(bins+.5)*width,y=grouped.to_numpy()))
                assert points.y.notna().all() and points.t_h.is_unique
                self.observations[name,lab] = points
        self.obs = pd.concat([self.observations[PRIMARY,lab] for lab in LABS],ignore_index=True)
        self.configure_temperature("reference_20_45")

    def _process_temperature(self, lab):
        raw = self.raw_temperature[lab]
        minute = raw.set_index("timestamp")[["T", "SP"]].resample("1min").median()
        minute["T"] = fill_short_gaps(minute["T"], 2)
        result = pd.DataFrame(index=minute.index)
        result["raw_1min"] = minute["T"]
        for name, med, mean in (("reference_20_45", "20min", "45min"), ("strong_30_60", "30min", "60min")):
            result[name] = np.nan
            for a,b in runs(minute["T"].notna()):
                segment = minute["T"].iloc[a:b]
                filtered = segment.rolling(med,center=True,min_periods=1).median().rolling(mean,center=True,min_periods=1).mean()
                result.iloc[a:b,result.columns.get_loc(name)] = filtered.to_numpy()
            valid = result[name].notna() & result.raw_1min.notna()
            self.temp_audit.append(dict(lab=lab,variant=name,raw_std_C=float(result.loc[valid,"raw_1min"].std()),
                filtered_std_C=float(result.loc[valid,name].std()),mean_change_C=float((result.loc[valid,name]-result.loc[valid,"raw_1min"]).mean()),
                max_change_C=float(abs(result.loc[valid,name]-result.loc[valid,"raw_1min"]).max())))
        result["SP"] = minute.SP
        result["time_h"] = (result.index-self.t0[lab]).total_seconds()/3600.
        self.temperature[lab] = result

    def _process_co2(self, lab):
        raw = self.raw_co2[lab]
        dt = float(raw.timestamp.diff().dt.total_seconds().median())
        assert 5. <= dt <= 30., (lab,dt)
        series = raw.set_index("timestamp")[["flow_sccm", "flow_filt_sccm"]].resample(pd.Timedelta(seconds=dt)).median()
        series.index += pd.Timedelta(seconds=dt/2.)
        series["flow_sccm"] = fill_short_gaps(series.flow_sccm, int(60./dt))
        time = (series.index-self.t0[lab]).total_seconds().to_numpy()/3600.
        clean = series.flow_sccm.copy()
        frame = pd.DataFrame(dict(time_h=time,raw_sccm=series.flow_sccm.to_numpy(),
            recorded_sccm=series.flow_filt_sccm.to_numpy(),clean_sccm=clean.to_numpy()),index=series.index)
        frame["despiked_sccm"],frame["hampel_spike"] = np.nan,False
        blocks = [(a,b) for a,b in runs(clean.notna()) if b-a > 100]
        for name in FILTERS:
            frame[name] = np.nan
        for a,b in blocks:
            despiked, flag = centered_hampel(clean.iloc[a:b].to_numpy(), dt)
            frame.iloc[a:b,frame.columns.get_loc("despiked_sccm")] = despiked
            frame.iloc[a:b,frame.columns.get_loc("hampel_spike")] = flag
            for name,tau in FILTERS.items():
                frame.iloc[a:b,frame.columns.get_loc(name)] = zero_phase(despiked,tau,dt)
        # One sensor-zero estimate, from the same raw-derived despiked baseline,
        # is shared by every smoothing variant. Nothing is subtracted from chemistry.
        baseline = (time >= 2.5) & (time <= 12.) & frame.despiked_sccm.notna().to_numpy()
        for event in self.artifacts[lab]:
            baseline &= ~((time >= event["start_h"]) & (time <= event["end_h"]))
        assert baseline.sum() > 20, lab
        zero = max(0.,float(frame.loc[baseline,"despiked_sccm"].quantile(.1)))
        self.fit_exclusions = getattr(self,"fit_exclusions",{})
        # Padding is a numerical extension only, never a fit exclusion margin.
        guard = 0.
        exclusions = []
        self.fit_exclusions[lab] = exclusions
        valid = frame[PRIMARY].notna().to_numpy()
        for name,tau in FILTERS.items():
            uncorrected = frame[name].to_numpy().copy()
            frame[name] = np.maximum(uncorrected-zero,0.)*FACTOR
            use = valid & (time >= 0.)
            peak = int(np.nanargmax(np.where(use,frame[name],np.nan)))
            self.filter_audit.append(dict(lab=lab,variant=name,tau_s=tau,order=3,passes=2,
                raw_dt_s=dt,zero_sccm=zero,n_raw=len(raw),n_grid=len(frame),
                n_hampel=int(frame.hampel_spike.sum()),n_fit_dense=int(use.sum()),
                peak_g_l_h=float(frame[name].iloc[peak]),peak_h=float(time[peak]),
                negative_before_clipping_fraction=float(np.nanmean(uncorrected < zero)),
                data_start_h=float(time[0]),data_end_h=float(time[-1]),guard_h=guard))
        frame["despiked"] = np.maximum(frame.despiked_sccm-zero,0.)*FACTOR
        frame["recorded"] = np.maximum(frame.recorded_sccm-float(pd.read_csv(self.v2/"sensor_audit.csv").set_index("lab").loc[lab,"zero_sccm"]),0.)*FACTOR
        frame["valid_for_fit"] = valid
        self.dense[lab] = frame
        self.filter_blocks = getattr(self,"filter_blocks",{})
        self.filter_blocks[lab] = (dt, blocks)

    def _choose_horizons(self):
        self.horizons = {}
        for lab in LABS:
            dense = self.dense[lab]
            time = dense.time_h.to_numpy()
            if lab in LABS[3:]:
                last_chem = float(self.chem[self.chem.lab.eq(lab)&~self.chem.is_NUT].t_h.max())
            else:
                last_chem = float(max(self.density[self.density.lab.eq(lab)].t_h.max(),
                                      self.biomass[self.biomass.lab.eq(lab)].t_h.max()))
            # Horizon is fixed by the primary observation preprocessing, never
            # by a fitted model. Any unresolved ending is explicitly censored.
            frame = dense[dense.time_h.ge(0.)&dense.valid_for_fit].copy()
            frame["bin"] = np.floor(frame.time_h/OBS_STEP_H).astype(int)
            ten = frame.groupby("bin")[PRIMARY].median()
            tt = (ten.index.to_numpy()+.5)*OBS_STEP_H
            last_active = float(tt[ten.to_numpy() >= LOD][-1]) if (ten>=LOD).any() else 0.
            quiet_end = np.nan
            for i in range(len(ten)-11):
                chunk = ten.iloc[i:i+12]
                if tt[i] >= last_active and np.all(np.diff(chunk.index)==1) and chunk.le(QUIET).all():
                    quiet_end = float((chunk.index[-1]+1)*OBS_STEP_H)
                    break
            available = min(float(dense.time_h.max()),float(self.raw_temperature[lab].t_h.max()))
            requested = max(last_chem,quiet_end) if np.isfinite(quiet_end) else available
            cut = min(requested,available)
            assert last_chem <= available+1e-6, (lab,last_chem,available)
            self.horizons[lab] = cut
            self.coverage_rows.append(dict(lab=lab,last_chemical_or_offline_h=last_chem,
                previous_v2_end_h=float(self.v2_initials.loc[lab,"horizon_h"]),
                raw_co2_end_h=float(self.raw_co2[lab].t_h.max()),raw_temperature_end_h=float(self.raw_temperature[lab].t_h.max()),
                last_detectable_CO2_h=last_active,quiet_confirmed_h=quiet_end,cut_h=cut,
                quiet_threshold_g_l_h=QUIET,quiet_duration_h=2.,
                right_censored=not np.isfinite(quiet_end),chemistry_covered=last_chem<=cut+1e-8))

    def configure_temperature(self, variant):
        self.cores,self.cache,self.theta_by_case = {},{},{}
        self.batches = {}
        for lab in LABS:
            # Integrate beyond the reported cutoff, using actual remaining
            # temperature, so the zero-phase observation operator has context.
            available = min(float(self.dense[lab].time_h.max()),float(self.raw_temperature[lab].t_h.max()))
            horizon = available
            events = ast.literal_eval(self.initials.loc[lab,"N_events"])
            grid = np.unique(np.r_[np.arange(0.,horizon,1./12.),horizon,[t for t,_ in events]])
            temp = self.temperature[lab].dropna(subset=[variant])
            assert temp.time_h.min() <= 0. and horizon-temp.time_h.max() <= 1./60.+1e-8
            row = self.v2_initials.loc[lab]
            self.batches[lab] = self.base.BatchData(medium="natural",batch=lab,time=grid,
                temperature_c=np.interp(grid,temp.time_h,temp[variant]),
                initials={s:float(row[s]) for s in self.base.STATE_NAMES},
                pulses={**{s:() for s in self.base.INPUT_CHANNELS},"N":events},
                observations={s:np.full(len(grid),np.nan) for s in self.base.STATE_NAMES})
        self.temperature_variant = variant

    def prepare_all(self):
        for case,key in ((name,name) for name in CASES):
            self.prepare(case,self.thetas[key],LABS)
        self.saved_core_contexts[self.temperature_variant] = (self.batches,self.cores,self.cache,self.theta_by_case)

    def set_context(self, name):
        self.batches,self.cores,self.cache,self.theta_by_case = self.saved_core_contexts[name]
        self.temperature_variant = name

    def observed_prediction(self, case, lab, params, filtering=PRIMARY, mode="v2", max_step=None):
        cache = self.source_cache(case,lab,params,mode)
        physical,cd,qout = release_forward(cache,params,max_step=max_step)
        dense = self.dense[lab]
        t = dense.time_h.to_numpy()
        native = np.interp(t,cache["time"],physical,left=0.)
        filtered = np.full(len(t),np.nan)
        dt,blocks = self.filter_blocks[lab]
        for a,b in blocks:
            filtered[a:b] = np.maximum(zero_phase(native[a:b],FILTERS[filtering],dt),0.)
        return filtered,physical,cd,qout

    def v3_residual(self, params, case, labs, filtering=PRIMARY, mode="v2"):
        parts = []
        for lab in labs:
            pred = self.observed_prediction(case,lab,params,filtering,mode)[0]
            obs = self.observations[filtering,lab]
            p = np.interp(obs.t_h,self.dense[lab].time_h,pred)
            y = obs.y.to_numpy()
            error = np.where(y>=LOD,p-y,np.maximum(p-LOD,0.))
            assert np.isfinite(error).all(), (case,lab,filtering)
            parts.append(error/np.sqrt(len(error)))
        return np.concatenate(parts)

    def fit_layer(self, case, labs, label, filtering=PRIMARY, mode="v2", starts=3, max_nfev=180):
        labs = tuple(labs)
        def scalar_objective(logg):
            r = self.v3_residual({**self.old,"matrix_gain":float(np.exp(logg))},case,labs,filtering,mode)
            return r@r
        scalar = minimize_scalar(scalar_objective,bounds=np.log(GAS_BOUNDS[2]),method="bounded",options={"xatol":1e-8})
        z1 = {**self.old,"matrix_gain":float(np.exp(scalar.x))}
        extra = ("pulse_activity_gain","pulse_t_rise_h") if mode=="positive_mix" else ()
        names = GAS_NAMES+extra
        bounds = GAS_BOUNDS+((.05,1.5),(6.,120.)) if extra else GAS_BOUNDS
        lo,hi = np.log(np.array(bounds).T)
        seeds = [z1,{**z1,"kCO2_release_h":2.,"CO2sat_scale":1.},
                 {**z1,"kCO2_release_h":.15,"CO2sat_scale":2.4}][:starts]
        solutions = []
        for i,seed in enumerate(seeds):
            def fun(x):
                params = {**self.old,**dict(zip(names,np.exp(x)))}
                return self.v3_residual(params,case,labs,filtering,mode)
            sol = least_squares(fun,np.clip(np.log([seed[p] for p in names]),lo+1e-9,hi-1e-9),
                bounds=(lo,hi),max_nfev=max_nfev,ftol=1e-7,xtol=1e-7,gtol=1e-7)
            solutions.append(sol)
            self.fit_runs.append(dict(theta=case,training=label,filtering=filtering,mode=mode,
                temperature=self.temperature_variant,start=i,success=bool(sol.success),nfev=sol.nfev,
                objective=float(sol.fun@sol.fun),message=sol.message))
        best = min(solutions,key=lambda s:s.fun@s.fun)
        z2 = {**self.old,**dict(zip(names,np.exp(best.x)))}
        singular = np.linalg.svd(best.jac,compute_uv=False)
        assert best.fun@best.fun <= scalar.fun+1e-6
        for stage,p,success,obj in (("Z1",z1,scalar.success,scalar.fun),("Z2",z2,best.success,best.fun@best.fun)):
            key = (self.temperature_variant,filtering,mode,case,label,stage)
            self.v3_fits[key] = p
            self.fit_table.append(dict(temperature=self.temperature_variant,filtering=filtering,mode=mode,
                theta=case,training=label,labs=",".join(labs),stage=stage,success=bool(success),objective=float(obj),
                jacobian_ratio=float(singular[-1]/singular[0]) if stage=="Z2" else np.nan,
                active_bounds=",".join(n for n,x,a,b in zip(names,best.x,lo,hi) if min(x-a,b-x)<.005) if stage=="Z2" else "",
                **{n:p[n] for n in names}))
        print(self.temperature_variant,filtering,mode,case,label,"Z1/Z2",round(float(scalar.fun),6),round(float(best.fun@best.fun),6),flush=True)
        return z1,z2

    def curve_v3(self, case, lab, params, filtering=PRIMARY, mode="v2"):
        observed,physical,cd,qout = self.observed_prediction(case,lab,params,filtering,mode)
        cache = self.source_cache(case,lab,params,mode)
        t = cache["time"]
        return pd.DataFrame(dict(t_h=t,CO2_physical=physical,CO2_observed_operator=np.interp(t,self.dense[lab].time_h,observed),
            Cd=cd,qgas=qout,qprod=cache["source"],gate=cache["gate"],
            temperature_C=self.batches[lab].temperature_c))

    def metrics_v3(self, case, params, labs, filtering=PRIMARY, mode="v2", common_target=False):
        rows = []
        for lab in labs:
            pred = self.observed_prediction(case,lab,params,filtering,mode)[0]
            obs = self.observations[filtering,lab]
            p = np.interp(obs.t_h,self.dense[lab].time_h,pred)
            y = obs.y.to_numpy()
            if common_target:
                # Despiked raw native signal is the same reference for all filters.
                rawp = self.curve_v3(case,lab,params,filtering,mode)
                p = np.interp(obs.t_h,rawp.t_h,rawp.CO2_physical)
                d = self.dense[lab]
                bins = np.floor(d.time_h/OBS_STEP_H+1e-10).astype(int)
                y = d.groupby(bins).despiked.median().reindex(obs.bin).to_numpy()
            error = p-y
            after_peak = obs.t_h.to_numpy()>=float(obs.t_h.iloc[int(np.argmax(y))])
            for window,mask in (("all",np.ones(len(obs),bool)),("after_peak",after_peak),("after_100h",obs.t_h.to_numpy()>=100.)):
                if not mask.any():
                    continue
                rows.append(dict(theta=case,lab=lab,window=window,n=int(mask.sum()),
                    RMSE=float(np.sqrt(np.mean(error[mask]**2))),MAE=float(np.mean(abs(error[mask]))),
                    bias=float(error[mask].mean()),peak=float(p.max()),observed_peak=float(y.max()),
                    peak_h=float(obs.t_h.iloc[int(np.argmax(p))]),target="despiked_raw_common" if common_target else "same_offline_operator"))
        return pd.DataFrame(rows)

    def chemistry_v3(self, case):
        rows = []
        for lab in LABS[3:]:
            core = self.cores[case,lab]
            data = self.chem[self.chem.lab.eq(lab)&~self.chem.is_NUT&self.chem.t_h.gt(0.)]
            for channel,column,mult in (("N","YAN_mg_l",1000.),("G","G_g_l",1.),("F","F_g_l",1.),("GF","GF_g_l",1.),("E","E_g_l",1.)):
                points = data[["t_h",column]].dropna()
                e = np.interp(points.t_h,core.index,core[channel]*mult)-points[column].to_numpy()
                rows.append(dict(temperature=self.temperature_variant,theta=case,lab=lab,channel=channel,
                    n=len(points),RMSE=float(np.sqrt(np.mean(e**2))),bias=float(e.mean())))
        return pd.DataFrame(rows)
def load(root):
    instance=RecalibrationV3(root)
    instance.process()
    instance.configure_temperature('reference_20_45')
    return instance
