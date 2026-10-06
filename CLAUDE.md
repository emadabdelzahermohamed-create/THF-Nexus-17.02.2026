# Claude Agent Entry Point

Before any analysis or code change, read in this order:
1. `AGENTS.md`
2. `ReleaseOps/AI_SWARM/PROTOCOL.md`
3. `ReleaseOps/AI_SWARM/STATE.json`
4. `ReleaseOps/AI_SWARM/START_PROMPTS.md`
5. GitHub Launch Board issue #41 and the assigned lane issue/PR.

Git is the source of truth. Never redo a verified PASS for the same SHA. Work only on a dedicated `agent/claude/<lane>/<yyyymmdd>` branch. Preserve strict project isolation; never expose secrets/signing material. Submit small reviewable PRs with tests/build/runtime evidence and do not merge release/main yourself.

Use deep reasoning/review capacity for architecture, hard bugs, CI diagnosis, safety/security and high-risk cross-module changes. Avoid spending expensive model capacity on mechanical conversions or already-proven checks.
