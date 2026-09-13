# Android Physical-Device Acceptance Protocol — V1 — 2026-09-13

Purpose: prevent a repeat of the prior condition where an APK passed build/signature checks but failed at runtime because Godot project data or service configuration was missing.

## Candidate identity lock

Before installation, the APK SHA-256 must exactly match the ReleaseOps integrity checkpoint. A device result from any other hash is not evidence for the current candidate.

Current candidate hashes:

- THF Core RC6: `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`
- THF Terra RC34: `388f3c09bd8e0d64ebb5ad5e9c10b92d3b17f05851949936a07fb5b3db5b18c7`
- THF Rift RC37: `fe35328b6ec4ed98a4c26cd5067e8056310fd773d9a3e7c3212943249eb024b1`

## Mandatory checks per app

1. Install succeeds through Android Package Installer without package parse/signature failure.
2. Cold launch from launcher succeeds after force-stop; no immediate process exit, Godot error dialog, missing `.pck`/project-data error, or blank fatal screen.
3. Package identity and displayed version correspond to the candidate lane.
4. Core: service-connected screen must initialize against the staging HTTPS endpoint; the old `service not configured` state is a FAIL.
5. Terra/Rift: initial Godot scene must render, accept touch/input, and remain alive for at least 60 seconds. Missing project data, renderer initialization failure, or crash is a FAIL.
6. Background/foreground cycle once, then resume successfully.
7. Rotate/orientation behavior must not cause fatal restart if the app allows rotation; otherwise the declared orientation must remain stable.
8. Network loss/recovery must fail gracefully for network-dependent surfaces; no secret/token material may be displayed in UI or logs.
9. Re-launch after process kill must succeed.
10. Record device model, Android version, install timestamp, APK SHA-256 and PASS/FAIL notes.

## Evidence classification

- `DEVICE-PASS`: all mandatory checks pass for the exact candidate hash.
- `DEVICE-FAIL-RUNTIME`: installation works but runtime/interaction fails.
- `DEVICE-FAIL-INSTALL`: Android Package Installer refuses the exact candidate.
- `DEVICE-INCONCLUSIVE`: candidate hash or observed package/version cannot be proven.

A CI PASS is never promoted automatically to DEVICE-PASS.

## Promotion gate

Only after DEVICE-PASS may a candidate proceed to final production-signing preparation / Play Internal readiness. This protocol does not authorize production signing, Play publication, Cloudflare production cutover, token transactions, or destructive cloud actions.

## WAVE isolation

WAVE_MAWJA does not inherit THF device evidence. WAVE must receive its own candidate identity, SHA-256 and device acceptance only after the exact RC13/RC14 canonical runtime/source is recovered and verified. Older RC9 material must not be substituted.
