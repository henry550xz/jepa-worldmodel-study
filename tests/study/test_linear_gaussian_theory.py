import numpy as np
import pytest
from study.linear_gaussian_theory import cell, fit_jepa
from study.linear_gaussian import sample


def test_interesting_and_failure_regimes():
    d = cell(4,.5)['results']
    assert not d['pixel']['state_selected'] and d['jepa']['state_selected']
    assert d['jepa']['future_task_state_mse'] == pytest.approx(.19,abs=.02)
    assert d['pixel']['future_task_state_mse'] > .9
    d = cell(4,.95)['results']
    assert not d['pixel']['state_selected'] and not d['jepa']['state_selected']


def test_jepa_scale_invariance():
    a,b = [cell(scale,.7)['results']['jepa'] for scale in [.25,8]]
    assert a['unit_variance_coordinate_squared_loadings'] == pytest.approx(b['unit_variance_coordinate_squared_loadings'],abs=1e-10)


def test_variance_constraint_and_signed_correlations():
    x,y,_=sample(20000,.5,2,-.9,np.random.default_rng(0))
    mean,w,a=fit_jepa(x,y)
    assert (np.mean(((x-mean)@w)**2)+np.mean(((y-mean)@w)**2))/2 == pytest.approx(1)
    assert a < -.85
    assert (2*w[1])**2 > w[0]**2
