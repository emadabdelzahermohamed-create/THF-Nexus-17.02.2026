# Fitness V2 Play Health and Data Safety draft — not submitted

Status: **DRAFT / owner review required / no Play claim**  
Candidate: `22c11488f8b1fad28631c55df0a18a7815fbec03`  
Package/version: `com.topherofit.thf.pulse` / `51003`

This draft maps the exact candidate behavior to the Play Console forms. It is not
evidence that any declaration was submitted or approved.

## Health apps declaration

- App category: Health & Fitness.
- Health feature: activity and fitness tracking, workout recording and progress summaries.
- Health Connect is optional and initiated from the visible Health screen after an
  Arabic/English pre-permission explanation.
- Requested reads and justifications:
  - `READ_STEPS`: show the user's seven-day on-device step summary.
  - `READ_EXERCISE`: show the user's seven-day exercise-session summary and support
    Samsung Health interoperability through Health Connect.
  - `READ_DISTANCE`: show distance for supported walking/running/cycling sessions.
  - `READ_ACTIVE_CALORIES_BURNED`: show active-calorie totals for the same summary.
- Requested write and justification:
  - `WRITE_EXERCISE`: write a user-completed THF workout as an
    `ExerciseSessionRecord` with a stable client record id/version so retries deduplicate.
- Heart rate is not requested or surfaced by this candidate.
- Health Connect summary values are processed on-device and are not sent to the THF
  backend by this candidate. Optional account sync sends THF-created workout records,
  not the imported seven-day Health Connect summary.

## Data Safety working answers

The Console answers must be reviewed against the finally deployed runtime and every SDK.

| Data category | Collected | Shared | Purpose / handling |
|---|---:|---:|---|
| Account identifier supplied by the identity provider | Yes, only when optional sign-in is used | No sale or advertising sharing | Authentication, account-scoped sync, fraud/security |
| User-entered workout/fitness records | Yes, only when optional sync is used | No | Cross-device workout history, progress, dedup and competitions |
| Health Connect steps/sessions/distance/active calories | No server collection in this candidate | No | On-device seven-day Health screen only |
| Completed THF workout written to Health Connect | User-directed device write | No | User-requested health record interoperability |
| Advertising data | No | No | No advertising SDK is present in the inspected Android candidate |

- Data in transit: HTTPS is required for the account and API origins.
- Android access token: short-lived and memory-only; browser cookies are not embedded in
  the WebView or stored by the native client.
- Local offline data: excluded from Android backup and device transfer by policy files.
- Account-data deletion is visible from Profile and routes to the public instructions.
  The bounded authenticated server route deletes THF app-owned data and signs the app
  session out. It does not claim to delete an external Google/Apple/X/email/AppDeploy
  identity because the connected AppDeploy SDK exposes no identity-deletion primitive.
- The public deletion URL remains **deployment pending** for this candidate.

## App access working instructions

- Core offline browsing and workout logging do not require an account.
- Reviewers can open Today, Train, Progress, Health and Profile without signing in.
- Testing account sync requires a reusable non-privileged QA account that does not depend
  on an OTP or expiring credential. No such credential is stored in Git or this draft.
- Health Connect behavior requires an Android device/configuration where Health Connect is
  available; Samsung-origin verification additionally requires Samsung Health to write
  user-authorized activity to Health Connect.

## Submission blockers

1. Deploy the exact candidate privacy/deletion pages and deletion handler after the
   AppDeploy quota resets, then verify them with a disposable account.
2. Produce the signed release AAB and its upload/app-signing certificate fingerprints.
3. Publish certificate-correct Digital Asset Links; the current URL returns HTTP 403.
4. Complete physical Health Connect and Samsung-origin QA.
5. Reconcile the final deployed SDK inventory before pressing Submit in Play Console.

## Official references checked on 2026-10-03

- Health apps declaration form: https://support.google.com/googleplay/android-developer/answer/14738291?hl=en
- Health app categories: https://support.google.com/googleplay/android-developer/answer/13996367?hl=en
- Health Connect publishing guidance: https://developer.android.com/health-and-fitness/health-connect/publish
- Account deletion requirements: https://support.google.com/googleplay/android-developer/answer/13327111?hl=en
