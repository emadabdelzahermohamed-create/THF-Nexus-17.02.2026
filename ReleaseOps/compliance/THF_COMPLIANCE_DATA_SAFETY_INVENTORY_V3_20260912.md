# THF Compliance / Data Safety Inventory V3 — 2026-09-12

Scope: THF runtime only. WAVE_MAWJA is technically isolated and was not read or modified by the runtime probe.

## Evidence
- GitHub Actions run: `34694992123` (`THF Runtime Compliance Inventory V3B`).
- Result: **PASS** after correcting the inventory script so an empty filename match is evidence rather than a CI error.
- Access path: GitHub OIDC/WIF -> GCP -> IAP -> private builder `thf-wave-builder`.
- Persistent cloud keys: **not used**.
- Runtime root checked: `$HOME/thf-runtime-s1/runtime/THF_NEXUS_6_FINAL`.
- Runtime root presence: **PASS**.
- THF tree WAVE-path isolation: **PASS**.

## Policy resource inventory
The exact running THF tree contains **0 filename matches** for independent Privacy, Terms, account-deletion, or `security.txt` resources under `docs/`, `clients/`, and `config/`.

This confirms the earlier Compliance V2 observation that `/privacy`, `/terms`, and `/.well-known/security.txt` resolve through the generic SPA fallback rather than independent policy resources. HTTP 200 alone must not be treated as policy compliance.

### Status
- Technical policy-resource readiness: **FAIL / OPEN**.
- Publication-ready legal content: **BLOCKED-LEGAL-IDENTITY** until real operator/legal/privacy contact details are supplied and accepted for release.
- We must not fabricate those values.
- A reversible routing/resource patch may be prepared and tested before production, but public policy pages must not be represented as final until the approved legal content is bound.

## Route / deletion evidence
The probe found session deletion SQL and multiple relational `ON DELETE` persistence rules, but it did **not** find a dedicated public account-deletion route/resource in the exact running tree. Therefore account deletion remains an explicit Play release-readiness gap; database cascade semantics are not a substitute for the user-facing deletion workflow required by store declarations.

## Preliminary Data Safety surface inventory
These are lexical source-surface counts, not declarations of collection, sharing, retention, or purpose. They identify areas that require contract-level review before completing Google Play Data Safety:

| Surface keyword | Files matched |
|---|---:|
| health | 3 |
| fitness | 34 |
| location | 4 |
| camera | 8 |
| microphone | 1 |
| photo | 9 |
| video | 10 |
| media | 14 |
| advert | 3 |
| analytics | 5 |
| oauth | 0 |
| email | 0 |
| phone | 1 |
| wallet | 4 |
| token | 17 |
| notification | 0 |
| chat | 6 |
| message | 11 |
| profile | 6 |
| biometric | 0 |

These counts must be resolved into actual collect/share/purpose/retention/security behavior from route/service contracts before store submission. Keyword presence by itself is not evidence that data is collected or shared.

## Safety boundary
- Runtime mutation: **FALSE**.
- Production signing: **FALSE**.
- Google Play upload/publish: **FALSE**.
- Cloudflare production cutover: **FALSE**.
- Solana financial action: **FALSE**.
- WAVE_MAWJA touched: **FALSE**.

## Parallel release state
- Terra current canonical remains RC34 and already has proven Godot 4.7.2 / API 36 unsigned test-AAB evidence.
- Rift current canonical is now **RC42**, not RC37/RC41. RC42 source validation is already PASS, but exact RC42 package bytes are not currently addressable in Library/Drive staging. Do not downgrade release readiness to RC41 or reconstruct RC42 from older bytes.
- WAVE current persistent checkpoint remains RC14; its real live gate still requires the actual `/root/workspace/wave-mawja` runtime and remains independent of this THF probe.

## Next safe gates
1. Build a contract-level Data Safety matrix from exact THF route/service behavior (collection, local-only vs server persistence, sharing, purpose, retention/deletion).
2. Prepare a reversible policy-routing/resource patch that prevents SPA fallback from masquerading as Privacy/Terms/security.txt; keep final legal text values external until approved.
3. When exact Rift RC42 bytes become available, verify part SHAs and full SHA before fresh Godot 4.7.2 parser/import/headless + unsigned API 36 AAB export.
4. Continue WAVE independent checks without Cloudflare production cutover or production signing.
