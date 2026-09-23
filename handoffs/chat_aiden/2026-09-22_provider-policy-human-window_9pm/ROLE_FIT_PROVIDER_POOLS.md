# Role-fit provider pools and credential plan

## Policy

A role owns an **ordered collection of eligible provider/model candidates**. The collection is tested, versioned and revisable.

Example:

```json
{
  "role": "answer_synthesis",
  "candidates": [
    {"provider":"gemini","model":"<verified-id>","status":"eligible"},
    {"provider":"cloudflare-workers-ai","model":"<verified-id>","status":"eligible"},
    {"provider":"openrouter","model":"<explicit-model-id>","status":"eligible"}
  ]
}
```

The attempt ring walks the role's eligible collection, records every result, respects provider-specific backoff/reset state and stops when a usable answer satisfies the Question's stop condition.

A role can have a different collection:
- scout/question finding
- evidence extraction
- synthesis
- skeptic/reviewer
- coding/runtime
- multilingual/local-context
- long-context/document work
- vision

No single total model score is required.

## Provider deny rule

**NO GROQ.** Groq is denied until the user explicitly changes this instruction. The deny rule applies to:
- direct Groq API calls;
- benchmark/evaluation;
- fallback lists;
- hidden upstream routing through aggregators.

For OpenRouter, use explicit model/provider routing controls rather than opaque automatic routing. Provider allowlists/ignore rules must preserve the Groq deny rule.

## Secrets: one per service, not one per model

Models hosted by the same service normally share that service credential.

### Initial useful AI ring

1. **Gemini**
   - credential: existing `GEMINI_API_KEY` / current Google auth-key equivalent
   - one Google credential can select multiple eligible Gemini models
   - quota remains project/model specific

2. **Cloudflare Workers AI**
   - secret: `CLOUDFLARE_API_TOKEN`
   - nonsecret configuration: `CLOUDFLARE_ACCOUNT_ID`
   - the same Cloudflare token/account can invoke many Workers AI models
   - do not create one secret per model

3. **OpenRouter**
   - secret: `OPENROUTER_API_KEY`
   - one key can invoke the permitted OpenRouter model pool
   - requests should name explicit models and constrain providers so denied upstreams cannot be selected

This means the initial three-provider AI ring needs **two new secrets** if Gemini's key is already present: one Cloudflare token and one OpenRouter key.

### Optional later direct provider

4. **Mistral**
   - secret: `MISTRAL_API_KEY`
   - add only when direct Mistral evaluation is ready; no need to create it merely because support is conceivable

### Search/sensor credentials are separate from model credentials

5. **Tavily**
   - secret: `TAVILY_API_KEY`
   - add when the search adapter is ready

6. **Brave Search**
   - secret: `BRAVE_SEARCH_API_KEY`
   - defer unless Brave is actually added as a search fallback

### Future communication credentials

- Research Gmail: OAuth credential set/refresh token only when mail ingestion is implemented.
- Discord: bot token only when a Discord bot is implemented.
- Vercel: current ChatGPT connection does not automatically give GitHub Actions a Vercel deployment credential; choose Git integration or a scoped deployment token only when a portal is actually built.

## Secret handling

- Store credentials in GitHub Actions Secrets or the relevant platform secret store.
- Never commit secret values to Git.
- Account IDs, model IDs and endpoint URLs are configuration, not necessarily secrets.
- Add a secret only when a reviewed adapter is ready to consume it.
- A credential existing does not make a provider eligible.
