"""Common, unchanged experimental inputs for the nv2 comparison."""
from pathlib import Path
from dataclasses import replace
import re
import numpy as np
import pandas as pd
from scipy.signal import butter,sosfiltfilt
from . import model

def natural_batches(root):
    root=Path(root);labs=tuple(f'LAB{i:03}' for i in range(4,10))
    data=pd.read_csv(root/'data/compatibility/chemistry/observations_cleaned_lab004_009.csv')
    for state,column in model.STATE_COLUMNS.items():
        data[column]=pd.to_numeric(data[column],errors='coerce');data.loc[data[column]<0,column]=0.
    original=model.make_batches(data)
    clocks=pd.read_csv(root/'data/compatibility/chemistry/clocks.csv').set_index('batch').t0
    pulses={};profiles={};batches=[]
    for lab in labs:
        sheet=pd.read_excel(root/'data/cleaned/natural/lab004_012/mosto_natural_depurado.xlsx',sheet_name=lab)
        event=sheet[sheet['pulso real'].notna()]
        assert len(event)==1 and np.isclose(event.pulso_nut.iloc[0],80.)
        pulses[lab]=float(event['pulso real'].iloc[0])
        paths=sorted(p for p in (root/'data/original/natural/process_logs').rglob('*.csv')
            if p.name.lower().startswith('temp') and re.search(rf'lab0*{int(lab[3:])}(?:\D|$)',p.name,re.I))
        fragments=[]
        for path in paths:
            frame=pd.read_csv(path,usecols=['timestamp','T','SP']);frame['timestamp']=pd.to_datetime(frame.timestamp,errors='coerce')
            for col in ('T','SP'):frame[col]=pd.to_numeric(frame[col],errors='coerce')
            fragments.append(frame.dropna(subset=['timestamp']))
        raw=pd.concat(fragments).sort_values('timestamp',kind='stable')
        duplicate=raw[raw.timestamp.duplicated(keep=False)]
        if len(duplicate):assert duplicate.groupby('timestamp')[['T','SP']].nunique().le(1).all().all()
        raw=raw.drop_duplicates('timestamp');t0=pd.Timestamp(clocks[lab])
        raw['t_h']=(raw.timestamp-t0).dt.total_seconds()/3600.
        raw=raw[raw.t_h.ge(0)].dropna(subset=['T'])
        profile=raw.set_index('timestamp')[['T','SP']].resample('30min').median().dropna(subset=['T']).reset_index()
        profile['t_h']=(profile.timestamp-t0).dt.total_seconds()/3600.+.25
        profile=profile[profile.t_h.between(0,raw.t_h.max())].copy()
        gap=profile.t_h.diff().gt(.500001);step=profile.SP.diff().abs().gt(.5)
        profile['segment']=(gap|step).cumsum();profile['filtered']=np.nan
        sos=butter(2,1/4.,fs=2.,output='sos')
        for _,group in profile.groupby('segment'):
            smooth=group['T'].rolling(3,center=True,min_periods=1).median().to_numpy()
            profile.loc[group.index,'filtered']=sosfiltfilt(sos,smooth) if len(smooth)>9 else smooth
        profiles[lab]=profile
        old=next(b for b in original if b.batch==lab);horizon=float(old.time[-1])
        knots=np.arange(0,horizon+1e-9,2.);switches=profile.loc[profile.segment.diff().fillna(0).ne(0),'t_h'].to_numpy()
        knots=np.r_[knots,switches,switches-.5]
        grid=np.unique(np.r_[old.time,knots[(knots>=0)&(knots<=horizon)]])
        observations={state:np.full(len(grid),np.nan) for state in model.STATE_NAMES}
        for state in model.STATE_NAMES:observations[state][np.searchsorted(grid,old.time)]=old.observations[state]
        batches.append(replace(old,time=grid,temperature_c=np.interp(grid,profile.t_h,profile.filtered),
            pulses={**old.pulses,'N':((pulses[lab],.08),)},observations=observations))
    return data,batches,profiles
