# WAVE RC15.18 — Google Play Data Safety Submitted

Date: 2026-09-26  
Package: `com.wave.mawja`  
Android release reference: `versionCode 15302`

## Result

Workflow: `.github/workflows/wave-data-safety-submit.yml`  
Commit: `c061266e5e052351b812e6230ac34b6de12c3568`  
Run: `36243903548`  
Result: **SUCCESS**

Google Play Data Safety API:
- `POST /androidpublisher/v3/applications/com.wave.mawja/dataSafety`
- HTTP: **204**
- `WAVE_DATA_SAFETY_SUBMIT=PASS`

## Pre-submit gates

- Live privacy policy: `https://wave-mawja.p-my.workers.dev/privacy` — HTTP 200
- Live account deletion page: `https://wave-mawja.p-my.workers.dev/delete-account` — HTTP 200
- Exact Google Play-generated APK re-inspection: PASS
- package: `com.wave.mawja`
- versionCode: `15302`
- no Camera permission
- no Microphone permission
- no Location permission
- no AD_ID permission
- no AdMob SDK markers
- no Firebase Analytics markers

## Declaration generation

The workflow fetched Google's current public Data Safety CSV template, blanked sample/default response values, appended the newer account/deletion rows required by the Publisher API when absent from the public sample, and filled only WAVE's evidence-backed declarations.

Generated schema:
- rows: 775
- populated answer keys: 41
- CSV generation: PASS
- API validation/submission: PASS

Declared collected data is limited to WAVE account/service data supported by the implementation evidence, including name/display name, email, account identifiers/metadata, language/locale preference, and account interaction/progress data. No third-party advertising SDK or Android advertising identifier was declared.

This closes the Google Play Data Safety blocker for the current 15302 release.
