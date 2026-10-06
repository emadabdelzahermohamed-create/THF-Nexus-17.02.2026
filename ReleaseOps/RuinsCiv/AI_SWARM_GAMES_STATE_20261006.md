# RuinsCiv — AI Swarm Games State (2026-10-06)

## Canonical execution baseline
- Lane branch: `agent/gpt-games/ruinsciv-20261006`
- Base branch: `automation/ruinsciv-android-qa-20260922`
- Verified base SHA: `4d009d73ce3031266e5658b8c924178c804c1f1b`
- Base commit states: **source recovery and Android QA provenance gates are green**; QA-only signing boundary is preserved; physical-device evidence remains pending.
- Engine/package contract: Godot 4.7.2, Android API 36, arm64-v8a, QA package `com.topherofit.ruins.civ.phoneqa`.

## Reconciliation versus stale main backlog
`main:ReleaseOps/RuinsCiv/RUINSCIV_UNIFIED_BACKLOG_V1_20260918.json` predates the 2026-09-22 verified QA/provenance merge. Therefore do **not** repeat P0 source-recovery/provenance work that is already proven green at SHA `4d009d73...`.

## Current gates
| Gate | State | Evidence / boundary |
|---|---|---|
| Source recovery / provenance | PASS | verified in base commit `4d009d73...` |
| Android QA provenance | PASS | verified in base commit `4d009d73...` |
| Production signing | NOT CLAIMED | QA-only ephemeral signing boundary; no production key access |
| Physical Android runtime | PENDING | install/boot/touch/camera/movement/GPU/FPS/RAM/thermal evidence required |
| Visual/avatar runtime | PENDING EVIDENCE | metadata/asset presence alone is not visual PASS |
| Production / Play | NOT CLAIMED | blocked behind exact-candidate runtime + production signing/release gates |

## P0 next task
Obtain exact-candidate physical Android runtime evidence for the already-proven QA lineage. Validate install, boot, touch controls, camera, locomotion, representative animation transitions, avatar/world rendering, GPU/FPS/RAM/thermal behavior, background/resume and crash-free core journey. Do not churn versions or rebuild provenance unless the exact candidate/source changes.

## Visual/motion acceptance
The candidate must retain the approved modern MPFB/MakeHuman lineage (137+ joints / 195+ clips where applicable), exclude `thf_humanoid_v1..v6` from active export, and provide runtime evidence for clean idle/walk/run/action blending, foot-contact/anti-sliding behavior where supported, usable camera framing, coherent PBR/lighting/shadows/weather, and representative mobile performance. A file inventory is necessary but not sufficient for PASS.

## Blocker policy
If no authorized physical Android device is reachable, record **PHYSICAL_DEVICE_EVIDENCE_PENDING** once and move to the next independent release-critical game task. Do not weaken the gate and do not substitute emulator/static metadata for phone evidence.
