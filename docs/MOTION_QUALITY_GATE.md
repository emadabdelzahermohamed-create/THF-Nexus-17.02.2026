# THF Ecosystem — Motion Rules & Shared Animation Quality Gate

## Scope & Purpose
This specification documents reusable motion standards and quality acceptance gates across the THF ecosystem (Fitness apps, Web, and Godot 3D games) without directly coupling project code.

---

## Part 1. 2D Exercise Demonstration Motion Rules

### 1. Visual Quality & Asset Integrity
- **Baseline Rule**: Never replace high-quality, clear exercise imagery or photography with a low-quality avatar merely to obtain motion. Exercise clarity and anatomical correctness are non-negotiable.
- **Source Preservation**: Motion implementations MUST use approved, permissively licensed assets (e.g., `free-exercise-db` under Unlicense) without downscaling or artifact introduction.

### 2. Deterministic Frame Advance & Cadence
- **Automatic Playback**: Exercise demonstrations MUST advance automatically upon view launch without requiring user tap interactions.
- **Cadence Options**:
  - **Ping-Pong (Default for 2-frame sequences)**: Advances `0 → 1 -> ... → N-1 -> N-2 -> ... → 0`. Eliminates harsh visual jumping between terminal flexion/extension and setup frames.
  - **Loop (Default for multi-frame continuous clips)**: Advances `0 → 1 -> ... → N-1 → 0` with a uniform frame interval (recommended 800ms - 1200ms per frame depending on exercise tempo).
- **Manual Control Overrides**: Provide explicit Play/Pause (`#toggleMotionPlay`) and frame step controls so users can freeze and inspect specific anatomical setups or posture cues.

### 3. Preloading & Offline Performance
- **Image Cache**: All frame assets for a given exercise sequence MUST be preloaded into memory before initiating playback loop to guarantee zero frame flicker.
- **Offline Availability**: All exercise motion media must reside in local app bundle or offline cache; network fetches during workout sessions are prohibited.

### 4. Lifecycle & Battery Awareness
- **Visibility Observers**: Listen for Page Visibility API (`visibilitychange`), window `blur`/`focus` events, and view lifecycle enter/leave transitions to pause animation timers when non-visible.
- **Accessibility (`prefers-reduced-motion`)**: Respect OS and app-level reduced-motion flags by defaulting to static keyframe display unless explicitly overridden by user toggle.

---

## Part 2. 3D Game & Character Animation Quality Gate

### 1. Avatar & Model Lineage
- **No Low-Quality Placeholders**: Substitutions using low-poly generic humanoids are prohibited. Characters must conform to approved project art direction.
- **Skeleton & Mapping**: Bone hierarchies must support standard humanoid IK chains (hips, knees, ankles, spine, neck, shoulders, elbows, wrists).

### 2. Locomotion & Blend Trees
- **Transitions**: Idle $\leftrightarrow$ Walk $\leftrightarrow$ Run transitions must use continuous parameter blending (directional blend trees / 2D blend spaces) rather than hard clip cuts.
- **Foot Contact & IK**: Feet must maintain solid contact with ground geometry during stance phase; foot sliding (skating) must be prevented using foot-IK pinning or root motion matching.

### 3. Framing, Camera & Environment
- **Camera Occlusion**: Cameras must employ collision spheres/raycasts to prevent clipping into terrain, walls, or character geometry.
- **Lighting & Shadows**: Directional lighting and real-time shadows must remain coherent across character motion and locomotion transitions.

### 4. Performance Budgets
- **Frame Rate Target**: Stable 60 FPS on representative mobile targets (Android API 36 devices).
- **Draw Call / Polygon Budget**: Keep rigged mesh polycounts within project LOD guidelines and batch static environment geometry.

---

## Acceptance Checklist Matrix

| Quality Criteria | 2D Fitness Demos | 3D Game Characters | Gate Status |
| :--- | :--- | :--- | :--- |
| **Visual Quality** | High-res image quality preserved | Approved model lineage | **PASS** |
| **Motion Mode** | Auto-playing ping-pong / loop | Blended animation tree | **PASS** |
| **Offline Cache** | Deterministic local preloading | Bundled glTF/resource packs | **PASS** |
| **Lifecycle Safety** | Timer pause on background/blur | Pause tree processing on pause | **PASS** |
| **Accessibility** | `prefers-reduced-motion` support | Configurable camera/motion blur | **PASS** |
