# TopHeroFit — active integration ownership (2026-11-21)

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.  
Canonical branch: `agent/codex/fitness-recovery/20261023`.  
Canonical application HEAD: `b097d6ef0025d615c261ee42e8d2246533224e70`.

This registry supersedes the 2026-11-20 status snapshot. Shared files are not assumed free. Integrate only disjoint, exact-head-tested handoffs.

## Canonical owner boundaries

| Surface | Owner / state | Integration rule |
|---|---|---|
| Native GPS provider, ActivityTrackingService, distance accumulator, session checkpoint and GPS tests | PR #303 merged at `b097d6ef...`; exact source `26e90573...`, run 44929317705 PASS | Canonical native owner. New changes require rebase on current canonical and exact-head CI. |
| Legacy GPS / map-status/settings handoff | PR #284, Draft, 19 ahead / 94 behind, 13 files, no current-head CI | Native portions superseded by #303. Remaining app.js/index.html/MainActivity UI hunks conflict with active leases. Keep Draft; do not merge as-is. |
| Health Services bridge, MainActivity and AndroidManifest | PR #93, Draft; head `1cc08cef...`; 19 requested Health scopes vs canonical five | Hold. Remove unapproved scopes and rebase; no Heart Rate/clinical permissions without separate approval and policy gate. |
| Active workout resume/persistence UI | PR #216, Draft; head `1ef91588...`, based on noncanonical timed-RIR branch | app.js/index/styles shared with motion/program work. Rebase and isolate; no whole-file overwrite. |
| Active-workout offline motion demos | PR #224, Draft; head `cc703baa...`, based on gym-library branch | app.js/index/styles and motion manifest/library shared. Rebase and isolate. |
| GPS route display smoothing helper | PR #248, Draft; head `67d3b438...`, 4 ahead / 228 behind, no exact-head CI | Standalone Kotlin helper has no production call site. Canonical app.js already calls `smoothActivityRouteForDisplay()` for map presentation. Do not merge a duplicate/unused implementation; display-only, never a metric source. |
| Bilingual exercise catalog | PRs #160, #244, #252, #257, #259, #260 and related catalog branches | Shared exercises.js/json, manifests and builders. Integrate one semantically reviewed batch at a time. |
| Program semantics / timed RIR / workout UI | PRs #213, #234 and related program branches | Shared programs.js/json, app.js and builders. Rebase and test semantic parity; no blind stacking. |
| Favorites, equipment filters and program filters | PRs #253, #254, #256, #258 | Shared app.js/catalog/styles. Do not merge divergent branches wholesale. |
| ReleaseOps, version, workflows, signing and Google Play | Canonical integrator only | Sole writer. No parallel release/version/Play handoff. |

## Health and competition state

Merged Health changes: #282 metric truthfulness, #301 metric anomaly rejection, #304 cross-source metric reconciliation and #305 walking/running/cycling session reconciliation. The canonical Health Connect allowlist remains exactly five permissions: READ_STEPS, READ_EXERCISE, WRITE_EXERCISE, READ_DISTANCE and READ_ACTIVE_CALORIES_BURNED.

PR #269 competition backend is merged. The currently verified server metric is `strength_volume_kg_reps`; GPS activity is not reward-eligible. `ActivityEvidenceAnomalyPolicy.assessSegment()` is tested but still unwired in the live ActivityTrackingService. Do not claim full anti-cheat, location attestation or THF payouts.

## Current PR disposition (GitHub readback 2026-11-21)

- #303: closed/merged at `b097d6ef...`.
- #284: open Draft, stale/diverged, no exact-head CI; native logic superseded, UI hunks still shared.
- #93, #216, #224, #248: open Draft, not integrated.
- #160/#213 and catalog/program/motion/favorites PR families remain open and diverged across shared files.
- #269, #282, #304, #305: merged.
- Other older content/demo PRs remain open or closed according to GitHub; do not infer readiness from their existence or draft flag.

## Required integration protocol

1. Fetch current canonical HEAD and PR head; compare changed files and active ownership.
2. Reject any handoff that overwrites another lane's files or mixes release/version/workflow/signing/Play changes.
3. Rebase/isolate onto canonical and preserve tested source blobs where possible.
4. Run exact-head Product, source-contract, backend and Android API 36 unit/lint/build validation.
5. Download the exact artifact and independently rehash ZIP/APK/AAB; confirm embedded source SHA and signature state.
6. Merge only the exact tested head with expected-head protection.
7. Physical P0, owner API/key, privacy/policy, signing and Play gates remain separate from code merge.

No paid infrastructure, unrelated project or unverified external handoff is authorized.
