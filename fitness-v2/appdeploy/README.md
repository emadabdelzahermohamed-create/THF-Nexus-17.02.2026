# Fitness V2 AppDeploy integration source

These modules are the deployment-owned bridge between the existing AppDeploy account
and the offline-first Android client. `native_auth_bridge.tsx` renders an explicit,
user-gesture sign-in screen in the authenticated
web origin. It requests a two-minute, PKCE-bound, single-use ticket and returns that
ticket through the app callback. `android_v2_routes.ts` stores only ticket/session
hashes, issues a 15-minute opaque Android session, scopes every record by a hash of
the stable AppDeploy user id, tracks dynamic V2 tables for bounded account deletion,
and calculates progress and competition facts server-side.

Deployment requires merging the exports into the applied AppDeploy snapshot:

- spread `fitnessV2AndroidRoutes` into the root `router({...})`;
- import `deleteFitnessV2UserData` and call it from the authenticated
  `DELETE /api/account` route. Combine its `done` value with the legacy deletion
  result so the client repeats the request until every bounded page is removed;
- render `AndroidAuthBridgeScreen` instead of the normal app when
  `readAndroidAuthRequest()` returns a request;
- keep the browser account endpoint and Android `THF_BASE_URL` on the same persistent
  HTTPS AppDeploy origin.

No access token, OAuth refresh token, password, cookie, or signing secret is stored in
this repository. The Android access token remains memory-only. A deployment is not
account-deletion compliant until the live route calls `deleteFitnessV2UserData` and a
non-privileged QA account verifies `done: true` followed by empty V2 history/progress.

The integration point is deliberately small and must stay authenticated:

```ts
import { deleteFitnessV2UserData, fitnessV2AndroidRoutes } from './fitness-v2-android';

// Inside the existing requireAuth()-protected DELETE /api/account handler:
const v2Deletion = await deleteFitnessV2UserData(c.user!.userId);
return json({ ok: true, done: legacyDeletionDone && v2Deletion.done, v2Deletion });
```

AppDeploy's published authentication SDK exposes sign-in, sign-out, token validation,
and scope checks, but no user-identity deletion primitive. The app-owned data deletion
route therefore cannot be represented as deleting the platform identity unless a
separate, documented AppDeploy identity-deletion mechanism is made available.
