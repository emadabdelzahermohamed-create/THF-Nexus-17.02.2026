# RuinsCiv — Google Play Console Prefill V1
Date: 2026-09-18
Status: TECHNICAL PREFILL — submit only after the final signed AAB and production provider audit.

## Immutable identity
- Store name: RuinsCiv
- Android package: com.topherofit.ruins.civ
- Product type: Game
- Suggested category: Simulation
- Distribution model: Free core; no pay-to-win competitive advantage
- Android targetSdk: 36
- Primary listing language: English (United States)
- Arabic localization: required at launch

## Store listing copy
### English
Short description:
Build a life, explore a living world, meet players, create, trade and progress.

Full description:
RuinsCiv is a persistent social world where you create a human avatar, explore a living city, meet other players and build your own path. Discover neighborhoods and interiors, take on jobs and quests, develop property and production, fish and farm, customize your look, and join social activities and seasonal world events.

The Android app and web experience use the same RuinsCiv account and world state. Progress and economy-changing actions are validated by the service rather than trusted to the client.

RuinsCiv is designed around fair progression. Competitive or ranked outcomes must not be sold, and purchases must not falsify progression, activity or authoritative game state.

### العربية
الوصف المختصر:
ابنِ حياتك واستكشف عالمًا حيًا وتعرّف على لاعبين واصنع وتاجر وتقدّم.

الوصف الكامل:
RuinsCiv عالم اجتماعي مستمر تنشئ فيه شخصية بشرية خاصة بك، وتستكشف مدينة حية، وتتفاعل مع لاعبين آخرين وتبني مسارك بطريقتك. استكشف الأحياء والمباني، ونفّذ الوظائف والمهام، وطوّر الممتلكات والإنتاج، وشارك في الصيد والزراعة، وخصّص مظهرك، واستمتع بالأنشطة الاجتماعية والمواسم والأحداث داخل العالم.

يستخدم تطبيق Android وتجربة الويب حساب RuinsCiv نفسه وحالة العالم نفسها. العمليات التي تغيّر التقدم أو الاقتصاد يتم التحقق منها على الخادم ولا يُعتمد فيها على ادعاءات العميل.

تم تصميم RuinsCiv حول التقدم العادل؛ لا تُباع أفضلية تنافسية، ولا تسمح المشتريات بتزييف التقدم أو الحالة المعتمدة للعبة.

## App content / access
- Login/account creation: YES.
- Account deletion: must remain available in-app and through a public HTTPS web resource.
- OAuth providers: only declare providers actually enabled in production. Current adapters: Google, Discord, Facebook; credentials are external RUINSCIV_* configuration.
- Play Games linking: do not declare complete until native linking is implemented and tested.
- App access for Google review: create a dedicated non-privileged review account after production auth is live; never provide an admin account.
- Ads: declare NO unless a final binary/runtime audit proves an ad SDK or ad-serving flow is enabled.
- In-app purchases: declare only after the actual Play Billing integration is enabled and verified.
- Content rating: answer from actual social/UGC/chat functionality; moderation/reporting controls must be active before public release.
- Target audience: do not select child-directed distribution without completing the separate child-safety/families requirements.

## Data Safety — conservative technical prefill
Re-audit the final signed production binary before submission.

Data expected for the current social-world design:
- Account identifiers and authentication/session security data.
- Username/profile/avatar preferences and locale/settings.
- Friends/social graph and messages where social features are enabled.
- User-generated media only where the user explicitly uploads/selects it.
- App interactions, progression, inventory/economy events and virtual-world coordinates.
- OAuth identifiers for each production-enabled identity provider.

Do NOT classify in-world coordinates as GPS/device location.
Do NOT declare camera, microphone, precise location, advertising ID, health/fitness data, payments data or third-party sharing merely because older THF code once supported it. Declare those only if the final RuinsCiv binary and production backend actually use them.

## Release gates
1. Build AAB with package com.topherofit.ruins.civ and targetSdk 36.
2. Verify Godot payload, arm64, merged manifest, dependencies, permissions and signature.
3. Complete real-device install/launch/touch/camera/movement/FPS/RAM/thermal QA.
4. Freeze HTTPS production backend and web URLs.
5. Enroll RuinsCiv in Play App Signing and record the app-signing certificate separately from the upload certificate.
6. Register the package name under Android developer verification when required.
7. Publish privacy, terms and account-deletion HTTPS resources.
8. Re-run Data Safety and SDK/permission audit on the exact signed AAB.
9. Upload to Internal testing; install from Play and complete pre-launch checks.
10. Complete Closed testing / production-access requirements if the developer account is subject to them.
11. Promote only the exact tested artifact.

## Official-policy checkpoints reviewed 2026-09-18
- New apps and updates submitted after 2026-08-31 must target Android 16 / API 36 or higher.
- Apps that create accounts must provide both an in-app account-deletion path and an external web deletion resource.
- Every published app must complete the Data Safety form based on actual data collection/sharing.
- Play Console app creation is performed under All apps > Create app; the package identity is permanent and must be treated carefully.
- Android developer verification introduces package-name registration requirements; the final public signing certificate must be tracked separately from the upload key.
