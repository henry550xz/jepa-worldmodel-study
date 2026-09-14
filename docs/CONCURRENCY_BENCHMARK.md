# Concurrency benchmark and pilot launch decision

**Decision: THREE-WAY training, followed by sequential common evaluation.**

Benchmark source `91886472be1263f884931b5f406d54ccd42901f5`; frozen FP32 batch32, seed0, episode partitions, architecture and optimizer unchanged. Each group used20 warmup updates then60 seconds of measured training, including data-loader wait. No benchmark evaluation/checkpoints; unique disposable manifests/logs preserved. All benchmark processes exited; GPU compute-process list was empty before pilot launch.

| Arm | Solo windows/s | Three-way windows/s | Solo training estimate h | Three-way training estimate h | Three-way allocated/reserved GiB |
|---|---:|---:|---:|---:|---:|
| pixel | 111.08 | 94.86 | 9.23 | 10.81 | 7.701/8.312 |
| gaussian | 111.88 | 96.35 | 9.16 | 10.64 | 7.810/8.131 |
| sparse | 114.68 | 94.82 | 8.94 | 10.81 | 7.810/8.131 |

Sequential-equivalent useful throughput: **112.52 windows/s** (harmonic mean because all arms process the same data budget). Measured simultaneous aggregate: **285.85 windows/s**, **+154.0%**. Do not compare concurrent aggregate with the sum of solo rates: those solo rates cannot occur simultaneously.

Training budget per arm:1,844,915 windows/epoch ×2 =3,689,830 windows;57,654 optimizer batches/epoch ×2 =115,308 updates (last batch19). Validation:53,507 windows/epoch; unchanged. Sequential training estimate27.33h total; three-way training makespan10.81h (~60% less elapsed training time). Estimates extrapolate a short interval and exclude startup, validation/checkpoint overhead and full common evaluation. Full evaluation time remains unmeasured; total queue ETA is therefore~10h49m training plus those unmeasured stages.

## Resource and stability evidence

| Group | Mean GPU % | Peak driver MiB | Process CPU cores | Host iowait % | Process disk-read MB/s |
|---|---:|---:|---:|---:|---:|
| solo-pixel | 33.8 | 9710 | 5.77 | 0.002 | 0.00 |
| solo-gaussian | 29.8 | 9526 | 5.84 | 0.181 | 0.00 |
| solo-sparse | 28.0 | 9526 | 5.84 | 0.003 | 0.00 |
| three-way | 82.7 | 28752 | 15.91 | 0.001 | 0.00 |

Three-way peak driver memory28,752/32,607MiB leaves3,855MiB (~3.76GiB) headroom. All arms had zero allocator retries and zero OOMs. Per-arm throughput decreased moderately while aggregate throughput rose strongly; no scientific settings were tuned. CPU includes benchmark process descendants (data loaders); host CPU/iowait metrics span the host, not just this project. Process disk-read counters exclude page-cache hits; read_chars includes pipes and is not treated as physical disk throughput.

Loader-wait fractions (solo → concurrent):
- pixel: 66.2% → 44.6%.
- gaussian: 61.1% → 39.4%.
- sparse: 60.6% → 39.4%.

The bottleneck was substantially input/CPU-side in the solo trials, not exhausted GPU compute. Three processes improved utilization while using the same four workers per arm. A nonfatal upstream NCCL shutdown warning appeared at benchmark exit; processes exited0 and no CUDA compute contexts survived. No drivers, CUDA installation, MPS settings, batch sizes, accumulation, splits or seeds changed.

## Launch validation and persistent execution

Before benchmarking, a full-path bug was found: matched bounded_steps=0 produced zero optimizer batches. The fix makes zero mean unlimited, implementing the already-frozen two-epoch protocol; it is not a change to that protocol. A regression test now verifies full train and validation traversal;30 worker tests passed. Frozen config, partitions and model/probe sources match the prepared protocol. This supersedes the earlier readiness claim that the full-path loop was already validated.

Authorized launch SHA: `fade5b690451efd23d5e428bcf5013c0e32a8aec`. Worker command: isolated env Python `-u -m study.concurrent_pilot --authorized-full-pilot`, launched in a detached session. The same lock and queue-directory guard exclude simultaneous sequential/concurrent launchers. Any training failure stops remaining owned processes and preserves artifacts. Evaluation waits for all training, then runs Pixel → Gaussian → Sparse sequentially, stopping on failure.

Controller systemd observer `jepa-pilot-monitor.service` never launches jobs. It records `/mnt/research/jepa-worldmodel-study-storage/runs/pilot-queue.json`, retrieves compact evidence and retries transport failures; scientific/code failures are surfaced without queue advancement. Worker state: `runs/three-arm-pilot-queue/queue.json`. No tmux dependency.

Raw benchmark evidence: `/mnt/research/jepa-worldmodel-study-storage/runs/concurrency-20260914T182614/`, including interval timing, per-arm manifests, CPU/I/O/GPU time series and logs. These measurements are execution benchmarks, not research results.
