# Movement-specific exercise guidance design

## Intent

Replace the catalog's one-size-fits-all safety, regression, and progression copy with useful bilingual guidance that matches each exercise's existing movement family. This makes the exercise detail service materially more professional without changing catalog size, approved media, runtime navigation, or Android tracking.

## Goals

- Provide distinct Arabic and English safety, regression, and progression guidance for all 12 existing movement families.
- Keep all 112 exercise identities, sections, prescriptions, tracking metadata, provenance, and 224 offline images unchanged.
- Generate the runtime JSON/JS and manifest deterministically from the catalog builder.
- Test consumer-visible catalog output, including high-risk jump/locomotion/recovery examples and complete family coverage.

## Non-goals and anti-goals

- No medical diagnosis, treatment instruction, or claim that an exercise is safe for every user.
- No change to Android tracking, notifications, release files, Play, runtime layout, approved images, or open-PR-owned web files.
- No new exercise count or marketing claim.

## Approach

Three approaches were considered:

1. Hand-edit each generated exercise: rejected because regeneration would erase the work and 112 copies would drift.
2. Add per-exercise overrides: appropriate only for named exceptions; excessive for a catalog whose existing architecture already classifies every item into a movement family.
3. Extend the existing 12-family builder metadata and regenerate: selected because it is deterministic, bilingual, auditable, and changes every consumer without duplicating content.

Each family receives six new fields: safety, regression, and progression in Arabic and English. The builder emits those values into each catalog item. Product tests assert every family is represented and receives meaningful, family-specific copy; exact representative literals prevent a generic fallback from passing.

## Acceptance

- Twelve unique guidance triplets exist across the 12 movement families.
- Every catalog entry has non-empty bilingual values.
- Jump guidance mentions landing/control; locomotion guidance addresses pace/environment; recovery guidance prevents joint/nerve pressure.
- Catalog remains 112 exercises and 224 verified offline assets.
- Full product, source-contract, and backend suites stay green.
