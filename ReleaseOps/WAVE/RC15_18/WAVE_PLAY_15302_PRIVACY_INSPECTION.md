# WAVE Play 15302 — Exact Privacy/Permission Inspection

Date: 2026-09-26  
Package: `com.wave.mawja`  
Version code: `15302`

## Evidence

Workflow: `.github/workflows/wave-play-apk-privacy-inspect.yml`  
Commit: `dd1f692078c13e142e4db23bd916cdffa8e75500`  
Run: `36243580600`  
Result: **SUCCESS**

The workflow downloaded the **Google Play-generated universal APK** using the generated APK metadata API and `?alt=media`, then inspected the exact Play-signed artifact.

APK SHA-256:

`961e5f60fe8b4694472029b09a34357d6e2004114c9ecfb2a69c831895041dc7`

## Exact shipped manifest / SDK result

- package: `com.wave.mawja`
- versionCode: `15302`
- permissions:
  - `android.permission.INTERNET`
  - `android.permission.ACCESS_NETWORK_STATE`
- Camera permission: **absent**
- Microphone permission: **absent**
- Fine/coarse location permissions: **absent**
- Advertising ID permission/marker: **absent**
- AdMob SDK markers: **0**
- Firebase Analytics markers: **0**

## Conclusion

The earlier source-wide scan that found Camera/Microphone/Location/AdMob signals was a false positive caused by scanning non-canonical/stale Android source material. The Google Play-generated APK is the authoritative release artifact for Android privacy-permission evidence.

Data Safety work must use this exact Play artifact as the Android release reference and separately account for server/web account data handled by WAVE.
