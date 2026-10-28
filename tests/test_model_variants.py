
import unittest,json
from pathlib import Path
import numpy as np
import pandas as pd
from wine_fermentation import model as old
from wine_fermentation.models.without_transporters import kinetics as direct
from wine_fermentation.models.with_transporters import kinetics as transport
from wine_fermentation.shared.gas import simulate as gas

ROOT=Path(__file__).resolve().parents[1]
class Variants(unittest.TestCase):
    def setUp(self):
        self.p=json.loads((ROOT/'configs/theta/theta_nv2.json').read_text())
        self.batch=old.BatchData('natural','test',np.array([0.,1.]),np.array([20.,20.]),
             {'N':()}, {},dict(X=.5,N=.15,G=80.,F=80.,E=10.))
    def test_direct_zero_effect_recovers_original_rhs(self):
        p={**self.p,'aN':0.,'KNa':.03}
        y=direct.initial(self.batch,p)
        np.testing.assert_allclose(direct.rhs(0,y,p,self.batch),old.rhs(0,y,self.p,self.batch),rtol=1e-13)
    def test_no_growth_consumption_after_required_sugar_exhaustion(self):
        p={**self.p,'aN':.3,'KNa':.03}
        y=direct.initial(self.batch,p);y[2]=0.
        rates=direct.terms(0,y,p,self.batch)
        self.assertEqual(rates['mu'],0.)
        self.assertEqual(direct.rhs(0,y,p,self.batch)[2],0.)
        self.assertGreater(rates['beta_f'],0.)
    def test_transport_nitrogen_and_pulse_accounting(self):
        p={**self.p,'alpha':.7,'eta0':.01,'KTr':.03,'aTr':1.,'YTrN':6.25}
        y=transport.initial(self.batch,p);q=transport.terms(0,y,p,self.batch)
        derivative=transport.rhs(0,y,p,self.batch)
        self.assertAlmostEqual(derivative[1]+derivative[2],-q['mu']*y[0]/p['Yxn']-q['vTr']/p['YTrN'])
        after=transport.nutrition(y,.08,p)
        self.assertAlmostEqual(after[1]+after[2]-y[1]-y[2],.08)
        self.assertEqual(after[0],y[0])
    def test_retention_and_transfer_conserve_inventory(self):
        p={**self.p,'aN':0.,'KNa':.03,'mu0':0.,'betaG0':0.,'betaF0':0.}
        core=pd.DataFrame([direct.initial(self.batch,p)]*2,index=[0.,1.],columns=direct.STATES)
        retained=gas('without_transporters',self.batch,p,core,dict(kLa=1.,gain=.7,Cd0=.1),lambda t:np.ones_like(t)*1.95)
        np.testing.assert_allclose(retained.Cd,.1)
        np.testing.assert_allclose(retained.qgas,0.)
        released=gas('without_transporters',self.batch,p,core,dict(kLa=1.,gain=.7,Cd0=3.),lambda t:np.ones_like(t)*1.95)
        self.assertGreater(released.qgas.max(),0.)
        self.assertAlmostEqual(float(np.sum(np.diff(released.index)*released.qgas.to_numpy()[1:])),
                               float(released.Cd.iloc[0]-released.Cd.iloc[-1]))

class GasPartitions(unittest.TestCase):
    def test_primary_and_inverse_are_disjoint(self):
        from wine_fermentation.comparison import partition,PRIMARY_TRAINING,LABS
        train,holdout=partition(PRIMARY_TRAINING)
        self.assertEqual(train,('LAB019','LAB020','LAB021'))
        self.assertEqual(holdout,('LAB016','LAB017','LAB018'))
        self.assertFalse(set(train)&set(holdout))
        self.assertEqual(set(train)|set(holdout),set(LABS))
        inverse=partition('train_016_018')
        self.assertEqual(inverse,(holdout,train))
        with self.assertRaises(ValueError):partition('all_six')
    def test_optimizer_never_sees_holdout(self):
        from wine_fermentation.comparison import partition,PRIMARY_TRAINING,LABS,fit_prediction
        train,holdout=partition(PRIMARY_TRAINING)
        observed={lab:pd.DataFrame({'time_h':[0.,1.,2.],
            'co2_raw_g_l_h':[2. if lab in train else 9999.]*3}) for lab in LABS}
        called=[]
        def predict(lab,values):
            called.append(lab)
            return pd.DataFrame({'qpred':[values[0]]*3},index=[0.,1.,2.])
        solution=fit_prediction(predict,observed,train,[1.],[(.1,10.)])
        self.assertTrue(solution.success)
        self.assertAlmostEqual(float(np.exp(solution.x[0])),2.,places=5)
        self.assertEqual(set(called),set(train))
        self.assertFalse(set(called)&set(holdout))

if __name__=='__main__':unittest.main()

