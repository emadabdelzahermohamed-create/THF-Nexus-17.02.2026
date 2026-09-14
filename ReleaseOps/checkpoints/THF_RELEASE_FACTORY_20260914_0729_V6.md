# THF Release Factory Checkpoint — 2026-09-14 07:29 Africa/Cairo

STATUS=NOT_FINAL
PHYSICAL_DEVICE_STATUS=PENDING
FINAL_OR_PLAY_READY=FALSE

## Material change
- Added Physical Device Evidence Validator V6.
- V6 extends V5 single-session binding by requiring objective ADB/runtime capture evidence and performance/FPS-RAM-thermal capture evidence to be real non-empty bundle files bound by SHA-256.
- This closes a tooling gap where typed JSON values for install/launch/PSS/framestats/thermal/FPS/RAM could satisfy structural validation without immutable capture files.

## Commits
- validator: 8619aea1814f20f6d68ea4ad4004c07c8f74d1f7
- regression tests: 291b87295ad910362a98f7619f645397f717bcc5
- workflow: 87276682609801c1a7b4dbc92cb31612452538b1

## Gate
- workflow: THF Game Physical Device Evidence Tooling V6
- run: 34806213981
- result: SUCCESS
- compile: PASS
- V5 session-integrity regression: PASS
- V6 capture-integrity regression: PASS
- release-truth preservation: PASS

## Policy truth
- No physical-device test was fabricated.
- No GPU/FPS/RAM/thermal observation was fabricated.
- No production-signed AAB, Play approval, production deployment, or stable production endpoint is claimed.
- Exact-candidate physical-device evidence remains required for all six game candidates.
- THF and WAVE remain isolated.
- WAVE canonical-source/OS-Login blocker was not bypassed in this checkpoint.

## TokenOps observation
- Historical run 34803820248 failed because its test fixture omitted token_program after the integration contract became stricter.
- Current main test_financial_control_plane.py includes token_program in the Vault/Forge/Core contract fixture, so the stale failure is not authoritative for current main.
- The historical run was not rerun because rerunning it would execute its historical SHA rather than current repaired main.

BODY_SHA256=cea4e42c5d061300e55a159f64e890b81730e7348096e997e86b13dced6dd6b1
