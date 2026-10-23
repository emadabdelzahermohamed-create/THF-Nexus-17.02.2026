# Fitness 51010 build checkpoint — 2026-10-23

## Verified outcome
- Package: `com.topherofit.thf.pulse`
- Candidate: versionCode `51010`, versionName `5.0.0-v2-alpha10`.
- GitHub Actions deterministic build run: `40007921548` — SUCCESS.
- Run head SHA: `2bf7d35479d3e149315bb14ec6c688ce9d3fa90f` on `agent/codex/fitness-recovery/20261023`.
- Job `120601488991` (`deterministic-build`) completed SUCCESS, including Android API 36 setup, unit tests, lint, APK and AAB build.
- Artifact: `fitness-activity-candidate-51010`, ID `12525417127`, size `37490260` bytes, archive digest `sha256:e80b126efd5fac32de999a3c23852a8aae127cf9e06ca002e25f814967b1fd7d`.
- Extracted debug APK size `19703067` bytes; SHA-256 `98c5a35ad9b4b6f90f539a3c8e34ec674410d1cd38464e0dd44f70774b8ad6f2`.
- Extracted release AAB size `18132858` bytes; SHA-256 `02471764ef166a78aa423c12e469e0ec270441ba6fbccd12e9d2256a0fd63637`.

## Release-state boundary
This proves BUILT for 51010. It does not prove PHONE-TESTED, PLAY-INTERNAL, Health Connect real provenance, outdoor GPS correctness, or PRODUCTION. 51009 remains the last proven Play-installed phone version until 51010 promotion/propagation is verified.

## Next exact action
Use the existing authorized Internal signing/promotion workflow for 51010 without rebuilding it. Verify `committed=true`, track=`internal`, versionCode=51010 and source/artifact association. After Play propagation, update SM-A217F through Play without uninstall/force-stop/data deletion, then execute notification permission Allow and Deny paths plus notification Stop. Outdoor GPS and actual Health Connect record-level provenance remain explicit later gates.
