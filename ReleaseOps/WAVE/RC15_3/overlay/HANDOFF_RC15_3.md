# WAVE MAWJA RC15.3 — first-party auth + ABR/Data Saver evidence

Baseline: RC15.1 exact source artifact SHA-256 `a1d702b396df75e2738c4ed319dc2876432536c03d6eec08da498daf4cb3d30c`.

## Closed source gaps
- Replaced the mobile/worker sign-in dependency on `/signin-with-chatgpt` with a WAVE-owned `/login` flow and first-party session cookie. Legacy OpenAI authenticated headers remain accepted when WAVE is actually hosted by that environment, but mobile/worker sign-in no longer redirects to `chatgpt.site`.
- Added PBKDF2-SHA256 password derivation (210,000 iterations), random salts, hashed session tokens, Secure/HttpOnly/SameSite=Lax cookies, same-origin POST checks, safe local return paths, logout/revocation, and D1 schema for credentials/sessions.
- Made quality availability explicit: HLS renditions populate the selector; direct MP4 explains that no alternate qualities exist until HLS transcoding.
- Made Data Saver auditable in the UI. On HLS it caps to the lowest rendition, uses an 8-second forward buffer / 12-second maximum and zero back-buffer. On direct MP4 it explicitly reports the limited behavior (metadata preload only) instead of claiming bitrate savings.

## Validation completed here
- Python/source suite: **39/39 PASS**.
- Local `npm ci` could not be completed because the current isolated runtime timed out reaching the registry; therefore typecheck/build and Android compilation remain for the networked GCP builder.

## Release truth
No production deployment, production signing, Play approval, or physical-phone acceptance is claimed by this source handoff. Run `WAVE_RC15_3_EXECUTE_ONE_COMMAND.sh` on the networked builder, then test the generated APK on a physical phone.
