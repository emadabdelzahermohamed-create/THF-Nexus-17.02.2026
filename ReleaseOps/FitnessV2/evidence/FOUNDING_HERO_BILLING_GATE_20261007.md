# Fitness V2 Founding Hero billing gate — 2026-10-07

## Scope and deduplication

- Project: Top Hero Fit Fitness V2 only.
- Task ID: `FITNESS_V2_FOUNDING_HERO_BILLING_20261007`.
- Base SHA: `950372f15efd89b99f6197d3f46f3c3fdb51c508`.
- Dedup key: `FITNESS_V2_FOUNDING_HERO_BILLING_20261007@950372f15efd89b99f6197d3f46f3c3fdb51c508`.
- Cash spend: zero.
- WAVE, Creator AI, TokenOps, games, signing material and production rollout are unchanged.

## User-visible product

The Android Profile screen now contains one bounded digital offer:

- Google Play one-time product ID: `thf_founding_hero_lifetime`.
- Android candidate identity: `com.topherofit.thf.pulse`, versionCode `51004`, versionName `5.0.0-v2-alpha4`.
- Entitlement: a Founding Hero profile badge and gold profile accent.
- The offer is explicitly cosmetic. It does not restrict exercises or Health Connect, grant competitive advantage, distribute tokens, or promise a financial return.
- Price is never hard-coded; the UI uses the localized price returned by Google Play.
- The UI supports purchase, pending, owned, restore, canceled, loading and unavailable states in Arabic RTL and English LTR.

## Safety and lifecycle contract

- Google Play Billing Library `9.1.0` Java client, avoiding an unnecessary Kotlin-metadata dependency while retaining the current official API.
- One active BillingClient, automatic service reconnection, pending one-time purchases, startup/resume ownership reconciliation and connection shutdown.
- Fresh product-detail query before purchase; no stale price or offer token is persisted.
- The app grants the cosmetic entitlement only for the exact product, `PURCHASED` state and a valid Play RSA signature.
- `PENDING` never grants entitlement.
- Purchased non-consumables are acknowledged and can be restored through `queryPurchasesAsync`.
- No purchase token, order ID, signature, card information or bank information is exposed to the WebView.
- The public Play licensing key defaults to empty. In that state the offer is disabled and explains the configuration dependency before any purchase can launch.

## Local verification

- Fitness V2 source contracts: `15/15` PASS.
- Product/content contracts: `12/12` PASS.
- Backend unit/security contracts: `8/8` PASS.
- JavaScript syntax: PASS.
- `git diff --check`: PASS.
- Kotlin billing state tests cover catalog/ownership callback ordering, pending fail-closed behavior, unrelated products and signature verification.
- CI run `37638001930` exposed and eliminated the unnecessary Billing KTX/Kotlin metadata mismatch.
- CI run `37638434976` then passed Kotlin compilation and Android unit tests, and exposed an Activity Result/old transitive Fragment lint violation. The source pins the compatible stable Fragment Java runtime instead of suppressing lint; a fresh workflow run must prove the final package.

## Fail-closed release truth

This checkpoint does **not** claim a live product, successful payment, revenue, Play Internal, signed AAB, phone runtime or purchase restoration PASS. Remaining release actions are:

1. Build and test the source in GitHub Actions.
2. Configure the one-time product in Play Console for package `com.topherofit.thf.pulse`.
3. Configure the app's public Play licensing key as repository variable `THF_PLAY_LICENSE_KEY`; the protected workflow passes it into the build without logging the value and otherwise records a fail-closed status.
4. Test purchase, pending, cancel, acknowledge and restore with a Play license tester on the exact signed Internal candidate.
5. Verify the final product presentation and Data Safety / privacy declarations before production rollout.
