# Current project status

Working snapshot; research history is in [CHATGPT_RESEARCH_HANDOFF.md](CHATGPT_RESEARCH_HANDOFF.md). Updated 2026-09-15 after authorized four-arm queue launch.

## Scientific goal / project definition

Controlled study of temporal observation/pixel prediction versus Gaussian JEPA versus sparse JEPA for world models, initially PushT. We are testing WHETHER and WHEN JEPA helps, not assuming it must win. OGBench Cube, synthetic dynamics and potentially PDEBench are later work. This project is isolated from MARL, DA3, dehazing and old PushT projects.

## Environment and immutable baseline

- Checkout `/mnt/research/robotics/jepa-worldmodel-study`; storage `/mnt/research/jepa-worldmodel-study-storage`, both on mounted research volume. Branch `study/mechanisms`.
- Upstream `YilunKuang/lpworldmodel`, commit `bdd812d9432cccda8c350086006401b436f91982`; annotated tag `baseline/upstream-initial`. Origin `henry550xz/jepa-worldmodel-study`; upstream/main preserved.
- Worker `autodl-jepa`, RTX5090,32607MiB VRAM, driver595.71.05. Workspace `/root/autodl-tmp/robotics/jepa-worldmodel-study` on its50GB data disk. Dedicated `envs/lpwm-5090/bin/python`: Python3.12.3, PyTorch2.8.0+cu128, CUDA runtime12.8; base/drivers unchanged.
- Official PushT dataset SHA256 `442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08`, worker `datasets/pusht_noise`. Compatibility choices and full specifications are in manifests/conf/study and the reproduction report.

## Latest validated state and next action

Four mechanism configurations are implemented: standard teacher-forced Pixel, free-running rollout-reconstruction Pixel, Pixel+latent consistency, and Gaussian JEPA. **All bounded training and common-evaluation smokes passed. User subsequently authorized full execution (“run it”), using the recommended matched-window/update budget with measured unequal compute. The four-arm queue is now active.** Configuration and definitions: [MECHANISM_EXPERIMENT_PROTOCOL.md](MECHANISM_EXPERIMENT_PROTOCOL.md), `conf/study/mechanism.json`; measured audit: [MECHANISM_READINESS_AUDIT.md](MECHANISM_READINESS_AUDIT.md).

Shared seed0, ViT384/AdaLN, batch32 FP32, history3/frameskip5, frozen partitions,6-frame windows/3 common target times, muP optimizer schedule, initial module hashes and first data batch hash verified identical. Fourteen tests passed; four real smokes each8 updates +2 validation batches; four common evaluator smokes each4 readiness episodes,6 horizons,1 candidate bank and2 replans, with temporal/cycle closure diagnostics. Smoke checkpoints are not research results.

Budget decision: matched windows/updates, not equal FLOPs. All arms use seed0, batch32, two epochs,52,215 updates/epoch (104,430 total), identical six-frame windows/three targets. Teacher-forced versus free-running conditioning differs intentionally. Horizon3, auxiliary coefficient1.0 and Gaussian regularizer0.5 unchanged. Actual compute and resource use must be reported separately. No claim of exact equal compute or arbitrary method superiority.

The user has now supplied the exact beta/rho toy hypothesis. The shared-encoder, unit-variance latent-prediction solver and requested CPU sweep are complete:360/360 requested-grid method/seed selections match the analytic prediction, with finite-sample uncertainty near the boundary. Both the interesting regime and JEPA nuisance-selection failure regime are validated. See [LINEAR_GAUSSIAN_THEORY_RESULTS.md](LINEAR_GAUSSIAN_THEORY_RESULTS.md). The earlier provisional fixed-target reference is preserved, not treated as the specified JEPA objective.

Exact next action: inspect the existing queue and recent logs; do not launch duplicates. Pixel training is active. After each arm the queue runs full common evaluation (124 held-out error-vs-horizon episodes as sequence lengths permit;50 candidate/planning episodes) and latent closure, then advances only on success. Authorized order: Pixel → rollout Pixel → consistency Pixel → Gaussian. Stop/preserve/diagnose scientific or code failure. Full results are not yet available.

## Environment, snapshots and retained evidence

Worker `autodl-jepa`: active detached queue PID488900 (historical observation; recheck live), Pixel train PID489052. Queue `mechanism-seed0-20260915T2225Z`; immutable training/evaluation SHA `98816c638b4c2329079feffafde4090c0614cf3a`. Worker state `runs/mechanism-seed0-20260915T2225Z/state.json`; launch log beside queue directory. Controller observer `jepa-mechanism-monitor.service` retains compact evidence and hash-verifies completed latest checkpoints on durable controller storage. It never launches scientific stages. Worker queue owns sequencing and waiting; detached execution survives SSH disconnect but not machine destruction/reboot. Reconcile checkpoints/manifests before any recovery.

Run IDs share prefix `mechanism-seed0-20260915T2225Z-` with suffixes `pixel`, `pixel_rollout`, `pixel_consistency`, `gaussian`; future arm directories are created when reached. Launch command from committed worker snapshot: `bash scripts/study/worker/run_mechanisms.sh --authorized-full mechanism-seed0-20260915T2225Z` (ALREADY RUN; do not repeat). Worker data headroom20GiB at launch; controller research headroom13GiB. Fourteen tests and new8-update full-loop Gaussian preflight passed before launch. Initial Pixel loss finite/decreasing; GPU active. ETA pending sustained wall-clock measurement; initial compute timings suggest roughly4–5h per arm, with separate evaluation overhead.

- Training smoke snapshot `1ab94751e93e5f0e73cdab775db3400406323b9f`; evaluator snapshot `0e7c3f69f68f2d09c36654fa96d3876468092bb4`. Later config-wiring/instrumentation/documentation commits keep tested numerical settings but are not new trained snapshots.
- Controller `runs/mechanism-smokes-20260915-r2/state.json`, `audit.json`, `retention.json` under durable storage identify four run IDs and verified evidence. Per-run manifests, resolved YAML, telemetry, logs, probes and evaluation metrics retained. Disposable8-update checkpoints remain on worker; validated older research checkpoints remain retained on controller.
- Training peak allocated/reserved GiB: Pixel11.24/12.46, rollout7.77/8.41, consistency12.88/14.08, Gaussian11.36/11.90.24GiB+ recommended for sequential work pending longer profiling. No new concurrency assumption.
- Specified theory snapshot `6732a6d3ade3559a639c11a104c5dfaf2fe99d98`; artifacts: storage `artifacts/linear-gaussian-theory-20260915/` (JSON, PNG, PDF). Earlier provisional artifacts remain preserved.
- Initial80-update synthetic overfit criterion failed consistency arm;300 equal updates passed all arms without objective/threshold change. First evaluator prefix numerical assertion failed; consistent causal prefixes/per-step readout fixed it without retraining or loosening tolerances. Failed evidence preserved.

## Prior scientific results and limitations

Completed pilot and inference controls remain in [THREE_ARM_PILOT_REPORT.md](THREE_ARM_PILOT_REPORT.md), [PIXEL_FAILURE_ANALYSIS.md](PIXEL_FAILURE_ANALYSIS.md), [REENCODE_CONTROL_RESULTS.md](REENCODE_CONTROL_RESULTS.md). Those controls showed partial feedback/readout repair but weak final planning; this motivated the mechanism study. Do not substitute older checkpoints as matched new-arm results. Original pilot checkpoint integrity: storage `runs/pilot-checkpoint-retention.json`; control evidence `artifacts/reencode-control-20260915-r3/retention-verification.json`. Single-seed, post-hoc and short-horizon limitations remain. General scientific method superiority remains unresolved; the specified toy boundary is validated within its assumptions.
