# Optional Health Services Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Real optional Health Connect reads with granular consent and truthful provenance.
**Architecture:** Native hub; isolated optional reader; pure Kotlin access/result policy. Basic activity/reward/writer code is unchanged.
**Tech Stack:** Kotlin, AndroidX Activity/Lifecycle, Health Connect 1.1.0, JUnit4.
**Spec:** docs/superpowers/specs/2026-10-25-health-services-design.md

## Global Constraints
- minSdk 26 / targetSdk 36; existing dependencies; read-only new scopes; existing exercise-only writes unchanged.
- Native files only; do not edit busy web UI, canonical, release version/workflows, signing or Play.
- Memory-only health data; foreground-only; no diagnostic or rewards claim.

## Review Focus
- Permission revoked while a read runs: erase result and show permission required.
- Permission denied for one type: another granted type remains readable.
- Missing data vs zero: preserve measured zero; never fabricate zero for null.
- Overlapping sources: provider aggregates for cumulative totals, not client sums.
- Background/return: blank sensitive values immediately, reload grants; no stale screen.

### Task 1: Ship the optional native hub as one independently reviewable increment

**Files:** Create HealthServiceModels.kt, HealthServicesReader.kt, HealthServicesActivity.kt and HealthServicePolicyTest.kt / HealthServicesReaderTest.kt; modify native manifest, rationale resources, MainActivity openHealthSettings only.

**Interfaces:** HealthService defines id, read permission, title/purpose in Arabic and English; HealthMetricResult defines status, values, origins, observedAt/window and method. HealthServicesReader reads one HealthService independently. HealthServiceAccessPolicy masks results when the grant is absent; it never persists data.

- [ ] Write failing behavioral tests for permission masking, partial grants, absent-vs-zero, revocation and independent per-type results; run them and record RED.
- [ ] Implement minimal pure policy, then real Health Connect read adapter and native consent surface.
- [ ] Run targeted tests GREEN; source/product/backend suites; Kotlin unit + lint + APK build using existing CI workflow on the isolated branch.
- [ ] Review privacy/provenance/error paths and exact file ownership; fix important findings with regression tests.
- [ ] Commit, open tested PR to canonical, checkpoint exact SHA/build/artifact and unresolved phone/declaration gates. Integrator merges and allocates release version.
