# THF Canonical Archive Source Compare V1

Status: **PASS / CANONICAL PROVENANCE VERIFIED**

## Evidence
- GitHub Actions run: `34721092917`
- Workflow commit: `8f608c2c21d5d340dd1beae27524e8a7a38523e5`
- Canonical source archive: `THF_NEXUS_6_FINAL_SOURCE_20260829.zip`
- Archive SHA-256: `8c060bdb7776ccf485b6294cda513a75b0fd3be28d43a416431d1368260a4884`
- Existing `inner.sha256` verification: `OK`
- Runtime deterministic `src+clients` manifest SHA-256: `c5e75105ab416d8c992bba032d025fb5205f3660e2d211268167ede3f5ce9ca0`
- Extracted archive deterministic `src+clients` manifest SHA-256: `c5e75105ab416d8c992bba032d025fb5205f3660e2d211268167ede3f5ce9ca0`
- Runtime matches extracted canonical archive: **TRUE**
- THF/WAVE isolation: PASS

## Interpretation
Earlier aggregate hashes (`710336...`, `dd5b647...`, `c924479...`, `415817...`) were not suitable canonical identifiers because earlier recipes either included generated Python bytecode or hashed absolute-path-bearing `sha256sum` output. The canonical comparison now normalizes each file to `SHA256 + relative path`, excludes generated `__pycache__/*.pyc/*.pyo`, and compares the resulting sorted manifests. The runtime and immutable source archive match under this deterministic recipe.

## Version markers
The canonical archive contains runtime release markers `6.0.0` in `src/thf/__init__.py`, `THFNexus/6.0` in `src/thf/app.py`, and `/health` release `6.0.0`. `pyproject.toml` still reports `5.0.0`; this remains packaging metadata drift to correct only in a versioned candidate.

## Safety
- Canonical archive mutation: FALSE
- Runtime mutation: FALSE
- Production DB mutation: FALSE
- Production signing: FALSE
- Play upload: FALSE
- Cloudflare production cutover: FALSE
- Solana financial action: FALSE
- WAVE_MAWJA mutation: FALSE

## Next
Build the account-deletion endpoint candidate from a disposable extraction of this exact canonical archive, validate authenticated identity binding and the already-proven DB transaction strategy, and package the candidate separately without overwriting either the archive or runtime.