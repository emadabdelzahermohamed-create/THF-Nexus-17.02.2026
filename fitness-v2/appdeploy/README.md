# Fitness V2 AppDeploy integration source

These modules are the deployment-owned bridge between the existing AppDeploy account
and the offline-first Android client. `native_auth_bridge.tsx` renders an explicit,
user-gesture sign-in screen in the authenticated
web origin. It requests a two-minute, PKCE-bound, single-use ticket and returns that
ticket through the app callback. `android_v2_routes.ts` stores only ticket/session
hashes, issues a 15-minute opaque Android session, scopes every record by the stable
AppDeploy user id, and calculates progress and competition facts server-side.

Deployment requires merging the exports into the applied AppDeploy snapshot:

- spread `fitnessV2AndroidRoutes` into the root `router({...})`;
- render `AndroidAuthBridgeScreen` instead of the normal app when
  `readAndroidAuthRequest()` returns a request;
- keep the browser account endpoint and Android `THF_BASE_URL` on the same persistent
  HTTPS AppDeploy origin.

No access token, OAuth refresh token, password, cookie, or signing secret is stored in
this repository. The Android access token remains memory-only.
