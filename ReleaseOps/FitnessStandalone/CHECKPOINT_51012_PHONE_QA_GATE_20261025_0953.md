# Fitness 51012 candidate identity and phone-QA gate — 2026-10-25

## Scope

Physical-phone QA lane for `com.topherofit.thf.pulse`. This checkpoint records a newly built exact candidate and the current device gate. It does not claim phone, Google Play Internal promotion, or Production acceptance.

## Exact candidate

- Canonical source branch: `agent/codex/fitness-recovery/20261023`
- Source SHA: `cb425fef23b8541499acb02cecd8b86312b0eb34`
- Source change: merge of PR #87 (keyboard focus visibility)
- Workflow: Fitness Activity Candidate Build
- Run: `40163572486` — completed / success
- Artifact: `12586864799`
- Artifact name: `fitness-activity-candidate-51012`
- Artifact archive size: `37506227` bytes
- Artifact archive SHA-256: `ac0adffe4f56787da049e69b4deae30269e59a0e68a8c2bc82b11edbac624279`
- Version code recorded by the artifact: `51012`
- Debug APK SHA-256: `a8d6a6b2b987134eae80da7f43081117b1f519a3bb9505f757e0547c58ab6c40`
- Release AAB SHA-256: `eae15bec8d0b38d63c23531a3aa6113db9e4896be5d6da9e192a405f34bb6479`

The workflow log ends with `BUILD SUCCESSFUL in 2m 2s` and includes unit tests, lint, debug APK assembly, and release bundle generation. These are build gates only.

## Device observation

A single bounded read-only ADB check returned:

```text
List of devices attached

error: no devices/emulators found
```

No reconnect loop, install, launch, data clearing, or interaction was attempted. The user's workout state and phone data were not touched.

## Release truth

- The earlier signed 51012 Play Internal artifact remains separately evidenced from source `29bfe57d58b84a5391e201120888d053f54ed055`, build run `40125830819`, artifact `12572602451`, promotion run `40126227388`, signed AAB SHA-256 `c5ae818b45d9775b1850dae9fb36f8c211ac6b9141c4117f17d85da54e56a374`.
- This newer source candidate `cb425fef...` has not been installed on the phone and has not been promoted to Play.
- No Phone PASS and no Production PASS.

## Remaining physical gates

When ADB becomes available and this exact APK remains the newest candidate:

1. Confirm package/version and installed artifact identity.
2. Install/upgrade without clearing user data.
3. Verify collapsed and expanded ongoing notification metrics plus Stop.
4. Verify Home and screen-off continuity without interrupting an active workout.
5. Verify Health Connect provenance and voice where feasible.
6. Capture logcat/crash/ANR and screenshots only where useful.

If a newer source/artifact exists first, supersede this candidate and do not spend a run testing stale bytes.
