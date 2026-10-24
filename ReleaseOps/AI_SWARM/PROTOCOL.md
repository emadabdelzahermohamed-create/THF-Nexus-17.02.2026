# THF execution protocol

## Authority
Root AGENTS.md, STATE.json and the live project checkpoint are the startup authority. Git is the source of truth; chat statements and old snapshots do not override newer verified evidence. Active scope is Fitness and zero-upfront funding. Historical plans remain available in Git history.

## Current sources
- Fitness canonical development: `agent/codex/fitness-recovery/20261023`; read `ReleaseOps/FitnessStandalone/EXECUTION_20261024.md` and `RECOVERY_20261023.md` there.
- Funding receipts: `agent/codex/token-funding/20261023`; sponsorship draft: `agent/codex/sponsorship/20261024`.
- Root main routes work; it is not the latest Fitness application source. A development branch is not proof of Play release.

## Ownership and delivery
1. Read current state, exact SHA, active work and previously passed gates.
2. Select one bounded task in your assigned lane and create `agent/<provider>/<lane>/<yyyymmdd>`.
3. Check exclusive ownership of shared files/device. If busy, choose independent work. Only integrator modifies canonical, version codes, release workflows or Play.
4. Implement and run checks appropriate to the change. Preserve approved assets and working integrations.
5. Commit and open PR stating base/result SHA, changed scope, tests, user-visible effect, remaining gates and production impact.
6. Integrator reviews actual diff and evidence before merging; never merge solely on an agent completion claim.
7. Build/sign validated meaningful candidates with unique versions; verify actual Play Internal committed track/version. Public Production requires its full gates.
8. Persist exact artifact/run/digest/version/track evidence and next executable action before waiting.

## Resource and failure rules
- Reuse valid same-SHA checks. Do not run broad audits without a new progress token or failure.
- Optional authentication never blocks unrelated work. Unattended runs never start interactive browser login. Record blocked auth once; don't retry declined/cancelled handoffs or bypass them.
- Poll long-running CI with brief calls. Tool timeout is not a guarantee that interactive authentication will return promptly.
- Device offline/locked is not app failure or permission to interrupt user sessions. Continue repository work.
- No paid resources, secrets in Git, project mixing, fabricated runtime evidence, guaranteed funding or assumed scheduler execution.

## Quality gates
Fitness exercise motion remains automatic, continuous, anatomically faithful, lifecycle-safe and usable offline without degrading approved artwork. Preserve Arabic RTL/accessibility. Prove sensor provenance and background behavior separately from source tests; never fabricate outdoor GPS/Health Connect/voice/device acceptance. Other projects remain isolated and paused, retaining their approved assets and runtime requirements for future reactivation.

## Cleanup
Before deleting old files, prove no live references/dependencies and verify the complete standalone replacement. Record old-to-new mapping and tests in a reversible commit. Preserve licensing, release evidence, rollback history and unrelated projects. No history rewrite or blanket dated-file deletion.
