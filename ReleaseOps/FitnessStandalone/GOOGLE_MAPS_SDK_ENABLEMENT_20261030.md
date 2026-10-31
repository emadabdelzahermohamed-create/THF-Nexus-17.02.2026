# Top Hero Fit — Google Maps SDK enablement checkpoint

Date: 2026-10-30
Existing project: `project-b5e10d7e-8ce8-4aa4-a15`
Project number used by Workload Identity Federation: `1035420130588`
Android package: `com.topherofit.thf.pulse`
Existing release identity: `thf-release-builder@project-b5e10d7e-8ce8-4aa4-a15.iam.gserviceaccount.com`

## Authorization
The app owner explicitly approved enabling Google Maps SDK for Android in the existing THF Cloud project. No new project or billing-account changes are authorized.

## What was verified
- GitHub Actions Workload Identity Federation successfully authenticated as the existing release-builder service account.
- The configured GCP project ID was confirmed by `gcloud projects describe`.
- The service account currently lacks `serviceusage.services.enable` for `maps-android-backend.googleapis.com`.
- The first attempt to read billing state was blocked because Cloud Billing API was not enabled for the WIF quota project; billing state remains unverified. No billing changes were made.
- The subsequent Maps SDK enablement attempt failed with `PERMISSION_DENIED` on `serviceusage.services.enable`. The Maps SDK API is not yet confirmed enabled.
- No API key was created, no billing account was linked or changed, and no new billable API/service was enabled.

## Required owner action
Either enable the SDK directly in the existing project:
https://console.cloud.google.com/apis/library/maps-android-backend.googleapis.com?project=project-b5e10d7e-8ce8-4aa4-a15

Or grant the existing release-builder service account the least relevant predefined role `roles/serviceusage.serviceUsageAdmin` on this project, then rerun the workflow. To create/manage the restricted key automatically, it would additionally need `roles/serviceusage.apiKeysAdmin`; alternatively the owner can create the key in Cloud Console and store it in Secret Manager without disclosing it in chat.

## Required Play signing fingerprint
Before creating the Android-restricted API key, obtain the Google Play **app signing certificate SHA-1** (not the upload-key SHA-1) from Play Console > Top Hero Fit > Test and release > App integrity > App signing. Package restriction must be `com.topherofit.thf.pulse`. The existing upload certificate SHA-1 `D8:BB:CA:BC:17:78:03:43:2E:5D:95:7B:19:61:D2:03:6A:3A:03:06` is not a substitute for the Play app-signing certificate when Play App Signing is active.

## Official references
- Maps SDK setup and key restrictions: https://developers.google.com/maps/documentation/android-sdk/get-api-key
- Google Play signing key and API-provider registration: https://support.google.com/googleplay/android-developer/answer/9842756
- Service Usage Admin / API Keys Admin roles: https://docs.cloud.google.com/iam/docs/roles-permissions/serviceusage

## Release boundary
Do not merge or publish the Maps SDK integration until the API is enabled, a restricted key is provisioned securely, both debug/test and Play app-signing fingerprints are handled, CI builds pass, and device QA confirms Google basemap rendering.