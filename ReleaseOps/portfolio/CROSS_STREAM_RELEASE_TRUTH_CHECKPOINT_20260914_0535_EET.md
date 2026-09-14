# THF + WAVE Cross-Stream Release Truth Checkpoint — 2026-09-14 05:35 EET

## Truth boundary
- FINAL_OR_PLAY_READY=FALSE.
- Physical-device evidence remains required and SHA-bound for every mobile candidate.
- No production signing, signed AAB, Play approval, production deployment, GPU/device QA, or stable production HTTPS/WSS is claimed.
- WAVE remains isolated from THF.

## Material issue found
The portfolio readiness matrix is stale relative to the authoritative apps/games candidate registries. More importantly, two Android package identities exist in both registries with different exact APK SHA-256 values:
- com.topherofit.thf.spark
  - apps registry: 92bc7f913d560a185044af2df7b1955d3a0b29eca920034edf3cd9741bce0c23
  - games registry: 9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea
- com.topherofit.thf.rush
  - apps registry: 304164035cc4b82d23e2b2e6bf48abca3c466c46f5668a203cf0b4cfca223e99
  - games registry: 3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a

Because physical-device acceptance and Play promotion are exact-candidate-SHA bound, neither package can be promoted while two different candidates are simultaneously represented as authoritative.

## Safe repair
Added a fail-closed cross-stream candidate consistency validator, regression tests, and GitHub Actions evidence workflow.
- validator commit: 7584ea00eebde977d4f3d77d926cdb43ed5c36f5
- test commit: d0478b17e6e5076a23198f02a4f16f64f19b6211
- workflow commit: 0424e5514e36392e94f3d5b741f130003c9790f1
- CI bootstrap repair: a1ef5c81c9aa8f9a3a1eb6d729d50661546414ad

The first workflow run 34799648808 failed in test-tool bootstrap before candidate evaluation. This was repaired by explicitly installing pytest. The rerun 34799679870 completed SUCCESS: regression tests PASS, registry evaluation completed fail-closed, and evidence was uploaded.

## Evidence
- workflow run: 34799679870
- artifact: THF-CROSS-STREAM-CANDIDATE-CONSISTENCY-V1
- artifact ID: 10331470255
- artifact digest: sha256:cbf648486d90cbac142b63830688fddb57db91f412542fcb54577847a39701cb
- promotion remains blocked for conflicting package identities; this is an intentional release-policy result, not a CI crash.

## Other current material state
- Latest game offline/local truth workflow 34798602367 is SUCCESS after a conservative Android XML namespace exception; no APK bytes changed.
- World/economy/social semantic authority proof run 34798467300 is SUCCESS and remains non-production/isolation-bound.
- Apps and games registries remain physical-device pending.
- WAVE RC14 remains blocked on CI OS Login access to canonical /root/workspace/wave-mawja; no older WAVE source was substituted and no SSH/OS Login weakening was performed.
- Stable production HTTPS/WSS, production signing/AAB, Play Internal acceptance, and exact-candidate physical-device evidence remain unproven.

## Next safe action
Reconcile Spark/Rush release authority by selecting one exact candidate lineage per package only after proving the selected candidate preserves all required app + game functions. Do not delete the alternate evidence; mark it superseded/rejected only after the combined-function candidate passes exact payload/runtime gates. Continue all unrelated candidates independently.

Evidence body SHA-256: cbcccc3e23daef0c1190e683f311b76eca5baec793935c69e7502548be527550
