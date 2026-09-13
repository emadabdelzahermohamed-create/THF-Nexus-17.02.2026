# THF / WAVE Program Daily Checkpoint — 2026-09-13

Status: **NO PUBLIC ROLLOUT / SAFE PREPARATION ONLY**

This checkpoint records only reversible engineering, QA, release-preparation, and evidence work. No owner identity verification, paid spend, production/treasury signing, Play production upload, Cloudflare production cutover, or Solana financial action was performed.

## Completed / verified today

### THF Core RC6 — installability gate PASS
- GitHub Actions run: `34738496429` (`THF Core RC6 Installable QA APK`) — **success**.
- Canonical source SHA-256 before/after build: `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a` (unchanged).
- Package: `com.topherofit.thf.core`.
- Version: `6.2.2-rc6` / versionCode `62200`.
- minSdk: 26; targetSdk: 36.
- Launchable activity present: `com.topherofit.thf.core.MainActivity`.
- QA APK signed and verified with APK Signature Scheme v2 + v3.
- QA APK SHA-256: `d6c4844460e63f9219f3dc7ce95c4dbe424f846eac365a086d2a3eb3b41b13d0`.
- QA APK size: `45,768` bytes.
- Artifact: `THF-Core-RC6-INSTALLABLE-QA`, artifact ID `10311941633`.
- Isolation checks: `CORE_WAVE_ISOLATION=PASS`; canonical source mutation false.
- Explicit safety evidence: production signing/upload/cutover/Solana action all false.

Interpretation: **APK structure/signing/installability packaging gate is green.** This does not replace a physical-device install/launch/smoke test or Google Play Internal Testing validation.

### THF Terra RC34 — prior same-day installability evidence retained
- Installable QA pipeline was rebuilt and passed earlier on 2026-09-13.
- Package: `com.topherofit.thf.terra`.
- Version: `4.6.8-rc34` / versionCode `42068`.
- targetSdk: 36.
- APK signing verification: v2 + v3 PASS.
- QA APK SHA-256: `b45a1b461cf24bbe4eb7d8499ed15ab440df3ef1232c5c83e70759d89fa0ca31`.
- No production signing or public rollout was performed.

### Repository / operational review
- Earlier `main` head inspected: `2d335f3463f915ce47ad231cef11240c8d29d469` (`releaseops: add Core RC6 canonical-package installable QA gate`).
- `ReleaseOps/` contains current GCP/WIF inventory, Google Play roadmap, WAVE recovery inventory, compliance material, and RC intake evidence.
- Connected operational Drive evidence for WAVE/THF is older than today's GitHub build evidence in several places. Treat those older state files as historical until reconciled; do not regress newer installability evidence to an older blocked snapshot.

## Current blockers / gates

1. **Physical Android install + launch smoke test** still required for Core RC6 and Terra RC34 on at least one representative device. CI verifies package metadata/signing, not end-user installation behavior.
2. **Google Play Internal Testing** remains a separate gate. No production rollout should occur until install, launch, update path, signing lineage, and store-policy checks are confirmed there.
3. **WAVE evidence reconciliation** is needed: current connected WAVE operational documents predate today's Core/Terra evidence and still carry historical Play/signing/live-gate blockers. Refresh before using them as the master state.
4. **Rift current installability/runtime status** must be revalidated from the latest canonical artifact/runtime evidence before declaring release-ready; do not rely on older handoff snapshots alone.
5. **Production signing / owner-controlled credentials / treasury actions** remain intentionally out of scope for unattended work.
6. Node 20 deprecation warnings are present in GitHub Actions dependencies. They did not fail today's gates, but action versions should be refreshed in a controlled compatibility pass.

## Next executable safe tasks

- Reconcile WAVE current-state/critical-closure evidence against the newest GitHub commits and runtime artifacts; record superseded evidence explicitly rather than deleting history.
- Run/read-only validate Rift's newest APK/AAB metadata, signature, SHA-256, launchable activity, ABI/minSdk/targetSdk, and artifact provenance.
- Add a unified four-app Android QA matrix (Core / Terra / Rift / WAVE) covering package ID, versionCode, minSdk, targetSdk, launchable activity, signature scheme, SHA-256, device test, Internal Testing status, and blockers.
- Refresh the Google Play release roadmap from evidence only; keep Production rollout disabled.
- Update Actions dependencies away from deprecated Node runtimes after compatibility verification; no production deployment required.
- Preserve build artifacts/checksums and keep all changes rollback-safe.

## Release posture

**NO-GO for irreversible public rollout.**

Safe engineering and QA preparation can continue. Core RC6 packaging/installability is now evidence-backed green in CI; Terra RC34 has same-day installability evidence; WAVE/Rift and device/Internal-Testing closure remain required before any broader release claim.

---

## Latest verified addendum — runtime triad + artifact integrity

The older installability-only entries above are retained as historical evidence; the following newer evidence supersedes them for current runtime-candidate status.

### Core RC6 current runtime candidate
- Runtime-configured staging run `34743356308`: PASS.
- Candidate APK SHA-256: `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`.
- GitHub artifact ID `10312629324`, artifact digest/ZIP SHA-256 `ecb52d75fbc99960937f4e00ad2019ba3dbdc723296a76278ff0a7ebdcb916d9`.
- Downloaded artifact was unpacked into a disposable directory and APK SHA-256 independently recalculated: MATCH.
- `TRUTH.txt`: HTTPS service URL embedded, health PASS, targetSdk 36, production signing false, production cutover false, canonical mutation false, WAVE untouched.

### Terra RC34 current runtime candidate
- Runtime-fixed run `34752636192`: PASS.
- Candidate APK SHA-256: `388f3c09bd8e0d64ebb5ad5e9c10b92d3b17f05851949936a07fb5b3db5b18c7`.
- Canonical source SHA-256: `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`.
- GitHub artifact ID `10315967515`, artifact digest/ZIP SHA-256 `5b8d923366fd2ab4028f4acc1e42af4ab6a17a992183df898e026959eea43bda`.
- Independent artifact extraction/re-hash: MATCH.
- Godot payload PASS, `project.binary` present, assets=461, targetSdk 36, QA-only signing recovery, canonical mutation false, WAVE untouched.

### Rift RC37 current runtime candidate
- Runtime-fixed run `34752636187`: PASS.
- Candidate APK SHA-256: `fe35328b6ec4ed98a4c26cd5067e8056310fd773d9a3e7c3212943249eb024b1`.
- Canonical source SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`.
- GitHub artifact ID `10315992361`, artifact digest/ZIP SHA-256 `0de948ba21fe96e275c2ec459d95820202e4ba11c5fcdf54c49a03214323f0dd`.
- Independent artifact extraction/re-hash: MATCH.
- Godot payload PASS, `project.binary` present, assets=450, targetSdk 36, QA-only signing recovery, canonical mutation false, WAVE untouched.

### New release-control artifacts
- `ReleaseOps/Compliance/THF_ANDROID_ARTIFACT_INTEGRITY_CHECKPOINT_V1_20260913.md` records exact run/artifact/source/APK digests.
- `ReleaseOps/DEVICE_ACCEPTANCE_PROTOCOL_V1_20260913.md` makes physical-device evidence mandatory and binds it to exact APK SHA-256 values.
- `ReleaseOps/Compliance/THF_PLAY_DATA_SAFETY_PREFILL_V3_20260913.md` converts current technical data-flow evidence into a conservative Play Console preparation worksheet; it is explicitly not a legal submission.

### Current highest-priority blockers
1. Physical-device install/cold-launch/interactive acceptance remains P0 for the exact Core/Terra/Rift hashes above.
2. WAVE remains blocked on recovery of the exact RC13/RC14 canonical `/root/workspace/wave-mawja` runtime/source; older RC9 is not an acceptable substitute.
3. Stable production API hostname remains blocked pending separately authorized Cloudflare production cutover.
4. Privacy/Terms/deletion-retention wording and production security contact values still require owner/legal approval.
5. Production signing and any Play upload/publication remain closed gates until separately authorized.

Open PR review: PR #2 remains open/draft and isolated to TokenOps read-only work. No Solana transaction, signing, burn, transfer or authority mutation was performed.

---

## Release Factory addendum — WAVE RC14 canonical builder access (2026-09-13)

### Repair/checkpoint
- WAVE RC14 workflow was made self-contained in commit `070f9542ffa6d5df05ac9a53465ca976ad7c8d6f`; it no longer depends on an ad-hoc `$HOME/wave-rc13-remote.sh` or assumes passwordless sudo.
- The rerun (`34763097317`) proved WIF authentication, `setup-gcloud`, IAP TCP tunneling, SSH key generation and VM reachability are all functioning.
- GCP OS Login **rewrites an explicit `root@thf-wave-builder` request** to the mapped service-account OS user `sa_115575029018678177962`. The job therefore fails closed before reading or mutating `/root/workspace/wave-mawja` with `BLOCKER=CANONICAL_ROOT_OS_LOGIN_REQUIRED`.

### Exact remaining WAVE infrastructure requirement
One of the following owner/admin-controlled changes is required before unattended CI can verify canonical RC14:
1. Grant the release-builder service account an approved OS Login admin path (`roles/compute.osAdminLogin`) scoped as narrowly as practical; **or**
2. Preferably, expose a read/build-capable copy of the canonical WAVE checkout under a dedicated service-account-owned release workspace, with its source SHA/manifest bound to `/root/workspace/wave-mawja`, avoiding persistent root automation.

This is not a WIF/IAP outage and must not be repaired by weakening SSH, disabling OS Login, or granting broad project Owner permissions.

### Mobile Real-Function posture
- Core RC6, Terra RC34 and Rift RC37 retain exact-candidate CI/package integrity evidence above, but remain **NO-GO final** until the exact candidate hashes complete physical-device acceptance.
- WAVE RC14 remains **NO-GO** until canonical source/runtime access is restored, a real candidate is produced/inspected, stable production endpoints are validated, and exact-candidate phone evidence exists.
- No production signing key, Play approval, physical-device/GPU evidence, Cloudflare production cutover or public deployment is claimed by this checkpoint.
