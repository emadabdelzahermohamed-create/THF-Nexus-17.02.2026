# WAVE RC15.19 — Google Play App Access and Reviewer Notes

Recorded UTC: 2026-09-26T22:47:00Z  
Product: WAVE_MAWJA  
Package: `com.wave.mawja`  
Exact Android candidate: versionCode `15302`, versionName `1.0.0-rc15.15-twa-fix`  
Live origin: `https://wave-mawja.p-my.workers.dev`

## Purpose

This checkpoint prepares evidence-backed Google Play App Access answers and reviewer navigation notes without storing credentials in Git or changing the approved Android artifact.

## Recommended App Access declaration

Consumer functionality is available without a privileged account:

- Home, catalog, search/filtering, legal open-license content, live page, download information, privacy, terms, child-safety information, and account-deletion instructions are publicly reachable.
- Playback of the legal sample catalog does not require an account after the on-device age-band choice.
- Optional consumer account features use first-party, self-service registration inside WAVE. A reviewer can choose **Create account** and enter a name, email address, and password; there is no external identity provider or invite-only membership gate.
- `/profile` redirects unauthenticated users to `/login?return_to=%2Fprofile`.
- `/admin` and `/publisher` are protected operational control-plane aliases. They are not required to review the consumer Android experience and must not be opened with shared production-admin credentials.

Recommended truthful Console choice:

> Some optional account functionality requires login, but no special membership, paid subscription, geographic entitlement, or externally issued credential is required for the consumer app. Reviewers may create a normal account directly in the app. Administrative control-plane access is not part of the consumer app review path.

Do not publish or store a production admin key, reusable reviewer password, OTP, or session token in Git.

## English reviewer instructions

1. Launch WAVE MAWJA versionCode 15302.
2. At the privacy-preserving age prompt, choose **18+** to review the complete legal sample catalog. No date of birth is collected.
3. Open **Movies / Browse** to view and filter the public catalog.
4. Open **Sintel** to verify the public player. The title is an open-license Blender Foundation sample (CC BY 3.0).
5. The player exposes automatic/manual quality status, Data Saver status, offline/download entry, subtitles/license metadata, and related titles where supported by the source.
6. Open **Live** to inspect the official NASA source presentation.
7. Account-only features are optional. If needed, open **Sign in**, select **Create account**, and register a normal test account inside WAVE using reviewer-controlled details.
8. Open the profile to test account management and in-service deletion. Public deletion instructions are also available at `/delete-account`.
9. Do not use the Admin or Publisher routes; they are a separate protected operational control plane and are not needed to review the consumer application.

## إرشادات المراجع بالعربية

1. شغّل WAVE MAWJA بالإصدار `15302`.
2. اختر فئة **18 سنة فأكثر** من نافذة العمر لمراجعة المكتبة القانونية كاملة؛ لا يجمع التطبيق تاريخ الميلاد.
3. افتح **أفلام / استكشف** لمراجعة البحث والفلاتر والمكتبة العامة.
4. افتح **سينتل** لمراجعة المشغّل العام ومعلومات الترخيص CC BY 3.0.
5. راجع حالة الجودة وموفر البيانات والتنزيل المصرح والترجمة ومعلومات الحقوق حسب دعم المصدر.
6. افتح **مباشر** لمراجعة عرض المصدر الرسمي لـNASA.
7. الحساب اختياري. لاختبار خصائص الحساب، افتح **دخول موحّد** ثم **حساب جديد** وأنشئ حسابًا عاديًا ببيانات يتحكم فيها المراجع.
8. اختبر إدارة الحساب والحذف من الملف الشخصي؛ وتوجد تعليمات عامة في `/delete-account`.
9. لا يحتاج مراجع تطبيق المستهلك إلى مساري Admin أو Publisher؛ فهما لوحة تشغيل محمية منفصلة.

## Live verification evidence

Public browser verification on 2026-09-26 UTC:

| Route | Observed result |
|---|---|
| `/` | WAVE home rendered with Arabic/English language controls and age-band prompt |
| `/browse` | Public catalog rendered; four open-license titles and filters were visible |
| `/watch/sintel` | After hydration, `data-wave-age-band=adult`, no age lock, one HTML video element, public MP4 source present |
| `/live` | Official NASA live-source presentation rendered |
| `/downloads` | Authorized offline/download UI and Android test download information rendered |
| `/login` | Sign-in and self-service **Create account** tabs rendered |
| registration tab | Name, email, password, and **Create account** controls rendered; no external login/invite control |
| `/profile` unauthenticated | Redirected to `/login?return_to=%2Fprofile` |
| `/admin` | Redirected to protected `/admin-login?return_to=%2Fcontrol` |
| `/publisher` | Redirected to protected `/admin-login?return_to=%2Fcontrol` |
| `/delete-account` | Public Arabic account-deletion instructions rendered |

Player evidence after client hydration:

- final URL: `https://wave-mawja.p-my.workers.dev/watch/sintel`
- age band: `adult`
- age lock: absent
- video element count: `1`
- media source observed: `https://archive.org/download/Sintel/sintel-2048-stereo_512kb.mp4`

## Existing release evidence reused, not rerun

- Live account E2E: run `35985314664`, attempt 2, PASS.
- Internal upload 15302: run `35986508330`, PASS.
- Consolidated readiness: run `36243068952`, PASS.
- Data Safety submission: run `36243903548`, HTTP 204, PASS.
- Exact Play APK privacy inspection: run `36243580600`, PASS.
- Cloudflare Auth Gate at prior checkpoint: run `36260456546`, PASS.

## Remaining boundary

This checkpoint prepares App Access/reviewer evidence only. It does not claim Play Console App Access submission because the standard Android Publisher Edits API does not expose the full App Content questionnaire and no authenticated Play Console session was available in this non-interactive run.

Production access remains externally blocked by the closed-testing prerequisite tracked in issue #39. Preserve versionCode 15302 and do not repeat already-PASS gates unless the artifact or source changes.
