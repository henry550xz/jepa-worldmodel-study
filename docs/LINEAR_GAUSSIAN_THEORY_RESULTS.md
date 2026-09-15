# Linear-Gaussian state/nuisance toy hypothesis

## Definition and estimator

This implements the user's newly specified toy hypothesis, not a claim from LpWM or evidence that nonlinear JEPA must win. Independent stationary unit-variance state and nuisance follow AR(1) transitions; observation x=(s,beta*n). rho_s=0.9. Both methods have one scalar linear bottleneck.

Pixel minimizes future observation squared error using train-only reduced-rank regression. JEPA uses the SAME encoder at both times, unit latent variance, and a scalar latent predictor. It does not use the previous fixed-whitened-target surrogate. For normalized coordinate loadings u,v with u²+v²=1, lag correlation is c=rho_s*u²+rho_n*v². Optimizing a gives loss 1-c². Thus maximizing squared lag correlation selects the coordinate with largest absolute correlation; at equal positive correlations all mixtures tie. Pixel's explained observation variance scores are rho_s² and beta²*rho_n². Its tie is likewise non-identifiable; no unique switch direction is expected exactly on the boundary.

The empirical JEPA solver uses pooled present/future training covariance to estimate stationary variance, symmetric lag covariance, and the eigenvector of largest absolute whitened lag eigenvalue. This is a closed-form stationary moment estimator, not SGD on an asymmetric finite-sample loss. In the population it matches the supplied objective. No test data enters encoders, centering, variance estimates, or downstream fits.

## Reproducibility

Code snapshot: `6732a6d3ade3559a639c11a104c5dfaf2fe99d98`. Command:

```bash
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/mnt/research/jepa-worldmodel-study-storage/artifacts/mpl-cache python3 -m study.linear_gaussian_theory --output /mnt/research/jepa-worldmodel-study-storage/artifacts/linear-gaussian-theory-20260915
```

Output must be a new directory; existing evidence is never overwritten. Requested grid: rho_n=[0.1,0.3,0.5,0.7,0.85,0.95], beta=[0.25,0.5,1,2,4,8]. Seeds0–4,20,000 independent stationary training transition pairs and20,000 independent test pairs per cell/seed. Methods share data; common random numbers across grid points aid comparisons. Additional boundary checks use beta=(0.9/rho_n)*[0.90,0.95,1,1.05,1.10]. Total660 fitted representations including boundary checks. Six tests pass, including signed correlations, normalization, scale invariance and both regimes.

Artifacts: `/mnt/research/jepa-worldmodel-study-storage/artifacts/linear-gaussian-theory-20260915/` contains `results.json`, `phase-diagram.png`, `phase-diagram.pdf`. JSON records all squared state/nuisance loadings in unit-variance coordinates, raw encoder weights, future-state MSE, current-state probe MSE, future-observation error (sum and per-coordinate mean), JEPA latent error, seeds and source SHA. Downstream state/observation readouts are fitted on training data only. JEPA's observation decoder is diagnostic, not part of its objective. Here “reconstruction” means next-observation prediction, not same-frame autoencoding.

## Validated results

All360 method/seed fits on the requested36-cell grid selected the analytically predicted coordinate (all score margins exceed0.05). For rho_n>=0.3, all five seeds select state at5% below the Pixel boundary and nuisance at5% above it. At rho_n=0.1, the5% points give state selection3/5 below and1/5 above; at10% below/above,4/5 and0/5. Weak nuisance correlation and large beta increase finite-sample uncertainty. Exactly at the boundary, mixed loadings/random selection are expected; these are not failures.

Five-seed mean examples:

| beta / rho_n | method | future state MSE | future observation squared-error sum |
|---|---|---:|---:|
|4 /0.5|Pixel|0.99894|13.04045|
|4 /0.5|JEPA|0.19002|16.20640|
|4 /0.95|Pixel|0.99907|2.56445|
|4 /0.95|JEPA|0.99904|2.56628|

The first regime exhibits the hypothesized task/objective tradeoff: Pixel predicts observation variance better but loses task state. The second confirms that normalized predictability alone does not identify task relevance. The state-selected irreducible future-state MSE is1-0.9²=0.19; nuisance-only state prediction has MSE1.

## Limits and next action

This verifies the hypothesis under its diagonal, linear, independent, stationary, rank-one assumptions using a global closed-form solver. It does not test neural optimization, collapse under soft regularization, actions, multimodal images, rollout stability, or planning. Finite-sample switches are uncertain near ties. The earlier provisional experiment remains preserved and is superseded only as the implementation of the now-specified theory. Theory-definition blocker is resolved. Robotics full runs remain unauthorized pending the documented matched-update versus equal-compute decision; no GPU contact or training occurred here.
