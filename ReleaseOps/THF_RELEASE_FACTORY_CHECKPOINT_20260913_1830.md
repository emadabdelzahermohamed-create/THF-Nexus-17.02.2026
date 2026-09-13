# THF / WAVE Release Factory Checkpoint — 2026-09-13 18:30 EEST

Status: **NO-GO for public rollout; safe release-engineering advanced**

This checkpoint records reversible release/tooling/QA work only. No production signing, Play upload, Cloudflare production cutover, physical-device result, legal acceptance, billing action, Solana transaction, or destructive cloud mutation is claimed.

## Repairs completed in this pass

### 1. Small-games workflow definition repaired
- Previous run `34765736888` failed before creating any jobs because `.github/workflows/thf-small-games-source-audit-v1.yml` contained a malformed YAML/heredoc indentation boundary.
- Repair commit: `61349f37e5c7791a37a78be9a584e513f3e80f87`.
- Verification run: `34765849683` — workflow executes successfully through WIF/GCP and uploads evidence.
- Evidence artifact: `THF-SMALL-GAMES-SOURCE-AUDIT`, artifact ID `10320775762`, digest `sha256:7b343e09fae34b38f7a98e32e917da0b6cd2740ee542864248f24dbc2cbe842b`.

### 2. Mobile Real-Function hard gate added to Learn/Fitness Games
The successful descriptive audit exposed that the authoritative exact-SHA sources are not sufficient as playable mobile games:
- Learn source SHA-256: `dbd259b224924e60902fb0e1b2ebca77bc243e5f29a64d04fd3114438fd41484`; runtime markers: input=0, game_loop=0, player=0, placeholder=1.
- Fitness source SHA-256: `da3c865a76848c170d679547e05d6edbc0b5ffd6a48002b12ad0d26415fd0273`; runtime markers: input=0, game_loop=0, player=0, placeholder=1.
- Enforcement commit: `15d192c85295319f1ba9a2bebc9e4cc5c00762ca`.
- Verification run: `34765968724` — **FAIL as intended** in the real-function classification step; evidence upload still succeeds.
- Failure evidence artifact ID `10321080960`, digest `sha256:6a039180f5f88be89dda002e9b63c159c499e94457c8e2ff69a2092861ac55c9`.

Interpretation: source/archive integrity is valid, but these exact candidates are blocked from mobile-game release until a real interactive payload exists and later passes exact-candidate device evidence.

### 3. APPS-RC2 false-positive PASS closed
Run `34765737655` previously returned PASS even though all nine exact APPS-RC2 source archives were absent from the accessible service-account builder home:
- total=9
- source_missing=9
- built=0
- inspection_pass=0
- artifact ID `10320701495`
- artifact digest `sha256:6fae4e743fad5ff04f3bc7dced32644fbac70f5263cc88b10fcf9628b67d6fc4`

Truth-gate repair commit: `f17d74e021d291db3481e1e9ca005511eb3e6236`.
Verification run `34765907265` now **FAILS at Truth and safety gate as intended** unless all nine exact sources are found, built, signed for QA inspection, package-correct and targetSdk 36.

The promoted APPS-RC2 hashes are preserved in `ReleaseOps/portfolio/THF_APPS_RC2_I18N_HANDOFF_HARDENING_20260913.md`, but the exact archives are not currently present under the accessible service-account builder home. Do not substitute older APPS-RC1 or differently hashed archives.

## Current Android release truth
No regression was found in the previously proven runtime candidates:
- Core RC6 APK SHA-256 `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`, targetSdk 36.
- Terra RC34 APK SHA-256 `388f3c09bd8e0d64ebb5ad5e9c10b92d3b17f05851949936a07fb5b3db5b18c7`, targetSdk 36.
- Rift RC37 APK SHA-256 `fe35328b6ec4ed98a4c26cd5067e8056310fd773d9a3e7c3212943249eb024b1`, targetSdk 36.

All three remain **NO-GO FINAL** until exact-hash physical-device acceptance covers install, cold launch, touch, responsive layout/orientation, background/resume, offline/network transitions, core journey and crash-free smoke; Terra/Rift additionally require player/avatar load, movement/camera/gameplay and FPS/RAM/thermal observation.

Core's current runtime-configured candidate remains staging-only: its embedded endpoint class is `cloudflare_quick_staging`. This is not a stable production hostname and must not be relabeled production.

## WAVE RC14
WIF, GCP authentication, IAP tunnel and VM reachability remain working. WAVE RC14 remains blocked because GCP OS Login maps the CI service account to `sa_115575029018678177962`, which cannot read the canonical `/root/workspace/wave-mawja` checkout.

Safe closure requires either:
1. a narrowly scoped owner/admin-approved OS Login admin path; or
2. preferably a service-account-owned WAVE release workspace whose exact source SHA/manifest is cryptographically bound to the canonical root checkout.

Do not disable OS Login, weaken SSH, grant broad Owner, or substitute older RC9 source.

## Runtime / endpoint / cloud posture
- THF runtime local health remains PASS, release `6.0.0`.
- Temporary Cloudflare Quick Tunnel evidence exists but remains staging-only.
- No stable public production API hostname is currently frozen.
- Public default SSH TCP/22 and RDP TCP/3389 firewall rules remain a production-hardening finding and were not mutated without explicit authorization.

## Non-delegable / authorization gates
Continue to treat these as explicit blockers while advancing independent work:
- exact-candidate physical-device testing;
- production upload/signing keys and Play App Signing;
- Play Console ownership, legal declarations and publishing;
- Privacy/Terms/deletion-retention and production security-contact approval;
- stable Cloudflare production cutover;
- any GCP IAM/firewall mutation requiring owner/admin authorization.

## Safety
THF and WAVE remained isolated. No canonical source was overwritten. No production signing, Play upload, production deployment/cutover, financial transaction, or fabricated device/GPU evidence was performed.
