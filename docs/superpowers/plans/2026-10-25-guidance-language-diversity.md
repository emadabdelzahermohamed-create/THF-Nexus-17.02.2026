# Guidance Language Diversity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make catalog generation fail when Arabic or English movement-family guidance loses independent diversity.

**Architecture:** Add a pure validator to the existing catalog builder, call it before asset generation, and test it with the real guidance map plus one-language mutations. Runtime assets remain byte-for-byte unchanged.

**Tech Stack:** Python 3, `unittest`, deterministic catalog builder.

**Spec:** `docs/superpowers/specs/2026-10-25-guidance-language-diversity-design.md`

## Global Constraints

- Do not modify runtime catalog data, images, Android tracking/notifications, release files, workflows, versioning, signing, or Play.
- Validate exactly the 12 current movement families and the three fields `safety`, `regression`, and `progression` independently for `ar` and `en`.

## Review Focus

- Arabic-only duplicate guidance must fail even if English remains distinct.
- English-only duplicate guidance must fail even if Arabic remains distinct.
- Missing language keys must fail clearly rather than silently reducing coverage.
- The current real guidance map must pass.
- Catalog output and manifest hashes must remain unchanged.

---

### Task 1: Enforce independent language diversity

**Files:**
- Modify: `fitness-v2/product/tools/build_catalog.py`
- Modify: `fitness-v2/product/tests/test_catalog.py`

**Interfaces:**
- Consumes: `GUIDANCE`, a mapping of movement family to bilingual guidance fields.
- Produces: `validate_guidance_diversity(guidance: dict) -> None`, raising `ValueError` for a non-distinct or incomplete language contract.

- [x] **Step 1: Write failing mutation tests**

Add tests that import the builder, validate the current map, then duplicate only the Arabic or only the English guidance triplet across two families and require `ValueError` naming the affected language.

- [x] **Step 2: Run the targeted tests and verify RED**

Run: `python -m unittest fitness-v2/product/tests/test_catalog.py -v`

Expected: failure because `validate_guidance_diversity` does not exist.

- [x] **Step 3: Implement and invoke the validator**

Validate all 12 expected families and the three guidance fields separately for `ar` and `en`; call the validator at the start of `build()` before any output is written.

- [x] **Step 4: Run targeted and full verification**

Run the product, source-contract, and backend suites; compare generated runtime catalog and manifest hashes with the canonical base; run `git diff --check`.

- [x] **Step 5: Commit and submit a PR**

Commit only the two implementation files plus this spec and plan, push the dedicated branch, and open a PR into `agent/codex/fitness-recovery/20261023`.
