# TopHeroFit policy and privacy reconciliation — 2026-11-08

Status: **HOLD / internal evidence only / no Play declaration submitted / no listing write**  
Canonical app-source SHA: `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3`  
Canonical release branch: `agent/codex/fitness-recovery/20261023`

## Current Android permission surface

Manifest `fitness-v2/android/app/src/main/AndroidManifest.xml` (blob `0969cdb2f18775f23e0870bf754612a04376895f`) declares:

- Health Connect: `READ_STEPS`, `READ_EXERCISE`, `WRITE_EXERCISE`, `READ_DISTANCE`, `READ_ACTIVE_CALORIES_BURNED`.
- Activity/location: `ACTIVITY_RECOGNITION`, `ACCESS_COARSE_LOCATION`, `ACCESS_FINE_LOCATION`.
- Runtime service/notification: `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_LOCATION`, `FOREGROUND_SERVICE_HEALTH`, `POST_NOTIFICATIONS`.
- Network: `INTERNET`, `ACCESS_NETWORK_STATE`.

No `READ_HEART_RATE`, resting heart-rate, sleep, weight, blood pressure, blood glucose, oxygen saturation, nutrition or body-composition permission is declared. Do not add any of those without a concrete user-visible feature, a minimum-scope review, updated declaration/privacy evidence and physical tests.

## Verified Health Connect data flow in current source

Source files inspected at the canonical app-source tree:

- `HealthConnectRepository.kt` blob `cb191c3db3322cef4c27be8a034e90c72c2875e2`
- `HealthReadPermissionPolicy.kt` blob `713053ecd5421b1990da14c71a86244db1356fbb`
- `HealthSyncGate.kt` blob `8a71fbe1a2cda5771f67aafe7a9394145f28f63f`
- `HealthRecordEvidencePolicy.kt` blob `432042f7bf2ab69a430a125f140c7b04418e70a0`
- `HealthSourceTrustPolicy.kt` blob `0656981a3dd34c8b76291efbfb0b3dc6596cffcf`
- `MainActivity.kt` blob `b97e08756d5aba515c30f2d1a05517f56631ebf0`

Findings:

1. Each Health Connect metric is read only when its own permission is granted. Missing permission is `null`; a granted read with no records is numeric zero.
2. `syncHealthInternal()` reads the seven-day snapshot, stores sync time and aggregate record counts in local preferences, and dispatches the snapshot to the WebView UI. That path does not call the THF backend.
3. Backend sync is a separate queue for THF-created workout records. It does not send the imported Health Connect summary through the Health summary path.
4. THF-created exercise sessions are written to Health Connect only after the user grants `WRITE_EXERCISE`.
5. Record provenance retains provider package, record type/id, recording method and device metadata. The current provider allowlist is Google Fit, Samsung Health and Samsung Wear Health; compatible device classes include phone, watch, fitness band, chest strap and ring.
6. The provenance policy is not cryptographic device/wearable attestation. Manual, unknown, self-authored, unapproved-provider or incompatible/unknown-device records remain ineligible for rewards. Do not describe this as tamper-proof or physically verified.

The current data-flow behavior supports the repository privacy statement that imported Health Connect summaries stay on-device. Revalidate this statement whenever Health sync or backend upload code changes.

## Current disclosure and declaration state

- `ReleaseOps/FitnessV2/PLAY_HEALTH_DATA_DECLARATION_DRAFT_20261003.md` remains an unsubmitted draft for historical candidate `d79c9c621dab30748e0779bd5a5fc35e385593d5` / versionCode 51003. It is not a declaration for the current app-source tree and must be refreshed before a future release.
- The current Play readback does not expose the Play Console privacy-policy URL or the submitted Health apps declaration state. Both remain `NOT_VERIFIED`; do not infer submission or approval.
- The current Play listing's English disclaimer says the app does not provide medical diagnosis or replace professional medical advice. The Arabic text says it does not provide a medical diagnosis or replace specialist advice. Neither explicitly states that Top Hero Fit is not a medical device and does not diagnose, treat, cure or prevent a medical condition.
- Repository `fitness-v2/appdeploy/public/privacy.html` (blob `a5d43ac08ffeff52a0e9c35bde1d6ade2a384d82`) includes the current Google Play purchase disclosure and external identity-provider deletion limit. Repository `account-deletion.html` (blob `031be7223f956b5593fb848ec3d08a22a3a4077e`) describes app-owned deletion and the Google Play purchase exception.
- Existing AppDeploy web snapshot `1793087800913` (2026-10-27) is Ready but its stored `public/privacy.html` omits the purchase disclosure present in the current repository file, and its stored `public/account-deletion.html` omits the purchase-retention paragraph present in the current repository file. The snapshot is stale relative to the repository. The public page URLs could not be independently fetched in this check; live reachability and content are therefore `NOT_VERIFIED`.
- AppDeploy secret-name inventory for `thf-fitness-pulse-ul26f1` is empty. No deployment or secret was changed. The existing snapshot also has frontend WebGL-context and remote Arabic-font load errors; it is not Android or Play acceptance evidence.

## Required policy/privacy work before Production

1. Refresh the Health apps declaration and Data Safety answers against the exact future release source and actual deployed SDK inventory. Keep the five Health Connect permissions above unless a separately approved feature justifies a minimal addition.
2. Submit and verify the Health apps declaration in Play Console; capture the resulting state. Do not claim it is submitted or approved from repository drafts.
3. Publish the current repository privacy and account-deletion pages to the existing free HTTPS host, then independently read back the public pages and compare them with these exact repository blobs. Do not use an older AppDeploy snapshot as current evidence.
4. Verify the privacy-policy URL in Play Console and the in-app Privacy/Account-deletion entry points on a physical device.
5. Update both localized store descriptions with a clear non-medical disclaimer. Suggested English text: “Top Hero Fit is not a medical device. It does not diagnose, treat, cure, or prevent any medical condition. Consult a qualified healthcare professional for medical advice, diagnosis, or treatment.” Suggested Arabic text: “تطبيق Top Hero Fit ليس جهازًا طبيًا، ولا يهدف إلى تشخيص أي حالة مرضية أو علاجها أو شفائها أو الوقاية منها. استشر مختصًا صحيًا مؤهلًا للحصول على المشورة أو التشخيص أو العلاج الطبي.”
6. Complete physical Health Connect grant/partial-grant/revoke/no-data/error and Samsung Health-origin checks. Confirm the app remains useful when permissions are declined and never converts missing permission into zero.
7. Close the separate security gate: dependency audit, Android network-security review, deletion/authentication review and server-side Play Integrity exchange for ranked/reward-sensitive paths.

## Official policy basis checked 2026-11-08

- Google Play Developer Program Policy effective 2026-10-29: https://support.google.com/googleplay/android-developer/answer/18265346
- Health Content and Services: https://support.google.com/googleplay/android-developer/answer/16679511
- Android health permissions guidance: https://support.google.com/googleplay/android-developer/answer/12991134
- Permissions and APIs that Access Sensitive Information: https://support.google.com/googleplay/android-developer/answer/16558241

Google's current guidance requires a Health apps declaration, an accessible privacy policy in Play Console and in-app, clear prominent disclosures and consent, accurate listing claims, and minimum necessary health permissions. Other health/medical apps must include a clear “not a medical device” disclaimer and advise users to consult a healthcare professional.

## Release decision

**HOLD.** No Play listing edit, declaration submission, signing, upload, version allocation or Production promotion occurred in this reconciliation. VersionCode 51020 remains unallocated. No paid infrastructure was added.
