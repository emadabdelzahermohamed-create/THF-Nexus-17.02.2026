# THF + WAVE Large-Batch Release/QA Checkpoint — 2026-09-14 02:00 EET

## Truth boundary
- FINAL_OR_PLAY_READY=FALSE.
- No physical-device/GPU QA, production signing, signed AAB, Play approval, or production cutover is claimed.
- WAVE remains isolated from THF.
- Mobile Real-Function Release Policy remains a hard blocker until exact-candidate physical-device evidence exists.

## Starting authoritative state
- Games checkpoint: `ReleaseOps/games_factory/THF_GAMES_LARGE_BATCH_CHECKPOINT_20260914_0130_EET.md`.
- Apps checkpoint: `ReleaseOps/apps_factory/THF_APPS_FACTORY_CHECKPOINT_20260914_0108_EET.md`.
- Program/WAVE evidence: `ReleaseOps/THF_WAVE_LARGE_BATCH_20260914_0030_EVIDENCE.md`.
- Runtime source authority SHA-256 remains `6abec6481f40272f6a847e8da4ef6890243d55243e6d88d806cde6bfa97ac046`.

## Material repair performed
The prior `THF Game Backend Authority Static V2` gate failed because the diagnostic parser assumed ordinary route registration and could not associate sensitive paths inside the custom `_api/_dispatch` dispatcher with HTTP mutation methods. WIF/OIDC, GCP auth, IAP and builder SSH had succeeded; this was a tooling blind spot, not proof of an application or infrastructure failure.

1. Commit `231ecf9ef69c12a9d1ffc2d1a9b6c77f745829c9`
   - `fix(games): make authority audit registration-shape aware`
   - Follow-up run `34787132790` remained fail-closed and proved five sensitive route contexts, but methods were still unresolved.
   - Diagnostic artifact SHA-256: `a51993fa77eaf135a595d7d0f2127d6d394680c60bf6b15b0d2aab67753c3d23`.

2. Commit `2cd70e41b862e9b1848010acebc1badb06546db6`
   - `fix(games): resolve custom dispatcher HTTP methods by call graph`
   - Added conservative call-graph propagation from `do_GET/do_POST/do_PUT/do_PATCH/do_DELETE/...` into dispatcher helpers without weakening the fail-closed gate.
   - No product runtime, host, secret, or WAVE source was modified.

## Verification
Final rerun `34787225217`: SUCCESS.
- WIF/OIDC -> GCP: PASS.
- IAP/SSH -> builder: PASS.
- Sensitive route contexts: `5`.
- Sensitive mutation routes: `5`.
- Unknown method contexts: `0`.
- Handler auth-guard signals: `5`.
- Handlers without local guard signal: `0`.
- `DYNAMIC_AUTHORITY_PROOF_REQUIRED=YES`.
- Artifact ID: `10326538143`.
- Artifact ZIP SHA-256: `bc74679ffc5e9a62f03426ca0fde0376ca3dc6e03683d5ae1fdc35f825dfac70`.

Interpretation: the static authority-audit tooling blocker is RESOLVED. This is not a security acceptance. Dynamic fail-closed tests must still prove that unauthorized sensitive mutations cannot change authoritative state, including token/session failure paths and replay/invalid authority cases.

## Candidate integrity
No authoritative candidate SHA regression was observed in this pass. Exact physical-device candidates remain:
- Terra: `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift: `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark: `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush: `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games: `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games: `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`
- Core MobileFix1: `507c47676445bfe0e7b54bc4005369315df365967f83e2717b055db268c58f8e`

## Remaining hard blockers
- Exact-candidate physical-device acceptance for every app/game remains PENDING.
- Production signing / signed AAB / Play Internal approval remain NOT PROVEN.
- Stable production HTTPS/WSS endpoint/cutover remains NOT PROVEN; Quick Tunnel evidence is staging only.
- Dynamic authoritative-mutation rejection proof remains required for game backend security.
- WAVE RC14 remains blocked by CI OS Login access to canonical `/root/workspace/wave-mawja`; WIF/GCP/IAP are operational. Do not weaken OS Login/SSH or substitute older WAVE sources.
- User-only signing keys, legal acceptance, Play ownership/console actions, 2FA/OAuth/billing, and physical-device actions remain non-delegable where applicable.

## Next safe autonomous work
Advance dynamic game authority rejection tests against an isolated/non-production target, continue exact-hash endpoint/runtime evidence and Play/compliance preparation, while preserving THF/WAVE isolation and keeping all FINAL gates fail-closed.

Evidence body SHA-256 (checkpoint text before this self-describing line): `43c2e9cd7da328b48cac21116714c43dc3d00048e11a2ae5708c4bc715ab24d5`
