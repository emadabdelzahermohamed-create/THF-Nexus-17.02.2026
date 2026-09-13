# THF Apps Factory checkpoint — 2026-09-14 02:07 EET

## Truth boundary

`FINAL_OR_PLAY_READY=FALSE`

Scope: THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass/shared identity, federation and cross-app handoffs. Dedicated native game streams and token finance excluded.

No production signing, public rollout, paid spend, owner verification, legal acceptance, treasury/token action, native-game mutation, or WAVE mutation was performed.

## Same-SHA skip discipline

Core RC6 and the nine runtime-bound Android exact-candidate package gates were not rebuilt or re-promoted: no regression evidence exists for their authoritative candidate SHAs. Their API 36/package/runtime evidence remains inherited from the prior authoritative state, and all physical-device gates remain PENDING.

## THF Pass — isolated HTTPS lifecycle/federation rehearsal

Added workflow: `THF Pass Private HTTPS Staging V1`.

- workflow commit: `a4f717258aa596cf09ce3fbf7694f6ffe67f8d3e`
- successful run: `34788521954`
- artifact: `THF-PASS-PRIVATE-HTTPS-STAGING-V1`
- artifact ID: `10327258382`
- artifact ZIP SHA-256: `01ab9c42a70b0a3975369b5debe7d628a3ade2cc6ff73863b978310256719a0b`

Immutable runtime baseline was verified before and after the rehearsal:
- `src/thf/app.py`: `471a8e0c6b67320386db6efcd32a3718265a645a30af3d7a9ea95060258058be`
- `src/thf/identity/service.py`: `8421a63db2e05bbd3b10b60da3edb0a3190ad7c2ea0498f4a1a704c3f7827b9f`

Exact disposable candidate hashes were re-bound and verified:
- `app.py`: `7f839cdba4307c5cd9a9aa258c4a3cdbf8bb55308f84ddda2b0217582ecc1ab2`
- `identity/service.py`: `36c9a173d394a9c2d19c931dbf8e89ab5478c27b197b278ce76b9b9b8286443c`

Private HTTPS execution used only loopback `127.0.0.1`, a temporary DB and an ephemeral self-signed certificate generated inside the disposable rehearsal. Proven over HTTPS:
- health: PASS;
- register/login: PASS;
- refresh token rotation: PASS;
- old/expired refresh rejection: PASS;
- logout revokes current session: PASS;
- revoke-all invalidates concurrent/handoff sessions: PASS;
- one-time audience-bound handoff exchange: PASS;
- wrong-audience handoff rejection: PASS;
- handoff replay rejection: PASS;
- existing HTTP/security/unified-runtime regression suite: PASS;
- deployed baseline hashes unchanged after test: PASS;
- rollback proof: PASS;
- public endpoint changed: FALSE;
- deployment performed: FALSE.

Interpretation: HTTPS transport plus lifecycle/federation semantics are now proven for the exact disposable Pass candidate in an isolated runtime. This is stronger than the prior plain-loopback rehearsal, but it is deliberately **not** externally reachable/stable staging evidence and does not promote the public/shared runtime auth state.

## Spark/Rush — remove NO-SOURCE false confidence

The exact authoritative RC3 source archives were first inventoried without mutation.

Inventory workflow/run:
- workflow commit: `150fff5e6c7e5c01210366935d008b1b5b64122d`
- run: `34788546294` — SUCCESS
- artifact ID: `10326729139`
- artifact ZIP SHA-256: `f1378f8381fc648f490cfa4a18c71cea2c8bf6dcec9e1b8d1748bdf29d6a5be5`

The inventory confirmed that neither authoritative archive contains an existing Python/Android source test suite. Therefore existing Gradle `NO-SOURCE` remains explicitly **not** a test PASS.

Authoritative source bindings used:
- Spark RC3 source SHA-256: `dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0`
- Rush RC3 source SHA-256: `bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b`

Added repository-controlled external regression packs that are executed against clean extraction of those exact SHA-bound archives, without changing the source ZIPs:
- Spark test pack commit: `3c18f9e628429c58a79d9e1f66df3f459fc850f8`
- Rush test pack commit: `8d7fc3f8b6d291a7d0ea54537e2a140199edf886`
- execution workflow commit: `c39137ad3c1a74b15e687617e3d1eaed780c8093`
- run: `34788612192` — both matrix jobs SUCCESS.

Spark real regression result:
- exact archive SHA verified before test: PASS;
- 6 real tests passed;
- deterministic seeded level behavior: PASS;
- real catalog/health behavior: PASS;
- unauthenticated score mutation fails closed: PASS;
- unauthenticated league mutation fails closed: PASS;
- unauthenticated AI proposal mutation fails closed: PASS;
- artifact ID: `10326439802`;
- artifact ZIP SHA-256: `8fef5838d9bc2335153a6c6de752597e2def3570e59d486b2322d978b4a12796`.

Rush real regression result:
- exact archive SHA verified before test: PASS;
- 6 real tests passed;
- health and anti-cheat capability contract: PASS;
- no-pay-to-win policy surface: PASS;
- anti-cheat truthfulness/privacy language: PASS;
- unauthenticated session mutation fails closed: PASS;
- unauthenticated league mutation fails closed: PASS;
- leaderboard read surface reachable: PASS;
- artifact ID: `10326564676`;
- artifact ZIP SHA-256: `078a786ac677b5d11415e549a1a8e1f49e0e5beb9abd4200e7f896a78edc4ce7`.

These are genuine executable regression tests against the exact authoritative sources. They do not rewrite history: the source archives themselves still contain no embedded tests, and the external packs do not constitute Android physical-device evidence.

## Remaining blockers and next safe autonomous work

1. THF Pass candidate is still not proven on a stable, externally reachable, non-public HTTPS staging endpoint with trusted TLS. Public/shared runtime `auth_flow` and `thf_pass_contract` therefore remain NOT_PROVEN.
2. App-specific notification/provider implementation remains absent across the nine authoritative app sources; shared notification contract exists, but `PUSH_READY=FALSE` remains correct.
3. Every exact Android candidate still requires physical-phone install/launch/touch/responsive-layout/orientation/background-resume/offline↔network/Data Saver/accessibility/RTL/core-journey/crash-free evidence bound to its exact APK SHA.
4. Production signing, signed AAB/Play Internal acceptance, legal/OAuth/owner/2FA actions remain later owner-controlled gates.
5. The Spark/Rush FastAPI test stack emits upstream TestClient deprecation warnings; tests are green, but dependency migration should be scheduled before the deprecated compatibility path becomes a build blocker.

Next autonomous block: preserve the exact candidate/package state, add a reproducible fail-closed external-test registry so Spark/Rush coverage cannot silently disappear, then advance notification implementation readiness that does not require provider credentials and prepare a stable private HTTPS Pass staging lane without changing the public endpoint.
