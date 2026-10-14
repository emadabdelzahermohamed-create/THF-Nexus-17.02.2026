# One-Day Mobile Rescue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Produce installable Android APKs for the core THF apps/games from one shared, testable rescue runtime, prioritizing real phone functionality over polish.

**Architecture:** One Android app module with product flavors. Each flavor gets its own applicationId/title/key while sharing hardened native primitives. Product-specific screens are real offline/local functions; network-dependent functions fail visibly rather than faking success.

**Tech Stack:** Android Java, AGP 8.11.1, Gradle 8.13, SDK 36, JUnit 4, GitHub Actions.

**Spec:** User request of 2026-10-14 plus ReleaseOps/APK_FIRST_TARGETS.json.

## Global Constraints
- targetSdk 36.
- No secrets in source.
- Produce debug-signed phone-test APKs first.
- Never report a feature successful without a real build/test artifact.
- Core functions must work offline where the product permits it.

## Review Focus
- Every declared product maps to exactly one package id and APK.
- Offline products still function with airplane mode.
- Media picker cancellation does not crash.
- Game touch controls remain bounded on screen.
- Network failure in watch-only TokenOps is shown to the user.

---

### Task 1: Canonical product registry
**Files:** test ProductRegistryTest.java; create ProductRegistry.java.
- [ ] Write registry test covering all rescue products and unique package ids.
- [ ] Run test and verify RED because ProductRegistry is absent.
- [ ] Implement ProductRegistry minimally.
- [ ] Run test and verify GREEN.

### Task 2: Functional native rescue surfaces
**Files:** MainActivity.java, AndroidManifest.xml, resources, app/build.gradle.
- [ ] Add smoke tests for supported mode selection.
- [ ] Implement real screens: dashboard, workout timer/animation, local media picker/player, persisted social feed, share publisher, watch-only token lookup, persistent vault, RuinsCiv local world/farm loop, EndCiv local combat loop.
- [ ] Run unit tests and assemble all flavors.

### Task 3: CI APK factory
**Files:** .github/workflows/rescue-mobile-day1.yml.
- [ ] Build on isolated rescue branch with Java 17 + Android SDK 36.
- [ ] Verify APK files exist for every flavor and generate SHA-256 manifest.
- [ ] Upload one phone-test artifact containing all APKs plus checksums.
