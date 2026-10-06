# THF Fitness — Google Play submission metadata draft

Date: 2026-09-18
Package: `com.topherofit.thf.pulse`
Target SDK: 36
Track target: Internal Testing first

This file is a release-preparation draft. Console answers must match the exact signed artifact and live service at upload time.

## Current policy gates verified from Google documentation
- New apps and app updates submitted after 2026-08-31 must target Android 16 / API 36 or higher. This project targets API 36.
- Apps with account creation must provide both an in-app deletion path and a web deletion resource.
- The Health apps declaration must be completed for apps distributed on testing or production tracks. Do not claim Health Connect integration until it exists and is verified in the Android artifact.

Official references:
- https://support.google.com/googleplay/android-developer/answer/11926878
- https://support.google.com/googleplay/android-developer/answer/13327111
- https://support.google.com/googleplay/android-developer/answer/14738291

## Public URLs
- Web app: https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/
- Privacy: https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/privacy.html
- Account deletion: https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/account-deletion.html
- Terms: https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/terms.html

## App access
The service requires authentication for private goals, workout logs, history, and account deletion. Authentication is exposed through the production web identity flow embedded by the Android WebView. Play reviewer access must use a working test account/provider flow at review time. Do not submit reviewer credentials into source control.

## Data Safety working map
Validate these entries again against the final signed artifact and identity provider configuration.

Data handled by the current production service:
- Account identifier supplied by the identity system.
- Email/display name when granted by the sign-in provider.
- Fitness goals selected by the user.
- Workout sessions and exercise logs.
- Workout completion/progress information.
- Security/trust metadata where implemented server-side.

Current purposes:
- Account management and authentication.
- App functionality and cross-client synchronization.
- Fitness progress/history.
- Fraud/abuse prevention for trust-sensitive features.

Current controls:
- HTTPS production service.
- Private fitness state requires authentication.
- Records are scoped to authenticated account identity.
- In-app account-data deletion path.
- Public deletion instructions.
- No finalization of ranked/economy-sensitive outcomes from offline claims alone.

Do not state that data is sold.
Do not state that Health Connect data is collected until the Android integration and corresponding permissions are present and production-tested.

## Health apps declaration
THF Fitness clearly offers fitness functionality, so the declaration must be completed before Play submission. The Android RC2 source currently has no verified Health Connect implementation. Declare only functionality actually present in the artifact; Health Connect remains a separate release gate.

## Internal Testing release notes
Arabic:
"نسخة اختبار داخلية لتطبيق THF Fitness المستقل: خطط وتمارين، تسجيل الجلسات والتقدم، واجهة عربية/إنجليزية، وربط آمن بخدمة الويب والإدارة المشتركة للحساب."

English:
"Internal test of standalone THF Fitness: workout plans and exercises, session/progress logging, Arabic/English UI, and secure shared-account connectivity with the production web service."

## Fail-closed upload rules
Do not upload unless all are true:
- AAB is production-signed with the registered Play upload key.
- targetSdk 36 verified.
- package is exactly `com.topherofit.thf.pulse`.
- Production base URL is the approved HTTPS endpoint.
- No debug applicationId suffix in the release bundle.
- Emulator/device install-launch smoke passes.
- Account deletion and privacy URLs are reachable.
- Store declarations match the actual artifact.
