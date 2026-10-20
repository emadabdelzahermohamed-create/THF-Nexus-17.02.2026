# THF Proof-of-Workout — Solana Foundation Grant Application Draft

Date: 2026-10-20
Project account email: TopHeroFit@gmail.com
Status: SUBMISSION DRAFT — no funds requested/accepted and no on-chain broadcast authorized by this file.

## Project
Top Hero Fit (THF) / Proof-of-Workout

## One-line description
A privacy-preserving verifiable-human-activity primitive that turns on-device workout evidence into auditable, replay-resistant proofs that Solana applications can consume without receiving raw workout video by default.

## Why this matters to Solana
Consumer reward systems need credible proof that an activity was performed by a real person rather than a replay, script, emulator, mock-location feed, or manual claim. THF is building the commercial fitness experience and proposes to release reusable proof formats, verification logic, threat-model documentation, reference integrations, and SDK/API documentation as public-good components. Solana is useful because low-cost/high-throughput settlement can support large numbers of small activity attestations/reward events and composability lets independent apps/challenges consume proofs.

## Privacy/security architecture
Raw camera frames remain on-device by default. The client derives pose landmarks, motion/activity metrics, timestamps, sensor summaries and integrity evidence. Server-issued session nonces and signed sessions bind evidence to a live session. Verification considers replay, mock-location, impossible-speed, device/app integrity and anomaly signals. Only verified sessions qualify for official economic rewards; manual logs remain personal-history data.

## Proposed milestone scope
M1 — Verification specification and threat model
Deliverables: public proof schema/specification; threat model covering replay, spoofing, mock location, device farms and evidence tampering; reference verifier; automated acceptance tests.
Acceptance: published repository/docs + reproducible test suite.

M2 — Android evidence pipeline
Deliverables: on-device pose/sensor evidence for walking/running, squat, push-up and plank; privacy defaults; signed session/nonce flow; evidence-score API.
Acceptance: installable Android build/test evidence and deterministic fixture tests demonstrating accepted/rejected evidence classes.

M3 — Solana devnet integration
Deliverables: devnet proof/attestation integration; explorer-verifiable transactions; SDK/API example for third-party consumers; CI tests.
Acceptance: public demo and explorer links plus reproducible integration tests.

M4 — Pilot and public measurements
Deliverables: consenting-user pilot; aggregate verification/fraud/retention measurements; remediation of discovered abuse cases; release of grant-safe reusable components.
Acceptance: public report, tagged release and final test evidence.

## Funding request policy
Request amount: TO BE COSTED FROM VERIFIED WORK PACKAGES BEFORE SUBMISSION.
Funding should be milestone-based. Each tranche should map to measurable deliverables and acceptance evidence. Do not choose the amount by the maximum available grant size. Evaluate any convertible-grant route separately from this public-good milestone scope.

## Public/community value
The reusable verification layer is intended to let Solana consumer applications add credible proof-of-human physical activity without collecting raw video by default. Reference formats, threat-model material, verifier components and integration documentation are candidates for open-source release. Top Hero Fit remains the commercial application that uses and extends the primitive.

## Current evidence required before submit
- Public website/demo URL: PENDING CURRENT VERIFIED URL
- Grant-safe public repository/component: CREATED in `ReleaseOps/ProofOfWorkout/` (spec + JSON schema); public URL still requires the repository/branch to be publicly reachable and verified
- Android build/test evidence: PENDING CURRENT LINK
- Devnet explorer transaction: PENDING
- On-chain project addresses: MUST RE-VERIFY IMMEDIATELY BEFORE SUBMISSION
- Per-milestone budget: SCENARIO MODEL CREATED; final rate basis still PENDING evidence
- Legal/privacy review: PENDING

## Form-field routing
Company/project name: Top Hero Fit / THF Proof-of-Workout
Applicant/project email: TopHeroFit@gmail.com
Country: use truthful applicant/entity jurisdiction at submission time; do not infer an entity jurisdiction.
Funding category: select the closest current official category after re-opening the live form.
Why You: use the project-value narrative above plus current shipped evidence; never claim users, transactions, partnerships or traction that are not evidenced.

## Hard gates
Do not solicit Egyptian retail token investment. Do not promise returns, listing, price appreciation or a liquidity date. Do not put private keys, seeds, OTPs, recovery codes or long-lived access tokens in this file/repository. Acceptance of investment funds, investment contracts, token sale/transfers, liquidity funding or irreversible on-chain broadcasts require the applicable legal gate and final owner confirmation.
