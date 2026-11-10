# TopHeroFit activity-route backup/sync design — 2026-11-10

**Status: DESIGN ONLY. NOT IMPLEMENTED. NO GPS ROUTE OR PRECISE-LOCATION CLOUD UPLOAD EXISTS OR IS CLAIMED.**

Scope is TopHeroFit only. This design reuses the current account/backend contract and free AppDeploy deployment; it does not introduce a new paid service, map provider, live-location stream, or competition/reward data path.

## 1. Existing behavior and contracts verified

- `persistFinishedActivity()` in `fitness-v2/android/app/src/main/assets/pulse/app.js` writes completed activity history, including route points, to WebView local storage (`pulse.v2.activities`). The local history is bounded to the latest 100 entries. No authenticated route-upload call is present in that completion path.
- `ActivityTrackingService` persists the active-session checkpoint locally in Android preferences. Its bounded route checkpoint is local and is not a cloud route-sync queue. The map's approximately one-second presentation refresh is a local UI update, not a sync interval.
- `BackendSyncRepository` reuses `AccountAuthRepository` and the existing bearer-token flow for THF-created workout records. Its current payload is set/workout metadata; it uses `Authorization: Bearer` and an `Idempotency-Key` with `/api/v2/workouts/sync` and `/api/v2/workouts`. It does not serialize GPS coordinates or route geometry.
- The Android access token is held in memory by the native activity/auth bridge; the current account flow uses short-lived authenticated sessions. Existing workout sync consent must not be interpreted as consent to upload location.
- `fitness-v2/appdeploy/android_v2_routes.ts` has a strict workout-field allowlist and no activity-route endpoint/table. Unknown route fields are not an accepted extension to the existing workout contract. The server derives the account from the authenticated Android session rather than trusting a client-supplied user ID.
- The AppDeploy deletion helper tracks ticket/session/idempotency/workout resources. Its resource-kind allowlist and safe-table-name validation do not currently include route tables. The README requires the authenticated account-deletion route to call `deleteFitnessV2UserData`; a route table would need to be included in that same bounded deletion contract and tests.
- The Python backend workout contract also contains no GPS route upload path. No existing authenticated backend route-sync endpoint was found in the Android/AppDeploy contracts inspected for this checkpoint.

## 2. Consent model — fail closed

Use three independent states; all new location-backup states default to OFF:

1. `activitySummaryBackupEnabled` — explicit account-level opt-in to back up finished activity summaries. This may include sport, start/end time, elapsed duration, distance, steps and estimated metrics, but **never coordinates, address, altitude, route polyline or route points**.
2. `preciseRouteBackupEnabled` — a separate, clearly worded opt-in for precise GPS route storage. It is not implied by account login, Health Connect permission, GPS permission, existing workout-history sync, or the summary-backup switch.
3. Per-session `includePreciseRouteInBackup` — defaults OFF for every finished session. Precise route points are uploadable only when both the account-level precise-route switch and the per-session choice are ON and a current consent receipt exists.

The disclosure must state that time-stamped route points can reveal home, work and travel patterns; identify the exact fields, purpose, account scope and deletion behavior; and explain that routes are private backup data, not public leaderboard data. Store a versioned consent receipt (scope, policy version/hash, locale, granted-at and revoked-at). Do not silently migrate existing users into consent.

## 3. Proposed API boundary

Keep route backup separate from the existing set-based `/api/v2/workouts` contract:

- `POST /api/v2/activity-routes/consent` — authenticated, versioned record of summary and precise-route consent scopes. The server derives the user from the bearer session.
- `POST /api/v2/activity-routes/sync` — authenticated, idempotent upload of one **finished** activity. Summary fields are allowed only with summary consent. `routePoints` are rejected unless the precise-route consent receipt is active and the per-session opt-in is present.
- `GET /api/v2/activity-routes?limit=...` — authenticated restore for the same account. Return summaries by default; return route points only while precise-route consent is active.
- `DELETE /api/v2/activity-routes/{clientRecordId}` — delete one account-owned activity/route record.
- `POST /api/v2/activity-routes/consent/revoke` — immediately stop future precise-route queueing/uploads and purge previously backed-up precise route points. Summary records may remain only if the separate summary consent remains enabled.

Every request uses the existing short-lived bearer-session model and an `Idempotency-Key`. The server obtains `userId` from `androidUser()`/the verified session; a body-supplied user/account ID is ignored or rejected. Use a stable client record ID plus monotonically increasing client version. Same ID/version/same payload is idempotent; same ID/version/different payload returns conflict; older versions cannot overwrite newer records.

Do not upload active-session samples. Queue only after explicit Finish, then retry offline through a dedicated `ActivityRouteSyncRepository`/worker. If auth expires, consent is revoked, the user signs out, or the per-session opt-in is absent, the precise-route queue must not send. Do not attach route payloads to the one-second map/UI refresh.

## 4. Payload and storage minimization

- Store route backups in a separate per-user route resource/table, not inside the existing `V2Workout` set record.
- Summary-only payload contains no latitude/longitude, polyline, geohash, altitude, address, home/work inference or reverse-geocoded place name.
- If precise route consent is active, upload only already quality-gated accepted GPS fixes from the finished session. Bound the route to the existing local maximum (1,200 points). Each point needs only latitude, longitude, timestamp and horizontal accuracy. Do not upload altitude, heading, raw sensor samples or smoothed coordinates.
- Distance, speed, pace and calorie calculations continue to use raw accepted fixes and existing metric policies. Display smoothing remains presentation-only and is never a metric source.
- Route backups are private account data. They are not sent to competitions, leaderboards, token rewards, advertising, analytics or third-party map providers.
- Apply request-size, point-count, coordinate-range, timestamp-order, duplicate-point and accuracy validation on the server. Reject malformed or over-limit payloads; never silently truncate in a way that changes recorded metrics.

## 5. Retention and deletion semantics

- Summary records remain until the user deletes them or deletes the account, subject to the existing account-history disclosure.
- Precise route points remain until the user deletes that route, revokes precise-route consent, or deletes the account. This is the only retention promise that can be made from the currently inspected storage contract.
- The current AppDeploy database adapter exposes record operations but no verified TTL/scheduled-purge contract was established in this review. Do not promise automatic 90-day/12-month expiry until a free, reliable TTL or purge scheduler is verified and tested. If a fixed expiry is later required, implement and independently test the purge before enabling precise-route backup.
- Revoking precise-route consent purges all server-side route points and pending precise-route uploads, while preserving summary-only records only if summary consent remains active. Deleting one activity removes both its summary and route points.
- Account deletion must remove route records, route-consent receipts, route idempotency records and route-resource registry entries. Extend the resource-kind allowlist and safe table-name validation to include route resources; add route counts to the deletion result. `done=true` is returned only after every route resource is deleted. Partial deletion remains retryable and must not be reported as complete.
- Before enabling this feature, verify the deployed authenticated `DELETE /api/account` path invokes the deletion helper and independently read back an empty route/history state. The public account-deletion page and privacy policy must describe route data, retention and deletion.

## 6. Security and privacy gates

- HTTPS only; per-user resource isolation; short-lived bearer auth; server-derived account identity; idempotency and strict request validation.
- Never log coordinates, route polylines, consent tokens or raw route payloads. Redact them from errors, diagnostics and support exports.
- Verify the AppDeploy storage-at-rest and operator-access guarantees for precise location data before enabling uploads. If those guarantees are insufficient or undocumented, do not store precise routes until an independently reviewed encryption/key-management design exists.
- Update the in-app prominent disclosure, privacy policy, account-deletion page and Google Play Data Safety/location declarations before the first route upload. No location upload may precede those reviews.
- No public sharing, competition scoring, rewards or third-party transfer is part of this design.

## 7. Required tests before implementation can ship

1. Default-off test proves no route request, no route queue and no coordinate field when all new consent switches are OFF.
2. Summary-only test proves an opted-in summary contains no latitude, longitude, route points, polyline, geohash or address.
3. Precise-route upload succeeds only with both current account consent and per-session opt-in; every missing, revoked, expired or unknown-consent state fails closed.
4. No active-session or one-second map-refresh path can enqueue or transmit route data; upload begins only after Finish.
5. Validate 1,200-point bound, coordinates, timestamp order, accuracy, duplicate IDs, same-version idempotency, conflicting-version rejection and retry behavior.
6. Cross-account tests prove one user cannot list, read, replace or delete another user's routes.
7. Revocation stops queued uploads and deletes existing route points while preserving summary only when its separate consent remains active.
8. Per-route deletion and account deletion remove route tables, consent receipts, idempotency records and resource registry entries; partial deletion retries until `done=true`.
9. Restore test on a second device/account session proves the route is returned only to the same authenticated account and only while precise-route consent is active.
10. Network/source-contract tests prove no GPS coordinates enter existing workout sync, Health Connect sync, competitions, logs or analytics.

## 8. Implementation gate

Design is ready for a separately reviewed implementation after the GPS/session P0 and account-deletion contract are stable. Before any precise-route upload: implement the separate consent UX, backend allowlist/table/deletion changes, tests, privacy/Data Safety updates, storage-security review and physical account/restore/delete QA. Until those gates pass, completed GPS routes remain local-only.

**Current release effect: none.** No route-sync code, cloud upload, new permission, new infrastructure, versionCode, signing, Play listing or Production change was made.