# Media — Unified Execution Backlog

Updated: 2026-09-18
Authoritative upstream: THF_Echo_FINAL_BASELINE_20260916_FULL_SOURCE.zip
Upstream SHA-256: c1a51136d3da51ee334756de14e368934a38ed84be205cbdd874da3486f9f904

| Priority | Gate | Task | Status |
|---|---|---|---|
| P0 | Source | Resolve newest Media source and preserve WAVE/THF isolation | PASS |
| P0 | Baseline | Backend regression + exact Android build on API 36 | PASS |
| P0 | Identity | Standalone Media Identity; remove THF Pass runtime dependency | PASS |
| P0 | Security | Bind uploads/chat/calls/reactions/follows to authenticated server identity | PASS |
| P0 | Identity | Google Android Credential Manager + server token/nonce verification | CODE_PASS / CONFIG_BLOCKED |
| P0 | Identity | Web OAuth Google + optional Microsoft/GitHub; configured buttons only | CODE_PASS / CONFIG_BLOCKED |
| P0 | Web | Same backend/service for website and Android | STAGING_PASS |
| P0 | Deploy | Persistent Media service + HTTPS staging tunnel, isolated from WAVE | STAGING_PASS |
| P0 | Deploy | Stable production domain/named tunnel or Cloud Run | BLOCKED_EXTERNAL_PERMISSION |
| P0 | Android | Independent package com.topherofit.media, API 36 staging debug build | PASS |
| P0 | Android | Release signing + physical-phone install/smoke | TODO |
| P0 | Play | AAB + Play Internal upload + post-upload verification | BLOCKED_PLAY_ACCESS |
| P1 | Avatar | Optional canonical MPFB/MakeHuman avatar enhancement | DEFERRED |
| P1 | Media | FFmpeg HLS ladder, thumbnails, upload scanning, quotas, resilient storage | TODO |
| P1 | Calls | TURN-backed WebRTC cross-network verification | TODO |
| P1 | Push | Android/web push notifications and lifecycle | TODO |
| P1 | Safety | Moderation, report/block/mute, rate limits, abuse/spam controls | TODO |
| P1 | Privacy | Account export/retention + privacy/terms/UGC disclosures | TODO |
| P1 | UX | Arabic/English first, RTL, accessibility, Data Saver, responsive parity | TODO |
| P2 | Social | Communities, creator tools, verified professionals, discovery/recommendations | TODO |
| P2 | Economy | Signed creator rewards/events without client-side reward authority | TODO |
| P2 | Release | Store listing/screenshots/icon/feature graphic/release notes | TODO |
| P2 | Ops | Monitoring, backups, rollback, audit evidence, release manifest/SHA | TODO |
