# THF + WAVE Large-Batch Release Checkpoint — Raw ADB Semantic Evidence

## Authority and unchanged candidate truth
- Run-start main authority: `277f6b6acc1a23fbae0ab7e793aae5c7480712fd` (`checkpoint(games): raw ADB transition evidence v12`).
- THF app candidate bytes were not changed in this batch. The authoritative apps registry remains 10 candidates, all `PENDING_PHYSICAL_PHONE`, with `final_or_play_ready=false`.
- THF game candidate bytes were not changed in this batch. Terra/Rift/Spark/Rush/Learn Games/Fitness Games remain `NOT_FINAL / PHYSICAL_DEVICE_PENDING`.
- No unchanged APK/AAB was rebuilt merely to manufacture a newer timestamp.

## Material finding
The prior raw-ADB evidence gates strongly bound raw files to the session, package, exact candidate SHA, source/registry lineage, physical-device fingerprint, ADB command, timestamp, exit code and summary SHA. However, the raw stdout payload itself was not semantically constrained enough: a metadata-complete but non-representative payload could satisfy the structural gate.

## Repairs implemented
### Apps — Physical Device Evidence V10
- `60fd52d4e80476c04385af748c0573cc92ff87cc` — semantic validator.
- `b750c9c7c9de93f01d5cb5af38720a88f1d4da25` — semantic regression coverage.
- `4bd6126a06e2f2d940003eab0d2a2c39ba6616db` — permanent CI gate.
- GitHub Actions run `34833866209`: SUCCESS.

V10 layers V9 and now requires a bounded raw stdout payload for every offline/local/online capture. Offline `dumpsys connectivity` evidence must be connectivity-shaped and must not contain a VALIDATED network; restored-online evidence must contain a VALIDATED network; local `uiautomator` evidence must contain a hierarchy/node for the exact candidate package. Missing bounds, wrong semantics, wrong package or contradictory connectivity state fail closed. V10 cannot self-promote FINAL/PLAY_READY.

### Games — Physical Device Evidence V13
- `3220428ebb687bef40a88b1d9fb09f9accb063b0` — semantic validator.
- `f3be5c64088fe22a77a6910a5eb4f4787cf1c271` — semantic regression coverage.
- `ff87784daa2d18d2d80c0a1fc1418d73ee18c2ed` — permanent CI gate.
- GitHub Actions run `34833956733`: SUCCESS.

V13 layers V12 with the same semantic anti-substitution property for game evidence. It preserves the exact package/session/SHA/device/timestamp chain while requiring the raw ADB payload to demonstrate the claimed offline, local-game UI and restored-online states. V13 cannot self-promote FINAL/PLAY_READY.

## Remaining non-substitutable Mobile Real-Function gate
No physical Android phone was available to this execution environment. Therefore no app/game was promoted. Exact installed-candidate physical sessions are still required for install, launch, touch, responsive layout/orientation/safe area, same-process background/resume, offline/network transition, core user journey and crash-free smoke. Games additionally still require avatar/player load, movement/camera/gameplay interaction and FPS/RAM/thermal observation. Notification receive/tap/background-resume evidence also remains physical/provider-dependent.

## Platform / runtime / Play posture
- Existing GCP evidence keeps the THF runtime health at PASS, release `6.0.0`, behind the established WIF + IAP/OS Login path.
- Stable production HTTPS/WSS and a fixed production Cloudflare hostname are not frozen; temporary Quick Tunnel evidence is not a production endpoint.
- Production signing, signed final AABs, Play App Signing/ownership, Internal-track acceptance, legal approval for final policy wording and public production deployment are not claimed.
- Public default SSH/RDP firewall rules remain recorded as a hardening finding; no consequential firewall mutation was performed in this batch.

## WAVE isolation
WAVE RC14 remains isolated. The known blocker is still `CANONICAL_ROOT_OS_LOGIN_REQUIRED`: WIF/IAP/VM reachability works, but OS Login maps CI to the service-account OS user and does not authorize canonical `/root/workspace/wave-mawja`. No SSH/OS Login weakening, broad Owner grant, old-source substitution or WAVE mutation was performed.

## Repository governance finding
The `main` branch is currently reported unprotected with required status-check enforcement off. This batch did not attempt an administrative branch-protection mutation. Repository owner/admin action is required to install a branch ruleset/protection policy requiring the release gates (including current app V10 and game V13) before merge/promotion while preserving an explicit emergency rollback path.

## Safety / isolation
No physical-device/GPU evidence, production signing, Play approval/upload, production deployment, Cloudflare production cutover, Solana/token mutation, canonical archive overwrite or WAVE source/runtime mutation was fabricated or performed.

Body SHA-256 (content above this line): `e8019216edda8de7354d7aa53a3c13c86fc34df0b29c2632ac1e08bcee19512a`
