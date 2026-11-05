"""Numerical checks of the added training-only analysis, not of the old notebooks."""
import numpy as np
import analysis_core as c

def check_source_mapping():
    p=c.THETA;w=np.array([1.2,.08,60.,70.,25.,.2,0.]);T=20.;S0=170.;k,g=c.ARCHIVED_GAS
    def perturbed(eta):
        x,n,G,F,E,Cd=w[:6];mu,bg,bf,kd,m,A,cs=c.terms(w,T,S0)
        rc=mu*x+eta[0];rG=bg*x/p['Yeg']+eta[1];rF=bf*x/p['Yef']+eta[2]
        rd=kd*x+eta[4];rm=m*x+eta[5]
        prod=A*(rc/12.72+(p['Yeg']*rG+p['Yef']*rF)/1.05+eta[3])
        acc=min(prod,k*max(cs-Cd,0.))-k*max(Cd-cs,0.)
        return np.array([rc-rd,-rc/p['Yxn'],-rc/p['Yxg']-rG-G/(G+F+1e-8)*rm,
            -rc/p['Yxf']-rF-F/(G+F+1e-8)*rm,p['Yeg']*rG+p['Yef']*rF,acc,g*(prod-acc)])
    L=c.noise_L(w,T,S0,k,g);eps=1e-7
    numeric=np.column_stack([(perturbed(np.eye(6)[j]*eps)-perturbed(-np.eye(6)[j]*eps))/(2*eps) for j in range(6)])
    np.testing.assert_allclose(L,numeric,atol=1e-8,rtol=1e-6)
    sigma=np.array([.003,.08,.08,.01,.001,.01]);Q=L@np.diag(sigma**2)@L.T
    assert np.linalg.eigvalsh(Q).min()>-1e-12
    np.testing.assert_allclose(L[:,4],[-1,0,0,0,0,0,0])
    np.testing.assert_allclose(L[:,5],[0,0,-60/(130+1e-8),-70/(130+1e-8),0,0,0])
    return float(np.max(abs(L-numeric)))

if __name__=='__main__':
    print('All six L columns match finite perturbations of their defining balances. Max error:',check_source_mapping())
