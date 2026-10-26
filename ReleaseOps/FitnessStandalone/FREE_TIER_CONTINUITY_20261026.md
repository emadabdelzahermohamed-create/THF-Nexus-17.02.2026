# TopHeroFit continuity after paid ChatGPT access — 2026-10-26

## Objective
Keep Fitness development, physical QA, evidence, and Google Play delivery resumable even if paid ChatGPT capabilities disappear. GitHub is the durable source of truth; no step may depend on an ephemeral chat state.

## Zero-cost execution baseline
- Source/evidence: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026` plus exact commit SHA, PR, run ID, artifact digest, versionCode, and Play track readback.
- Device lane: authorized Android/Termux + ADB. Never erase app data or interrupt an active workout.
- Build lane: existing GitHub Actions Android runner and current repository workflows; reuse a passed run for unchanged SHA and never rebuild only to obtain another log.
- Release lane: existing Google Play Developer API, Workload Identity Federation, and Play-bound upload key path. No owner-funded build service is required.
- Local verification: Python/unittest, git, gh, shell checks, and available Android/ADB inspection.
- No paid AI/API/GPU/listing/builder dependency is part of the Fitness release path.

## Five durable lanes
1. **Activity Engine** — steps/walk/run/cycle, GPS, distance, pace/speed, valid calorie estimates, foreground/background service, persistent live notification and Stop.
2. **Health + Anti-Cheat** — Health Connect services, consent/partial grants/revoke/no-data, provenance/dedup, evidence fusion, spoof/anomaly rejection, privacy/Play scope reconciliation.
3. **Exercise Experience** — offline auto-motion, correct exercise mapping, Arabic/English guidance and voice, timer/lifecycle, accessibility, truthful catalog quality.
4. **Physical QA** — exact candidate only; safe preflight; in-place install/update; notification/background/GPS/Health/voice/crash evidence; no fabricated motion.
5. **Integrator + Play** — sole canonical/version/workflow/Play writer; combine meaningful tested deltas, issue one versionCode, build once, read back Internal, then promote only after real release gates.

## Anti-stall rules
- Read current canonical `RECOVERY` and live PR/branch heads before changing code.
- Do not repeat a PASS gate for unchanged bytes. Reuse exact run/artifact hashes.
- One blocker cannot stop the other disjoint lanes. Record it once, then switch to an unblocked release-relevant task.
- Keep file ownership disjoint; Integrator alone changes canonical release/version/Play state.
- Every material run must leave external evidence: tested commit/PR, build artifact, phone result, or Play state change. Status-only activity is not progress.
- Preserve last known good Play build and rollback information before any newer promotion.

## Paid-plan-loss handoff
If scheduled/agentic ChatGPT execution is no longer available after the account changes tier, do not recreate the project from chat history. Resume from this repository using the newest canonical `RECOVERY`, open Fitness PRs, and GitHub Actions/ADB evidence. The same five lane contracts remain valid as a manual or lower-capability execution queue.

## Release cadence
1. Workers finish isolated tested changes.
2. Integrator combines only compatible green changes.
3. Run source/product/backend verification and Android unit/lint/APK/AAB gate once for the exact SHA.
4. Allocate a new versionCode only for a meaningful green candidate.
5. Sign/upload exact AAB to Play Internal and independently read back committed version/track/source evidence.
6. Physical QA verifies the exact bytes without data loss.
7. Production remains blocked until all required device, policy, privacy, and Play gates are actually satisfied.

## Current transition
The 2026-10-26 last-day schedule has already been consolidated to these five Fitness lanes. Funding, games, WAVE, and unrelated work remain outside this release window. Current candidate work must continue from exact Git evidence rather than this document's prose if newer evidence exists.
