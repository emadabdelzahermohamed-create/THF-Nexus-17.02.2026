# THF Fitness release checkpoint — 2026-10-27

## Verified release outcome
- Android package: `com.topherofit.thf.pulse`
- Candidate version code: `51019`
- Candidate version name: `5.0.0-v2-alpha19-debug` (the debug APK identity recorded by the candidate workflow)
- Target SDK: `36`
- Candidate source commit: `76053bd9127c38d8065eb7ac250bdeb34ab67854`
- Candidate workflow run: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/40516382792
- Candidate artifact: `fitness-activity-candidate-51019-76053bd9127c38d8065eb7ac250bdeb34ab67854`
- Candidate artifact SHA-256 (artifact ZIP digest): `sha256:88699e2865cacc4cc8e157a7863721c0634a1b440cdbc5e07e3aa8629dcd57a6`
- Promotion workflow run: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/40518110062
- Promotion source SHA was independently pinned by the workflow to `76053bd9127c38d8065eb7ac250bdeb34ab67854`; the exact candidate AAB SHA-256 before signing was checked against `aa4ecfdfcbab20587b69ae59b75e09c47827f2ecce3c272199afc3c347ffce93`.
- The Play-bound upload key fingerprint check, AAB signature verification, bundletool validation, package/version/targetSdk identity check, Google Play Internal upload, and independent Internal-track readback all passed.
- Google Play Internal readback: `PASS`, track `internal`, version code `51019`, release name `THF Fitness 51019 Internal`.
- Promotion evidence artifact: `fitness-51019-internal-promote-evidence`, artifact id `12739484276`, ZIP digest `sha256:12492bdd85019eb8420858baf69bee480b22a462a03dd814f2c08524c717fc2c`.

## Features present in the exact promoted source
- Session persistence/navigation guard work from PR #128.
- Exercise motion/demo manifest and runtime assets from PR #131.
- Motion-manifest/runtime parity regression coverage from PR #143.
- Account workout-history restore uses the bounded history endpoint `/api/v2/workouts?limit=200`.
- Candidate workflow passed the product/source-contract/backend regression step, Android unit tests, Android lint, APK assembly and release AAB bundle task.

## Important scope boundary
- This proves upload and availability on the **Google Play Internal testing track**, not production rollout and not that every tester/device has installed the update.
- No physical-device end-to-end run for this exact candidate is recorded in this checkpoint. Do not claim GPS accuracy, background persistence, Health Connect behavior, exercise playback, or cross-device account restoration has passed on a real device until tested.
- The app's Play production rollout/closed-testing eligibility and publication status must be read from Google Play before any production promotion. Do not reuse a 51018/51019 artifact built from a different SHA.
- Candidate artifacts and evidence ZIPs expire after 14 days; preserve critical metadata in this checkpoint.

## Next verification queue
1. Install/test the exact 51019 candidate on a real Android device or Play internal tester: sign-in, account data/history restore on fresh install/second device, session continues across navigation/background, notification controls, GPS start/stop and permission denial, Health Connect opt-in/denial, and exercise motion demos offline.
2. Confirm the internal tester install path and current Google Play track/release state; keep production untouched until test evidence is complete.
3. Fix/understand the separate `THF Fitness Publication State Probe` workflow failures before relying on it for listing/track status. Its failures are not evidence that the successful 51019 upload/readback failed.
