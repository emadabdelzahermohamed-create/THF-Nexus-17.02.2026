# Guidance Language Diversity Contract

## Intent

Prevent a future catalog edit from collapsing the safety, regression, or progression guidance to generic copy in either Arabic or English while the other language still makes the existing combined bilingual assertion appear diverse.

## Goals

- Validate movement-family guidance diversity independently for `ar` and `en`.
- Fail catalog generation before runtime assets are written when either language is not distinct across all 12 movement families.
- Add a mutation-style product test proving an Arabic-only or English-only collapse is rejected.

## Non-goals

- No runtime catalog, exercise image, timer, animation, voice, Android, release, version, workflow, signing, or Play change.
- No requirement that every exercise have unique prose; movement-family reuse and named outlier overrides remain intentional.

## Constraints

- Keep all 112 exercises, 224 offline images, bilingual RTL/LTR behavior, and existing provenance unchanged.
- Work only in `fitness-v2/product/tools/build_catalog.py` and `fitness-v2/product/tests/test_catalog.py` plus these design/plan documents.

## Approaches

1. Keep the combined bilingual uniqueness assertion. Rejected because one language can regress while the other masks it.
2. Add separate assertions against the generated catalog. Better, but a passing current dataset does not prove the guard rejects a one-language regression.
3. Add a small builder validator and mutation tests for each language. Chosen because the build fails closed and the tests demonstrate guard sensitivity without changing runtime data.

## Acceptance

- The validator accepts the current 12-family guidance map.
- Replacing one family's Arabic triplet with another family's Arabic triplet raises a clear error while English remains untouched.
- The equivalent English-only mutation also raises.
- Existing product, source-contract, and backend suites remain green.
