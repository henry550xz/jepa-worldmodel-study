# Project operating rules

Keep these rules project-local and durable. Record active scope, worker/environment, services, queue paths, run IDs, immutable SHAs and current authorization in `docs/CURRENT_PROJECT_STATUS.md`, not here. Do not change global Codex configuration.

## Infrastructure and boundaries

- The controller checkout is canonical. Use project-specific helpers and explicit worker selection from current status; verify paths, artifacts and capacity before a run. Never assume a worker switch migrates evidence or environments.
- Verify `mountpoint -q /mnt/research` before controller writes. Keep large artifacts on project data storage, not `/`.
- Never expose credentials, dump full environments, modify `/root/.ssh`, or alter unrelated projects. Preserve working worker drivers/base packages. Synchronization must not delete remote-only evidence or transfer credentials.
- Run committed snapshots. Documentation commits do not change an active immutable experiment snapshot. Never launch duplicate jobs or repeat completed experiments.
- Commit/push documentation and instruction changes consistently with repository practice. Machine-readable queue updates are distinct from human-maintained Markdown documentation.

## Long-running experiment workflow

Long-running training/evaluation jobs must use persistent background queues/monitors. Interactive Codex sessions must not remain open for hours waiting on jobs.

Whenever the user resumes and says **continue**:

1. Read the current snapshot, latest research handoff entry and existing queue state.
2. Inspect the active background job and recent logs.
3. Verify progress is advancing; check for obvious errors, OOM, NaN and disk-space problems.
4. Do not launch duplicate jobs.
5. If a stage finished, verify its artifacts/results and let the existing queue advance to the next planned stage.
6. If it is running correctly, compute a fresh ETA from recent observed throughput. Separate measured training estimates from unknown planning time.
7. Keep routine progress in queue state and session reports. After a validated experiment or major research decision, update both documentation files under the Documentation rule below.
8. Report what is running, progress, health, ETA and the automatic next step.
9. If the remaining goal ETA is under five minutes, stay, check progress at intervals, verify completion/artifacts and deliver the final report. Otherwise exit while the persistent supervisor continues.

If infrastructure fails: preserve evidence, diagnose, repair and safely resume the existing queue within the authorized scope. Reconcile worker manifests/processes before retrying ambiguous launches; never repeat completed experiments. Reporting a recoverable error is not task completion. If a scientific stage fails, diagnose and apply protocol-preserving fixes where possible; document retries/deviations and do not skip failed stages. Stop only for a real unresolved blocker, recording the required next action. Exit once the persistent supervisor is demonstrably advancing the authorized queue, or a real blocker remains.

**The persistent monitor owns waiting. Interactive Codex owns checking, decisions, the final handoff and reporting.**

## Completion and authorization

An authorized research goal is complete only after all requested experiments and evaluations finish, outputs are validated, required checkpoints and compact evidence are retained on controller storage with integrity verified, and the required report and both documentation files are updated. A successful subprocess exit, queue launch or healthy background run is not completion of the research goal. Ending an interactive check while the queue runs does not mark that goal complete.

Continue authorized stages without requesting permission again. Recommendations, historical plans and results do not authorize new experiments. Repair recoverable infrastructure failures and apply validated protocol-preserving code fixes within existing authorization; preserve failed attempts and provenance, reconcile active runs before retrying, and never skip a failed scientific stage or silently change the frozen protocol. If completion requires a protocol change, additional resources beyond an explicit limit, or work outside authorization, report the blocker and the needed decision. Distinguish completed, failed, blocked and unrun work; do not label an incomplete study complete.

## Documentation

After every validated experiment or major research decision, update BOTH:

    docs/CURRENT_PROJECT_STATUS.md
    docs/CHATGPT_RESEARCH_HANDOFF.md

The two documents have DIFFERENT roles; do not duplicate a research diary in both.

### Current status: concise working snapshot

`docs/CURRENT_PROJECT_STATUS.md` contains only what a future agent needs to work
safely now: active scope, latest validated state, authoritative artifact links,
important limitations, blockers, worker/environment and resume details, and the
exact next authorized action. Distinguish recommendations from authorization.
Rewrite/update this snapshot in place as circumstances change. Remove obsolete
progress notes from the snapshot, preserving any unique history in the handoff
or a linked immutable archive first. Do not accumulate dated historical entries.

### Handoff: append-only chronological research history

`docs/CHATGPT_RESEARCH_HANDOFF.md` is ordered OLDEST TO NEWEST. Append each new
dated entry at the BOTTOM so the last entry is the most recent. Record the
experiment, exact configuration, artifact/provenance links, validated results,
interpretation, failures/limitations, blockers, decision, and recommended next
experiment (including whether authorized). Preserve past entries and negative
results; add dated corrections/superseding decisions rather than rewriting old
findings. Historical instructions describe their time and do not authorize
resuming old experiments. Do not prepend new entries or duplicate entire reports.

### Reading and preservation

Read the current snapshot first, then a bounded tail of the research handoff;
retrieve older entries only as needed. Verify timestamped process observations
against live queue/logs before acting. Routine unchanged progress checks do not
require a documentation entry. Maintain this one authoritative pair; keep detailed
protocols and results in linked reports. Before historical reorganization, retain
and verify a byte-identical archive. Archives preserve evidence and are not an
additional instruction source.
