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
- Entitlement: a Founding Hero profile badge and gold profile accent.
- The offer is explicitly cosmetic. It does not restrict exercises or Health Connect, grant competitive advantage, distribute tokens, or promise a financial return.
- Price is never hard-coded; the UI uses the localized price returned by Google Play.
- The UI supports purchase, pending, owned, restore, canceled, loading and unavailable states in Arabic RTL and English LTR.

## Safety and lifecycle contract

- Google Play Billing Library `9.1.0`, the current official release documented on 2026-10-07.
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
- Kotlin billing state tests cover catalog/ownership callback ordering, pending fail-closed behavior, unrelated products and signature verification. Android compilation/units await the PR workflow because no local Gradle executable is present in the runner.

## Fail-closed release truth

This checkpoint does **not** claim a live product, successful payment, revenue, Play Internal, signed AAB, phone runtime or purchase restoration PASS. Remaining release actions are:

1. Build and test the source in GitHub Actions.
2. Configure the one-time product in Play Console for package `com.topherofit.thf.pulse`.
3. Inject the app's public Play licensing key as `THF_PLAY_LICENSE_KEY` into the protected signed-build workflow.
4. Test purchase, pending, cancel, acknowledge and restore with a Play license tester on the exact signed Internal candidate.
5. Verify the final product presentation and Data Safety / privacy declarations before production rollout.
