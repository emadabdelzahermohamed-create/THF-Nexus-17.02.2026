# THF Nexus + WAVE_MAWJA Autopilot Checkpoint V8 — 2026-09-13

Status: SAFE PROGRESS / NO IRREVERSIBLE ACTIONS

## Inspected

- `main` current release-control state and recent commits.
- Latest successful Core/Terra/Rift candidate matrix and candidate SHAs.
- GitHub Actions state and new mobile-gate CI.
- Open pull requests: only PR #2, TokenOps read-only/draft.
- WAVE recovery evidence in Library; RC14 state exists but exact RC13/RC14 live workspace/source is still unavailable to this runner.

## Completed this checkpoint

1. Hardened `ReleaseOps/mobile/mobile_real_function_gate.py` so physical-device evidence is cryptographically bound to the APK under test:
   - gate recomputes APK SHA-256;
   - `exact_candidate_sha256` must match the computed APK SHA exactly;
   - offline/network transition evidence is mandatory;
   - Terra/Rift game source additionally requires touch-input evidence;
   - nested Godot project discovery is supported while requiring one unambiguous `project.godot`.
2. Added regression tests covering:
   - exact-SHA mismatch rejection;
   - exact-SHA acceptance;
   - Godot engine/template APK without exported payload rejection;
   - Godot payload acceptance;
   - sensor-landscape + expand + touch source contract;
   - network placeholder rejection.
3. Added GitHub Actions workflow `THF Mobile Real-Function Gate Tests`.
4. Verified workflow run `34760535595` completed SUCCESS; compile and unit-test steps both PASS.
5. Updated `ReleaseOps/ANDROID_QA_MATRIX_V1_20260913.md` with exact-SHA device-gate enforcement and current next sequence.

## Git evidence

- Exact-SHA gate hardening: `14df8c03c03be0fbbcd09043d0479bfa6e93a5ae`
- Gate regression tests: `a04f6b3db1f3455025eac0584965376bd7b0432a`
- Gate CI workflow: `00c34cb0025fcb6452074ef86b02489ac3bfdc26`
- Updated Android QA matrix: `a4330390a1a5ca38ab34c8dc876ea8014d15da67`

## Current exact Android candidates

| Product | Candidate SHA-256 | Package/runtime state | Mobile real-function state |
|---|---|---|---|
| THF Core RC6 | `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba` | API 36, HTTPS staging runtime/package PASS | BLOCKED pending exact-SHA physical-phone acceptance |
| THF Terra RC34 | `388f3c09bd8e0d64ebb5ad5e9c10b92d3b17f05851949936a07fb5b3db5b18c7` | API 36, Godot payload/package PASS | BLOCKED pending exact-SHA touch/orientation/gameplay/performance physical-phone acceptance |
| THF Rift RC37 | `fe35328b6ec4ed98a4c26cd5067e8056310fd773d9a3e7c3212943249eb024b1` | API 36, Godot payload/package PASS | BLOCKED pending exact-SHA touch/orientation/gameplay/performance physical-phone acceptance |

No candidate above may be labeled FINAL or PLAY_READY until its physical-device evidence passes the exact-SHA gate.

## WAVE_MAWJA isolation and blocker

- WAVE remains technically isolated from THF mutations.
- Library recovery found `WAVE_CURRENT_STATE_RC14.json` and earlier RC10/RC11/RC12 scripts, but not the exact full RC13/RC14 canonical source/workspace archive.
- RC14 state says the real `/root/workspace/wave-mawja` execution remains pending external Termux/runtime and lists that runtime as a blocker.
- Therefore `WAVE-LIVE-SOURCE-MISSING` remains active. Do not build from RC9/RC10/RC11 fallbacks or infer package identity from them.

## PR / financial safety

- PR #2 remains open and draft, scoped to TokenOps read-only controls.
- No Solana transaction, signing, burn, transfer, authority change, treasury mutation, or production signer operation occurred.

## Irreversible-gate status

Not performed:

- production Android signing;
- Google Play irreversible publication;
- Cloudflare production cutover;
- destructive GCP mutation;
- persistent cloud-key creation/use;
- canonical source overwrite/delete.

## Highest-priority next safe work

1. Preserve Core/Terra/Rift exact candidate SHAs and collect physical-phone acceptance evidence against those exact APK bytes.
2. Reject any phone evidence whose recorded SHA differs from the APK recomputed by the gate.
3. For Terra/Rift require sensor-landscape, touch interaction, responsive full-screen layout, player/avatar load, movement/camera/gameplay, background/resume, offline/network transition and FPS/RAM/thermal observations.
4. For Core require real HTTPS backend health/auth and real core-user journeys; placeholder/unconfigured-service screens are automatic FAIL.
5. Continue reversible compliance/Play preparation independent of the device gate.
6. Resume WAVE only when the exact RC13/RC14 canonical workspace/source becomes recoverable; SHA/identity verification must precede any build.
