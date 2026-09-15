# THF Network Endpoint Release Policy V1

Status: ACTIVE / FAIL-CLOSED
Scope: ALL THF Android applications and games, including Apps, Fitness and Games factories.
Owner of PHONE_TEST_TARGET promotion: THF Release Factory.

## Incident that triggered this gate
A physical-phone Core test reached a dead `*.trycloudflare.com` hostname and Android WebView reported `net::ERR_NAME_NOT_RESOLVED`. This class of defect must not recur in another promoted phone candidate.

## Mandatory rule
No network-required APK may be promoted to `APK_CANDIDATE`, `PHONE_TEST_TARGET`, `PHONE_PASS`, `PLAY_CANDIDATE` or later if any required runtime endpoint is ephemeral, unresolved, unreachable, placeholder-only, localhost-only, or tied to a developer process.

Forbidden as release authority:
- `*.trycloudflare.com` / Cloudflare Quick Tunnel URLs
- localhost / 127.0.0.1 / emulator-only hosts
- temporary preview URLs whose lifetime is tied to a process/session
- placeholder/example domains
- HTTP endpoints when the product contract requires trusted HTTPS

Quick/preview tunnels may be used only for development and must never be embedded in a promoted phone artifact.

## Required pre-promotion endpoint gate
For every network-required application/game, Release Factory must inspect the exact APK payload/config and record all required base URLs/endpoints. Promotion fails closed unless all of the following pass for the exact artifact:
1. DNS resolution succeeds for every required hostname.
2. TLS/HTTPS verification succeeds without disabling certificate validation.
3. Required health/bootstrap endpoint returns an accepted success response.
4. Required application bootstrap/API contract is reachable, not only the web root.
5. Endpoint is stable/persistent and is not a Quick Tunnel or process-lifetime preview URL.
6. The exact URL/config found in the APK matches the endpoint that was health-tested.
7. Offline behavior is genuine and does not fabricate network/economy/social/ranked truth.
8. Network failure produces a usable retry/offline/error state instead of a blank/crashed UI.

For native games, the same gate applies to login, matchmaking, economy, content/bootstrap, telemetry or any other required network service before phone promotion.

## Build-time prevention
Candidate build/release workflows must fail if extracted APK/source/config contains `trycloudflare.com`, localhost, 127.0.0.1, obvious example/placeholder endpoints, or an empty required production/staging base URL.

A successful historical health check is insufficient. The gate must run again immediately before promotion/handoff because DNS/service state can change after build.

## Phone-test handling
If a pinned PHONE_TEST_TARGET later fails this gate, keep its SHA in history but mark it `PHONE_FAIL` or superseded with the exact reason. Never silently substitute a newer DEV_HEAD. Release Factory must deliberately promote the corrected exact APK.

## Current Core finding
The previously surfaced Core MobileFix1 QA artifact reached a dead `trycloudflare.com` endpoint during physical-phone testing and is therefore not acceptable network evidence for release promotion. The existing APK-first board target must not be treated as PHONE_PASS until Release Factory reconciles the physical-device failure and promotes a corrected artifact with a persistent endpoint.

## Architecture requirement
Production/staging phone candidates should use a stable hostname backed by a persistent service (for example a named Cloudflare Tunnel/custom hostname or another persistent HTTPS deployment). Backend endpoint configuration should remain environment-managed and auditable; secrets must not be embedded in APKs.

## Evidence required per product
Record in the candidate/release manifest:
- exact APK SHA-256
- package/version/source SHA
- exact non-secret endpoint host(s)
- DNS result
- TLS result
- health/bootstrap result
- timestamp of endpoint gate
- offline/error-state test result
- candidate state

No exception is implied by a successful compile, unit test, package check, signing check, or previous endpoint check.