# Gemini Agent Entry Point

Before any analysis or code change, read in this order:
1. `AGENTS.md`
2. `ReleaseOps/AI_SWARM/PROTOCOL.md`
3. `ReleaseOps/AI_SWARM/STATE.json`
4. `ReleaseOps/AI_SWARM/START_PROMPTS.md`
5. GitHub Launch Board issue #41 and the lane-specific issue/PR.

Git is the source of truth. Never redo a verified PASS for the same SHA. Work only on a dedicated `agent/gemini/<lane>/<yyyymmdd>` branch. Preserve project isolation and keep secrets/signing material out of Git. Open a PR with tests/build/runtime evidence; do not merge release/main yourself.

P0 shared visual rule: preserve the approved high-quality Fitness V2 exercise imagery and implement automatic continuous motion without requiring a tap. No visual-quality downgrade is acceptable merely to obtain animation.
