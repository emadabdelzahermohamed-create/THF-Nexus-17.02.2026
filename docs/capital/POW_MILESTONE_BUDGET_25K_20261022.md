# Proof-of-Workout — $25,000 Milestone Grant Budget

Date: 2026-10-22
Status: proposal baseline; adaptable to grant-provider rules

## Milestones

### M1 — Public verification specification and threat model — $4,000
- Versioned Proof-of-Workout claim schema.
- Privacy/data-minimization model.
- Fraud/replay/self-authored/duplicate threat model.
- Reference verification policy.

**Evidence:** public spec, schema tests and documented threat matrix.

### M2 — Adversarial verifier and abuse fixtures — $5,000
- Duplicate and replay rejection.
- Implausible cadence/speed/distance combinations.
- Overlap and conflicting-source handling.
- Deterministic policy tests and CI.

**Evidence:** public test suite, CI run and machine-readable test report.

### M3 — Solana Devnet commitments and receipts — $4,000
- Privacy-preserving commitment format.
- Devnet write/read reference flow.
- Explorer-verifiable transaction evidence.
- Idempotency/nonces and expiry semantics.

**Evidence:** Devnet signatures, explorer links and source commit.

### M4 — Android Health reference integration — $5,000
- Health Connect provenance bridge.
- Sensor fallback and explicit permission/sync states.
- On-device evidence -> verifier -> receipt demonstration.
- Offline/retry behavior.

**Evidence:** reproducible Android build, device run evidence and release artifact.

### M5 — Third-party integration and SDK/docs — $4,000
- Minimal verifier client/SDK.
- Integration guide.
- Example downstream game/app consuming an eligibility claim without receiving raw health data.

**Evidence:** standalone example repository/module and integration test.

### M6 — Security, documentation and reproducibility hardening — $3,000
- Key-separation guidance.
- Failure/rollback documentation.
- Reproducible setup and public-good deployment guide.
- Final audit checklist and handoff.

**Evidence:** release checklist, documentation and tagged milestone release.

## Total

**$25,000** milestone-based request.

The budget deliberately avoids token issuance, liquidity provision, retail marketing or treasury distribution. Those are separate legally reviewed activities.
