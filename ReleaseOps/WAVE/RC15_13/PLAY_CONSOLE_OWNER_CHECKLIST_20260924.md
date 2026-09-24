# WAVE MAWJA — Google Play owner checklist

Checkpoint date: 2026-09-24  
Package: `com.wave.mawja`  
Current tested bundle: versionCode `15301`  
Current Play state: Internal completed; closed-test track created as draft; Production unavailable while app remains Draft.

## Already completed automatically

- Production web is live on Cloudflare: https://wave-mawja.p-my.workers.dev
- Direct privacy policy is live: https://wave-mawja.p-my.workers.dev/privacy
- Direct terms page is live: https://wave-mawja.p-my.workers.dev/terms
- Android targetSdk/compileSdk are 36 in the approved TWA source.
- versionCode 15301 is already on Play Internal with status completed.
- Play API read/write access is working.
- Closed-testing track `wave-closed-readiness` exists and contains versionCode 15301 as a draft release.
- Arabic title/short description/full description, contact website, icon, feature graphic, and four real live-app screenshots have all individually passed the Play upload API.
- Current Android manifest requires only INTERNET and ACCESS_NETWORK_STATE.
- Current source scan found no AdMob or Firebase Analytics SDK in the Android bundle.
- Account passwords are stored as PBKDF2-SHA256 derived hashes with random salts; sessions use secure cookie controls.

## Owner-only / Play Console declarations still required

1. **Store listing support email — BLOCKING**
   - Google Play requires a public support email for the app.
   - The listing edit cannot validate or commit until this field is populated.
   - Do not use a personal address unless the owner explicitly approves making it public.

2. **Privacy policy**
   - In Play Console > Policy > App content, set:
     `https://wave-mawja.p-my.workers.dev/privacy`

3. **App access**
   - Confirm whether reviewers need login credentials to reach any material user-facing feature.
   - If credentials are needed, provide a stable reviewer account in App access.

4. **Ads declaration**
   - WAVE contains an internal advertising/campaign surface in the source.
   - Confirm the declaration based on the exact live behavior presented to ordinary users.

5. **Target audience and content**
   - Select the actual intended age groups.
   - Do not select children unless WAVE is intentionally designed for them and the Families requirements are satisfied.

6. **Content rating**
   - Complete the IARC questionnaire accurately for the streaming/catalog content and any user-generated or communication features that are enabled in the submitted build.

7. **Data safety**
   - Base answers on the RC15.13 source evidence, including account data, session/authentication data, watch/library/progress data, local preferences/downloads, operational/security logs, and any external processing actually enabled in production.
   - Do not declare data types that are not actually collected by the submitted build.
   - Keep the declaration aligned with the live privacy policy.

8. **Closed testing / production access**
   - If this is a qualifying new personal developer account, Google currently requires at least 12 testers opted into a closed test continuously for 14 days before applying for Production access.
   - After Play allows a non-draft closed release, move versionCode 15301 to completed on the closed track and add the required tester group/list.
   - Apply for Production access after the testing requirement is fulfilled.

## Release rule

Do not upload a different package or regenerate a different app identity. Continue only with `com.wave.mawja`.  
Do not replace versionCode 15301 unless a real Android code change requires a new versionCode.
