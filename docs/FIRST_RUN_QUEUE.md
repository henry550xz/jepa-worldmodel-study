# Authorized first worker queue

Worker: autodl-jepa, RTX5090. Environment envs/lpwm-5090. Verified official dataset SHA256: 442f5dee246edf670964ed7bdecd248683cd6d00580fa0e4d458abb53f92da08.

1. Environment/import/CUDA smoke: passed; 21 worker correctness tests passed.
2. Gaussian tiny smoke: passed on snapshot 0f1720a0be0c73a98a16ce48936c052d7aaee3a6; run gaussian-s0-20260913T214005-c6af006c0be4. Two training batches plus two validation batches, B=2, first2 episodes, no long open-loop diagnostics. 10.424s process wall, 1,828,423,680 peak allocated VRAM bytes, 463,359,923-byte latest checkpoint. These are plumbing checks, not scientific reproduction metrics.
3. Sparse tiny smoke: passed, run sparse-s0-20260913T214117-05d8b6b356e8,10.354s process wall,1,829,343,744 peak allocated VRAM bytes; same bounded conditions.
4. Official Gaussian: seed0, 2 epochs, B64, 20 data workers, frameskip5, history3, D384, Deep-AdaLN, identity link, p2, RDMReg agg=b weight.5, muP LR1e-4. Then official planning seed99, 50 episodes, horizon/prefix5, CEM300 candidates/30 elites/30 iterations, max10 MPC replans.
5. Official sparse: same as Gaussian except reprelu link, p1, mu0. Then identical official planning protocol.
6. Only after both upstream runs are validated: pixel/Gaussian/sparse seed0 study pilot. No large sweep.

Official training dataset contains18,685 episodes,2,336,736 raw frames and1,981,721 sliced training windows. Validation:21 episodes,2,514 frames,2,115 windows. Each full reproduction requires30,965 batches per epoch (including partial final batch),61,930 total; this is a substantial run, not a tiny pilot. Preserve exact official counts; do not silently subsample to save rental time.

Wrappers emit unique run manifests and store large files under worker data disk. Record actual full-batch throughput before extrapolating total wall time. A full run failing VRAM requires an explicit disclosed strategy; reducing minibatch changes SWD reference estimation and is not automatically equivalent to gradient accumulation.
