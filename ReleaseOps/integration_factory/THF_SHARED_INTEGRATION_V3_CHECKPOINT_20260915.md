# THF Shared Integration V3 Checkpoint — 2026-09-15

## Scope
Shared THF integration only. WAVE_MAWJA was not touched. No production financial, store, signing, deployment or irreversible action was performed.

## Authoritative V3 commits
- `d4284dd0566c7988cab878d839101cf426cea426` — V3 account/auth replay and health provenance contracts.
- `dfd2d66775b675ccde29d96ce5df83f3bf0dd1ca` — V3 regression coverage.
- `0797531015469a9b8e0aed2925badeda7a0c6dbf` — Android shared integration manifest promoted to V3.
- `cea1dd045de8a7b164450aaa72451355ee370091` — V3 CI gate.

## CI evidence
GitHub Actions run `34900307226` — **THF Shared Integration V3** — completed **SUCCESS**.
Passed steps:
- Python compile of shared contracts/tests.
- Shared integration unit/regression tests.
- Machine-readable Android V3 manifest validation.

## V3 additions
### Identity and session
- Session-bound product visibility: operator products are not exposed from unauthenticated/guest role lists.
- THF Admin requires authenticated identity subject plus owner/admin role.
- THF Publisher requires authenticated identity subject plus owner/admin/publisher role.
- Google mobile config rejects embedded client secrets; ID token claim acceptance still requires prior cryptographic signature verification.
- Email-code fallback contract uses only hashed code material, maximum 10-minute lifetime, bounded attempts, rate limiting and single-use semantics.
- Password fallback policy uses 12–256 character bounds, allows paste, avoids arbitrary composition rules, requires compromised-password rejection and server-side password hashing, and forbids client password persistence.
- Passkey assertion contract now requires RP/credential identity, matched server challenge, user verification, signature verification and one-time challenge consumption.
- Account deletion contract requires authenticated session, recent reauthentication within 300 seconds and confirmation nonce; it revokes sessions, unlinks identity providers and queues owned-data cleanup. Client deletion is never authoritative.
- Guest-to-identity linking still requires verified identity proof.

### Replay protection
- A fail-closed reference/test replay ledger now covers `passkey`, `email_code`, `handoff` and `motion` namespaces.
- The reference ledger is explicitly **not production durable**. Production requires an atomic durable server-side store; no production replay guarantee is claimed until it is bound and evidenced.

### Cross-app federation
- Cross-app handoffs remain maximum 300 seconds, server-signed, single-use and carry neither roles nor secrets.
- No server signer binding is claimed yet.

### Health integration
- Health Connect remains the primary Android bridge.
- Samsung Health Data SDK remains an optional partner adapter; absence is nonfatal and falls back to Health Connect.
- Health records now carry explicit provider/source provenance and optional canonical source identity.
- Deduplication can suppress the same canonical device/provider record across Health Connect and Samsung adapters without collapsing unrelated records.
- Background/history read remains opt-in rather than default.
- Health-provider data alone has no reward authority.

### Motion verification
- Motion evidence supports per-event nonce/replay protection in addition to monotonic clock, confidence and sensor-attestation metadata.
- Client motion evidence never has reward authority; server verification remains mandatory.

### Shared UX preferences
- Locale/RTL, Data Saver, Reduce Motion and High Contrast contracts remain shared user preferences while each product keeps independent presentation.

## Package/name compatibility
Public user-facing naming metadata remains mapped onto the existing package identities; package IDs were not changed. Operator products remain private/internal by policy and role enforcement.

## Truth boundary / remaining external or runtime bindings
The following remain **FALSE/PENDING** and must not be represented as production-complete:
- Google OAuth production console/client/consent configuration.
- Real backend Google signature verifier binding.
- Durable atomic passkey/email-code/handoff/motion replay/challenge store.
- Email authentication delivery backend binding.
- Account deletion transactional backend/media cleanup binding.
- Cross-app handoff production server signer.
- Samsung Health production partner registration and approved SDK boundary.
- Physical-device Health Connect / Samsung Health validation.
- Exact-candidate physical phone acceptance.
- `FINAL_OR_PLAY_READY`.

## Release truth
`FINAL_OR_PLAY_READY = FALSE`
`PHYSICAL_DEVICE_PASS = FALSE`
