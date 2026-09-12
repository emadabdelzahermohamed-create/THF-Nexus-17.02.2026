# THF Runtime Compliance V2 — 2026-09-12

Status: FAIL-POLICY-CONTENT
Scope: THF runtime only. WAVE_MAWJA remained untouched.

## Evidence

- Workflow: `THF Runtime Compliance Probe V2`
- Run: `34691838066`, retry attempt after one transient WIF/gcloud connection reset.
- Branch: `cp/v2`
- Gate commit: `1aa941fdeb136324d136d6ee9ca44e1785bdadbb`
- WIF authentication: PASS
- GCP/IAP runtime access: PASS on retry
- Local `/health`: PASS, release `6.0.0`
- External `/health`: PASS, release `6.0.0`
- Required headers: CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy — PASS

## Policy-content finding

The earlier route-existence probe was insufficient because it only checked HTTP reachability. The stricter V2 semantic gate proved these public paths currently resolve to the same SPA fallback body:

- `/privacy`: 15702 bytes, SHA-256 `8f2f118bf6890dc50babff369116523cb00fd6b1f1e343bb6d0cd43773c7b7ca`
- `/terms`: 15702 bytes, SHA-256 `8f2f118bf6890dc50babff369116523cb00fd6b1f1e343bb6d0cd43773c7b7ca`
- `/.well-known/security.txt`: 15702 bytes, SHA-256 `8f2f118bf6890dc50babff369116523cb00fd6b1f1e343bb6d0cd43773c7b7ca`

V2 failed first on `privacy content marker missing`; the identical hashes independently prove the routes are not distinct policy/security resources. `security.txt` must also be served as a real text resource with at least `Contact:` and `Expires:` fields before the compliance gate can pass.

## Classification

This is a runtime/static-routing compliance blocker, not a WIF/IAP blocker and not an Android/Godot build regression. Existing Core/Terra/Rift unsigned/test AAB PASS checkpoints remain valid as test candidates.

## Next safe action

Add real, distinct Privacy and Terms resources to the THF runtime/static route map and a standards-oriented `/.well-known/security.txt`, then rerun V2. Do not use the temporary Quick Tunnel URL as a production policy URL; final URLs must be revalidated after the authorized stable production hostname is frozen.

## Safety

- Production signing performed: FALSE
- Play upload/publishing performed: FALSE
- Cloudflare production cutover performed: FALSE
- Solana financial action performed: FALSE
- Canonical source archive overwritten/deleted: FALSE
- WAVE_MAWJA modified or mixed with THF: FALSE
