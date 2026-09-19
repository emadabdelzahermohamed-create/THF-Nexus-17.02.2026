# THF Fitness / Pulse — Final Product Scope & Scientific UX Contract

Date: 2026-09-18
Status: binding product/release scope
Branch: `release/fitness-standalone-v1-20260918`

## Product principle
THF Fitness is not a collection of backend endpoints or static workout cards. Every material capability must be a complete user journey with:
1. user-facing UI,
2. persisted/account-scoped data where applicable,
3. Android + Web parity for core workflows,
4. scientific/safety rules,
5. automated UI/API evidence,
6. admin/trainer controls where applicable,
7. accessibility/localization,
8. no false claims when sensors, health data or visual verification are unavailable.

The uploaded screenshots are quality/UX references only. They are not to be cloned. THF keeps its own identity while matching the level of polish, clarity, progression, discoverability and session execution shown by mature fitness applications.

## A. Core sport/training domains
The shared training engine must support the agreed domains with sport-specific prescriptions rather than copying the same logic everywhere:
- Home fitness and bodyweight training.
- Gym / resistance training / hypertrophy / strength.
- Weight-management fitness goals (loss, gain, maintenance).
- Running and walking with GPS-derived distance/pace/route where permission and device capability allow.
- Cycling with distance/speed/elevation/route where supported.
- Football conditioning.
- Swimming plans and session logging.
- Gymnastics / calisthenics.
- Yoga, mobility and flexibility.
- Recovery sessions, relaxation, meditation and breathing.
- Warm-up, cool-down, injury-risk warnings and regressions/progressions across applicable sports.

## B. Scientific training prescription
The prescription engine must use evidence-informed parameters appropriate to the sport:
- frequency, intensity, time and type,
- progressive overload and progression/regression,
- training volume and density,
- RPE/RIR where relevant,
- work/rest intervals,
- weekly structure and recovery,
- beginner/intermediate/advanced/pro levels,
- equipment availability,
- body area / movement pattern,
- goals and schedule,
- deload/recovery rules when appropriate,
- safety flags and stop/modify guidance.

No plan may be labelled personalized solely because a generative model produced prose. Personalization requires actual user inputs/history and rule-based constraints.

## C. Professional session UX
Every supported workout type should converge on a mature session experience:
- plan-generation onboarding,
- weekly target and day scheduling,
- searchable/filterable exercise library,
- exercise detail with instructions,
- target/secondary muscle visualization,
- movement demonstration,
- canonical 3D Stage16A demonstration where mapped,
- timers/counters/sets/reps/load/distance as applicable,
- voice/TTS guidance,
- pause/resume/skip/previous/next,
- rest timer with configurable extension,
- warm-up/work/rest/cool-down phases,
- perceived difficulty and session feedback,
- completion summary, streak/progress and recovery follow-up,
- offline-safe local execution with server reconciliation.

## D. Canonical 3D Motion Coach
- Only MPFB/MakeHuman Stage16A lineage is allowed.
- Contract: 137 joints / 195 animation clips.
- Legacy humanoid fallback is forbidden.
- 3D must be visibly rendered in actual training flows, not merely named in text.
- Exercise-to-animation mapping must be explicit and QA'd.
- Camera framing, transitions, IK/foot contact, LOD, shadows and mobile performance are release gates.
- Motion/sensor coaching must distinguish: demonstrated movement, sensed movement, and verified movement.
- Never claim rep/form verification when device/sensor/camera evidence is unavailable.

## E. Activity, health and wearable data
Production Android should use Health Connect as the primary Android health-data interoperability layer where supported and permissioned.
User-visible domains include, when supported and consented:
- steps and activity,
- exercise sessions,
- distance and calories,
- heart rate,
- sleep,
- body weight/body composition,
- nutrition/hydration,
- routes/location for workouts,
- other vitals only when actually integrated and permitted.

Samsung/wearable integrations are adapters, not a replacement for the core account model. Data-source provenance, deduplication, permission state and sync status must be visible enough to avoid double-counting.

## F. Tracking/reporting UX
- daily/weekly/monthly reports,
- workouts, duration, energy expenditure and streaks,
- body-weight trend,
- body-measurement trend where entered or synced,
- sport-specific metrics,
- recovery/readiness context without presenting medical diagnosis,
- personal bests,
- training consistency,
- export/delete/privacy controls.

## G. AI Coach
AI Coach must be a real screen and action layer, not a chat decoration.
It should:
- read permitted goals/history/training state,
- explain why a recommendation changed,
- adapt volume/intensity/schedule within scientific constraints,
- propose safe alternatives,
- use trainer/admin-approved content rules,
- clearly separate fitness/wellness guidance from medical diagnosis,
- fail closed on health-red-flag scenarios.

## H. Trainers and gyms
### Trainer workspace
- trainer application and verification,
- trainer profile/specialty,
- client bookings,
- client list limited to authorized relationships,
- program/plan assignment,
- follow-up notes and progress review,
- video/session links where enabled,
- messaging/notifications,
- completion/cancellation state,
- no client-data access before verification and relationship authorization.

### Gym integration
- gym discovery/profile,
- membership/entitlement adapters,
- opening/peak-time/occupancy data where a partner provides it,
- gym-specific classes/plans,
- trainer marketplace,
- gym challenges/leaderboards,
- QR/NFC/check-in adapters when a gym integration supports them,
- activity/calorie integration,
- equipment-aware plan selection,
- real-store/equipment/nutrition surfaces kept distinct from competitive fairness.

## I. Nutrition
Nutrition is a first-class user journey:
- goal-driven calorie and macro targets,
- meal logging,
- food search and favorites,
- hydration,
- dietary preferences/restrictions,
- meal-plan suggestions,
- shopping/prep guidance,
- nutrition trend reports,
- integration with Health Connect nutrition data when appropriate.

Nutrition guidance must not diagnose or treat disease. Disease-specific therapeutic diets require an explicit professional/medical boundary.

## J. Dietary supplements
Supplement content must be evidence-first and safety-first:
- ingredient fact cards,
- evidence strength,
- common uses,
- known safety concerns,
- medicine/supplement interaction warnings,
- upper-limit/overdose cautions where authoritative data exists,
- athlete/bodybuilding contamination/doping-risk warnings where relevant,
- personal supplement log,
- clinician/pharmacist discussion prompt for higher-risk use.

No supplement is automatically recommended because it is sold in the THF ecosystem. Commercial placement must not override evidence or safety. Prescription/restricted substances and unsafe/high-risk unregulated products are excluded.

## K. Habit change / quitting
The habit-change system must support recovery-friendly, non-punitive behavior change:
- choose habit and reason for change,
- baseline and trigger logging,
- goal/quit date where appropriate,
- craving/urge check-ins,
- coping-plan prompts,
- streaks plus lapse recovery without resetting identity/progress narratives destructively,
- reminders,
- social/professional support paths,
- progress reports.

For tobacco/nicotine cessation, evidence-based counseling/support resources are allowed. Medication decisions remain clinician/pharmacist territory; the app does not prescribe.

## L. Competitions, leagues and anti-cheat
- visible competition discovery and rules,
- individual/team challenges,
- running/activity/fitness events,
- free and paid leagues where policy permits,
- leaderboards,
- seasons,
- prizes/rewards,
- proof-of-activity / proof-of-human,
- server-authoritative scoring,
- anti-cheat and trust score,
- penalties/appeals workflow,
- no manual score entry for trusted/ranked outcomes,
- no pay-to-win and no purchases that falsify fitness evidence.

## M. Social and motivation
- friends/follow relationships,
- group challenges,
- shareable achievements with privacy controls,
- accountability groups,
- trainer/community content,
- motivational surfaces that do not shame users,
- notifications based on user preferences,
- Arabic/English RTL/LTR first, localization-ready thereafter.

## N. Settings/accessibility/privacy
- language,
- TTS/voice,
- workout settings,
- Health Connect permissions/sync state,
- wearable integrations,
- Data Saver,
- Reduce Motion,
- High Contrast,
- scalable text,
- notification controls,
- privacy/data export/account deletion,
- app-access and consent surfaces.

## O. Admin/control plane
Admin must be able to manage without code changes:
- exercises,
- sports,
- plans,
- animation mappings,
- trainer/gym entities,
- competitions,
- scoring/trust thresholds,
- nutrition/supplement content,
- habit programs,
- localization,
- safety copy,
- feature flags,
- staged preview/validate/publish/rollback.

## P. Evidence/safety source policy
Production health/fitness content should prefer authoritative, updateable sources and licensed/open data.
Baseline authoritative references include:
- WHO physical-activity guidance.
- Android Health Connect official APIs and data-type/permission guidance.
- NIH Office of Dietary Supplements (ODS) fact sheets/API for supplement evidence and safety.
- CDC/other authoritative public-health cessation resources for tobacco quitting.
- Peer-reviewed or recognized professional exercise-science guidance for sport-specific prescription.

Every imported/open-source dataset or library must have license/provenance recorded before production use.

## Q. Release definition of done
A feature is not complete when only backend code exists.
It is complete only when the applicable set passes:
- UI journey,
- backend persistence/data,
- permissions,
- auth/RBAC,
- scientific/safety rules,
- Android/Web parity,
- offline behavior where relevant,
- automated tests,
- physical/device tests where sensors/GPU/wearables are involved,
- admin controls where needed,
- observability,
- rollback,
- Play policy/declaration fit.

## Current release direction
Do not ship the older simplified RC2 UX as the final product. The next production candidate must inherit the user-visible/scientific scope above and preserve the canonical Stage16A avatar. Release work remains publication-first, but publication cannot intentionally regress the agreed visible Fitness product.
