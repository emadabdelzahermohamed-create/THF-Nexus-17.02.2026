# THF Fitness Android 50002 successor overlay

This overlay upgrades the verified V5 RC2 source to the Android 50002 release successor without duplicating the 26.3 MB canonical Stage16A GLB in Git.

It adds versionCode 50002 with targetSdk 36, a real first-install offline Stage16A motion coach, a vendored model-viewer runtime and license, an HTTPS autoVerify Digital Asset Links intent filter, Health Connect read steps plus read/write exercise-session implementation, and localized Android strings plus the Health permission rationale.

The apply_overlay.py script copies the canonical Stage16A GLB from the verified source into Android assets during the build. Production signing remains fail-closed and is materialized only from GCP Secret Manager in CI.
