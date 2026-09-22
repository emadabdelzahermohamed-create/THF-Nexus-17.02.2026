# THF Token Manager — Safe-planning v2 Web deployment evidence

Date: 2026-09-22
Scope: independent THF TokenOps / Token Manager only.

## Source authority
- Canonical branch: `token-manager-ar-v1-20260920`.
- Canonical merged Git SHA: `ecc2a7c5fe11ef6a6eef7cf36f4fea0edcdadc6a`.
- The four deployed files were compared against both the previous Git source and the merged source before deployment.
- The live source matched the previous Git source exactly before the update.
- After deployment, all four files match the merged Git source exactly:
  - `backend/index.ts`
  - `backend/tokenService.ts`
  - `src/TokenManager.tsx`
  - `tests/tests.json`

## Production deployment
- AppDeploy app: `thf-token-manager-yrh1nu`.
- Production snapshot: `1790082990998`.
- Terminal deployment state: `ready`.
- Production URL: `https://thf-token-manager-yrh1nu.v2.appdeploy.ai/`.
- QA timestamp: `1790083006936`.
- Web and mobile QA screenshots were produced.
- Reported runtime errors: frontend `0`, backend `0`, network `0`.
- AppDeploy did not return an automated E2E result for this deployment, so authenticated/in-depth E2E is not claimed.

## Verified safety behavior
- Live supply and mint-account reads are bound to a common confirmed anchor with `minContextSlot`.
- Contexts older than the anchor fail closed.
- Token amounts use exact 8-decimal integer base units; no JavaScript floating-point financial calculation is used.
- Review packets include a snapshot digest and a 15-minute expiry.
- The visible Arabic review packet states `Sign: لا`, `Broadcast: لا`, and external Multisig signing only.
- The deployed backend contains:
  - `executionAuthorized=false`
  - `transactionBytesCreated=false`
  - `externalSignerRequired=true`
  - `sign=false`
  - `signed=false`
  - `submitted=false`
  - `broadcast=false`
- Post-deploy scan found no transaction signing, transaction submission, SPL burn, or SPL transfer call surface.

## Gates
- Node unit tests: `8/8 PASS`.
- TypeScript syntax checks: PASS.
- Acceptance JSON parse: PASS.
- Non-execution boundary scan: PASS.
- High-confidence secret scan: PASS.
- GitHub Actions before merge: Safe Planning V2 run `35707288979` PASS; No Arbitrary Artifact Size Cap run `35707289016` PASS.

## Boundaries retained
- No burn, transfer, distribution, liquidity action, signature, or broadcast was executed.
- No private key, seed phrase, signing key, or signed transaction was introduced or accessed.
- TokenOps remains independent from Vault and Forge.
- No WAVE, Fitness, game, or other independent project source/deployment/configuration was touched by this deployment.
- This checkpoint is not `FINAL`, `PLAY_READY`, or proof of physical-device/service/account execution.

