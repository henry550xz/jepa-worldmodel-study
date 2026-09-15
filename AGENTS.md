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

- Active pilot observer: controller systemd `jepa-pilot-monitor.service`; detached worker `study.concurrent_pilot` owns execution. The reproduction service is historical/completed. No tmux dependency; infrastructure retries must be idempotent, scientific failures stop for diagnosis.
- Active pilot state: `/mnt/research/jepa-worldmodel-study-storage/runs/pilot-queue.json`; worker `runs/three-arm-pilot-queue/queue.json`. Historical reproduction state: `runs/reproduction-queue.json`.
- Confirmed worker: `autodl-jepa`; workspace `/root/autodl-tmp/robotics/jepa-worldmodel-study/`.
- Read the live queue for the active run and immutable experiment SHA; never assume an old run ID is still active.
- Authorized active pilot: Pixel/Gaussian/Sparse seed-0 training concurrently, then common evaluation sequentially Pixel → Gaussian → Sparse. Frozen scientific protocol unchanged. No additional sweeps authorized.
- The three-arm seed-0 pilot above is already authorized, including Pixel and the queued common evaluations. Additional experiments, seeds, sweeps or changes to the frozen scientific protocol require new user authorization.
- Verify `mountpoint -q /mnt/research` before controller writes. Keep large artifacts on project data storage, not `/`.
- Never expose credentials, dump full environments, modify `/root/.ssh`, or alter unrelated projects. Preserve working worker drivers/base packages.
- Run committed snapshots. Documentation-only handoff updates may advance controller HEAD without changing the active experiment snapshot. Commit/push instruction and handoff changes consistently with repository practice. The monitor updates machine-readable queue state, not the Markdown handoff.

## Chronological handoff

Keep `docs/CURRENT_PROJECT_STATUS.md` chronological: scientific definition and immutable environment first, then concise validated milestones oldest to newest. Never prepend a new result or duplicate historical current-status blocks. Add new milestones immediately before the single final `## CURRENT / LATEST STATE` section. That final section must always be last and identify worker/queue state, latest validation, exact next action, immutable run SHA and pending items.


## Completion and authorization

The authorized pilot is complete only after all three arms finish the frozen training protocol, all required common evaluations finish and their outputs are validated, required checkpoints and compact evidence are retained on controller storage with integrity verified, and a final comparison report and project handoff are updated. A successful subprocess exit, queue launch or healthy background run is not completion of the research goal. Ending an interactive check while the queue runs does not mark that goal complete.

Continue authorized stages without requesting permission again. Recommendations, historical plans and results do not authorize new experiments. Repair recoverable infrastructure failures and apply validated protocol-preserving code fixes within existing authorization; preserve failed attempts and provenance, reconcile active runs before retrying, and never skip a failed scientific stage or silently change the frozen protocol. If completion requires a protocol change, additional resources beyond an explicit limit, or work outside authorization, report the blocker and the needed decision. Distinguish completed, failed, blocked and unrun work; do not label an incomplete pilot complete.

## Handoff roles and update timing

Use one authoritative Markdown handoff: `docs/CURRENT_PROJECT_STATUS.md`. Its milestone sections preserve concise chronological history; its single final `CURRENT / LATEST STATE` section is the working snapshot recorded at the last handoff update. Do not introduce a second overlapping handoff or adopt another project's snapshot/history split without user direction. Keep detailed protocols and results in linked documents rather than duplicating reports.

For routine continuation, read the final current-state section and live queue first, then relevant historical milestones only as needed. Timestamped progress, PIDs and ETAs in the handoff are historical observations, not proof of present process state. Verify them against live queue/processes/logs. Historical authorization does not override the latest user instruction.

Keep routine progress in the live queue and session reports. Update the Markdown handoff once the authorized goal is finished, or when the user explicitly requests a handoff/documentation update; do not rewrite it on every check. When updating, append newly validated milestones immediately before the final section, then replace that final snapshot in place. Preserve important provenance and negative results; do not duplicate prior current-status blocks. Identify the authorized next action separately from unapproved recommendations, and distinguish active immutable run SHA from later documentation commits.
