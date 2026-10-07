# THF Fitness Product — bilingual runtime and navigation checkpoint (2026-10-02)

## Scope

Product/UX only. This checkpoint does not claim Motion/GPU, phone, Health Connect, Play, or final visual PASS.

## Published source lineage

- Navigation/accessibility patch: AppDeploy `v64`, snapshot `1790568313260`
- Deterministic Motion capture patch: `v65`, snapshot `1790568519318`
- WebGL fail-closed guard: `v66`, snapshot `1790568670855`
- Current production with all three changes plus the Motion exercise blend: `v67`, snapshot `1790910310382`
- Application: `thf-fitness-pulse-ul26f1`
- Public URL: https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/
- Current deployment: `ready`
- Frontend/backend/network errors: `0/0/0`
- Production QA captures: `1790910512577/mobile.png`, `1790910512577/web.png`

## Runtime checks on v67

All checks used the explicit non-privileged, in-memory visual fixture. No account, token, protected write, or external video was used.

### Arabic RTL

- `?visualQa=onboarding-ar`
  - document `lang=ar`, `dir=rtl`
  - the Training Profile Setup region rendered
  - step 1/3 and “ما النتيجة الأساسية التي تريدها؟” rendered with the four goal choices
- `?visualQa=dashboard-ar`
  - document `lang=ar`, `dir=rtl`
  - localized navigation landmark “أقسام التطبيق” rendered
  - activating the distant “المنافسات” item changed its runtime `aria-current` from absent to `page`
  - the competition surface became visible
- `?visualQa=workout-ar&motionQaPhase=25`
  - Bodyweight Squat active workout rendered
  - session phase, set 1/3, 40 s work, 45 s rest, muscle/technique control and next exercise were visible
  - absence of WebGL produced a localized in-flow error state rather than a blank page

### English LTR

- `?visualQa=onboarding-en`
  - document `lang=en`, `dir=ltr`
  - “Three steps to a plan that fits”, step 1/3, “What is your primary outcome?” and the four goal choices rendered
- `?visualQa=dashboard-en`
  - document `lang=en`, `dir=ltr`
  - navigation landmark “App sections” rendered
  - activating the distant “Competitions” item changed its runtime `aria-current` from absent to `page`
  - the competition surface became visible
- `?visualQa=workout-en&motionQaPhase=50`
  - Bodyweight Squat active workout rendered
  - the same session/set/rest/next-movement journey rendered in English
  - absence of WebGL produced the English canonical-render-unavailable state and retained the workout UI

## Product source contract verified in production

- localized navigation landmark
- `aria-current=page` on the active section
- keyboard-visible focus ring
- RTL/LTR horizontal scroll snapping
- persistent thin overflow affordance at mobile width
- non-privileged fixture boundary remains visible
- external video is suppressed only in fixture mode
- no blank-page regression when Stage16A WebGL construction fails

## Gate

`PROGRESS`, not `PASS`.

The old credit-limit blocker is resolved and the staged navigation patch is deployed. Product interaction and bilingual direction are runtime-proven. Final Product visual PASS remains open until screenshot/video artifacts cover the premium onboarding/dashboard/active-workout composition at mobile dimensions in both languages and the Motion lane supplies GPU-rendered Stage16A evidence inside that same workout flow.
