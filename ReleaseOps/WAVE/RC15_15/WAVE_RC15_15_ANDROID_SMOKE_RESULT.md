# WAVE RC15.15 — Android install/launch smoke result

Date: 2026-09-24
Package: `com.wave.mawja`
Version code: `15302`
Version name: `1.0.0-rc15.15-twa-fix`
Target SDK: 36
Emulator API: 35

## Root cause fixed

The previously tested versionCode 15301 installed but crashed during TWA launch because Android Browser Helper attempted to use:
`com.google.androidbrowserhelper.trusted.ManageDataLauncherActivity`
while that component was missing from the app manifest.

RC15.15 adds the Android Browser Helper manage-space activity declaration and application `android:manageSpaceActivity` attribute, then bumps the Android release to versionCode 15302.

## Automated evidence

Workflow: `WAVE Android Install Smoke`
Run: `35985903589`
Result: **SUCCESS**
Artifact: `WAVE-ANDROID-INSTALL-SMOKE` id `10802372219`

Validated:
- Signed release APK build: PASS
- APK signature verification: PASS
- Package identity `com.wave.mawja`: PASS
- versionCode `15302`: PASS
- targetSdk 36: PASS
- Emulator boot: PASS
- `adb install -r`: PASS
- Launcher event injection: PASS
- Screenshot capture: PASS
- package/activity dumpsys: PASS
- logcat capture: PASS
- WAVE fatal-crash scan: PASS / none detected

Result file:
```
package=com.wave.mawja
versionCode=15302
targetSdk=36
emulatorApi=35
install=PASS
launch=PASS
fatalCrash=NO
liveUrl=https://wave-mawja.p-my.workers.dev
```

## Screenshot note

The clean emulator reached Chrome's first-run screen after TWA handoff because Chrome had never been initialized on that emulator. This is a browser onboarding state, not an application crash. The prior 15301 failure produced an explicit WAVE Java fatal exception before this point; 15302 does not.

## Release decision

15301 must not be promoted further.
15302 is the Android candidate approved by the emulator install/launch gate for Google Play Internal upload.
