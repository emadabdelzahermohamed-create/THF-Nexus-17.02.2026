# WAVE RC15.17 — Release Readiness Checkpoint

Date: 2026-09-26
Branch: `releaseops/wave-rc15-9-admin-rbac-20260918`

## Automation

Active automation: `WAVE Release Autopilot`
Schedule: hourly at minute 45, timezone Africa/Cairo.
Execution contract: continue from latest Git checkpoint, WAVE only, no repeated PASS gates, persist every meaningful result.

## Security

The previously exposed WAVE admin access key was rotated.
Rotation workflow:
- commit: `a431df2283f05be03b200ee6460bb75da8966183`
- run: `36239304270`
- result: SUCCESS
- rotated login: HTTP 200
- authenticated `GET /api/control`: HTTP 200
- role: admin
The old key is no longer valid. No plaintext admin key is stored in Git.

## Consolidated release readiness

Workflow:
`.github/workflows/wave-release-readiness-matrix.yml`

Successful run:
- run: `36243068952`
- head SHA: `e7357aaee4478d96b6fca06384f6fef3b5ed19c7`
- result: SUCCESS

Verified API calls:
- Play edit insert: HTTP 200
- tracks: HTTP 200
- app details: HTTP 200
- Arabic listing: HTTP 200
- closed testers: HTTP 200
- generated APKs for versionCode 15302: HTTP 200
- Android Publisher discovery document: HTTP 200

Current release state:
- package: `com.wave.mawja`
- Android versionCode: `15302`
- Internal track: `completed:15302`
- Closed track `wave-closed-readiness`: `draft:15302`
- Production track: EMPTY
- Closed tester Google groups: 0
- Store title: `WAVE MAWJA`
- Public support email: `TopHeroFit@gmail.com`
- Contact website: `https://wave-mawja.p-my.workers.dev`
- generated APK metadata: PASS
- Android Publisher Data Safety API: AVAILABLE

## Current highest-priority release blockers

1. Complete an accurate Google Play Data Safety declaration matching the shipped implementation.
2. Complete remaining Play App Content declarations that are not exposed through the standard Edits API.
3. Add/qualify the required closed testers if this developer account is subject to Google's production-access testing requirement.
4. Request/promote Production only after policy/test gates are satisfied.

Previously closed:
- Store listing support-email blocker: CLOSED.
- Android 15301 TWA crash: CLOSED in 15302.
- Digital Asset Links / Play-signing fingerprint mismatch: CLOSED.
- production admin-secret 503: CLOSED.
