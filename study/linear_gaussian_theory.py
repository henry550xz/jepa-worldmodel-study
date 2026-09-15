"""User-defined rank-one AR(1) toy hypothesis; no robotics/learned-JEPA claim."""
import argparse
import json
import subprocess
from pathlib import Path
import numpy as np
from study.linear_gaussian import sample, fit_rank_one


def fit_jepa(x, y):
    # Same centering and encoder at both times; stationary variance estimated
    # from training pairs only. Maximize squared lag covariance / variance^2.
    mean = (x.mean(0) + y.mean(0)) / 2
    xc, yc = x - mean, y - mean
    covariance = (xc.T @ xc + yc.T @ yc) / (2 * len(x))
    values, vectors = np.linalg.eigh(covariance)
    whitening = (vectors * values**-.5) @ vectors.T
    lag = (xc.T @ yc + yc.T @ xc) / (2 * len(x))
    values, vectors = np.linalg.eigh(whitening @ lag @ whitening)
    w = whitening @ vectors[:, np.argmax(values**2)]
    # Pooled stationary estimate makes Var(z)=1; analytic optimum a=lag.
    a = float(w @ lag @ w)
    return mean, w, a


def cell(beta, rho, seed=0, n_train=20000, n_test=20000, rho_s=.9):
    rng = np.random.default_rng(seed)
    x, y, _ = sample(n_train, rho_s, beta, rho, rng)
    xt, yt, _ = sample(n_test, rho_s, beta, rho, rng)
    xm, _, wp, _ = fit_rank_one(x, y)
    jm, wj, a = fit_jepa(x, y)
    results = {}
    for method, mean, w in [('pixel', xm, wp), ('jepa', jm, wj)]:
        z, zt = (x-mean) @ w, (xt-mean) @ w
        design = np.column_stack([z, np.ones(len(z))])
        test_design = np.column_stack([zt, np.ones(len(zt))])
        # Identical train-only downstream fits; JEPA decoder is diagnostic only.
        decoder = np.linalg.lstsq(design, y, rcond=None)[0]
        prediction = test_design @ decoder
        current_probe = np.linalg.lstsq(design, x[:, 0], rcond=None)[0]
        loading = np.array([w[0], beta*w[1]])
        loading /= np.linalg.norm(loading)
        margin = rho_s**2 - ((beta*rho)**2 if method == 'pixel' else rho**2)
        results[method] = {
            'encoder_w_observation_coordinates': w.tolist(),
            'unit_variance_coordinate_squared_loadings': (loading**2).tolist(),
            'state_selected': bool(loading[0]**2 > .5),
            'analytic_margin': margin,
            'future_task_state_mse': float(np.mean((prediction[:,0]-yt[:,0])**2)),
            'current_task_state_probe_mse': float(np.mean((test_design@current_probe-xt[:,0])**2)),
            'future_observation_mse_per_coordinate': float(np.mean((prediction-yt)**2)),
            'future_observation_squared_error_sum': float(np.mean(np.sum((prediction-yt)**2, axis=1))),
        }
        if method == 'jepa':
            results[method].update(latent_predictor=a, heldout_latent_prediction_mse=float(np.mean((a*zt-(yt-mean)@w)**2)))
    return dict(beta=beta, rho_n=rho, rho_s=rho_s, seed=seed, results=results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    betas = [.25,.5,1,2,4,8]
    rhos = [.1,.3,.5,.7,.85,.95]
    rows = [cell(b,r,s) for r in rhos for b in betas for s in range(5)]
    # Densify only around the predicted switch, separate from requested grid.
    boundary = [cell(.9/r*f,r,s) for r in rhos for f in [.9,.95,1,1.05,1.1] for s in range(5)]
    data = dict(git_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                definition=__doc__, rho_s=.9, seeds=list(range(5)), n_train=20000,n_test=20000,
                sampling='independent stationary transition pairs; train/test independent; paired data across methods',
                jepa_estimator='pooled stationary covariance and symmetric lag; shared online encoder, unit variance; not fixed whitened targets',
                rows=rows, boundary_rows=boundary)
    (out/'results.json').write_text(json.dumps(data,indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax, method in zip(axes,['pixel','jepa']):
        for r in rhos:
            for b in betas:
                vals = [v['results'][method]['unit_variance_coordinate_squared_loadings'][0] for v in rows if v['beta']==b and v['rho_n']==r]
                scatter=ax.scatter(r,b,c=np.mean(vals),vmin=0,vmax=1,cmap='coolwarm',s=180,edgecolors='black')
        rr=np.linspace(.1,.95,200)
        ax.plot(rr,.9/rr,'k--',label='Pixel boundary β=0.9/ρn')
        ax.axvline(.9,color='green',linestyle=':',label='JEPA boundary ρn=0.9')
        ax.set(yscale='log',ylim=(.2,10),xlabel='Nuisance persistence ρn',ylabel='Nuisance magnitude β',title=method)
        ax.legend(fontsize=8)
    fig.colorbar(scatter,ax=axes,label='State loading fraction (five-seed mean)')
    fig.savefig(out/'phase-diagram.png',dpi=180)
    fig.savefig(out/'phase-diagram.pdf')
    away=[v['results'][m] for v in rows for m in ['pixel','jepa'] if abs(v['results'][m]['analytic_margin'])>.05]
    print(json.dumps({'grid_fits':len(rows)*2,'away_from_boundary_agreement':sum(v['state_selected']==(v['analytic_margin']>0) for v in away),'away_from_boundary_total':len(away),'output':str(out)}))

if __name__=='__main__':
    main()
