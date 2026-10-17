# Product visual QA fixture evidence — 2026-09-27

## Scope

This checkpoint closes part of the authenticated-surface evidence gap without using owner credentials. The live Top Hero Fit app now contains an explicit query-scoped visual QA fixture for `onboarding-ar`, `dashboard-ar`, `workout-ar`, `onboarding-en`, `dashboard-en`, and `workout-en`.

The fixture is deliberately non-privileged:

- It is enabled only by an explicit `visualQa` query value (or by a temporary capture constant during evidence generation).
- It never calls AppDeploy sign-in, never creates an auth token, and never reads or writes protected account state.
- Fixture workout/profile changes remain in React memory and are intercepted before protected API calls.
- A persistent amber banner states that it is a non-privileged visual fixture.
- External video embeds are suppressed in fixture mode so Stage16A remains the primary deterministic offline guide.
- The production root was restored to normal AppDeploy authentication before this checkpoint ended.

## Runtime evidence

### Arabic RTL onboarding

- AppDeploy source version: `1790499939566` (v56)
- QA timestamp: `1790499958940`
- Mobile: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790499962714/mobile.png
- Mobile SHA-256: `33de966811f06a574810c222f4965f270125a16e4e45d044317c6a60d9f65a2b`
- Web: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790499962714/web.png
- Web SHA-256: `2e214198a66cd746fc697b2c589a63544f7d95d79adac7a28b096f307657f621`
- Visual inspection: Arabic glyphs render correctly, RTL direction is correct, the premium dashboard hero and onboarding step one are visible, and the non-privileged boundary banner is legible.

### English LTR dashboard

- AppDeploy source version: `1790500005572` (v57)
- QA timestamp: `1790500022494`
- Mobile: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790500026414/mobile.png
- Mobile SHA-256: `86e123649cdcaf5906a1730d490f24a677dd7a844b09fc073a1a2b090196ef6e`
- Web: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790500026414/web.png
- Web SHA-256: `9cc3a4abfc853a62630889728be1fb44f7ddc6c7fc4cbdfe3541566592a0abda`
- Visual inspection: LTR hierarchy, metrics, navigation, and profile setup render without clipping; the fixture boundary remains visible.

### Restored production root

- Final AppDeploy source version: `1790500694233` (v63)
- QA timestamp: `1790500707991`
- Mobile: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790500731642/mobile.png
- Mobile SHA-256: `3b1ac322eb9f4026d833fae8fa268561fb6e8fec1cd5afdd5cce1ed96598817c`
- Web: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790500731642/web.png
- Web SHA-256: `ba19c001464503006ba6fee5c56dfa92d7ad5bcf7df7ce46560ddc7e1abf5c8e`
- Status: ready; frontend errors 0; backend errors 0; network errors 0.
- Visual inspection: normal signed-out authentication surface is restored and the real Stage16A human remains visible; no fixture banner or synthetic account state is exposed at the root URL.

## Test reconciliation

- `tests/tests.json` now has exactly one `sanity: true` test.
- Existing bilingual sign-in coverage now includes the non-privileged fixture boundary and external-embed suppression.
- No password, cookie, session token, or private credential was requested or used.

## Fail-closed boundary

The Arabic onboarding and English dashboard screenshots are visual composition evidence only. They are not backend-auth evidence and do not prove persistence. Temporary workout fixture versions became ready with zero surfaced runtime errors but AppDeploy returned no QA snapshot for those versions. Product remains `PROGRESS`; complete Arabic and English onboarding/dashboard/session evidence and real interaction evidence remain open.
