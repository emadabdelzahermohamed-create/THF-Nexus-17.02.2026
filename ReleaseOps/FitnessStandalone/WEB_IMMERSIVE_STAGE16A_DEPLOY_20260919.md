# THF Fitness — Immersive Stage16A production Web gate

Date: 2026-09-19
Scope: THF Fitness / Pulse standalone only. WAVE-MAWJA untouched.

## Production deployment
- AppDeploy app: `thf-fitness-pulse-ul26f1`
- Live URL: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`
- Source snapshot: `1789798972531`
- Terminal deployment status: `ready`
- Post-deploy QA: frontend errors `0`, backend errors `0`, network errors `0`.
- QA screenshot capture timestamp: `1789798987908`.

## User-visible change
- Active workout now embeds the canonical Stage16A renderer directly inside the session instead of limiting the 3D surface to the Coach tab.
- Session composition now has a dominant motion-coach viewport, current-move overlay, session progress bar, exercise progress count, current rest target and direct technique/log-set actions.
- Existing warm-up/work/rest/cool-down, exercise logging and completion flows remain in the same active session.
- Stage16A renderer now enables soft shadow mapping and ACES filmic tone mapping, adds key-light shadow casting, floor shadow reception and tighter camera framing.
- Canonical asset URL and no-legacy-fallback behavior remain unchanged. Contract remains 137 joints / 195 clips.

## Test reconciliation
`tests/tests.json` remains a five-workflow suite. The sanity workout test now explicitly requires the canonical Stage16A motion-coach stage inside the active workout while retaining persistence; exercise discovery, sports/wellness, trainer authorization, competitions/recovery/AI Coach and Stage16A contract coverage remain present.

## Evidence boundary
This gate proves successful Web deployment and AppDeploy browser/runtime QA with zero reported frontend/backend/network errors. It does **not** prove physical Android GPU quality, all 195 animation clips, Health Connect runtime permissions, sensor/form verification, Web↔Android cross-device synchronization, production Android signing or Play Internal publication. Those remain fail-closed.
