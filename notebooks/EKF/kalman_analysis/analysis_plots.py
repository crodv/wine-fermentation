"""Figures for the training-only noise study (English labels, internal legends)."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import analysis_core as c

def finish(fig,title):
    fig.suptitle(title,y=.995);fig.tight_layout(pad=.7,rect=(0,0,1,.965));plt.show()

def activity(data,records):
    rows=[]
    for lab in c.LABS:
        f=records['Original noise',lab][0];d=data[lab]
        for t,w in zip(d['grid'],f):
            T=c.temperature_at(t,d['available'],d['temperature']);mu,bg,bf,kd,m,A,cs=c.terms(w,T,d['S0'])
            x=max(w[0],0.);rows.append(dict(LAB=lab,t_h=t,Growth=mu*x,Glucose=bg*x/c.THETA['Yeg'],
                Fructose=bf*x/c.THETA['Yef'],Mortality=kd*x,Maintenance=m*x))
    frame=pd.DataFrame(rows);fig,axs=plt.subplots(2,3,figsize=(14,6.5))
    for ax,name in zip(axs.flat,['Growth','Glucose','Fructose','Mortality','Maintenance']):
        for lab,g in frame.groupby('LAB'):ax.plot(g.t_h,g[name],label=lab)
        ax.set(title=name,xlabel='Time [h]',ylabel='Flux [g/(L h)]');ax.grid(alpha=.2);ax.legend(fontsize=7)
    axs.flat[-1].axis('off');finish(fig,'Process activity along the reference EKF states')
    summary=[]
    for lab,g in frame.groupby('LAB'):
        for name in ['Growth','Glucose','Fructose','Mortality','Maintenance']:
            summary.append(dict(LAB=lab,process=name,max_flux=g[name].max(),active_fraction=float(g[name].gt(1e-8).mean()),
                                integral_g_L=float(np.trapezoid(g[name],g.t_h))))
    return pd.DataFrame(summary)

def mapping(data,records,gas):
    lab=c.LABS[0];d=data[lab];j=np.argmin(abs(d['grid']-24.));w=records['Original noise',lab][0][j]
    T=c.temperature_at(d['grid'][j],d['available'],d['temperature'])
    L=c.noise_L(w,T,d['S0'],*gas)
    fig,ax=plt.subplots(figsize=(11,4));im=ax.imshow(L,cmap='RdBu_r',vmin=-1.1,vmax=1.1)
    ax.set_xticks(range(6),c.SOURCE_NAMES,rotation=15,ha='right');ax.set_yticks(range(7),c.STATES)
    for i in range(7):
        for j in range(6):ax.text(j,i,f'{L[i,j]:.2f}',ha='center',va='center',fontsize=8)
    fig.colorbar(im,ax=ax,label='Mapping coefficient (units depend on row/source)')
    finish(fig,'Candidate L: columns are sources, rows are states · illustrative state')
    return pd.DataFrame(L,index=c.STATES,columns=c.SOURCE_NAMES)

def raw_noise(raw):
    fig,axs=plt.subplots(1,3,figsize=(14,3.5))
    for ax,lab in zip(axs,c.LABS):
        g=raw.loc[raw.LAB.eq(lab)];ax.plot(g.t_h,g.raw_SD,label='Within-window SD')
        ax.plot(g.t_h,g.naive_SE,label='IID standard error (assumption)')
        ax.axhline(.04,c='gray',ls=':',label='Original observation SD')
        ax.set(title=lab,xlabel='Time [h]',ylabel='CO₂ [g/(L h)]');ax.grid(alpha=.2);ax.legend(fontsize=7)
    finish(fig,'RAW variability is not automatically the uncertainty of a 30-minute mean')

def score_figures(study):
    scores=pd.DataFrame(study['scores']);cv=scores.loc[scores.fold.ne('All development')]
    pivot=cv.pivot(index='structure',columns='fold',values='score');fig,ax=plt.subplots(figsize=(10,4))
    pivot.plot.bar(ax=ax);ax.set(ylabel='Screened Gaussian score (lower is better)',xlabel='Noise structure')
    ax.tick_params(axis='x',rotation=15);ax.legend(fontsize=7,loc='best');ax.grid(axis='y',alpha=.2)
    finish(fig,'Internal leave-one-fermentation-out · gas refitted inside each fold')
    metrics=pd.DataFrame(study['metrics']);cv=metrics.loc[metrics.fold.ne('All development')]
    fig,axs=plt.subplots(2,3,figsize=(14,7))
    for ax,state in zip(axs.flat,['CO2','X','N','GF','E','F']):
        p=cv.loc[cv.variable.eq(state)].pivot(index='structure',columns='LAB',values='RMSE')
        p.plot.bar(ax=ax,legend=False);unit=cv.loc[cv.variable.eq(state),'unit'].iloc[0]
        ax.set(title=state,ylabel='RMSE ['+unit+']',xlabel='');ax.tick_params(axis='x',rotation=35,labelsize=7);ax.grid(axis='y',alpha=.2)
        ax.legend(fontsize=6,loc='best')
    finish(fig,'Internal validation: gas and chemical errors must be assessed together')

def parameter_figures(study):
    rows=[]
    for fit in study['fits']:
        for name,value in zip(fit['names'],fit['x']):rows.append(dict(fold=fit['fold'],structure=fit['structure'],parameter=name,value=10**value))
    params=pd.DataFrame(rows);leader=study['leader'];fig,ax=plt.subplots(figsize=(10,4))
    for fold,g in params.loc[params.structure.eq(leader)].groupby('fold'):
        ax.plot(g.parameter,g.value,marker='o',label=fold)
    ax.set_yscale('log');ax.set(ylabel='Multiplier or absolute amplitude (see parameter table)',xlabel='Parameter')
    ax.legend(fontsize=7);ax.grid(alpha=.2);finish(fig,'Parameter stability across training subsets · '+leader)
    profiles=pd.DataFrame(study['conditional_profiles']);fig,axs=plt.subplots(2,3,figsize=(14,6))
    for ax,(name,g) in zip(axs.flat,profiles.groupby('parameter',sort=False)):
        ax.semilogx(g.value,g.score,marker='o');ax.axvline(g.fit_value.iloc[0],c='gray',ls=':')
        ax.set(title=name,xlabel='Parameter value',ylabel='Conditional score');ax.grid(alpha=.2)
    for ax in list(axs.flat)[profiles.parameter.nunique():]:ax.axis('off')
    finish(fig,'Conditional sweeps: other parameters fixed · not confidence intervals')
    S=study['sensitivity'];fig,ax=plt.subplots(figsize=(6,5));im=ax.imshow(S['normalized_gram'],vmin=-1,vmax=1,cmap='RdBu_r')
    ax.set_xticks(range(len(S['names'])),S['names'],rotation=35,ha='right');ax.set_yticks(range(len(S['names'])),S['names'])
    fig.colorbar(im,ax=ax,label='Normalized local sensitivity inner product');finish(fig,'Local prediction/variance sensitivity alignment')
    return params

def innovation_figures(study):
    checks=pd.DataFrame(study['checks']);keep=checks.loc[checks.fold.eq('All development')&checks.structure.isin(['Original noise',study['leader']])]
    fig,axs=plt.subplots(1,3,figsize=(14,3.5))
    for ax,lab in zip(axs,c.LABS):
        for row in keep.loc[keep.LAB.eq(lab)].itertuples():ax.plot(range(1,11),row.acf,marker='o',label=row.structure)
        ax.axhline(0,c='gray',lw=.7);ax.set(title=lab,xlabel='Lag in 30-minute bins',ylabel='Innovation autocorrelation');ax.grid(alpha=.2);ax.legend(fontsize=7)
    finish(fig,'Residual temporal structure · missing update bins are not joined')

def trajectories(data,chem,records,leader,state,title):
    factor=1000 if state=='N' else 1.;unit='mg/L' if state=='N' else ('g/(L h)' if state=='CO2' else 'g/L')
    fig,axs=plt.subplots(1,3,figsize=(15,4.3))
    for ax,lab in zip(axs,c.LABS):
        d=data[lab];errors=[]
        for label,color,style in [('Original noise','#777777','--'),(leader,'#0072B2','-')]:
            f,P,dg=records[label,lab]
            if state=='CO2':
                mask=d['valid']&np.isfinite(dg[:,0]);tx=d['grid'][mask];pred=dg[mask,0]
                rmse=np.sqrt(np.mean((pred-d['y'][mask])**2))
            else:
                j=c.STATES.index(state) if state!='GF' else 2;tx=d['grid']
                pred=(f[:,2]+f[:,3]) if state=='GF' else f[:,j]
                variance=P[:,2,2]+P[:,3,3]+2*P[:,2,3] if state=='GF' else P[:,j,j]
                o=chem.loc[chem.lab.eq(lab)&chem.t_h.gt(0)&chem.t_h.le(d['horizon'])].dropna(subset=[c.CHEM_COLS[state]])
                if state=='GF':o=o.loc[~o.GF_zero_substitution.astype(str).str.lower().eq('true')]
                rmse=np.sqrt(np.mean((np.interp(o.t_h,tx,pred)-o[c.CHEM_COLS[state]].to_numpy())**2))*factor
                if label==leader:
                    sd=np.sqrt(np.maximum(variance,0));ax.fill_between(tx,(pred-1.96*sd)*factor,(pred+1.96*sd)*factor,color=color,alpha=.12,label='Fitted ±1.96 state SD')
            ax.plot(tx,pred*factor,color=color,ls=style,label='Original noise' if label=='Original noise' else 'Fitted noise')
            errors.append(('Original' if label=='Original noise' else 'Fitted')+f' RMSE = {rmse:.3f} {unit}')
        if state=='CO2':
            mask=d['valid'];ax.plot(d['grid'][mask],d['y'][mask],c='black',lw=.6,label='Samples')
        else:
            label='G+F' if state=='GF' else 'Samples';ax.scatter(o.t_h,o[c.CHEM_COLS[state]]*factor,c='black',s=20,label=label,zorder=5)
            ini=d['initial'][2]+d['initial'][3] if state=='GF' else d['initial'][c.STATES.index(state)]
            ax.scatter([0],[ini*factor],c='black',s=20,zorder=5)
        for t in d['grid'][d['doses']>0]:ax.axvline(t,c='gray',ls=':',label='N pulse')
        h,l=ax.get_legend_handles_labels();u=dict(zip(l,h));ax.legend(u.values(),u.keys(),loc='best',fontsize=6.6,title='\n'.join(errors),title_fontsize=7,framealpha=.9)
        ax.set(title=lab,xlabel='Time [h]',ylabel=title+' ['+unit+']');ax.grid(alpha=.2)
    finish(fig,title+' · development fits · same refitted gas parameters')
