# WAVE MAWJA — GCP Builder Probe (2026-09-12)

Scope: WAVE only. THF source/release artifacts were not modified.

## Inputs and authority
- Latest persistent WAVE checkpoint reviewed: RC14-ONE-COMMAND-LIVE-GATE.
- RC14 requires the canonical runtime path `/root/workspace/wave-mawja` and explicitly leaves real runtime execution external until that workspace is present.

## GitHub/GCP execution
- Branch: `w/r1`
- Workflow: `WAVE RC13 Builder Verify`
- Run 1: 34665523033 — CI quoting failure before any remote WAVE command; WIF itself passed.
- CI fix commit: `6e9598005c77ec4598ae51b1d2e90352d565f94a` — remote verifier transferred as a standalone script to avoid nested shell quoting.
- Run 2: 34665606559
  - GitHub checkout: PASS
  - GCP WIF auth: PASS
  - gcloud setup: PASS
  - IAP/SCP transfer to builder: PASS
  - IAP/SSH execution: PASS
  - WAVE canonical workspace identity: BLOCKED — `/root/workspace/wave-mawja` is absent on `thf-wave-builder`; verifier exited 21 with `WAVE_PROJECT_MISSING` before reading or modifying WAVE source.
  - Evidence manifest/upload: PASS
  - Evidence artifact id: 10289096464
  - Evidence artifact ZIP SHA-256: `89c50373a02af56fbaf282d2be14d28ef555ad5f7c4626a2d9077d95201bf00e`
  - Builder log SHA-256: `3fb44ddfd05baf918d335c70db8f8e314bdd7bd797f8921189770a34033b0fba`

## Safety / truth boundary
- No Cloudflare deploy.
- No content import.
- No production signing or Play upload.
- No media transcode claim.
- No THF mutation.
- No persistent cloud key used; WIF/IAP path only.

## Next safe action
Stage an authoritative full WAVE source/runtime workspace onto an isolated GCP path or execute RC14 in the existing Termux/Ubuntu `/root/workspace/wave-mawja`. Do not substitute the small RC14 gate bundle for the full WAVE source tree. Once the canonical workspace is present, rerun the verify-only gate, collect source/typecheck/build/Worker/Android evidence, and proceed to physical-device and external media/Cloudflare/Play gates separately.
