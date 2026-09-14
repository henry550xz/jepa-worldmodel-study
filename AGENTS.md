# Project operating rules

`docs/CURRENT_PROJECT_STATUS.md` is the authoritative live handoff. Keep these rules project-local; do not change global Codex configuration.

## Long-running experiment workflow

Long-running training/evaluation jobs must use persistent background queues/monitors. Interactive Codex sessions must not remain open for hours waiting on jobs.

Whenever the user resumes and says **continue**:

1. Read the handoff and existing queue state.
2. Inspect the active background job and recent logs.
3. Verify progress is advancing; check for obvious errors, OOM, NaN and disk-space problems.
4. Do not launch duplicate jobs.
5. If a stage finished, verify its artifacts/results and let the existing queue advance to the next planned stage.
6. If it is running correctly, compute a fresh ETA from recent observed throughput. Separate measured training estimates from unknown planning time.
7. Keep intermediate progress in queue state and session reports. Update `docs/CURRENT_PROJECT_STATUS.md` once the authorized goal is finished; do not rewrite or commit the handoff on every check.
8. Report what is running, progress, health, ETA and the automatic next step.
9. If the remaining goal ETA is under five minutes, stay, check progress at intervals, verify completion/artifacts and deliver the final report. Otherwise exit while the persistent supervisor continues.

If infrastructure fails: preserve evidence, diagnose, repair and safely resume the existing queue within the authorized scope. Reconcile worker manifests/processes before retrying ambiguous launches; never repeat completed experiments. Reporting a recoverable error is not task completion. If a scientific stage fails, diagnose and apply protocol-preserving fixes where possible; document retries/deviations and do not skip failed stages. Stop only for a real unresolved blocker, recording the required next action. Exit once the persistent supervisor is demonstrably advancing the authorized queue, or a real blocker remains.

**The persistent monitor owns waiting. Interactive Codex owns checking, decisions, the final handoff and reporting.**

## Current infrastructure and boundaries

- Supervisor: controller systemd service `jepa-reproduction-queue.service`; no tmux dependency. Automatic infrastructure retries must be idempotent; scientific failures stop for diagnosis.
- Queue state: `/mnt/research/jepa-worldmodel-study-storage/runs/reproduction-queue.json`.
- Confirmed worker: `autodl-jepa`; workspace `/root/autodl-tmp/robotics/jepa-worldmodel-study/`.
- Read the live queue for the active run and immutable experiment SHA; never assume an old run ID is still active.
- Planned queue: Gaussian training → official planning → verified checkpoint retention → sparse training → official planning → verified retention → final reproduction report.
- Do not start pixel experiments or additional sweeps without user authorization.
- Verify `mountpoint -q /mnt/research` before controller writes. Keep large artifacts on project data storage, not `/`.
- Never expose credentials, dump full environments, modify `/root/.ssh`, or alter unrelated projects. Preserve working worker drivers/base packages.
- Run committed snapshots. Documentation-only handoff updates may advance controller HEAD without changing the active experiment snapshot. Commit/push instruction and handoff changes consistently with repository practice; the monitor may subsequently refresh its live section.

## Chronological handoff

Keep `docs/CURRENT_PROJECT_STATUS.md` chronological: scientific definition and immutable environment first, then concise validated milestones oldest to newest. Never prepend a new result or duplicate historical current-status blocks. Add new milestones immediately before the single final `## CURRENT / LATEST STATE` section. That final section must always be last and identify worker/queue state, latest validation, exact next action, immutable run SHA and pending items.
