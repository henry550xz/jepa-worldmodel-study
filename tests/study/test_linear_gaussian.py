import pytest
from study.linear_gaussian import experiment,sample
import numpy as np

def test_phase_boundary_away_from_tie():
 for beta,rho,expected in [(0.5,.9,True),(3.,.9,False),(10.,0.,True)]:
  d=experiment(.8,beta,rho,n_train=20000,n_test=1000)['results']['pixel'];assert d['analytic_state_selected']==expected;assert (d['empirical_state_loading_fraction']>.5)==expected

def test_whitened_reference_removes_scale_boundary():
 a=experiment(.8,.5,.6)['results']['fixed_whitened_target'];b=experiment(.8,4.,.6)['results']['fixed_whitened_target'];assert a['empirical_state_loading_fraction']==pytest.approx(b['empirical_state_loading_fraction'],abs=1e-8)

def test_reject_nonstationary():
 with pytest.raises(ValueError):sample(2,.8,1.,1.,np.random.default_rng(0))
