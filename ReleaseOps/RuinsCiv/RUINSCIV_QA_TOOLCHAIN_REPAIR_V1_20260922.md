# RuinsCiv Android QA toolchain repair V1

Recorded UTC: 2026-09-21T22:58:20Z

## Scope and truth status

- Product: RuinsCiv only.
- QA package: `com.topherofit.ruins.civ.phoneqa`.
- Production identity remains `com.topherofit.ruins.civ`; this checkpoint does not create or promote a production artifact.
- WAVE, THF Terra, and every other game/app source, template, signing identity, secret, database, OAuth client, and Play listing remain out of scope.
- `physical_device_status=PENDING` and `final_or_play_ready=FALSE`.

## Observed failed run

- Source commit: `8e04560bdc032a779fce3aa28f74f0b206b4e8a3`.
- Actions run: `35643232783`; job: `106477371376`.
- Remote build step duration: 34 seconds; workflow result: failure.
- Diagnostics artifact: `10659185526`, 2,191 bytes, digest `sha256:4625aa7345e92a8754e1de12058bb8a6f6ea49487564e4fe779414ea911e9a52`.
- No APK was produced. The short duration is consistent with the 30-second obsolete settings bootstrap and an immediate pre-import failure; authenticated logs/artifact contents were not available, so this remains a bounded inference rather than a claimed exit code.

## Corrective change

- Replace the invalid `editor_settings-4.tres` bootstrap with a deterministic isolated Godot 4.7 settings file at `editor_settings-4.7.tres`.
- Keep Android SDK, Java, and export-template discovery inside a disposable RuinsCiv-only HOME.
- Restore only the installed official Godot `4.7.2.stable/android_source.zip`; do not search or copy templates from Terra, WAVE, THF, or another candidate tree.
- Extract the template with absolute-path, parent-traversal, and destination-escape rejection.
- Require an executable Gradle wrapper and continue to reject legacy package/name markers before export.
- Require a bounded headless main-scene boot after import; retain its log and fail closed on a nonzero result.
- Require ZIP integrity plus `apksigner` certificate verification before accepting any APK hash or package evidence.

## Local gates

- YAML parser: PASS.
- Extracted remote Bash body syntax: PASS.
- JSON backlog parser: PASS.
- Git whitespace/error check: PASS.
- Six static isolation/runtime/package/readiness contract tests: PASS.
- High-confidence credential/private-key signature scan of all changed files: PASS (no match).

## Required remote evidence

The next real workflow run must independently prove Godot 4.7.2 import, Android template restoration, export, APK signature, package identity, target SDK 36, arm64 payload, archive integrity, required Stage16A-or-better avatar assets, and absence of legacy identities. Until that evidence exists, this is a toolchain repair checkpoint only—not an Android candidate, device pass, final build, Play-ready build, or Play upload.
