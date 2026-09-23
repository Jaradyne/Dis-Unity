# Free AI provider introduction and evaluation plan

## VIBE BAN — NO GROQ

The user explicitly excludes Groq until further notice. **Do not add, call, benchmark, route through, recommend, or use Groq as a fallback or hidden upstream provider unless the user explicitly reverses this instruction.** Treat this as a provider-policy deny rule, not a technical ranking.

## Current candidate pool

### 1. Google Gemini
- Candidate: Gemini 3.8 Flash for agentic/reasoning work.
- User's Free project screenshot on 2026-09-22 visibly shows **5 RPM** for Gemini 3.6, 3.7 and 3.8 Flash. Active limits are per project and model; Google says actual capacity can vary.
- Free-tier content may be used by Google for product/model improvement. This project is intentionally public, so that is acceptable to the user.
- Treat 429 quota/rate and 503 capacity as different attempt outcomes.

### 2. Cloudflare Workers AI
Initial candidates to benchmark within the free 10,000-Neuron/day allocation:
- `@cf/nvidia/nemotron-3-120b-a12b` — agent/multi-agent oriented
- `@cf/google/gemma-4-26b-a4b-it` — reasoning/vision/function calling
- `@cf/zai-org/glm-4.7-flash` — multilingual reasoning and tool calling
- `@cf/qwen/qwen3-30b-a3b-fp8` — reasoning/function calling
- `@cf/openai/gpt-oss-120b` — OpenAI open-weight reasoning model
- `@cf/aisingapore/gemma-sea-lion-v4-27b-it` — Southeast-Asian-language/local-context specialization

Do not assume every catalog model is Free-plan eligible forever. Recheck current Cloudflare docs before runtime selection.

### 3. OpenRouter Free
- 25+ free models; 50 free API requests/day at present.
- Do not use `openrouter/free` as opaque roulette for evaluation.
- Select explicit models/providers so provenance and policy are known.
- Count **attempts** separately from **completed useful tasks**.
- On daily allowance exhaustion, mark provider unavailable until documented reset; if reset semantics are uncertain use a conservative cooldown and recheck before use.

### 4. Mistral (France)
- Mistral currently offers API Free mode with no card required, subject to rate/usage limits visible in its console.
- Candidate for direct-provider evaluation so Dis-Unity is not dependent on one U.S. or one Chinese ecosystem.

### 5. DeepSeek (China)
- Official API is currently paid, with peak/off-peak token pricing; therefore it is **not** an initial free-pool provider.
- Cloudflare's current DeepSeek V4 models require paid Workers access.
- Keep as a future optional provider or evaluate a clearly identified free third-party host only if provenance/terms are acceptable.

## Model-nationality diversity worth testing

The free/near-free ecosystem already exposes work from:
- United States: OpenAI open-weight GPT-OSS, NVIDIA Nemotron, Meta Llama
- Google ecosystem: Gemma
- China: Zhipu GLM, Alibaba Qwen, Moonshot/Kimi where eligible, DeepSeek when a suitable access path exists
- France: Mistral
- Singapore: AI Singapore SEA-LION
- India: AI4Bharat language/translation models
- Japan: PFN/PLaMo embedding models

The point is not a national scorecard. Diverse training, languages and model families may expose different blind spots.

## Work Aiden evaluation protocol

For each candidate model run the same **golden ticket set** with fixed source packets and hidden answer checks where possible.

Measure separately:
- factual extraction accuracy
- source/provenance obedience
- distinction between fact/inference/unknown
- refusal to invent inaccessible/current facts
- useful counterevidence
- ability to detect a locally important pattern
- birth-request restraint
- structured-output/schema compliance
- context retention
- coding/runtime quality where relevant
- multilingual/local-language competence where relevant
- latency
- provider errors/capacity
- token/Neuron/request efficiency

Do not create one total intelligence score. Classify **role fitness**, for example:
- scout/question-finding
- evidence extraction
- synthesis
- skeptic/reviewer
- coding/runtime
- multilingual/local-context
- long-context digestion
- vision/document reading

Ratings should be revisable as the model or prompts change.

## User-updated fallback policy

This supersedes the earlier absolute "best model only" rule:

- Free models that are **demonstrably fit for the assigned role** may be used as backups.
- No silent downgrade: the attempt record must name the actual model.
- A fallback is not independent corroboration merely because it is a different model.
- Groq is excluded regardless of technical eligibility until the user changes that instruction.
