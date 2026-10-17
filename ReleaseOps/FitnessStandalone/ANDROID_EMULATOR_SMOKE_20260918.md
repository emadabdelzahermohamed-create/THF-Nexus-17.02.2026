# Android Emulator Production-Backend Smoke — PASS

Date: 2026-09-18
Workflow run: `35356916175`
Artifact: `10552152173`
Artifact digest: `sha256:922e146df4d06acecf2a3688ed8eead19a9c9661ad38fee071c15313f1ebf5dd`
Workflow checkpoint: `09820c0147d66fdb6b5c220fd98e0068a071159a`

Tested APK SHA-256:
`aede65b003659b4b3ba46555b51744f365a9824e462029a5f0e6a3f1bd20f567`

Environment:
- Android API 34 Google APIs emulator
- x86_64 / Pixel 2 profile
- KVM acceleration enabled
- locale path: ar-EG
- production base URL: https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/

Evidence:
- install=PASS
- launch=PASS
- package=`com.topherofit.thf.pulse.debug`
- activity=`com.topherofit.thf.pulse.MainActivity`
- cold launch TotalTime=4987ms
- resumed activity is THF Fitness MainActivity
- no fatal app crash detected in logcat
- UI dump=PASS
- screenshot=PASS
- UI dump contains Arabic production sign-in screen and canonical Stage16A contract
- canonical text visible: MPFB/MakeHuman Stage16A / 137 joints / 195 clips / legacy fallback blocked

The earlier run `35355510211` failed before the custom app smoke because the emulator runner suffered an ADB broken-pipe condition. KVM + API 34 stabilized the environment; it was not treated as an application failure.

Boundary: this is automated virtual-device evidence, not a physical-device Health Connect/sensor/GPU validation.
