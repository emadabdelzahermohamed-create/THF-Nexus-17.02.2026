# AI Provider Matrix — Zero-Subscription-Dependency Strategy

## Goal
Keep the 10-day launch program moving even when one provider hits a quota, outage, or unavailable model. GitHub remains the only source of truth. Providers are workers; none is authoritative by itself.

## Hard rules
- No provider may be required for release. Every critical lane must have at least one fallback.
- Prefer free tiers, OAuth connections, open-source models, and self-hosted execution before any paid API.
- Never purchase, upgrade, or enable auto-billing without owner approval.
- Never commit API keys, tokens, signing material, OAuth client secrets, or private keys.
- Each provider works on a dedicated branch and opens a PR/checkpoint. GPT Integrator decides merge/release.
- A 429/quota exhaustion is a routing event, not a blocker: record it once, rotate immediately, and continue.
- Do not send every task to every model. Route by specialization to avoid duplicated cost and conflicting edits.

## Current connected lanes
| Provider | Verified status | Best use | Fallback role |
|---|---|---|---|
| GitHub | CONNECTED | source of truth, issues, PRs, Actions, evidence | mandatory coordination bus |
| ChatGPT / GPT Integrator | READY | architecture, review, merge, release decisions | final integration authority |
| Google Jules | ACTIVE | bounded GitHub implementation and issue fixes | primary autonomous coding worker |
| Gemini CLI | AUTHENTICATED / COOLDOWN | coding, review, tests, multimodal analysis | resumes after quota reset; never blocks launch |
| Groq | READY | fast bounded code/reasoning/review | low-latency API fallback |
| OpenRouter Free | READY | general reasoning/code fallback through zero-price router | cross-provider emergency fallback |
| Replit | READY | operational dashboards, web/admin prototypes and isolated web work | web/admin fallback |
| Superpowers | CONNECTED | TDD, debugging, planning, code-review discipline | quality/process guard |
| Hugging Face | READY OAuth, non-Pro | open-source model discovery and available jobs/research | open-source fallback |
| Context7 | READY | current library/API documentation | API-accuracy fallback |
| Desktop Commander local runner | READY | deterministic builds/tests/media conversion; FFmpeg/Pillow verified | strongest no-model-quota execution fallback while device is online |

## Runtime evidence
- Jules: applying the `jules` label to issue #42 was accepted by `google-labs-jules[bot]`, which created an active Jules task.
- Gemini: repository secret authentication is valid and the worker reached the Gemini generation API. The latest bounded WAVE run then exhausted the free-tier daily model quota, so its correct state is `COOLDOWN`, not authentication failure.
- Groq: the provider-health workflow performed a real authenticated chat inference successfully.
- OpenRouter Free: the provider-health workflow performed a real `openrouter/free` inference successfully.
- Local runner: Desktop Commander reports `cs-973169170814-default` online; FFmpeg 7.0.2 user-space and Pillow are verified.

## Routing while Gemini is cooling down
| Task class | Primary | Fallback 1 | Fallback 2 | Last-resort no-quota path |
|---|---|---|---|---|
| Architecture / cross-project integration | GPT Integrator | OpenRouter Free | local deterministic analysis | Gemini after cooldown |
| Bounded code implementation | Jules | Groq | OpenRouter Free | local runner |
| PR review / regression analysis | GPT Integrator | Groq | OpenRouter Free | local runner |
| Web/admin prototype | Replit | Jules | OpenRouter Free | local web toolchain |
| Animation orchestration / asset pipeline code | Motion lane + Jules/GPT | Hugging Face/open models | local FFmpeg/Pillow | Gemini after cooldown |
| Documentation / migrations / repetitive tests | Jules | Groq | OpenRouter Free | local scripts |
| Current API/library docs | Context7 | official docs | repository docs | pinned dependency docs |
| Build/test/package | GitHub Actions | local runner | Hugging Face where suitable | deterministic local tooling |

## Quota-aware state machine
`READY -> ACTIVE -> RATE_LIMITED -> COOLDOWN -> READY`

On `429`, quota exhaustion, or provider outage:
1. persist provider + task + timestamp + exact error;
2. do not retry in a tight loop;
3. move the task to the next compatible READY provider;
4. preserve the same Git base SHA and acceptance criteria;
5. resume the exhausted provider only after cooldown/reset;
6. deduplicate by task ID + base SHA so two providers never implement the same task simultaneously.

## Branch ownership
- `agent/jules/<lane>/<date>`
- `agent/gemini/<lane>/<date>`
- `agent/groq/<lane>/<date>`
- `agent/openrouter/<lane>/<date>`
- `agent/hf/<lane>/<date>`
- `agent/local/<lane>/<date>`
- `agent/replit/<lane>/<date>`

Only the Integrator merges into canonical release/main branches after evidence gates pass.
