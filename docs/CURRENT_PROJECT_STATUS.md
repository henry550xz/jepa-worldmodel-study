# Current project status

Working snapshot; research history is in [CHATGPT_RESEARCH_HANDOFF.md](CHATGPT_RESEARCH_HANDOFF.md). Updated 2026-09-15 after four-arm mechanism readiness gates and provisional CPU simulation.

## Scientific goal / project definition

Controlled study of temporal observation/pixel prediction versus Gaussian JEPA versus sparse JEPA for world models, initially PushT. We are testing WHETHER and WHEN JEPA helps, not assuming it must win. OGBench Cube, synthetic dynamics and potentially PDEBench are later work. This project is isolated from MARL, DA3, dehazing and old PushT projects.

## Environment and immutable baseline

- Checkout `/mnt/research/robotics/jepa-worldmodel-study`; storage `/mnt/research/jepa-worldmodel-study-storage`, both on mounted research volume. Branch `study/mechanisms`.
- Upstream `YilunKuang/lpworldmodel`, commit `bdd812d9432cccda8c350086006401b436f91982`; annotated tag `baseline/upstream-initial`. Origin `henry550xz/jepa-worldmodel-study`; upstream/main preserved.
- Worker `autodl-jepa`, RTX5090,32607MiB VRAM, driver595.71.05. Workspace `/root/autodl-tmp/robotics/jepa-worldmodel-study` on its50GB data disk. Dedicated `envs/lpwm-5090/bin/python`: Python3.12.3, PyTorch2.8.0+cu128, CUDA runtime12.8; base/drivers unchanged.
- Official PushT dataset SHA256 `442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08`, worker `datasets/pusht_noise`. Compatibility choices and full specifications are in manifests/conf/study and the reproduction report.

## Latest validated state and next action

Four mechanism configurations are implemented: standard teacher-forced Pixel, free-running rollout-reconstruction Pixel, Pixel+latent consistency, and Gaussian JEPA. **All bounded training and common-evaluation smokes passed; the full-run gate is closed.** No full runs launched. Configuration and definitions: [MECHANISM_EXPERIMENT_PROTOCOL.md](MECHANISM_EXPERIMENT_PROTOCOL.md), `conf/study/mechanism.json`; measured audit: [MECHANISM_READINESS_AUDIT.md](MECHANISM_READINESS_AUDIT.md).

Shared seed0, ViT384/AdaLN, batch32 FP32, history3/frameskip5, frozen partitions,6-frame windows/3 common target times, muP optimizer schedule, initial module hashes and first data batch hash verified identical. Fourteen tests passed; four real smokes each8 updates +2 validation batches; four common evaluator smokes each4 readiness episodes,6 horizons,1 candidate bank and2 replans, with temporal/cycle closure diagnostics. Smoke checkpoints are not research results.

Full-run blockers: exact compute is not equal (measured windows/s222.4/296.7/199.7/207.7 for Pixel/rollout/consistency/Gaussian), and teacher-forced versus free-running conditioning differs intentionally. Resolve the budget/conditioning interpretation before freezing a full protocol. Recommended primary design is matched windows/updates with explicit cost reporting; a compute-budget comparison would change update exposure. Draft horizon3 and auxiliary coefficient1 are declared choices, not tuned settings. No permission to launch full training follows from passed smokes.

Separately, `study/linear_gaussian.py` implements a provisional stationary state+nuisance rank-one prediction model.25 CPU-only cells and3 tests passed;43/43 cases away from the candidate boundary matched its analytic prediction. **The intended(beta,rho) theory is not supplied and correspondence remains blocked.** See [LINEAR_GAUSSIAN_PROVISIONAL.md](LINEAR_GAUSSIAN_PROVISIONAL.md); current beta=nuisance amplitude/rho=nuisance persistence are explicit provisional definitions, not an inferred user theory.

Exact next action: obtain intended beta/rho equations and review the compute/information audit with the user. Complete theory correspondence and budget decisions before any full-run preparation/launch. No active GPU job; no additional training authorized beyond completed bounded smokes.

## Environment, snapshots and retained evidence

Worker `autodl-jepa` observed idle after the evaluation gate (GPU0%,2MiB used); it was not shut down. Do not relaunch completed queues or trust historical process IDs. There is no active mechanism queue to resume.

- Training smoke snapshot `1ab94751e93e5f0e73cdab775db3400406323b9f`; evaluator snapshot `0e7c3f69f68f2d09c36654fa96d3876468092bb4`. Later config-wiring/instrumentation/documentation commits keep tested numerical settings but are not new trained snapshots.
- Controller `runs/mechanism-smokes-20260915-r2/state.json`, `audit.json`, `retention.json` under durable storage identify four run IDs and verified evidence. Per-run manifests, resolved YAML, telemetry, logs, probes and evaluation metrics retained. Disposable8-update checkpoints remain on worker; validated older research checkpoints remain retained on controller.
- Training peak allocated/reserved GiB: Pixel11.24/12.46, rollout7.77/8.41, consistency12.88/14.08, Gaussian11.36/11.90.24GiB+ recommended for sequential work pending longer profiling. No new concurrency assumption.
- Theory artifacts: storage `artifacts/linear-gaussian-provisional-20260915/results.json` and `phase-grid.png`.
- Initial80-update synthetic overfit criterion failed consistency arm;300 equal updates passed all arms without objective/threshold change. First evaluator prefix numerical assertion failed; consistent causal prefixes/per-step readout fixed it without retraining or loosening tolerances. Failed evidence preserved.

## Prior scientific results and limitations

Completed pilot and inference controls remain in [THREE_ARM_PILOT_REPORT.md](THREE_ARM_PILOT_REPORT.md), [PIXEL_FAILURE_ANALYSIS.md](PIXEL_FAILURE_ANALYSIS.md), [REENCODE_CONTROL_RESULTS.md](REENCODE_CONTROL_RESULTS.md). Those controls showed partial feedback/readout repair but weak final planning; this motivated the mechanism study. Do not substitute older checkpoints as matched new-arm results. Original pilot checkpoint integrity: storage `runs/pilot-checkpoint-retention.json`; control evidence `artifacts/reencode-control-20260915-r3/retention-verification.json`. Single-seed, post-hoc and short-horizon limitations remain. Full scientific method superiority and the exact requested theory boundary are unresolved.
