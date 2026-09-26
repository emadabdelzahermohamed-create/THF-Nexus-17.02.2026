# WAVE RC15.16 — Admin + Play checkpoint

Date: 2026-09-26  
Branch: `releaseops/wave-rc15-9-admin-rbac-20260918`

## Google Play listing

Public support email:
`TopHeroFit@gmail.com`

Store listing repair run:
- Run: `36237428268`
- Result: SUCCESS
- Listing update: HTTP 200
- Details update: HTTP 200
- Icon upload: HTTP 200
- Feature graphic upload: HTTP 200
- Four phone screenshots: HTTP 200
- Edit validate: HTTP 200
- Edit commit: HTTP 200

Persisted verification:
- title: WAVE MAWJA
- short description length: 61
- full description length: 607
- contact website: https://wave-mawja.p-my.workers.dev
- contact email: TopHeroFit@gmail.com
- icon count: 1
- feature graphic count: 1
- phone screenshot count: 4

## TWA / Digital Asset Links

Cloudflare deploy:
- Commit: `42214605dd193521fae0702fa5ffb0305c923bdc`
- Run: `36237447568`
- Result: SUCCESS
- Worker version: `5c964bf1-c35f-43a8-99b3-e932ed168569`
- `/.well-known/assetlinks.json`: HTTP 200

Google Play signing certificate:
`B7:78:50:F0:30:AA:7D:C9:FF:45:9F:FD:60:BA:50:0A:8C:C6:5A:89:98:34:91:2C:E3:C2:28:E6:0A:47:36:A0`

Asset Links rerun:
- Workflow run: `35986882634`, attempt 2
- Result: SUCCESS
- generatedApks API: HTTP 200
- live assetlinks: HTTP 200
- live fingerprint count: 1
- matchingStatement: true

## Admin/control source audit

Source audit run:
- Run: `36237638116`
- Result: SUCCESS

Verified:
- role guard: PASS
- ControlDashboard calls `/api/control`: PASS
- Control API GET: PASS
- Control API mutation handler: PASS
- standalone admin login page: PASS
- admin login API guard: PASS
- admin email allowlist implementation: PASS
- admin access-key secret implementation: PASS
- interactive dashboard controls/forms: PASS
- /admin alias -> /control: PASS
- /publisher alias -> /control: PASS

## Admin production configuration + authenticated E2E

Before configuration the live admin API returned HTTP 503 because production admin secrets were missing.

Production bootstrap:
- Commit: `a831da8aaed4740bc5c191baf578e7189588bc49`
- Run: `36237896854`
- Result: SUCCESS
- Admin email: `TopHeroFit@gmail.com`
- `WAVE_ADMIN_EMAILS`: installed as Cloudflare secret
- `WAVE_ADMIN_ACCESS_KEY`: installed as Cloudflare secret
- `WAVE_SESSION_SECRET`: installed as Cloudflare secret
- First two login attempts during secret propagation: HTTP 503
- Third login attempt: HTTP 200
- Authenticated GET `/api/control`: HTTP 200
- Authenticated account role: admin
- `canEdit=true`
- `canAdmin=true`
- Authenticated `/control`: HTTP 200
- Safe authenticated POST probe: HTTP 400 `invalid_action` as expected, proving the POST handler is reachable without mutating production data

Independent live readiness rerun:
- Run: `36237661322`, rerun attempt 2
- Result: SUCCESS
- Admin login page: HTTP 200
- Bad credentials: HTTP 401
- Admin configured: YES
- Unauthenticated control API: HTTP 401
- Unauthenticated control page: HTTP 307 to admin login
- /admin alias: HTTP 307
- /publisher alias: HTTP 307
- `WAVE_ADMIN_LIVE_READINESS=PASS`

No production admin access key is stored in Git.
