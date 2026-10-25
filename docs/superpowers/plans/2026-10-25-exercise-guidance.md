# Movement-specific Exercise Guidance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver bilingual movement-specific safety, regression, and progression guidance for every offline exercise.

**Architecture:** Extend the existing `FAMILY` mapping in the deterministic catalog builder. Generated runtime catalog files remain the only app-facing output; tests validate their observable content rather than grepping implementation text.

**Tech Stack:** Python 3, JSON, JavaScript data payload, `unittest`.

**Spec:** `docs/superpowers/specs/2026-10-25-exercise-guidance-design.md`

## Global Constraints

- Do not edit Android tracking, notification, release, Play, or open-PR-owned web files.
- Preserve 112 exercises, 224 approved offline images, source provenance, and bilingual RTL-ready strings.
- Guidance is educational and must not diagnose or promise medical safety.

## Review Focus

- A generic fallback must not silently return identical copy for all families.
- Every existing movement family must have complete Arabic and English guidance.
- Jump, locomotion, mobility, and recovery copy must describe their distinct risks.
- Generated JSON, JS, and manifest must remain deterministic and mutually consistent.
- Counts, IDs, assets, hashes, and provenance must not drift.

---

### Task 1: Pin the guidance contract

**Files:**
- Modify: `fitness-v2/product/tests/test_catalog.py`

**Interfaces:**
- Consumes: generated `exercises.json`
- Produces: behavioral assertions for family coverage and representative bilingual guidance

- [x] Write tests asserting 12 distinct movement-family guidance triplets and exact representative jump, locomotion, and recovery behavior.
- [x] Run the targeted tests and verify they fail because the current catalog has one shared triplet.
- [x] Commit the failing contract only with the implementation in Task 2.

### Task 2: Generate family-specific guidance

**Files:**
- Modify: `fitness-v2/product/tools/build_catalog.py`
- Modify: `fitness-v2/android/app/src/main/assets/pulse/data/exercises.json`
- Modify: `fitness-v2/android/app/src/main/assets/pulse/data/exercises.js`
- Modify: `fitness-v2/product/CATALOG_MANIFEST.json`

**Interfaces:**
- Consumes: `GUIDANCE[pattern]` bilingual guidance fields
- Produces: `regression`, `progression`, and `safety` in every catalog item

- [x] Add the six guidance fields to all 12 families with conservative, movement-relevant copy.
- [x] Replace generic emitted fields with the selected family's fields.
- [x] Regenerate using the pinned source checkout and verify the targeted tests pass.
- [x] Run all product, source-contract, and backend tests plus `git diff --check`.
- [x] Commit implementation; open the PR into the canonical branch with exact test evidence and runtime QA acceptance.
