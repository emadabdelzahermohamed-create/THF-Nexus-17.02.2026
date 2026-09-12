# THF Rift RC35 Source Delta

Base: RC34 `2b565ee09eb00d3c1a5b54c7d07910c68daad11b40fcd8d361b672477a4023f6`

RC35 closes the verified Android export-readiness gap without changing gameplay logic. The cumulative source now contains a source-controlled Godot Android export preset with:

- package: `com.topherofit.thf.rift`
- target SDK: 36
- min SDK: 26
- AAB export format
- arm64-v8a enabled
- Gradle build enabled
- versionCode: 42069
- versionName: `4.6.9-rc35`
- production signing embedded: false

`project.godot` release marker advances from Stage16-K to RC35. No production key, seed, token, service-account JSON, Play publish action, Cloudflare production cutover, Solana transaction, or WAVE file is included or modified.

Canonical RC35 source SHA-256: `ed3d1e3ede527b39f0110bbb83aab8e0d91cc4be4367b1634f14e17c02106558`

Parts:
- part.00 `e4e5b42d69bc4399c57a3e5b3a8f23a06134b09ecdc73d38ed5069704831f781`
- part.01 `679287f01480949a8233cc28cbaea82183d9750c6ac4f8211d057f6cb66a0db0`

Next gate is a debug/test-only Godot 4.7.2 Android API 36 AAB export through the existing WIF/GCP release path, followed by package and SHA evidence.
