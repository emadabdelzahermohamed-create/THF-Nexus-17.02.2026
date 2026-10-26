# Product mobile visual audit — 2026-09-27

## Scope

This checkpoint independently inspected the already-hashed runtime screenshots for the active Product task before proposing any source change. It did not use an owner account, password, cookie, session token, or protected API.

Applied production source remains AppDeploy v63 `1790500694233`; no production source was changed in this checkpoint.

## Runtime images verified

| Scene | Viewport | Source version | SHA-256 | Visual result |
|---|---:|---:|---|---|
| Arabic onboarding | 390×844 | `1790499939566` | `33de966811f06a574810c222f4965f270125a16e4e45d044317c6a60d9f65a2b` | Valid RTL glyph shaping, direction, hero hierarchy and visible non-privileged boundary |
| Arabic onboarding | 1280×720 | `1790499939566` | `2e214198a66cd746fc697b2c589a63544f7d95d79adac7a28b096f307657f621` | Wide layout remains legible and correctly right-aligned |
| English dashboard | 390×844 | `1790500005572` | `86e123649cdcaf5906a1730d490f24a677dd7a844b09fc073a1a2b090196ef6e` | LTR hierarchy and metric cards render without overlap |
| English dashboard | 1280×720 | `1790500005572` | `9cc3a4abfc853a62630889728be1fb44f7ddc6c7fc4cbdfe3541566592a0abda` | Wide dashboard hierarchy and plan setup are legible |

Screenshot sources:

- Arabic mobile: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790499962714/mobile.png
- Arabic web: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790499962714/web.png
- English mobile: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790500026414/mobile.png
- English web: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790500026414/web.png

## New Product finding

The core mobile content is not clipped, but the primary tab rail is only implicitly discoverable as a horizontal scroller:

- `src/index.css` gives `.tabs` `overflow-x:auto` but no scroll-snap behavior, focus-edge guarantee, or hidden-overflow affordance.
- `src/App.tsx` renders a semantic `nav`, but the rail has no localized `aria-label`; buttons do not expose `aria-current` or selected-tab state.
- The 390 px Arabic and English captures both show a partially visible edge item. This proves horizontal overflow exists, but not that keyboard, screen-reader, touch, and RTL/LTR navigation behavior is release-ready.

The safe Product-only patch prepared for the next deploy window is:

1. add a localized navigation label and `aria-current="page"` to the active tab;
2. add scroll snapping, touch momentum/overscroll containment, stable focus visibility and a non-intrusive edge affordance in both directions;
3. keep the existing labels, information architecture and backend behavior unchanged;
4. test AR/EN at 390 px and 1280 px, then capture the previously missing English onboarding and Arabic dashboard scenes.

## Deployment preflight result

The mandatory AppDeploy deployment-instructions preflight returned:

- code: `CREDITS_USAGE_LIMIT_REACHED`
- reset: `2026-09-28T00:00:00.000Z`
- message: fewer than the 14-credit deployment minimum remain
- instruction: do not retry before reset

Therefore no speculative source version was created and v63 remains the applied production source.

## Fail-closed decision

This is additional runtime visual-review evidence and a narrowed Product defect, not Product PASS. Bilingual active-workout screenshots, interaction proof, the reciprocal onboarding/dashboard language captures, and the tab-rail accessibility patch remain open.
