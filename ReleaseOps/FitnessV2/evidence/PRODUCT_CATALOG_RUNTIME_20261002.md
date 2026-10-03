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

## 2026-10-03 Product UX continuation

### User-visible source

- Product source checkpoint: `aa824fd896e71af77bd9b1dc07b5d5f6ce621ef8`.
- First-run onboarding now captures goal, experience level, two-to-six training days, and available equipment in Arabic or English, stores the profile locally, and replaces the generic Today card with one concrete program action.
- The production path now exposes 26 structured bilingual offline programs above the 80-exercise catalog; every program has real sessions, exercise references, progression, safety, prescription, and provenance metadata.
- The mobile active-workout logger now renders each set as a two-column card with visible Load/Reps/RPE/RIR labels and a full-width completion target. It no longer depends on a 520 px horizontal table.
- Entered load, reps, RPE, and RIR remain durable before completion. The hidden primary navigation no longer leaves its 76 px bottom reservation under the sticky save/rest controls.

### Automated gates

- Local Product tests: `11/11 PASS`.
- JavaScript syntax: `PASS`.
- `git diff --check`: `PASS`.
- Previous exact onboarding candidate `4053c8d2fd96ea87ebd64371a57de17fd34012bb`: GitHub Actions run `37071113582` / run number `12`, source job `111050519670` and Android job `111050519376`: `PASS`; artifact `11254333671`, digest `sha256:5f8716570cfe695d8cb57fdf2f80f3853f0523fd7400036df94a723f380c8512`.
- Current source `aa824fd896e71af77bd9b1dc07b5d5f6ce621ef8`: GitHub Actions run `37092403671` / run number `13`, source job `111115323542` and Android job `111115323614`: `PASS`; artifact `11262691469`, digest `sha256:ccf9a917b9f603b3efd9aab0e21d027c9418215b23cdc871149eeca87a469c4e`.

### Managed-browser runtime evidence

- AppDeploy QA app: `thf-fitness-v2-product-qa-690eb6e-lwhy3h`.
- Final tested snapshot: `1790996999779`; QA timestamp `1790997025015`.
- Status: `ready`; frontend/network/backend errors: `0/0/0`.
- QA screenshot pair: `https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-v2-product-qa-690eb6e-lwhy3h/1790997029278/mobile.png` and `https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-v2-product-qa-690eb6e-lwhy3h/1790997029278/web.png`.
- The QA wrapper constrains the real app iframe to `390x844`; the measured inner runtime was `388x842` with a `373 px` content width after the scrollbar.
- Arabic `ar/rtl` and English `en/ltr` both measured document overflow `0 px`, logger width/scrollWidth `355/353 px`, and set-card width/scrollWidth `319/317 px`.
- The visible completion target measured `293x44 px`; all four field labels were visible in both languages.
- A real interactive set entry of `20 kg x 12 reps`, RPE `7`, RIR `3` produced `240 kg`, persisted through reload, and displayed `2 of 2 complete` / `2 من 2 مكتملة`.
- With `body.workout-active`, the sticky workout action computed to `bottom: 5px` instead of reserving the hidden navigation height.
- Browser QA verdict for this task: `4/5`. The one-handed logger and bilingual responsive behavior are evidence-backed; physical Android touch/keyboard ergonomics remain a separate Platform/device gate.

### Updated fail-closed boundary

The former eight-plan and broad mobile-sampling blockers are resolved in source, managed-browser QA, and the terminal current-source workflow. Product remains `PROGRESS`, not whole-product or release PASS, until broader real-device visual acceptance is reconciled with the Platform lane. Android packaging, Health Connect, signing, physical-device, and Play evidence remain outside Product ownership and are not claimed here.
