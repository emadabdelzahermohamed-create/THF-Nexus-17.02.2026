# TopHeroFit continuity after paid ChatGPT access — 2026-10-26

## Objective
Keep Fitness development, physical QA, evidence, and Google Play delivery resumable when the ChatGPT account leaves Plus. GitHub is the durable source of truth; no step may depend on an ephemeral chat state.

## Verified ChatGPT Free scheduling constraints — checked 2026-10-26
OpenAI's current Scheduled Tasks documentation says eligible Free users can have at most **3 active scheduled tasks**. Free recurring tasks can run **no more than once per day** and use **flexible time windows**; hourly schedules and exact delivery times require an eligible paid plan. Therefore the five hourly Plus lanes are a last-day acceleration layout, not a valid long-term Free layout.

OpenAI's current Free-tier documentation also says Free keeps ordinary ChatGPT access including web search, data/file analysis, file/image upload and other tools subject to lower/separate limits. Do not assume paid Work/agent/browser capabilities remain available after downgrade.

Official references checked on 2026-10-26:
- https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt
- https://help.openai.com/en/articles/9275245-chatgpt-free-tier-faq

## Zero-cost execution baseline outside ChatGPT plan
These release assets are external to Plus and should remain the durable execution substrate as long as their own credentials/quotas stay valid:
- Source/evidence: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026` plus exact commit SHA, PR, run ID, artifact digest, versionCode, and Play track readback.
- Device path: authorized Android/Termux + ADB. Never erase app data or interrupt an active workout.
- Build path: existing GitHub Actions Android runner and repository workflows; reuse a passed run for unchanged SHA and never rebuild only to obtain another log.
- Release path: existing Google Play Developer API, Workload Identity Federation, and Play-bound upload key path. No owner-funded builder is required.
- Local verification: Python/unittest, git, gh, shell checks, and available Android/ADB inspection.
- No paid AI/API/GPU/listing/builder dependency is part of the Fitness release path.

## Five-lane Plus acceleration layout — 2026-10-26 only
1. **Activity Engine** — steps/walk/run/cycle, GPS, distance, pace/speed, valid calorie estimates, foreground/background service, persistent live notification and Stop.
2. **Health + Anti-Cheat** — Health Connect services, consent/partial grants/revoke/no-data, provenance/dedup, evidence fusion, spoof/anomaly rejection, privacy/Play scope reconciliation.
3. **Exercise Experience** — offline auto-motion, correct exercise mapping, Arabic/English guidance and voice, timer/lifecycle, accessibility, truthful catalog quality.
4. **Physical QA** — exact candidate only; safe preflight; in-place Play update; notification/background/GPS/Health/voice/crash evidence; no fabricated motion.
5. **Integrator + Play** — sole canonical/version/workflow/Play writer; combine meaningful tested deltas, issue one versionCode, build once, read back Internal, then promote only after real release gates.

## Free-tier three-lane consolidation
When the account is actually on Free and the five-hourly layout can no longer run, reduce to exactly three active daily flexible tasks. Preserve the five logical ownership contracts inside these three execution queues:

### Free Lane A — Core Activity + Physical QA
Daily flexible run. Own independent walking/steps, running, cycling, GPS, distance/pace/speed, calorie validity, foreground/background service and notification. Also perform safe read-only phone preflight and exact-candidate physical QA when the phone is idle/unlocked. Never sideload a differently signed build over a Play installation and never erase app data. If phone QA is blocked, continue activity-engine tests/code instead of idling.

### Free Lane B — Health/Anti-Cheat + Exercise Experience
Daily flexible run. Own Health Connect permission minimization, partial grants/no-data/revoke/provenance/dedup, anti-cheat/evidence contracts, and Play Health declaration/privacy reconciliation. In the same run, continue exercise offline motion/mapping, Arabic/English guidance/voice, timer/lifecycle, accessibility and catalog truth. Keep file ownership separated within the run and produce isolated commits/PRs when both areas change.

### Free Lane C — Integrator + Play
Daily flexible run. Sole canonical/version/workflow/Play writer. Read handoffs from A/B, integrate only compatible green changes, allocate one versionCode greater than the current verified baseline, build once, sign/upload exact AAB to Play Internal, independently read back the track, and update canonical recovery. Production remains fail-closed until real physical and policy/privacy gates pass.

## Current verified baseline for any post-Plus resume
- Google Play Internal baseline: `versionCode 51014`, `versionName 5.0.0-v2-alpha14`, package `com.topherofit.thf.pulse`, targetSdk `36`.
- Exact build source/workflow SHA: `50188b65efe335955d0296b67ac34465e5477a85`.
- Build run `40288559837`; promotion run `40289036989`; independent Play readback `40289183287`.
- Canonical integrated merge: PR #102 / merge commit `70263bb6965e794ec03dcf3811c3656dc6d46b54`.
- Current phone read-only ADB evidence on 2026-10-26 still shows Play-installed `51012`; 51014 physical propagation/runtime QA remains pending.
- Broad Health expansion PR #93 / #98 is build-proven but HOLD until exact Play Health declarations/privacy and physical Health verification are reconciled. Any future Health-expanded release must allocate a unique versionCode >51014.

## Anti-stall rules
- Read current canonical `RECOVERY_20261023.md` and live PR/branch heads before changing code.
- Do not repeat a PASS gate for unchanged bytes. Reuse exact run/artifact hashes.
- One blocker cannot stop the other disjoint ownership areas. Record it once, then switch to an unblocked release-relevant task.
- Integrator alone changes canonical release version/workflows/Play state.
- Every material run must leave external evidence: tested commit/PR, build artifact, phone result, or Play state change. Status-only activity is not progress.
- Preserve last-known-good Play build and rollback information before any newer promotion.
- Never purchase, upgrade, enable billing, or add a paid dependency merely to preserve automation throughput.

## Release cadence
1. Worker ownership areas finish isolated tested changes.
2. Integrator combines only compatible green changes.
3. Run source/product/backend verification and Android unit/lint/APK/AAB gate once for the exact SHA.
4. Allocate a new versionCode only for a meaningful green candidate.
5. Sign/upload exact AAB to Play Internal and independently read back committed version/track/source evidence.
6. Physical QA verifies the exact Play-delivered bytes without data loss.
7. Production remains blocked until all required device, policy, privacy, and Play gates are actually satisfied.

## Transition rule
Keep all five Fitness-only hourly lanes active for the remaining Plus window on 2026-10-26. Once Free limits are actually in force, the target state is the three daily flexible lanes above, not five hourly tasks. If ChatGPT scheduling becomes unavailable or existing tasks are paused during the tier transition, do not reconstruct state from chat history: resume from this repository manually or with whatever eligible Free tasks remain, using the same three-lane ownership map and the latest canonical evidence.
