# Fitness Phone QA Preflight Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tested, read-only, fail-closed gate before any physical Fitness QA interaction.

**Architecture:** A standalone Bash script performs one device inventory then only targeted `dumpsys`/`pm` reads. Python `unittest` supplies a fake ADB executable and asserts both classification and the complete command log.

**Tech Stack:** Bash, Python standard-library `unittest`, fake executable fixtures.

**Spec:** `docs/superpowers/specs/2026-10-25-fitness-phone-preflight-design.md`

## Global Constraints

- Never reconnect, pair, wake, unlock, install, launch, force-stop, tap, change permissions, or clear data.
- Exit zero only for `qa_state=READY_FOR_MANUAL_QA`.
- Perform exactly one `adb devices -l` call.
- Package is `com.topherofit.thf.pulse`.

## Review Focus

- Unauthorized/offline rows are not counted as usable devices.
- A requested serial must be present and in `device` state.
- Screen parsing must fail closed when interactive or keyguard evidence is ambiguous.
- Either `isForeground=true` or `startRequested=true` blocks QA.
- Version and installer parsing may be absent without falsely reporting readiness if the package itself is absent.

---

### Task 1: Read-only preflight and contract tests

**Files:**
- Create: `fitness-v2/scripts/fitness_phone_preflight.sh`
- Create: `fitness-v2/tests/test_fitness_phone_preflight.py`
- Modify: `ReleaseOps/FitnessStandalone/CHECKPOINT_51012_PHONE_QA_GATE_20261025_0953.md`

**Interfaces:**
- Consumes: `${ADB_BIN:-adb}` and optional `--serial SERIAL`.
- Produces: `qa_state=<STATE>` on stdout; exit `0` only for `READY_FOR_MANUAL_QA`.

- [ ] Write tests for offline, multiple-device, locked, active-session, and ready states, including one inventory call and forbidden-command assertions.
- [ ] Run the tests and verify RED because the script does not exist.
- [ ] Implement the minimal Bash classifier using read-only ADB commands.
- [ ] Run the targeted tests and verify GREEN.
- [ ] Run the repository Fitness test suite and `git diff --check`; record any unrelated baseline failures exactly.
- [ ] Append the current one-shot ADB-offline observation and the preflight contract to the owned QA checkpoint.
- [ ] Commit and update the existing QA pull request branch without changing canonical release state.
