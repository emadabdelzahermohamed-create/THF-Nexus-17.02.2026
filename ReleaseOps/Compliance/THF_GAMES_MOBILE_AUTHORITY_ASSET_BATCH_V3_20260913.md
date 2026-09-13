# THF Games — Mobile / Authority / Asset Large Batch V3 — 2026-09-13

## Scope and safety
THF-only game engineering checkpoint. WAVE_MAWJA paths were explicitly excluded from every discovery/audit workflow. All source archives were treated as immutable inputs and SHA-256 was rechecked after candidate work. No production signing, Play publishing, Cloudflare production cutover, token action, destructive cloud change, or persistent cloud key was used. GitHub OIDC/WIF + GCP IAP remained the execution path.

No item in this checkpoint is FINAL or PLAY_READY. Physical-phone exact-candidate evidence remains mandatory.

## 1. Terra RC34 / Rift RC37 reversible mobile candidate overlay — PASS for mobile configuration
Workflow: `THF Terra Rift Mobile Candidate Overlay V1`
Run: `34767848421` — SUCCESS
Artifact: `THF-TERRA-RIFT-MOBILE-CANDIDATE-OVERLAY-V1`
Artifact ID: `10321192923`
Artifact ZIP digest: `5fb2370731bc589150b9ba924906d576cb9bfd79cd9e5ecec54ff6fd18e0232c`

Inputs remained authoritative and unchanged:
- Terra RC34 canonical SHA-256: `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`
- Rift RC37 canonical SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`

The disposable overlay corrected, without touching the canonical ZIPs:
- `window/handheld/orientation=4` (`SCREEN_SENSOR_LANDSCAPE`)
- `window/stretch/aspect="expand"`
- desktop width/height override values disabled for the candidate

Both candidates then passed Godot `4.7.2.stable.official.ed1daf0bf` headless editor import and headless boot.

After the overlay, the Real-Function V2 source audit reduced the Terra and Rift required-failure sets to exactly one item each:
- `no_placeholder_endpoint`

Network authority therefore remains BLOCKED. Placeholder values were not printed; marker counts were 3 for Terra and 3 for Rift. A backend URL will not be invented or silently substituted.

Candidate manifest evidence:
- Terra mobile disposable tree manifest SHA-256: `f4b9b4e69e7b14f4c7da72e2016cbb316221ae83f83b56445f458b3763b22f87`
- Rift mobile disposable tree manifest SHA-256: `f74f82271f6a32c22462a8bbaf2e15d80b9726d37c764c84cd1007a77c968683`

Status: `device_status=PENDING`, `final_status=NOT_FINAL`.

## 2. THF game backend authority contract — discovered and isolated
Workflow: `THF Game Backend Authority Contract Discovery V1`
Run: `34768073058` — SUCCESS
Artifact: `THF-GAME-BACKEND-AUTHORITY-CONTRACT-V1`
Artifact ID: `10321380088`
Artifact ZIP digest: `2d1ecef8ecff231c81d3b46f99b1f367acb379a54e150edc4c74717e652478a8`

Read-only runtime source SHA-256: `6abec6481f40272f6a847e8da4ef6890243d55243e6d88d806cde6bfa97ac046`.

The current THF runtime contains 25 game-relevant route literals and 5 relevant service symbols. Confirmed route families include:
- `/health`
- `/api/auth/register`, `/api/auth/login`
- `/api/leaderboard`
- `/api/world/environment`, `/api/world/entities`, `/api/world/revisions`
- `/api/social/position`, `/api/social/send`, `/api/social/nearby`
- `/api/avatar`, `/api/avatar/generate`
- `/api/economy/balance`, `/api/economy/internal-award`
- `/api/fishing/inventory`, `/api/fishing/leaderboard`
- `/api/arena/start`, `/api/arena/action`

This proves that a server-authoritative THF game API contract exists in the runtime source. It does **not** prove that a stable authorized public HTTPS/WSS hostname is ready for the phone candidates. The remaining network gate is to bind the candidate to a reachable authorized endpoint, verify `/health`, auth, and game authority behavior, then rerun the real-function gate.

No host values, credentials, DSNs, headers, or secrets were emitted.

## 3. Spark / Rush authoritative RC2 sources recovered and audited
The extended THF-only lineage discovery recovered standalone source archives that the earlier narrower search missed:
- Spark RC2 source: SHA-256 `6b74f8d75df8c0b7f74d8c2fee8be7e3517f3803cb42968735bc7a10939bc18c`
- Rush RC2 source: SHA-256 `bb6ff035186b13cdde853145f42e66259c205889de2a7b368da34c9cb0582ba7`

Source audit workflow: `THF Spark Rush Authoritative Source Audit V1`
Run: `34768115807` — SUCCESS
Artifact: `THF-SPARK-RUSH-AUTHORITATIVE-SOURCE-AUDIT-V1`
Artifact ID: `10320613270`
Artifact ZIP digest: `0b6de172666927b6fb3c42f50d14db6ec0edea3aa797f476648c9a8658bc5d9b`

Spark clean extract: 45 files. It is a native Android + web/backend hybrid source, not Godot: one Android manifest, Gradle settings, one Java source, 23 XML resources, 3 web files. Real-Function V2 correctly rejects the current source contract with:
- `no_ui_only_shell`
- `real_input_wiring`
- `no_placeholder_endpoint`

Rush clean extract: 46 files. It is also native Android + web/backend hybrid: one Android manifest, Gradle settings, one Java source, 23 XML resources, 2 web files, plus a ranking client. Real-Function V2 rejects the current source contract with the same three blockers:
- `no_ui_only_shell`
- `real_input_wiring`
- `no_placeholder_endpoint`

Neither is being represented as a game-ready candidate. `device_status=PENDING`, `final_status=NOT_FINAL`.

## 4. Learn Games / Fitness Games recovered-candidate audit — provenance still pending, real-function still FAIL
Known canonical P49 RC2 inputs remain unchanged:
- Learn Games P49 RC2 SHA-256 `dbd259b224924e60902fb0e1b2ebca77bc243e5f29a64d04fd3114438fd41484`
- Fitness Games P49 RC2 SHA-256 `da3c865a76848c170d679547e05d6edbc0b5ffd6a48002b12ad0d26415fd0273`

Additional recovered archives were verified but are **not** promoted to authoritative status:
- Learn recovered `source.zip` SHA-256 `ce8547851c9573db02603ea6f11e020a1b7d346af0cac51e07947304f1a7c1f9`
- Fitness recovered `source.zip` SHA-256 `cf5d73c3a03ab503dbd7c36a2d4db3ec1449ec8281304627b9463e2cb8732a25`

Workflow: `THF Learn Fitness Games Recovered Candidate Audit V1`
Run: `34768210562` — SUCCESS
Artifact: `THF-LEARN-FITNESS-RECOVERED-CANDIDATE-AUDIT-V1`
Artifact ID: `10320478522`
Artifact ZIP digest: `8ff5687e4b417c0de96e500e8ddb08c953de0642890fbf565b7ed93f515f9ade`

Learn recovered candidate:
- clean extract: 14 files
- Android manifest: present
- Java source: 1; Kotlin: 0
- target SDK 36 marker: present
- touch/input token: present
- placeholder endpoint marker: absent
- Real-Function required failures: `no_ui_only_shell`, `real_input_wiring`, `player_or_avatar_load`, `locomotion_or_gameplay_action`, `learning_loop`
- `candidate_authority_status=PROVENANCE_PENDING`
- `device_status=PENDING`, `final_status=NOT_FINAL`

Fitness recovered candidate:
- clean extract: 14 files
- Android manifest: present
- Java source: 1; Kotlin: 0
- target SDK 36 marker: present
- touch/input token: present
- placeholder endpoint marker: absent
- Real-Function required failures: `no_ui_only_shell`, `real_input_wiring`, `player_or_avatar_load`, `locomotion_or_gameplay_action`, `fitness_loop`
- `candidate_authority_status=PROVENANCE_PENDING`
- `device_status=PENDING`, `final_status=NOT_FINAL`

Both recovered and canonical archives were SHA-reverified unchanged after the audit. P49 RC2 remains the canonical reference until provenance evidence proves the recovered lineage. Even if provenance later closes, the recovered candidates still require real gameplay implementation; API 36 and simple touch-token presence are not sufficient.

## 5. Shared avatar / MPFB / MakeHuman / UAL GLB integrity — PASS at asset-container level
Workflow: `THF Terra Rift Avatar Rig Integrity V1`
Run: `34768161537` — SUCCESS
Artifact: `THF-TERRA-RIFT-AVATAR-RIG-INTEGRITY-V1`
Artifact ID: `10320094350`
Artifact ZIP digest: `3ec30a294d11a8cf9563c2c0719cee32ee73c5800e795d365ae4743688c6dfe3`

The read-only GLB parser validated GLB v2 structure, declared file length and JSON chunks without loading or changing canonical assets.

Terra canonical source:
- 69 avatar/character/animation-related GLB candidates inspected
- 2 rigged GLBs
- 2 animated GLBs
- 0 parse/integrity errors
- `thf_mpfb_stage16a_ual12_animated.glb`: 1 skin, 195 animations, 141 nodes, 3 meshes
- `thf_humanoid_v6.glb`: 1 skin, 23 animations, 96 nodes, 1 mesh

Rift canonical source:
- 57 candidate GLBs inspected
- 8 rigged GLBs
- 8 animated GLBs
- 0 parse/integrity errors
- same MPFB/UAL avatar asset: 1 skin / 195 animations
- same humanoid v6: 1 skin / 23 animations
- six audited weapon GLBs also contain skins and 2–3 animations each (P90, Pistol, Revolver, Rifle, Shotgun, SniperRifle)

This is an asset-container integrity PASS, not proof of runtime animation blending, IK correctness, retarget quality, root motion, hit reactions or physical-device rendering. Those remain later runtime/device gates.

## 6. Lineage / asset discovery evidence
Workflow: `THF Small Games Lineage Avatar Discovery V2`
Run: `34767967509` — SUCCESS
Artifact: `THF-SMALL-GAMES-LINEAGE-AVATAR-DISCOVERY-V2`
Artifact ID: `10320934094`
Artifact ZIP digest: `ced398d19050e3853b7c2853fe4648aa7206ccb7bde882474864b482fb03e397`

The bounded discovery collected 160 source candidates and 160 avatar/animation asset candidates with WAVE paths explicitly excluded. It found MPFB/MakeHuman, UAL1/UAL2 provenance/runtime manifests, imported avatar assets and the recovered Spark/Rush sources. Discovery is evidence for lineage investigation, not automatic authority promotion.

## Next engineering gates
1. Resolve Terra/Rift `no_placeholder_endpoint` only against an authorized reachable THF HTTPS/WSS service. Validate `/health`, auth and backend-authoritative world/arena/economy/social transitions. Do not hardcode an arbitrary host.
2. After network authority PASS, export fresh candidate APKs from the new overlay bytes and rerun API 36/package/payload/signature/security checks. Old APK PASS cannot be reused for changed bytes.
3. Build real game loops for Spark/Rush instead of accepting the existing hybrid shell: touch/input events, player/game state, learning/fitness gameplay logic, explicit offline semantics and backend-authoritative online state.
4. Close provenance for the recovered Learn/Fitness archives using lineage evidence only. Regardless of lineage outcome, implement the missing real learning/fitness gameplay loop, avatar/player state and real input wiring before any game-ready label.
5. Extend avatar evidence from GLB integrity to actual Godot/native runtime load, animation tree/state machine, locomotion/IK/root-motion and gameplay binding tests.
6. Physical Android device gate remains mandatory for every exact candidate SHA: install, cold launch, touch, sensor-landscape where required, safe layout, background/resume, offline/network transition, core gameplay, crash-free smoke, avatar/player load, movement/camera/combat where applicable, and FPS/RAM/thermal observation.
