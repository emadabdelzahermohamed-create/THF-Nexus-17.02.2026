# Fitness V2 Product catalog and runtime evidence — 2026-10-02

## Scope and source

- Product/UX/content only on `release/fitness-v2-rebuild-20261002`.
- Source checkpoint: `690eb6e6e6a1f3d4e76549fc1d708fbbc7f7df6f`.
- Stage16A is absent from the production Product HTML/CSS/JS path.
- Android, Health Connect, signing, and release ownership were not edited.

## Catalog provenance

- Source: `yuhonas/free-exercise-db`, pinned commit `f00c92c7dcf1216a928a52c3706c7ce8e2f71ed5`.
- License: Unlicense / public-domain dedication.
- License SHA-256: `6b0382b16279f26ff69014300541967a356a666eb0b91b422f6862f6b7dad17e`.
- Dataset SHA-256: `5bb747e3fc658f095a60dcbf6d53c96627acdcc6ffb6fffde86f7e26995d40bf`.
- Generated catalog SHA-256: `c9a12c066277fc362fe752624b5c0c2e4860f0f1c53c9d7fc79109f4c5779ab7`.
- 80 bilingual exercises, 13 populated sections, and 160 hash-verified offline demo frames.

## Automated gates

- Product tests: 6/6 PASS after the input-persistence fix.
- Existing V2 source/Health contract: 5/5 PASS (read-only cross-lane check).
- Existing backend tests: 3/3 PASS (read-only cross-lane check).
- JavaScript syntax and `git diff --check`: PASS.
- GitHub Actions lookup for `690eb6e...` returned no associated PR-triggered run; no CI PASS is claimed.

## Runtime QA

- AppDeploy QA app: `thf-fitness-v2-product-qa-690eb6e-lwhy3h`.
- Latest QA deployment snapshot: `1790930664960`; QA timestamp `1790930694667`.
- State: ready; frontend/network/backend errors: 0/0/0.
- Arabic `ar`/`rtl`: Today has one next action; Barbell Bench Press renders both 850×567 frames and the complete guidance/safety/provenance contract.
- Active workout: load/reps/RPE/RIR, warm-up/working sets, rest timer, and volume work. A 40×8 plus 70×8 session produced `880 kg` and persisted after full reload with one workout and one PR.
- English `en`/`ltr`: `squat` search plus `barbell` and `squat` filters returned two real results; Barbell Squat rendered both 850×567 frames and the full English contract.
- All 13 sections returned positive counts and a loaded 850 px representative image: Gym 36, Home 10, Running/Walking 3, Cycling 2, Football 2, Swimming 2, Yoga/Pilates 4, Calisthenics/Gymnastics 6, Boxing/Martial Arts 2, HIIT/Cardio 6, Mobility/Stretching 3, Recovery 2, and Racket/Team Conditioning 2.

## Runtime defect found and fixed

The active-workout inputs listened only for `change`. Runtime testing reproduced a path where completing a set before a reliable blur persisted a zero load. Inputs now persist on `input` without rerendering the focused row, so the entered load contributes to volume. A source contract test prevents regression.

## Fail-closed boundary

This is Product `PROGRESS`, not V2 visual closure. The legacy eight-plan baseline still needs replacement by a structured bilingual program library, and broader mobile visual sampling remains open. Android packaging, physical device, Health Connect, signing, and Play remain owned by the Platform lane and are not claimed here.
