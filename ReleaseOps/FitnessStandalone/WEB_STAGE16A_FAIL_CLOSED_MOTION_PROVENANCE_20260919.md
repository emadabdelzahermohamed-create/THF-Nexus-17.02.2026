# Stage16A fail-closed motion/offline provenance — 2026-09-19

Production app: https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/
AppDeploy snapshot: `1789827903246`
QA screenshot run: `1789827920433`

## Completed
- Corrected offline-state semantics: a freshly downloaded GLB is no longer reported as an offline cache hit. `offlineReady` is true only when the renderer actually loaded the canonical Stage16A asset from Cache Storage.
- After a first network download, UI states that local replay becomes available on the next load; a subsequent cache hit explicitly reports local-cache provenance.
- Exercise motion mapping is now fail-closed in the visible runtime UI. The renderer exposes the actual animation clip name selected.
- A token/name match is explicitly labelled as a name match only and **not** biomechanical certification.
- If no clip name matches the exercise, the Stage16A surface explicitly says it is reference-only and is not exercise instruction.
- Canonical MPFB/MakeHuman Stage16A lineage remains unchanged: 137-joint / 195-clip contract, zero legacy humanoid fallback.

## Runtime evidence
- Deployment reached `ready`.
- Frontend errors: 0.
- Backend errors: 0.
- Network errors: 0.
- Desktop and mobile QA screenshots generated.

## Gate remains open
This change intentionally does **not** claim that the requested human-like offline exercise demonstrator has been completed. The current GLB still needs per-exercise biomechanical animation certification (or new compatible open/licensed clips), anatomical/muscle visual treatment, first-install Android asset bundling, foot-contact/IK validation, and physical-device GPU/runtime evidence. YouTube/reference video remains comparison evidence, not a substitute for an offline certified motion clip.
