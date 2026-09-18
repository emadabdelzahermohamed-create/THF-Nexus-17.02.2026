# WAVE publication gate — 2026-09-18

Scope: WAVE_MAWJA only. THF/RuinsCiv untouched.

## Change
- Cloudflare auth/live-origin workflow updated at commit `ab208b43ddda67b28b50f2fc3fdbd25679d749b9` to run automatically on WAVE-branch publication-gate changes as well as manual dispatch.
- Gate checks `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, Cloudflare `/user/tokens/verify` active status, and HTTP 200/non-empty response from `https://wave-mawja.p-my.workers.dev/`.

## Observed blocker
After the workflow-file push, repository Actions API still returned `total_count: 0` for this WAVE branch. Therefore no claim is made that Cloudflare credentials passed. This indicates the workflow is not being scheduled from this non-default branch (or repository Actions policy prevents it); it is not evidence of a Cloudflare-token failure.

## Safety
No production deployment was attempted from an unexecuted gate. No THF/RuinsCiv files changed.
