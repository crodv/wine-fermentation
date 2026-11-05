"""Measurement-uncertainty audit, restricted to LAB019--021.

No Q/R optimization, smoothing of the assimilated signal, or holdout loading.
Type-B scenarios are assumptions, not confidence statements from the datasheet.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import analysis_core as core

FACTOR=44.0095*60*.74/(1000*24.16)
FS=50.0  # software span; independently checked against current and logged flow
BANDWIDTH_SECONDS=(30,120,300,600)

def mean_variance_hac(values,bandwidth):
    """Bartlett HAC variance of a mean on observation-index lags.

    Exact for bandwidth=0 and iid residuals. Time-to-index conversion is an
    approximation for irregular records and is reported, never hidden.
    """
    x=np.asarray(values,float);x=x-x.mean();n=len(x);L=min(int(bandwidth),n-1)
    gamma=np.correlate(x,x,mode='full')[n-1:n+L]/n
    weights=1-np.arange(1,L+1)/(L+1)
    return float(max((gamma[0]+2*np.dot(weights,gamma[1:]))/n,0.))

def audit(root,data,out):
    root=Path(root);out=Path(out);out.mkdir(exist_ok=True)
    instrument=json.loads((root/'configs/co2_instrument.json').read_text())
    assert instrument['flow_range_sccm']==[0.,50.] and instrument['co2_correction_factor']==.74
    assert instrument['calibration_gas']=='air'
    assert tuple(data)==core.LABS
    raw=core.recent_raw(root/'data/original/natural/lab019_021/backup_global_co2_completo.csv',
                        ['timestamp','fermentador','flow_sccm','current_ma','voltage','status'])
    volume=core.filtered_csv(root/'data/processed/co2_mass_balance_lab016_021_g_l_h.csv',
                            usecols=['lab','time_h','record_kind','remaining_volume_L'])
    windows=[];chains=[];segments=[]
    for number,lab in enumerate(core.LABS,1):
        d=data[lab];g=raw.loc[raw.fermentador.eq('F'+str(number))&raw.t_h.between(-6,d['horizon'])].sort_values('t_h').copy()
        inside=g.loc[g.current_ma.between(4.05,19.95)&g.flow_sccm.between(.01,49.99)].dropna(subset=['current_ma','flow_sccm'])
        slope,offset=np.polyfit(inside.current_ma,inside.flow_sccm,1)
        reconstructed=np.clip((g.current_ma-4)*FS/16,0,FS)
        chains.append(dict(LAB=lab,interior_points=len(inside),flow_per_mA=slope,offset_sccm=offset,
            inferred_span_sccm=16*slope,reconstruction_max_sccm=float(np.nanmax(abs(g.flow_sccm-reconstructed))),
            clipped_below_4mA_fraction=float(g.current_ma.lt(4).mean()),clipped_upper_fraction=float(g.current_ma.ge(20).mean()),
            range_and_calibration_gas_confirmed=True))
        assert abs(16*slope-FS)<.02,'Logged span differs from the assumed software range'
        ev=volume.loc[volume.lab.eq(lab)&volume.record_kind.eq('withdrawal_after')].sort_values('time_h')
        et=ev.time_h.to_numpy();vv=ev.remaining_volume_L.to_numpy()
        V=lambda t: np.r_[2.,vv][np.searchsorted(et,np.asarray(t),side='right')]
        g['bin']=np.ceil(g.t_h/.5-1e-10).astype(int)
        pre=g.loc[g.t_h.between(-5,-.5)].dropna(subset=['current_ma'])
        # A pre-inoculation segment is NOT certified zero flow: gas/plumbing unknown.
        segments.append(dict(LAB=lab,label='Pre-inoculation, not a certified zero',n=len(pre),
            median_current_mA=float(pre.current_ma.median()),median_flow_sccm=float(pre.flow_sccm.median()),
            below_4mA_fraction=float(pre.current_ma.lt(4).mean())))
        for row in d['sensor'].itertuples():
            w=g.loc[g.bin.eq(round(row.t_h/.5))].dropna(subset=['flow_sccm'])
            if not row.valid or len(w)<30:continue
            t=w.t_h.to_numpy();flow=w.flow_sccm.to_numpy();vol=V(t);k=FACTOR/vol;y=k*flow
            assert abs(y.mean()-row.measured)<1e-12
            n=len(y);delta=np.diff(t)*3600;median_dt=float(np.median(delta));center=(t-t.mean())/.5
            coef=np.polyfit(center,y,1);residual=y-np.polyval(coef,center)
            med=np.median(y);mad=1.4826*np.median(abs(y-med));flag=abs(y-med)>max(5*mad,.005)
            # Calibration offsets are common across the samples: mean(k), not RMS(k)/sqrt(n).
            common_scale=float(np.mean(k));accuracy_half=common_scale*FS*.01
            repeat_half=common_scale*FS*.0015
            record=dict(LAB=lab,t_h=row.t_h,n=n,assimilate=bool(row.assimilate),mean_CO2=float(y.mean()),
                volume_min=float(vol.min()),volume_max=float(vol.max()),conversion_mean=common_scale,
                median_dt_s=median_dt,max_gap_s=float(delta.max()),cadence_CV=float(np.std(delta)/max(np.mean(delta),1e-12)),
                zero_fraction=float(np.mean(flow<=0)),upper_clip_fraction=float(np.mean(flow>=FS)),
                descriptive_outlier_fraction=float(flag.mean()),mean_minus_median=float(y.mean()-med),
                trend_over_window=float(coef[0]),residual_SD=float(np.std(residual,ddof=1)),
                iid_SE=float(np.std(residual,ddof=1)/np.sqrt(n)),
                lag1=float(np.corrcoef(residual[:-1],residual[1:])[0,1]) if np.std(residual)>0 else np.nan,
                accuracy_1pct_FS_half_width=accuracy_half,repeatability_half_width=repeat_half,
                accuracy_rectangular_u=accuracy_half/np.sqrt(3),repeatability_rectangular_u=repeat_half/np.sqrt(3),
                K4pct_reading_rectangular_u=.04*abs(float(y.mean()))/np.sqrt(3),
                K4pct_FS_rectangular_u=common_scale*FS*.04/np.sqrt(3))
            for seconds in BANDWIDTH_SECONDS:
                lag=max(1,round(seconds/max(median_dt,1e-9)))
                record[f'linear_HAC_SE_{seconds}s']=np.sqrt(mean_variance_hac(residual,lag))
                record[f'constant_HAC_SE_{seconds}s']=np.sqrt(mean_variance_hac(y-y.mean(),lag))
            # Random-only diagnostic and persistent-error working scenarios are kept separate.
            variance=max(record['linear_HAC_SE_120s']**2,record['accuracy_rectangular_u']**2)
            record['R_working_1pct_persistent']=variance
            record['R_working_4pct_FS_persistent']=max(record['linear_HAC_SE_120s']**2,record['K4pct_FS_rectangular_u']**2)
            windows.append(record)
    windows=pd.DataFrame(windows);chains=pd.DataFrame(chains);segments=pd.DataFrame(segments)
    assert set(windows.LAB)==set(core.LABS)
    calibration=[]
    for V in (2.,1.8,1.5):
        k=FACTOR/V
        calibration.append(dict(volume_L=V,conversion=k,one_pct_FS_half_width=k*.5,
            one_pct_rectangular_u=k*.5/np.sqrt(3),repeat_rectangular_u=k*.075/np.sqrt(3),
            four_pct_FS_half_width=k*2.,four_pct_FS_rectangular_u=k*2./np.sqrt(3),original_SD=.04))
    summary=[]
    for lab,z in windows.groupby('LAB'):
        for subset,g in [('All valid',z),('Assimilated',z.loc[z.assimilate])]:
            for name in ['iid_SE','linear_HAC_SE_30s','linear_HAC_SE_120s','linear_HAC_SE_300s','linear_HAC_SE_600s',
                         'constant_HAC_SE_120s','accuracy_rectangular_u','repeatability_rectangular_u',
                         'K4pct_reading_rectangular_u','K4pct_FS_rectangular_u','R_working_1pct_persistent','R_working_4pct_FS_persistent']:
                values=g[name]
                summary.append(dict(LAB=lab,subset=subset,quantity=name,n=len(g),q10=float(values.quantile(.1)),
                                    median=float(values.median()),q90=float(values.quantile(.9)),maximum=float(values.max())))
    sources=[]
    for name,pages in [('FMAA2100_2200_2300_2400.pdf','PDF page 2: accuracy, repeatability, response'),('M2842.pdf','PDF pages 5, 8, 9, 10: accuracy, zero, gas conversion, K table')]:
        p=root/'references/Sensor_omega'/name;sources.append(dict(path=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),locations=pages))
    report=dict(labs=list(core.LABS),software_full_scale_sccm=FS,gas_correction=.74,molar_volume_L_mol=24.16,
        physical_full_scale_confirmed=True,factory_calibration_gas_confirmed=True,calibration_gas='air',
        configuration_source='configs/co2_instrument.json',confirmation=instrument['confirmation'],
        original_R=.04**2,original_SD=.04,
        conclusion='Original 0.04 is not a manufacturer-specified standard deviation. Neither sensor-only R nor its unique decomposition from process variability is identified from these data. Range 0-50 SCCM, air calibration and factor 0.74 are user-confirmed. Remaining uncertainty concerns the measurement-error statistics and interpretation of the K-method accuracy.',
        datasheet=dict(accuracy_FS_fraction=.01,repeatability_FS_fraction=.0015,gas_K_method_accuracy=.04,
            K_method_percentage_basis='not stated explicitly in section 5.0',response_datasheet_seconds=5,response_manual_seconds='1-2'),
        sources=sources,uniform_distribution_assumed=True,averaging_systematic_errors='no sqrt(n) reduction',
        no_double_counting='max(empirical mean variance, type-B accuracy scenario); repeatability not added to inclusive accuracy',
        all_estimates_are_conditional=True)
    windows.to_csv(out/'R_window_audit.csv',index=False);chains.to_csv(out/'R_acquisition_chain.csv',index=False)
    segments.to_csv(out/'R_pre_inoculation_diagnostic.csv',index=False);pd.DataFrame(summary).to_csv(out/'R_summary.csv',index=False)
    pd.DataFrame(calibration).to_csv(out/'R_typeB_scenarios.csv',index=False)
    (out/'R_evidence.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
    return windows,chains,segments,pd.DataFrame(summary),pd.DataFrame(calibration),report

def figures(windows):
    for title,columns in [
        ('30-minute mean: conditional random variability and instrument scenarios',
         [('linear_HAC_SE_120s','Detrended HAC, 2 min'),('accuracy_rectangular_u','1% FS persistent, rectangular'),('K4pct_FS_rectangular_u','4% FS scenario, rectangular')]),
        ('Sensitivity to correlation bandwidth and trend removal',
         [('iid_SE','IID standard error'),('linear_HAC_SE_30s','HAC 30 s'),('linear_HAC_SE_300s','HAC 5 min'),('constant_HAC_SE_120s','HAC 2 min, no detrending')])]:
        fig,axs=plt.subplots(1,3,figsize=(15,4))
        for ax,lab in zip(axs,core.LABS):
            g=windows.loc[windows.LAB.eq(lab)]
            for col,label in columns:ax.plot(g.t_h,g[col],label=label,lw=1.)
            ax.axhline(.04,c='black',ls='--',label='Original SD = 0.04')
            ax.set(title=lab,xlabel='Time [h]',ylabel='Standard uncertainty / SE [g/(L h)]');ax.grid(alpha=.2);ax.legend(loc='best',fontsize=6.5)
        fig.suptitle(title,y=.995);fig.tight_layout(pad=.7,rect=(0,0,1,.95));plt.show()
    fig,axs=plt.subplots(1,3,figsize=(15,4))
    for ax,lab in zip(axs,core.LABS):
        g=windows.loc[windows.LAB.eq(lab)]
        ax.plot(g.t_h,g.zero_fraction,label='Zero-clipped samples')
        ax.plot(g.t_h,g.descriptive_outlier_fraction,label='Descriptive outlier fraction')
        ax.set(title=lab,xlabel='Time [h]',ylabel='Fraction of window samples');ax.grid(alpha=.2);ax.legend(fontsize=7,loc='best')
    fig.suptitle('Data-quality limitations: RAW mean is retained unchanged',y=.995)
    fig.tight_layout(pad=.7,rect=(0,0,1,.95));plt.show()
