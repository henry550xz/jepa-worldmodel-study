# Provisional linear-Gaussian state+nuisance simulation

The requested proposed `(beta,rho)` theory was not found in the repository or supplied conversation equations. Definitions were requested. The implementation below is a clearly labeled minimal candidate, not validation of that unspecified theory.

## Explicit model

Independent unit-variance stationary Gaussian state s and nuisance n:

`s_next = alpha*s + sqrt(1-alpha²)*epsilon_s`

`n_next = rho*n + sqrt(1-rho²)*epsilon_n`

Observation `x=(s, beta*n)`. Here **beta means nuisance amplitude** and **rho means nuisance persistence**; alpha is relevant-state persistence. Innovations are independent standard Gaussian. Stationary correlations have absolute value<1 and beta>0. No actions or learned nonlinear encoder are included.

For a rank-one encoder and optimal linear future-observation decoder, whiten input covariance. The predictive cross-covariance has singular values `|alpha|` and `|beta*rho|`, so explained output variances are `alpha²` and `beta²*rho²`. The population pixel objective selects the state direction iff `alpha² > beta²*rho²`; the boundary is `beta*|rho|=|alpha|`. At equality the optimum is not unique.

The fixed-whitened-future-target reference has predictive eigenvalues `alpha²,rho²`, hence state selection iff `|alpha|>|rho|`. It is NOT a learned JEPA model, and says nothing by itself about jointly learned target encoders or collapse prevention. It can select nuisance when nuisance is more predictable.

## Finite-sample implementation and validation

`study/linear_gaussian.py` draws independent stationary transition pairs, fits rank-one reduced-rank regression by SVD using training covariance only, and fits a relevant-state readout on training data only. Independent test pairs evaluate future-state and observation MSE. Independent pairs deliberately avoid time-series effective-sample-size confounds; this is not a trajectory-control simulation.

Seed0, alpha0.8, beta in0.25/0.5/1/2/4, rho in0/0.2/0.5/0.8/0.95;10,000 train pairs and20,000 test pairs per cell. All25 CPU-only cells completed. All43 objective/cell cases whose analytic margin exceeds0.05 in absolute value selected the predicted direction. Near-boundary cases are not treated as exact finite-sample pass/fail. Three tests passed: phase selection away from boundary, scale invariance of fixed-whitened reference, rejection of nonstationarity.

Results and phase-grid PNG: `/mnt/research/jepa-worldmodel-study-storage/artifacts/linear-gaussian-provisional-20260915/`. No GPU training used. The exact requested theoretical phase boundary remains **blocked on definitions/equations**; do not rename this provisional model as that theory without checking correspondence.
