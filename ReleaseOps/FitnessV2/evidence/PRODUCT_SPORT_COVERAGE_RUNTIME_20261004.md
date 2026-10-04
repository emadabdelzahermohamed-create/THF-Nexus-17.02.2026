# Fitness V2 sport coverage and runtime evidence — 2026-10-04

## Ownership and exact source

- Product/UX/content only on `release/fitness-v2-rebuild-20261002`.
- Expanded catalog source commit: `9ad838d6c879a375572067e46c8e55b5ab64e892`.
- Accessibility-localization fix: `ac1498d0e7da0cb4a493737876fafd3ab8bf66be`.
- Android, Health Connect, signing, Play, and release workflows were not edited by this lane.
- Stage16A remains absent from the production Product HTML/CSS/JavaScript runtime path.

## Catalog provenance and coverage

- Source dataset: `yuhonas/free-exercise-db`, pinned at `f00c92c7dcf1216a928a52c3706c7ce8e2f71ed5`.
- License: Unlicense / public-domain dedication, retained per item.
- Added in this checkpoint: 32 bilingual exercises and 64 offline start/finish frames.
- Total: 112 exercises, 224 bundled offline frames, 13 populated sections, and 26 structured programs.
- Generated catalog SHA-256: `2dd7d0e67fdcbb9899825f84b49bee0026808b1ecb7cd16d2eb7c9b75b3c5914`.
- Generated programs SHA-256: `246d82384809e2adb6b444b6da89c71ee1dda38cce09e28df840bec3b76cad3b`.

| Section | Exercises |
|---|---:|
| Gym | 36 |
| Home | 10 |
| Running & walking | 6 |
| Cycling | 6 |
| Football | 6 |
| Swimming | 6 |
| Yoga & Pilates | 6 |
| Calisthenics & gymnastics | 6 |
| Boxing & martial arts | 6 |
| HIIT & cardio | 6 |
| Mobility & stretching | 6 |
| Recovery | 6 |
| Racket & team conditioning | 6 |

All 64 new frames were reviewed together in a generated contact sheet. `Wind_Sprints` was rejected because its media depicted a hanging-leg-raise motion and was replaced by the license-compatible `Prowler_Sprint` source item before checkpointing.

## Automated gates

- Product tests: `12/12 PASS`, including a regression test for localized accessible names.
- Existing source/Health contract tests: `12/12 PASS` (read-only cross-lane verification).
- Existing backend tests: `8/8 PASS` (read-only cross-lane verification).
- JavaScript syntax, Python compilation, generated JSON validation, `git diff --check`, and production-runtime Stage16A scan: `PASS`.
- GitHub Actions run `37163629596` (run number 19), exact source `ac1498d...`:
  - source/backend job `111322001291`: `SUCCESS`.
  - Android build job `111322001417`: Gradle/unit/lint/APK/release-AAB/signing step `SUCCESS`; exact-package inspection `FAILURE` because the Platform-owned workflow still asserts exactly `160` demo images while this candidate correctly contains `224`.
  - Package evidence produced before that stale assertion: `com.topherofit.thf.pulse`, versionCode `51003`, compile/target SDK `36`.
  - Artifact upload was skipped after the inspection failure; no Android artifact PASS is claimed.

## Managed-browser runtime evidence

- Isolated AppDeploy QA app: `thf-fitness-v2-product-qa-690eb6e-lwhy3h`.
- Live QA URL: `https://thf-fitness-v2-product-qa-690eb6e-lwhy3h.v2.appdeploy.ai/`.
- Final snapshot: `1791072522792`; QA timestamp `1791072547070`.
- AppDeploy QA state: `ready`; frontend/network/backend errors: `0/0/0`.
- QA screenshots: `https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-v2-product-qa-690eb6e-lwhy3h/1791072551210/mobile.png` and `https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-v2-product-qa-690eb6e-lwhy3h/1791072551210/web.png`.
- The QA host received the exact `app.js`, `index.html`, `exercises.js`, and `programs.js` bytes from `ac1498d...`. Transport-only SHA query parameters were added in the isolated QA index to invalidate stale CDN/browser copies; production was not deployed or changed.
- English `en/ltr` runtime showed `26 programs · 112 documented exercises`, fully localized `Training content type`, `Training sections`, `Clear search`, and close-control accessible names.
- Arabic `ar/rtl` runtime showed `26 برنامجًا · 112 تمرينًا موثقًا` and the corresponding Arabic navigation, search, section, and close-control names.
- Both languages exposed the exact section counts above. The expanded Cycling section returned six real exercises.
- `Recumbent Bike` / `دراجة ثابتة بمقعد خلفي` rendered both offline start/finish images and the complete bilingual contract: section, muscles, equipment, level, movement, goal, setup, three execution steps, breathing, prescription, mistakes, regression, progression, safety, and provenance disclosure.

## Runtime defect found and fixed

The first exact-source browser pass exposed Arabic-only accessible names after switching to English for the training tablist, section rail, search clear control, chart, onboarding benefits, and modal close controls. Commit `ac1498d...` adds generic `data-i18n-aria-label` handling plus AR/EN copy and a source regression test. The final QA snapshot verifies the correction in English and Arabic.

## Fail-closed boundary and next work

This is Product `PROGRESS`, not whole-product or release closure. The previous thin-section blocker is resolved. Remaining Product work is broader mobile visual sampling across the newly added sections and continued editorial/media review; Platform must update the package invariant from 160 to 224 (preferably derive it from the catalog) and rerun the exact candidate. Physical Android, Health Connect, Samsung Health, signing, and Play remain outside Product ownership and are not claimed.
