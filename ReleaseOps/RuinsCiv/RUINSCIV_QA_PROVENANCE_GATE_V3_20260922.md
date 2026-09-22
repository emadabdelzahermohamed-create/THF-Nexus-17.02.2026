# RuinsCiv QA provenance gate V3 — 2026-09-22

## Scope and truth boundary

- RuinsCiv only; no WAVE, EndCiv, Rift, Spark, Rush, database, OAuth, production signing, or Play listing was touched.
- Canonical production identity remains `com.topherofit.ruins.civ`.
- QA identity remains `com.topherofit.ruins.civ.phoneqa`.
- THF Terra is historical/superseded source lineage only and remains forbidden from the active Android identity and payload.
- `physical_device_status=PENDING`; `final_or_play_ready=FALSE`; no Play upload.

## Code checkpoint

- GitHub code checkpoint: `bb12d5f392238cc916818f3674aad2247fca6f1f`.
- The Android QA gate now emits a deterministic source manifest before the build, re-emits it after export, and fails if any non-generated source byte changed.
- The evidence binds the APK to the source-manifest, project, world, and Stage16A avatar SHA-256 values.
- The APK file list now rejects environment files, private-key names, keystores, and certificate containers.
- The RC34 recovery path now rejects sensitive filenames and high-confidence private-key/token content before creating an artifact; build caches and signing material are excluded from both the manifest and archive.
- Source recovery can run in the isolated same-repository pull request and is serialized per candidate.

## Verified prior artifact evidence

- Failed workflow run: `35683425839`, source `9ad10a68b8c19ac6a60f5d461ea25cc8db2088ad`.
- Artifact ID: `10676530345`, ZIP SHA-256: `99a6716340d20faba8828b89a29129af35d4c2fd91efda82dc9870982f5a295d`.
- APK size: `195218678` bytes; APK SHA-256: `696b7fa941eac899326a52949219c741e6ea72e9dfe60bf701cd333c15186fb7`.
- Proven: Godot 4.7.2 import, bounded main-scene boot, Android export, ZIP integrity, arm64 Godot libraries, MPFB Stage16A import, footwear/wardrobe provenance and runtime PBR payload.
- Rejected: initial APK signature was absent. Package/API36/arm64 promotion was therefore not claimed by that run.

## Local gates

- Workflow/static contract tests: 10 passed.
- Both workflow YAML files parse successfully.
- Recovery helper and extracted remote QA Bash parse successfully.
- Backlog fail-closed JSON assertions pass.
- Git whitespace gate passes.

## Required remote evidence

The next run must end in terminal success and provide source-recovery plus APK artifacts proving source manifest stability, no sensitive material, import, scene boot, export, signature certificate, zipalign, package, target SDK 36, arm64, required avatar/assets, and SHA-256. This checkpoint alone is not an APK candidate, phone pass, final build, Play-ready build, or publication.
