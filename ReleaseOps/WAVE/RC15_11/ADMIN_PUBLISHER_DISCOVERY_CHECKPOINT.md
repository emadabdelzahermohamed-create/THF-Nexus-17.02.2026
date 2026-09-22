# WAVE RC15.11 — Admin/Publisher discoverability checkpoint

Recorded UTC: 2026-09-21T23:20:15Z

## Scope

- WAVE_MAWJA only, based on remote checkpoint `d6a5774be03a8140aa27e01a74ff38f28a359540`.
- No Media, Arena Social, OnePublish, THF, Fitness, RuinsCiv, database, secret, signing, package, or Play listing was touched.

## Verified pre-change runtime

- `/`, `/browse`, `/live`, `/offline`, `/downloads`, and `/admin-login` returned HTTP 200.
- Unauthenticated `/control` returned HTTP 307 to `/admin-login?return_to=%2Fcontrol`.
- Unauthenticated `/api/control` returned HTTP 401.
- `/admin` and `/publisher` returned HTTP 404.
- RC15.10 media-runtime workflow run `35474676266` passed source invariants, live media surfaces, and the production media-binding check. Its evidence artifact `10593078146` is 617 bytes with digest `sha256:4e60bad04b13d3cd1dcae32627617de9d436ba9e6cf6f45701229346481cdd80`.

## Change

- Add server-only `/admin` and `/publisher` entry routes that redirect to the existing guarded `/control` surface.
- Keep authentication and `viewer | publisher | admin` authorization in the existing control implementation; the aliases duplicate no session or role logic.
- Extend cumulative source/build/deployment gates to test the aliases and require exact live redirect behavior.

## Local gates

- Alias authorization-boundary contract tests: 2/2 PASS.
- Four changed workflow YAML documents: parser PASS.
- Embedded Bash in all four changed workflows: syntax PASS.
- RC15.11 state JSON: parser PASS.
- Git whitespace/error check: PASS.
- High-confidence private-key/token signature scan of changed files: PASS with no match.

## Truth boundary

This checkpoint is not deployed until the remote build/deploy workflow succeeds and live smoke proves both aliases. It does not change Android or upload anything to Google Play, and it is not a FINAL claim.
