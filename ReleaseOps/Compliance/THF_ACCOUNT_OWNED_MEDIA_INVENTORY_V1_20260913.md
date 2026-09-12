# THF Account-Owned Media Inventory V1

Status: **PASS / READ-ONLY**

## Evidence
- GitHub Actions run: `34721306352`
- Workflow commit: `3deb6b73e908ba2b3cc2748ae910b27f074cc344`
- Canonical input archive: `THF_NEXUS_6_FINAL_SOURCE_20260829.zip`
- Canonical input SHA-256 verified before inspection: `8c060bdb7776ccf485b6294cda513a75b0fd3be28d43a416431d1368260a4884`
- GitHub OIDC/WIF -> GCP -> IAP: PASS
- THF/WAVE source isolation: PASS
- Mutation performed: FALSE

## Local user-owned file surfaces
### Media
Canonical `src/thf/media/service.py` stores local media under:
- `runtime/media/`

Local uploaded files are named with the authenticated owner id prefix:
- `<uid>_<sha-prefix>.<ext>`

Streamed uploads use temporary files:
- `.upload-<uid>-<random>.tmp`

`media_posts.asset_url` stores URLs of the form:
- `/media/file/<name>`

The canonical source describes external/object storage as a future/production adapter for larger media, not an active destination proven by this gate.

### Avatar
Canonical `src/thf/avatar/service.py` writes:
- source/likeness image: `runtime/uploads/<avatar_id>.img`
- generated fallback GLB: `runtime/avatars/<avatar_id>.glb`

The `avatars` DB row records `user_id`, `avatar_id`, `likeness_reference_path`, `glb_path`, and photo SHA-256.

### Runtime directories observed in canonical source
- `runtime/uploads`
- `runtime/media`
- `runtime/avatars`
- `runtime/logs`
- `runtime/pids`

## Release implication
The V1 account-deletion endpoint candidate correctly removes/anonymizes database identity references, but account deletion is not release-complete until local owned media/avatar files are also handled safely.

A safe candidate must **not** blindly unlink DB-provided paths. Required design:
1. collect account-owned media/avatar references before deleting DB identity rows;
2. allow only validated basenames and roots under `runtime/media`, `runtime/uploads`, and `runtime/avatars`;
3. verify media basename ownership (`<uid>_...`) and derive avatar file names from the account's trusted `avatar_id` where possible;
4. stage files with same-filesystem rename into an account-deletion quarantine directory;
5. run the already-validated DB deletion transaction;
6. restore staged files if the DB transaction fails;
7. after DB commit, remove staged files and the temporary stage directory;
8. remove owned stale `.upload-<uid>-*.tmp` files using the same root-constrained process;
9. leave unrelated/sentinel files untouched;
10. fail closed on suspicious/out-of-root references rather than deleting arbitrary filesystem paths.

External object storage cleanup remains a provider-specific release gate if/when an object-storage provider becomes active.

## Safety
- Canonical archive mutation: FALSE
- Production runtime mutation: FALSE
- Production DB mutation: FALSE
- Production signing: FALSE
- Google Play upload: FALSE
- Cloudflare production cutover: FALSE
- Solana financial action: FALSE
- WAVE_MAWJA mutation: FALSE

## Next
Inspect the exact MediaService/AvatarService creation contracts, then extend the canonical-archive-derived account deletion candidate with staged local file cleanup and disposable filesystem tests, packaging it as a new candidate without overwriting V1.