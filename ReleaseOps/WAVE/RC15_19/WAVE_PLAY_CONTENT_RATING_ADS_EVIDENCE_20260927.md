# WAVE RC15.19 — Google Play Content Rating and Ads Evidence

Recorded UTC: 2026-09-26T23:00:00Z  
Product: WAVE_MAWJA  
Package: `com.wave.mawja`  
Release reference: versionCode `15302`

## Truth boundary

This is an evidence package for the Google Play Console declarations that are not fully exposed through the Android Publisher Edits API. It does not claim that the Console questionnaire was submitted.

## Ads declaration

Recommended Google Play **Contains ads** answer: **Yes**.

Evidence observed on the live consumer surface:

- The Live page contains a clearly labeled ad/sponsor placement outside the official player.
- Watch pages contain a clearly labeled sponsor placement between content sections.
- The UI states frequency capping and contextual placement.
- The current Play-generated 15302 APK contains no `AD_ID` permission, AdMob SDK marker, or Firebase Analytics marker.
- Data Safety for 15302 has already been accepted by the Android Publisher API and does not declare Android advertising identifiers.
- Child mode copy states contextual ads only; no personalized advertising claim should be made for children.

Reviewer-facing declaration:

> WAVE MAWJA contains clearly labeled contextual sponsor/ad placements outside the video player. The current Android artifact does not request the Advertising ID and does not embed AdMob or Firebase Analytics. Ads must remain non-personalized/contextual for child profiles and must not obscure controls or imitate system/download buttons.

Do not answer **No** while the live product displays labeled ad placements.

## Content rating evidence

WAVE is a curated streaming/catalog application, not a user-generated-content social platform.

Current public catalog evidence:

| Title/surface | Evidence |
|---|---|
| Sintel | Open-license fantasy/adventure short; WAVE metadata shows `+10` |
| Big Buck Bunny | Open-license family/comedy title |
| Tears of Steel | Open-license science-fiction/action title |
| Elephants Dream | Open-license fantasy/experimental title |
| Live | Official NASA source presentation |
| Catalog | Country/year/studio/language/age filters; no user upload control on the consumer surface |
| Rights | Each observed title exposes license/source information |

Conservative questionnaire facts:

- App category: entertainment / video streaming.
- Curated third-party/open-license media: yes.
- User-generated content exposed to consumers: not evidenced on the current public surface.
- Social sharing/chat between users: not evidenced on the current consumer surface.
- Gambling or simulated gambling: not evidenced.
- Real-money prizes or wagering: not evidenced.
- Sexual content/nudity: not evidenced in the observed sample catalog.
- Drugs/alcohol/tobacco: not evidenced in the observed sample catalog.
- Strong profanity: not evidenced in the observed sample catalog.
- Violence: answer conservatively based on the complete released catalog. The observed catalog includes fantasy/action titles and age labels up to `+13`; do not declare “none” if any released scene contains fantasy/action violence.
- Fear/horror: answer conservatively after viewing the complete released catalog; fantasy peril may be present.
- External links: yes, rights/source links and the official NASA source are exposed.
- Purchases/subscriptions: no evidence of an active in-app purchase or subscription flow in versionCode 15302.
- Location sharing: no; exact Play APK has no location permission.
- Camera/microphone: no; exact Play APK has neither permission.
- Age handling: a privacy-preserving on-device age-band prompt filters content; it does not collect a birth date.
- Child profile: family content and contextual ads only. Any commercial child-directed launch must continue to follow Google Play Families requirements and applicable parental-consent rules.

## Reviewer navigation

1. Choose the 18+ band to view the complete current sample catalog.
2. Open Browse and inspect all four titles and their age/license metadata.
3. Open Sintel and inspect the title metadata, license, player, offline entry, and related content.
4. Open Live and inspect the official NASA source presentation plus the ad label outside the player.
5. Open a watch page and inspect the clearly labeled sponsor placement.
6. Confirm Privacy, Child Safety, Content Rights, and account-deletion documentation from the footer.

## Existing technical evidence

- Play-generated 15302 APK privacy inspection:
  - run `36243580600`
  - APK SHA-256 `961e5f60fe8b4694472029b09a34357d6e2004114c9ecfb2a69c831895041dc7`
  - only `INTERNET` and `ACCESS_NETWORK_STATE`
  - no Camera, Microphone, Location, `AD_ID`, AdMob, or Firebase Analytics markers
- Data Safety submission:
  - run `36243903548`
  - HTTP 204 / PASS
- Release readiness:
  - run `36243068952`
  - PASS
- Live account E2E:
  - run `35985314664`, attempt 2
  - PASS

## Console owner action

In Play Console:

1. Set **Contains ads = Yes**.
2. Complete the IARC/content-rating questionnaire using the released catalog, not planned future content.
3. Use conservative answers for fantasy/action violence and fear after reviewing every released title.
4. Save the rating result and verify that it is compatible with the app’s selected target audience.
5. If future catalog/import tooling adds materially stronger content or user uploads, update the rating and policy declarations before publishing that change.

No production promotion should be attempted until these Console-only declarations and the closed-testing production-access prerequisite are complete.
