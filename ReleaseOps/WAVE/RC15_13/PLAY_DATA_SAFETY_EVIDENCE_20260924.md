# WAVE MAWJA — Play Data Safety evidence map

Checkpoint: 2026-09-24  
Package: `com.wave.mawja`  
Source baseline: RC15.3 + RC15.5 + RC15.7 + RC15.8 launch fix + RC15.11/RC15.13 web overlays.

This file records **code evidence**, not final legal declarations. Final Play Console answers must match the exact production configuration and business behavior.

## Android permission surface

The approved TWA manifest requests only:

- `android.permission.INTERNET`
- `android.permission.ACCESS_NETWORK_STATE`

It does **not** request camera, microphone, location, contacts, Bluetooth, external-storage/media-library, or advertising-ID permissions.

## Account and authentication data

Code evidence shows first-party account handling for:

- Email address.
- Display name.
- Password input used only for authentication.
- Stored password material is a PBKDF2-SHA256 derived hash plus a random salt and iteration count; plaintext passwords are not stored.
- Session tokens/cookies.
- Session cookie attributes include HttpOnly, Secure, and SameSite=Lax.

Relevant implementation: `lib/wave-auth.ts` and `app/api/auth/*`.

## User library / activity data

The account library stores user-linked playback state including:

- Content slug / content identifier.
- Favorite state.
- Playback progress seconds.
- Duration seconds.
- Last-updated timestamp.

The library is keyed to the signed-in user's email in the current schema.

Relevant implementation: `app/api/library/route.ts`.

## Profile data

The profile surface displays:

- Display name.
- Email address.
- Synced library/progress state.

Relevant implementation: `app/profile/page.tsx`.

## Local / offline data

The client contains offline-library and local preference features, including:

- Authorized offline media saved on the device when the user chooses that feature.
- Local quota / retention behavior.
- Device-side preferences such as age-band and playback/offline settings.

These should be distinguished from server-side collected data when completing Play Data Safety.

## Media / playback and service processing

The current source supports:

- HLS/MP4 playback.
- Watch progress.
- Subtitles / translation / dubbing pipelines when enabled.
- Internal media APIs and Cloudflare-backed infrastructure.
- Optional internal service synchronization using server-side credentials.

Any third-party or external processor actually enabled in production must be reflected in the final privacy/Data Safety answers.

## Ads / measurement

The current source contains an internal advertising/campaign surface and ad-slot logic.

The dependency scan did **not** find a direct AdMob or Firebase Analytics SDK dependency in the submitted Android/web package.

Whether Play's "Contains ads" declaration must be set to Yes should follow the exact live behavior visible to ordinary users, not the presence/absence of a third-party SDK alone.

## External embeds

The live page source includes at least one `youtube-nocookie.com` embed path for a live-stream fallback. If that path is reachable in the submitted experience, review the corresponding data behavior when completing Data Safety/privacy disclosures.

## Account deletion

The current source includes an account-deletion route that removes the user account and linked data where implemented, with anonymization of some references where operational/security records need to remain.

Relevant implementation: `app/api/account/route.ts`.

## Privacy policy

Live policy URL:

`https://wave-mawja.p-my.workers.dev/privacy`

The policy states the current account/authentication handling, local preferences/download behavior, internal ad measurement, security controls, and deletion/retention approach.

## Store / declaration guardrails

Do not claim:
- no data collection, if account/library/progress features are enabled;
- no ads, if ordinary users are shown promotional/ad campaign surfaces;
- child-directed use, unless the product is intentionally designed for children and all Families requirements are satisfied;
- data sharing with a processor unless that processor is actually enabled for the submitted production build.

Keep Play Console declarations synchronized with any future changes to authentication, analytics, ads, media processing, or third-party SDKs.
