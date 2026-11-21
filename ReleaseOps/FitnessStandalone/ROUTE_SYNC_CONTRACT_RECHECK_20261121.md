# TopHeroFit — authenticated route-sync contract recheck (2026-11-21)

**Status: DESIGN ONLY. NOT IMPLEMENTED. NO PRECISE GPS ROUTE UPLOAD EXISTS OR IS CLAIMED.**

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`. Canonical branch: `agent/codex/fitness-recovery/20261023`. Canonical application HEAD: `b097d6ef0025d615c261ee42e8d2246533224e70`.

This recheck follows the native GPS integration. It does not add an endpoint, database table, consent switch, worker, upload queue or cloud storage.

## 1. Local route persistence and map refresh are separate

- `persistFinishedActivity()` in `fitness-v2/android/app/src/main/assets/pulse/app.js` writes a finished activity object, including `route: snapshot.route || []`, to WebView localStorage key `pulse.v2.activities`. It replaces an entry with the same local activity ID and retains the latest 100 entries.
- `recoverPendingActivitySession()` consumes a native finished snapshot and calls the same local persistence function.
- The activity/map screen polls the native snapshot approximately every 1,000 ms. That is a local presentation refresh, not a network sync.
- The native `ActivitySessionCheckpoint` and bounded route points are stored locally for process recovery. They are not an authenticated upload queue.
- No route-upload call appears in `persistFinishedActivity()` or the inspected account sync repository.

## 2. Existing Android account and workout contract

- `AccountAuthRepository` exchanges a single-use browser ticket plus PKCE verifier at `POST /api/v2/auth/android/sessions`. The browser bridge requests a two-minute PKCE-bound ticket; the resulting Android bearer session is short-lived (15 minutes in the AppDeploy route).
- The Android bearer token is held in memory by the native account flow; `BackendSyncRepository` receives it at call time and does not persist it.
- `BackendSyncRepository` uses HTTPS, `Authorization: Bearer`, bounded response reads and an `Idempotency-Key`.
- Existing write: `POST /api/v2/workouts/sync`. Payload is a strict workout/set record: client record ID/version, start/end, sport, exercise-session type, source/provenance and sets. No coordinates, route points, polyline, geohash or altitude.
- Existing restore: `GET /api/v2/workouts?limit=200`. This returns authenticated workout history only.
- The Android client does not send a client-supplied account ID. The server derives the account from the verified bearer session.

## 3. Existing AppDeploy route/storage/deletion contract

Inspected `fitness-v2/appdeploy/android_v2_routes.ts`:

- `androidUser(event)` verifies the bearer token and resolves the stored Android session's user ID.
- Dynamic resource kinds are currently only `ticket | session | idempotency | workout-index`.
- `safeResourceTable` permits only `fitness_v2_ticket_*`, `fitness_v2_session_*`, `fitness_v2_idem_*` and `fitness_v2_workout_*` table names.
- Existing routes are Android ticket/session exchange, workout sync/restore, progress summary and competition operations. No `/api/v2/activity-routes` route or route-consent route exists.
- `deleteFitnessV2UserData(userId)` deletes workout history/indexes, legacy workouts, competitions, tracked resources and legacy Android auth ticket/session/competition rows. It has no route table, route-consent receipt or route-idempotency resource kind.
- The AppDeploy README explicitly requires the applied authenticated `DELETE /api/account` route to call `deleteFitnessV2UserData` and combine its `done` value with legacy deletion. It states account-deletion compliance is not established until the live route is verified with a non-privileged QA account and empty V2 history/progress is independently read back. The deployed route integration was not independently verified in this recheck.

## 4. Existing Python backend contract

Inspected `fitness-v2/backend/auth.py`, `api.py`, `workout_store.py` and `openapi.json`:

- Access-token verification is issuer/audience-bound, HMAC-SHA256 key-ring based, expiry checked and supports session revocation.
- The Python API requires HTTPS and a verified bearer principal; user identity is derived from the token subject.
- `/api/v2/workouts/sync` has a strict field allowlist and rejects unknown workout fields. Idempotency conflicts fail closed.
- The SQLite store has workout-session and workout-set tables only.
- OpenAPI lists workouts, progress and competition endpoints; no route or route-consent path exists.

The Python backend and AppDeploy routes are separate deployment adapters; do not assume a route added to one exists in the other or is deployed.

## 5. Privacy and deletion gaps before any route backup

- Live AppDeploy snapshot `1794247542845` privacy page matches canonical repository blob `a5d43ac08ffeff52a0e9c35bde1d6ade2a384d82`; it describes account/workout synchronization and says Health Connect summaries are not sent to the server. It does not disclose precise-route backup.
- The live account-deletion page matches canonical repository blob `031be7223f956b5593fb848ec3d08a22a3a4077e`; it lists app-owned goals, legacy/V2 workout history, Android sessions/tickets, sync/idempotency records and competition submissions; it does not describe route records or route-consent receipts.
- Neither page currently promises route backup, precise-location retention or route revocation. Do not enable location upload before updating and independently reviewing the in-app disclosure, privacy policy, account-deletion page and Google Play Data Safety/location declarations.
- Storage-at-rest encryption/key-management and operator-access guarantees for precise coordinates have not been verified. If they are undocumented or insufficient, do not store precise routes server-side.

## 6. Safe future design boundary

Retain the existing design in `ROUTE_SYNC_DESIGN_20261110.md`:

1. All new consent defaults OFF.
2. Separate activity-summary backup from precise-route backup.
3. Separate account-level precise-route opt-in from per-finished-session route inclusion.
4. Upload only after explicit Finish; never during the active session or the 1-second map refresh.
5. Use a separate authenticated route resource/endpoint; never extend the workout-set allowlist with arbitrary route fields.
6. Server derives user identity from the bearer session; use stable record IDs, versioning, idempotency and strict point-count/range/time/accuracy validation.
7. Route points are private account data, not competition/leaderboard/reward or analytics inputs.
8. Provide per-route deletion, precise-route consent revocation/purge and account deletion. Extend the resource-kind/table allowlist and bounded deletion registry; return complete only after all route resources and consent/idempotency rows are deleted.
9. Do not promise automatic TTL until a free, reliable purge mechanism is implemented and tested.
10. Test default-off/no-coordinate behavior, summary-only redaction, consent revocation, cross-account isolation, retries/conflicts, second-device restore and deletion on both deployment adapters.

## 7. Decision

No route-sync code or cloud upload was implemented. Completed routes remain local-only. The one-second map refresh remains local. The deployed source-level account-deletion hook is now verified, but a non-privileged runtime deletion/readback test is still outstanding. The next route-sync implementation gate is after GPS/session P0 and that runtime deletion test, followed by privacy/storage-security review and exact-head backend/Android tests. No new infrastructure, paid service, permission, versionCode, signing or Play mutation was introduced.
