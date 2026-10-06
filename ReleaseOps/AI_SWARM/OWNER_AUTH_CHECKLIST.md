# Owner Authorization Checklist — Free/No-Subscription Paths

Only these steps require owner interaction. Everything else should be automated by the swarm.

## 1. Google Jules — connect GitHub
- Open Jules and sign in with Google.
- Connect GitHub.
- Grant access only to the repositories you want Jules to work on, starting with `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
- Return to Jules and enroll the repo.
- Do not give Jules direct production secrets; it works through Git branches/PRs.

After connection, the swarm can assign bounded GitHub issues to Jules without rebuilding project context.

## 2. Gemini CLI GitHub Action — free API-key lane
- Create a Google AI Studio API key.
- In GitHub repo settings, add repository secret named exactly `GEMINI_API_KEY`.
- Never paste the key in chat, an issue, a PR, a commit, or a workflow log.

Once present, the Integrator can activate GitHub issue/PR workflows using the official Google `run-gemini-cli` action and the repository `GEMINI.md` instructions.

## 3. Groq Free Plan — fast fallback
- Create/sign into Groq Cloud.
- Create an API key.
- Add it only as secret `GROQ_API_KEY` in the secure runner/GitHub secret store.
- Keep billing upgrade disabled unless explicitly approved later.

## 4. OpenRouter free-model fallback
- Create/sign into OpenRouter.
- Create an API key.
- Add it only as secret `OPENROUTER_API_KEY`.
- Router policy must allow only zero-price/free model routes unless the owner explicitly changes the policy.

## 5. Context7 — current API/library docs
- Connect the Context7 plugin in ChatGPT when prompted.
- No project source-of-truth changes; it is read/reference only.

## 6. Self-hosted no-quota runner
Current authorized Desktop Commander device `thf-wave-builder` is offline. Bring the device/agent online when convenient. Once online the Integrator can inspect available CPU/RAM/GPU and install/configure an open-source local inference lane if the hardware supports it.

## Already connected / no action needed
- GitHub
- ChatGPT/GPT Integrator
- Replit
- Superpowers
- Hugging Face OAuth (Jobs/read scopes; non-Pro account)

## Never do
- Do not send secrets in chat.
- Do not create long-lived keys when OAuth/OIDC/WIF can replace them.
- Do not enable auto-top-up or paid upgrade for any provider without explicit approval.
- Do not give every provider access to every repository; least privilege by project.
