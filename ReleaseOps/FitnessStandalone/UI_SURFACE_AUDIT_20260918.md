# THF Fitness — User-visible Surface Audit

Date: 2026-09-18
Rule: a backend/API capability is NOT release-complete unless it has a usable user-facing surface and UI acceptance evidence.

## Confirmed visible now
- Standalone auth/login.
- Plans, exercises, warm-up/cool-down, logging, progress.
- Injury/recovery screening surfaces.
- Basic professional/gym directory in RC2.
- Admin control plane in RC2.
- Avatar source asset is present in RC2 and canonical SHA matches Stage16A.
- AppDeploy production currently exposes Stage16A only as a textual contract, not as a rendered GLB.

## Confirmed backend-only / under-surfaced gaps
- Trainer marketplace is only a directory; no real trainer workspace for clients, assignments, follow-up, or bookings.
- Competitions/leaderboards exist in RC2 APIs but are linked to raw JSON rather than a complete UI flow.
- AI Coach exists as API output in RC2 but is not a full user-facing coach screen.
- Production AppDeploy does not expose trainer network, competitions, leaderboards, recovery/injury flows, or trainer workspace.
- Production AppDeploy Coach tab shows only Stage16A metadata; it does not render the canonical 3D asset.
- RC2 photoreal renderer is blocked by configuration: external Three.js/GLTFLoader URLs are configured while external renderer modules are disabled.
- RC2 photoreal runtime manifest is stale: it still describes an older 109-clip asset while the canonical current asset is 137 joints / 195 clips.

## Release gates added
1. Every material backend route/domain must map to a visible screen/action or be explicitly admin/internal-only.
2. Every visible surface must have an automated UI test or device/browser evidence.
3. Android and Web must expose the same core user workflows against the same identity/data backend.
4. Canonical 3D means an actually rendered Stage16A avatar, not only the text '137 joints / 195 clips'.
5. Exercise-specific photoreal motion remains fail-closed until visual QA passes; a generic avatar preview may render the canonical asset without claiming exercise-motion certification.
6. Trainer functionality must include a trainer-facing workspace, not only trainer listings.

## Immediate implementation order
P0: fix 3D renderer configuration + stale manifest and add visible canonical avatar preview.
P0: add trainer workspace + booking/follow-up surfaces.
P0: replace raw JSON competition links with leaderboard/challenge UI.
P0: expose AI Coach as a real screen.
P1: mirror the same surfaces into the AppDeploy production web and Android WebView release.
P1: add UI/E2E coverage for all above.
