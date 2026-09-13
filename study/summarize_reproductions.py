"""Summarize preserved real manifests only; no generated/fabricated experiment scores."""
import csv
import json
import statistics
from pathlib import Path


def summarize(store, run_ids, disk_usage='not recorded'):
    store=Path(store)
    lines=['# Upstream PushT reproduction results','',
        'Generated from completed run manifests and upstream final evaluation logs. '
        'These are official-protocol reproductions, not the controlled three-arm study.','',
        '| Method | Run | Train wall s | Planning wall s | Train peak VRAM GiB | Planning peak VRAM GiB | Mean sampled GPU % | Checkpoint MiB | Success rate |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    records=[]
    for run_id in run_ids:
        folder=store/'runs'/run_id
        m=json.loads((folder/'manifest.json').read_text())
        if m['status']!='training_complete' or m['evaluation_settings']['status']!='complete':
            raise ValueError('cannot report an incomplete run as completed')
        metrics=json.loads((folder/'planning/metrics.json').read_text())
        utilization=[]
        with (folder/'gpu-utilization.csv').open() as f:
            for row in csv.DictReader(f):
                try:utilization.append(float(row[' utilization.gpu [%]'].strip().split()[0]))
                except (ValueError,KeyError):continue
        avg=statistics.mean(utilization) if utilization else None
        ev=m['evaluation_settings']
        def fmt(value):return 'unavailable' if value is None else f'{value:.3f}'
        lines.append('| '+' | '.join([m['method'],run_id,fmt(m['training_wall_seconds']),
            fmt(ev.get('wall_seconds')),fmt(m['peak_vram_bytes']/1024**3),
            fmt(ev.get('planning_peak_vram_bytes',0)/1024**3) if ev.get('planning_peak_vram_bytes') is not None else 'unavailable',
            fmt(avg),fmt(m['checkpoint_bytes']/1024**2),fmt(metrics.get('final_eval/success_rate'))])+' |')
        records.append(dict(manifest=m,final_metrics=metrics,mean_sampled_training_gpu_utilization=avg))
    lines += ['', '## Exact provenance and commands', '']
    for record in records:
        m=record['manifest'];run_id=m['run_id'];sha=m['git_sha']
        lines += [f"- {m['method']}: code `{sha}`, upstream `{m['upstream_baseline_sha']}`, dataset SHA256 `{m['dataset_version']}`.",
                  f"- Environment: Python {m['environment']['python']}, PyTorch {m['environment']['torch']}, CUDA runtime {m['environment']['cuda_runtime']}; GPU {m['gpu_model']}.",
                  '```bash', f'cd /root/autodl-tmp/robotics/jepa-worldmodel-study/code/{sha}',
                  f"/root/autodl-tmp/robotics/jepa-worldmodel-study/envs/lpwm-5090/bin/python -m study.run --method {m['method']} --phase reproduction --seed {m['seed']} --dataset-version {m['dataset_version']}",
                  f'/root/autodl-tmp/robotics/jepa-worldmodel-study/envs/lpwm-5090/bin/python -m study.plan_official {run_id}',
                  '```','Resolved training and planning configs, logs and metrics are under `runs/'+run_id+'`; selected checkpoint plus verified SHA256 under `checkpoints/'+run_id+'`.','']
    lines += ['## Deviations and interpretation','',
        'The RTX5090 environment preserves working torch2.8/cu128 rather than upstream2.3/cu121; Python3.12, Hydra1.3.2, W&B.17.9, scikit-image.24 and NumPy1.26.4 are disclosed compatibility choices. See the committed environment inventory and requirements. Upstream scientific source is unchanged; logging/output locations and instrumentation differ.',
        'Training and planning wall times include their diagnostics and startup; model-only latency is not separately instrumented. Sampled GPU utilization is not continuous measurement. Official CEM permits simulator-based early stopping and couples goal horizon, rollout horizon and action prefix. State distance mixes units; use the future common physical evaluator for controlled comparisons.',
        'Completing these runs validates executable behavior, not numerical agreement with a published target: no authoritative expected success rate for this exact selected cell has been established in the repository audit. Inspect curves and planning outcomes before deciding whether the baseline is scientifically reproduced closely enough. No pixel experiment or multi-seed sweep is authorized by this queue.',
        '', '## Final worker disk usage', '', '```text',disk_usage.strip(),'```','']
    report=store/'runs/UPSTREAM_REPRODUCTION_REPORT.md'
    report.write_text('\n'.join(lines))
    (store/'runs/UPSTREAM_REPRODUCTION_RESULTS.json').write_text(json.dumps(records,indent=2)+'\n')
    return report
