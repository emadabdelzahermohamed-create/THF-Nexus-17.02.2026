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
| Provider | Status | Best use | Fallback role |
|---|---|---|---|
| GitHub | CONNECTED | source of truth, issues, PRs, Actions, evidence | mandatory coordination bus |
| ChatGPT / GPT Integrator | CONNECTED | architecture, review, merge, release decisions | final integration authority |
| Replit | CONNECTED | operational dashboards, web/admin prototypes and isolated web work | web/admin fallback |
| Superpowers | CONNECTED | TDD, debugging, planning, code-review discipline | quality/process guard |
| Hugging Face | AUTHENTICATED OAuth, non-Pro | open-source model discovery and remote Jobs where free/available | open-source/compute fallback |
| Context7 | CONNECTING/OPTIONAL | current library/API documentation | accuracy fallback for changing APIs |
| Desktop Commander `thf-wave-builder` | OFFLINE at matrix creation | self-hosted/local deterministic builds and local-model fallback | strongest no-quota fallback once online |

## External provider lanes to authorize
### Tier A — direct GitHub agents
1. **Google Jules** — primary autonomous coding worker for bounded GitHub issues/PRs.
   - Owner action: sign in and connect only the THF repo(s) needed.
   - No paid subscription is part of the routing contract.
2. **Gemini CLI GitHub Action** — issue/PR assistant, reviewer, test writer, isolated coding worker.
   - Owner action: create a Google AI Studio API key and store it as GitHub secret `GEMINI_API_KEY`.
   - Never paste the key into chat or Git.
3. **Replit** — already connected; use only for isolated operational/web surfaces unless explicitly assigned a product branch.

### Tier B — free API fallbacks
4. **Groq Free Plan** — fast code/reasoning fallback for bounded generation/review jobs.
   - Owner action: create API key; store as `GROQ_API_KEY` in GitHub/runner secret store only.
5. **OpenRouter Free Router** — multi-model emergency fallback; route only to zero-price models.
   - Owner action: create API key; store as `OPENROUTER_API_KEY`.
   - Free route is rate-limited; never treat it as the only provider.
6. **Hugging Face OAuth/Jobs** — already authenticated for read/jobs; use public/open-weight models and free/available CPU/GPU resources where allowed.

### Tier C — local/open-source fallback
7. **Self-hosted runner / Ollama or compatible OpenAI-style server** on an authorized machine/VPS.
   - No recurring model quota.
   - Use for deterministic code review, smaller coding models, embeddings, asset metadata, conversion scripts, tests and build orchestration.
   - Heavy visual generation only when compatible GPU exists; otherwise route visual jobs to a free external lane.

## Not part of the automatic zero-cost pool
- Claude/Anthropic direct API is optional only. Do not make it a release dependency because direct API usage can require billing/paid entitlement.
- Any provider requiring a credit card, paid plan, auto-top-up, or subscription remains disabled unless the owner explicitly approves it.

## Task routing
| Task class | Primary | Fallback 1 | Fallback 2 | Last-resort no-quota path |
|---|---|---|---|---|
| Architecture / cross-project integration | GPT Integrator | Gemini | OpenRouter free reasoning model | local open-weight model + human/GPT review |
| Bounded code implementation | Jules | Gemini CLI | Groq | local coder model |
| PR review / regression analysis | GPT Integrator | Gemini CLI | Groq/OpenRouter | local coder/reasoner |
| Web/admin prototype | Replit | Gemini/Jules | local web toolchain | manual deterministic implementation |
| Animation orchestration / asset pipeline code | Motion lane + GPT | Gemini multimodal where available | HF/open models | Blender/FFmpeg/scripts locally |
| Documentation / migrations / repetitive tests | Gemini/Jules | Groq | OpenRouter free | local model/scripts |
| Current API/library docs | Context7 | official web docs | repository docs | pinned dependency docs |
| Build/test/package | GitHub Actions | self-hosted runner | HF CPU Job where suitable | authorized local machine |

## Quota-aware state machine
`READY -> ACTIVE -> RATE_LIMITED -> COOLDOWN -> READY`

On `429`, quota exhaustion, or provider outage:
1. persist provider + task + timestamp + exact error;
2. do not retry in a tight loop;
3. move the task to the next compatible provider;
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
