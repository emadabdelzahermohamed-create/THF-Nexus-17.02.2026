# WAVE RC15.14 — live account resilience result

Date: 2026-09-24

Production deploy:
- Commit: `8cf20699474f5ef857ab61e674984631d7c70655`
- GitHub Actions run: `35985605091`
- Result: PASS
- Cloudflare version: `d01acdd9-ffdb-4bea-83e9-9187853af80c`
- Live URL: https://wave-mawja.p-my.workers.dev

Root cause:
- Production D1 schema was verified read-only and contains all expected `user_accounts` columns.
- Account GET was failing because optional MEDIA_API account synchronization could throw and convert a valid first-party account read into HTTP 500.
- RC15.14 makes all three account synchronization calls best-effort while keeping the local D1 account lifecycle authoritative and functional.

Live E2E rerun:
- Workflow: `WAVE Live Account E2E`
- Run: `35985314664`, rerun attempt 2
- Result: PASS
- Public routes: /, /login, /privacy, /terms, /browse, /live, /downloads => HTTP 200
- Register => HTTP 200
- GET /api/account => HTTP 200
- /profile => HTTP 200
- Logout => HTTP 303
- Login => HTTP 200
- DELETE /api/account => HTTP 200
- Login after deletion => HTTP 401

Acceptance:
`WAVE_LIVE_ACCOUNT_E2E=PASS`
