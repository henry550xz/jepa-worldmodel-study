import json
import subprocess
import pytest
from study.manifests import create_manifest, provenance
from study.snapshot import export
from study.run import training_overrides


def repository(tmp_path):
    root=tmp_path/'repo'; root.mkdir()
    def git(*args):
        return subprocess.check_output(['git','-C',str(root),*args],text=True)
    git('init','-q'); git('config','user.name','Test'); git('config','user.email','test@example.invalid')
    (root/'source.py').write_text('x=1\n'); git('add','.'); git('commit','-qm','baseline')
    git('tag','-a','baseline/upstream-initial','-m','baseline')
    return root,git


def test_unique_manifest_and_required_fields(tmp_path):
    root,_=repository(tmp_path); info=provenance(root)
    kwargs=dict(provenance_info=info,method='gaussian',seed=0,dataset_path='/worker/data',
                dataset_version='sha256-verified',resolved_config={'seed':0},
                planning_settings={'rollout_horizon':5},evaluation_settings={'seed':99})
    path,a=create_manifest(tmp_path/'runs',**kwargs)
    _,b=create_manifest(tmp_path/'runs',**kwargs)
    assert a['run_id']!=b['run_id']
    assert a['git_sha']==b['git_sha'] and a['seed']==b['seed']
    assert json.loads((path/'manifest.json').read_text())==a
    assert {'peak_vram_bytes','checkpoint_path','training_start','training_end','metrics_path'} <= a.keys()


def test_dirty_code_refused_and_snapshot_verified(tmp_path):
    root,_=repository(tmp_path)
    target=tmp_path/'snapshot'; export(root,target)
    assert provenance(target)==provenance(root)
    (target/'source.py').write_text('x=2\n')
    with pytest.raises(RuntimeError): provenance(target)
    (root/'extra.py').write_text('uncommitted')
    with pytest.raises(RuntimeError): provenance(root)


def test_tracked_credentials_refused(tmp_path):
    root,git=repository(tmp_path)
    (root/'.env').write_text('NOT_A_REAL_CREDENTIAL=placeholder\n')
    git('add','.env');git('commit','-qm','test forbidden filename')
    with pytest.raises(ValueError): export(root,tmp_path/'snapshot')


def test_reproduction_settings_and_smoke_are_explicit():
    dense=training_overrides('gaussian','reproduction',0,'/worker','id')
    sparse=training_overrides('sparse','reproduction',0,'/worker','id')
    assert set(dense)^set(sparse)=={'link=identity','link=reprelu','target_p=1','target_p=2'}
    assert 'training.epochs=2' in dense and 'training.batch_size=64' in dense
    smoke=training_overrides('gaussian','smoke',0,'/worker','id')
    assert 'training.batch_size=2' in smoke and 'env.dataset.n_rollout=2' in smoke
    with pytest.raises(ValueError): training_overrides('pixel','reproduction',0,'/worker','id')
