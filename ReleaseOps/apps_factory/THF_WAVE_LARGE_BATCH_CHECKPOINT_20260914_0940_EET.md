# THF + WAVE Large-Batch Release Checkpoint — 2026-09-14 09:40 EET

Status: **ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING**

## Authoritative state read first

- Current `main` before this batch was `a1165c74c0772c69ecd245c4ce94227e343109d0`, the games V8 evidence-provenance checkpoint.
- Games exact APK candidates and their source lineage were unchanged, so no candidate APK was rebuilt and no already-green identical-SHA gate was rerun.
- WAVE remains isolated. The last authoritative program checkpoint still records RC14 as blocked because GCP OS Login maps CI to the service-account OS user and cannot read canonical `/root/workspace/wave-mawja`; WIF, gcloud, IAP tunneling, SSH-key generation and VM reachability are not the blocker.
- No production signing, Play upload/approval, Cloudflare production cutover, Solana mutation, owner/legal acceptance, or physical-device claim was performed.

## New independent gap closed — app evidence capture contents were not provenance-bound

`validate_app_device_evidence_v2.py` already required:
- exact registered app candidate SHA-256;
- physical Android device / non-emulator truth;
- one bounded session;
- installed `/data/app/.../base.apk` bytes matching the exact registered candidate SHA;
- hash-bound objective and per-check evidence files;
- all registry-required checks PASS;
- no self-promotion to FINAL/PLAY_READY.

However, V2 did not require the *contents* of those hash-bound capture files to identify the same session/package/candidate/check. A caller could therefore hash arbitrary non-empty bytes and separately declare a structured PASS.

This batch introduced App Physical Device Evidence **V3**:
- `ReleaseOps/mobile/validate_app_device_evidence_v3.py`
- `ReleaseOps/mobile/test_validate_app_device_evidence_v3.py`
- `.github/workflows/thf-app-physical-device-evidence-tooling-v3.yml`

V3 layers on V2 and requires canonical machine-readable capture content.

Objective capture must uniquely contain and match:
- V3 schema marker;
- session ID;
- package ID;
- exact candidate SHA-256;
- installed APK SHA-256;
- approved hash method;
- exact installed code path;
- package-dump presence;
- objective observation timestamp.

Every required check capture must uniquely contain and match:
- V3 schema marker;
- same session ID;
- same package ID;
- same exact candidate SHA-256;
- exact check name;
- `RESULT=PASS`;
- the same observation timestamp declared in structured evidence.

Duplicate canonical fields, missing fields, cross-session captures, wrong package/candidate/check substitution, capture-level FAIL disguised by structured PASS, objective installed-SHA mismatch, and objective hash-method mismatch all fail closed.

## Regression evidence

Relevant commits:
- `ad0e0152bc695481819407fc48d3a258206d0832` — V3 validator
- `ebb2d8902f3a42ee7a939b61f446921e4207157d` — V3 negative/positive regressions
- `a3e0b42b78cb067df54e4cd4cf187278a1624a7a` — permanent V3 CI gate

GitHub Actions run `34814311302` (`THF App Physical Device Evidence Tooling V3`) completed **SUCCESS**.
The job passed:
- V2/V3 compilation;
- V2 exact installed-byte regressions;
- V3 capture-content provenance regressions;
- authoritative app registry truth preservation.

The registry remains 10 candidates, all `PENDING_PHYSICAL_PHONE`; `FINAL_OR_PLAY_READY=FALSE`.

## Release truth preserved / remaining blockers

This closes an evidence-integrity gap only. It is not phone evidence.

All apps/games remain NOT_FINAL until a physical Android phone executes the exact registered candidate bytes and records the required install, launch, touch, layout/orientation, background/resume, offline/network transition, core journey and crash-free evidence. Games additionally still require player/avatar load, movement/camera/gameplay and FPS/RAM/thermal observation as applicable.

Production signing/signed AAB, Play Internal acceptance, stable production HTTPS/WSS and Cloudflare production cutover remain unproven/closed gates.

WAVE remains isolated and NO-GO until canonical RC14 source/runtime access is available through a narrowly authorized admin path or a cryptographically bound service-account-owned release workspace. No SSH/OS Login weakening or older WAVE source substitution was performed.

---
Body SHA-256 (all content above this separator, UTF-8): `c0dffca19f5bca8bd248fca73d4b61c89cc3c646fa237b22326956b5f7d82ac7`
