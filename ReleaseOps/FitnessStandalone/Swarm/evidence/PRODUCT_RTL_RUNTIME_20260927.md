# Product RTL runtime evidence — 2026-09-27

Lane: Product/UX only
Branch: `automation/fitness-swarm-product-20260924`
Live app: https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/

## Completed scope

- Added a deterministic Arabic webfont from the official `google/fonts` repository and applied it to RTL content.
- Synchronized `document.documentElement.lang` and `dir` with the Arabic/English locale state.
- Removed the unsupported arrow glyph from the signed-out CTA and centered its bilingual label.
- Preserved the existing product hierarchy and motion renderer contract; no Backend, Android, or Motion code was changed by this Product task.

## Font provenance

- Repository: `google/fonts`
- Source commit: `23e54b51ddffbc7713c583748e3bd86f62b1fa4a`
- Path: `ofl/notosansarabic/NotoSansArabic[wdth,wght].ttf`
- Blob: `f1d01edce4ebaedcbe9a06fc75fec07b304ec3df`
- Size: 844,676 bytes
- License directory contains `OFL.txt` (SIL Open Font License 1.1).

## Deployment and QA evidence

First Arabic-font snapshot:

- AppDeploy snapshot: `1790482095465`
- QA screenshot run: `1790482112107`
- Result: complete Arabic glyph rendering was restored; the CTA arrow was still an unsupported glyph.

Final Product snapshot:

- AppDeploy snapshot: `1790482175088`
- QA timestamp: `1790482188855`
- Mobile screenshot (390×844): https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790482197004/mobile.png
- Mobile SHA-256: `c3b9e686c9e0f7b967be1e0ba5f3f6e4a3544217ad945210e6467271188ec0bc`
- Web screenshot (1280×720): https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790482197004/web.png
- Web SHA-256: `394a485a85850bde9895923ffcbf7fffa1220eb975b085e9ef961ea1e5cc5978`
- Frontend errors: 0
- Backend errors: 0
- Network errors: 0

Visual inspection confirms complete, legible Arabic text on the public mobile and web surfaces, a centered bilingual sign-in CTA, and no missing-glyph box.

## Fail-closed boundaries

This evidence does **not** mark the Product lane PASS:

- The captured session is signed out; authenticated onboarding, dashboard, and workout/session screens remain without runtime screenshots.
- English LTR switching is implemented and covered by source/test assertions but is not visually proven by this screenshot run.
- The Stage16A canvas remains blank in this run. That is recorded as a Motion-lane blocker and is not counted as Product visual success.
- No physical-device, GPU, Android, Health Connect, Play, or full visual PASS is claimed.

Result: **PROGRESS**.
