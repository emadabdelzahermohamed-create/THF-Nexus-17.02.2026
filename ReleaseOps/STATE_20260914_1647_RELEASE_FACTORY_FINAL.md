# THF + WAVE Release Factory Checkpoint — 2026-09-14 16:47 Africa/Cairo

Checkpoint body SHA-256 (all content below this line): `c24ec611eef2f279041bf10b224d459014f8472dd10b34462da69f790441d642`

## Material changes
- TokenOps fail-closed incident response was repaired on `main` so SHA-256 evidence and the immutable incident artifact are created/uploaded before a `FAIL_CLOSED_CRITICAL` result is enforced. Repair commit: `719772c0320b6d5c0cc4c2adfd9c67942c02d161`.
- TokenOps verification run `34850350267` completed `SUCCESS`. Current mode remains `READ_ONLY_DEGRADED`, with zero critical reasons and one degraded reason: `holder_concentration_unavailable`. No execution or financial effect occurred and WAVE was not touched.
- TokenOps evidence root SHA-256: `279034321a7e997b6e538749021e8d9972c0b568933c7b91076cf38d511991bb`.
- TokenOps source root SHA-256: `b451a1134ee8b049e97fe02ec0894223f16a346943f3d5fec759ac767d3e29be`.
- TokenOps immutable artifact: `THF-TokenOps-Incident-Response-v1-34850350267`, artifact ID `10351310112`, ZIP SHA-256 `e99bb30ffef8da74b6653cc43606209160e9b538782ef867fd2fc0138c271167`.

## App physical-device evidence V12
- PR #16 (`apps: bind physical-device evidence to Android boot session (V12)`) was repaired after its initial regression failure.
- Root cause: V12 iterated the entire production `FOREGROUND_CHECKS` constant in reduced regression fixtures instead of the authoritative-registry-active subset already used by V11. This caused a `KeyError` and also made the validator inconsistent with the layered V11 model.
- The V12 validator and fixtures were corrected without weakening production policy. Production CI separately asserts the complete foreground-policy constant and all ten authoritative app candidates.
- PR #16 merged to `main` as merge commit `1e7c4c6db291d1bcdf6a5875b8726838b138b966`.
- Main V12 CI was additionally hardened in commit `92c6fe13674ab4a9bf14fac32f4ea0c62c4d74db`: `actions/checkout` and `actions/setup-python` are pinned to exact commit SHAs and checkout no longer persists credentials.
- Main V12 verification run `34851293042` completed `SUCCESS`.
- V12 compile and regression chain V2 through V12 passed; V12 enforces Android boot provenance via `/proc/sys/kernel/random/boot_id`, hashes the canonical raw boot UUID, and binds active foreground process provenance to the same boot ID.
- Release truth from the gate remains `APP_CANDIDATES=10`, `PHYSICAL_DEVICE_STATUS=PENDING`, `FINAL_OR_PLAY_READY=FALSE`.

## Release truth retained
- Mobile Real-Function Release Policy remains a hard blocker.
- No exact-candidate physical-device acceptance, GPU/FPS/RAM/thermal evidence, signed AAB, Play approval, stable production HTTPS/WSS readiness, Cloudflare production cutover, or production deployment is claimed.
- No app/game candidate bytes were promoted by the tooling changes in this pass.
- TokenOps remains non-executable/read-only and no private key or on-chain financial action was used.
- THF and WAVE remained isolated; no WAVE source, permission, deployment, or runtime mutation occurred.

## Governance and non-delegable blockers
- Repository rulesets query returned no rulesets. Branch-protection details could not be read by the current GitHub integration (`403 Resource not accessible by integration`), so branch-protection enforcement is not claimed.
- Owner/admin verification is still required for protected `main` and required release checks.
- Exact-candidate physical-phone sessions remain required for install, launch, touch, layout/orientation, background/resume, offline/network transitions, core journey and crash-free smoke; games additionally require player/avatar load, movement/camera/gameplay interaction and FPS/RAM/thermal observation.
- Production signing keys / Play App Signing, Play Console ownership/legal acceptance, stable production endpoint ownership/DNS/Cloudflare cutover, and WAVE canonical-workspace access remain non-delegable or permission-gated.
