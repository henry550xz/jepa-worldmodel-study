import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('watch',Path(__file__).resolve().parents[2]/'scripts/study/worker/watch_reproductions.py')
watch=importlib.util.module_from_spec(spec);spec.loader.exec_module(watch)


def test_monitor_waits_for_completion_before_returning(monkeypatch,tmp_path):
    transitions=iter([{'status':'running'},{'status':'training_complete'}])
    records=[];syncs=[]
    monkeypatch.setattr(watch,'manifest',lambda *a:next(transitions))
    monkeypatch.setattr(watch,'record',lambda p,s:records.append(dict(s)))
    monkeypatch.setattr(watch,'sync',lambda *a:syncs.append(a))
    monkeypatch.setattr(watch.time,'sleep',lambda _:None)
    result=watch.wait('alias','run','training',{},tmp_path/'state')
    assert result['status']=='training_complete'
    assert [r['status'] for r in records]==['running','training_complete']
    assert len(syncs)==2


def test_monitor_stops_on_failure(monkeypatch,tmp_path):
    monkeypatch.setattr(watch,'manifest',lambda *a:{'status':'failed'})
    monkeypatch.setattr(watch,'record',lambda *a:None)
    monkeypatch.setattr(watch,'sync',lambda *a:None)
    with pytest.raises(RuntimeError,match='failed'):
        watch.wait('alias','run','training',{},tmp_path/'state')
