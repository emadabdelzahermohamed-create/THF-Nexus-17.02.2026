# THF + WAVE Large-Batch Delta — 2026-09-14 09:42 EET

Status: **ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING**

## New repairs completed

### 1. App physical-device evidence V3 now binds capture contents to exact release lineage
The app evidence path already required exact installed APK bytes, a physical non-emulator Android device, one bounded session, hash-bound evidence files and all registry-required checks. A remaining provenance gap allowed a hash-bound file's bytes to be unrelated to the structured PASS fields.

V3 closes that gap fail-closed. Objective and per-check capture files must now contain canonical machine-readable values bound to:
- session ID;
- package ID;
- exact candidate APK SHA-256;
- authoritative source SHA-256;
- exact check identity and PASS result;
- observation timestamp;
- for objective capture: installed APK SHA, approved hash method, installed code path and package-dump presence.

Duplicate fields, missing fields, wrong package/candidate/source/check, cross-session captures, capture-level FAIL disguised by structured PASS, or objective SHA/hash-method mismatch all block acceptance.

Relevant commits:
- `ad0e0152bc695481819407fc48d3a258206d0832` — initial V3 validator
- `ebb2d8902f3a42ee7a939b61f446921e4207157d` — initial V3 regressions
- `a3e0b42b78cb067df54e4cd4cf187278a1624a7a` — permanent V3 CI gate
- `1f4c8b1907f5f9ef0e0e935bb1ad6d915da18335` — source-SHA binding in validator
- `c56414ed403a160622616dde37346a85fce94308` — source-SHA negative/positive regressions

Final V3 run `34814473748` completed **SUCCESS**. Compile, V2 installed-byte regressions, V3 content/source provenance regressions, and pending-truth preservation all passed.

### 2. Core exact candidate is now bound to canonical source SHA
The app registry had Core APK `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba` with a null source SHA even though authoritative RC6 evidence identifies canonical source SHA `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`.

Commit `dbe3c762c6d2b8d2dd9a78501a7da415c2a44abb` repaired that provenance field only; package identity and APK candidate bytes did not change.

That registry repair automatically reran the affected gates and all completed SUCCESS:
- Cross-Stream Candidate Consistency V1 — run `34814408683`
- Apps Physical Evidence Registry V1 — run `34814408621`
- App Physical Device Evidence Tooling V3 — run `34814408717`
- Apps Factory State Gate — run `34814408667`
- App Physical Device Evidence Tooling V2 — run `34814408594`

## Preserved release truth

All ten app candidates remain `PENDING_PHYSICAL_PHONE`; no candidate was promoted by evidence tooling. No physical-device/GPU result was fabricated.

The game V8 evidence-provenance gate remains green and game candidate bytes/source lineage were unchanged in this batch; no identical-SHA rebuild was performed.

Production signing/signed AAB, Play Internal acceptance, stable production HTTPS/WSS and Cloudflare production cutover remain unproven/closed gates.

## WAVE isolation / blocker

WAVE RC14 remains isolated and NO-GO. WIF, gcloud, IAP tunneling, SSH-key generation and VM reachability have previously been proven; the blocker remains access to canonical `/root/workspace/wave-mawja` because OS Login maps CI to the service-account OS user instead of root.

Safe non-delegable resolution remains either:
1. a narrowly scoped approved OS Login admin path (`roles/compute.osAdminLogin`), or
2. preferably a service-account-owned release workspace cryptographically bound to the canonical root checkout/source manifest.

No SSH/OS Login weakening, broad Owner grant, older WAVE source substitution, production deployment or destructive cloud change was performed.

---
Body SHA-256 (all content above this separator, UTF-8): `2df16b5f7b6381d169f94b1d4bfa9c65d4af83c49f5f387b554a0ec42cfe554e`
