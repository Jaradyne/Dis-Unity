# Proposed Mistral budget governor — zero-out-of-pocket design

Status: **Chat Aiden design for Work review. Not a live provider adapter.**

## Observed account facts

- The stored `MISTRAL_API_KEY` successfully authenticated to `GET /v1/models` on 25 September 2026.
- No inference was sent during that probe.
- Mistral's public Free plan currently advertises **$10/month in API credits**.
- Mistral documents Free mode as included monthly usage, with PAYG available separately to extend beyond included usage.
- **Do not infer that PAYG is off from the API-key probe.** Confirm Subscription state before inference.

## Fail-closed account boundary

Before any model inference:
1. Human confirms the Organization is in Free mode.
2. Human confirms PAYG is **OFF**.
3. No credit card/billing mechanism is enabled merely to expand API access.
4. If the provider later changes these semantics, brake Mistral use until reviewed.

With PAYG off, the provider-level boundary should be: included usage exhausts -> requests stop rather than creating out-of-pocket usage.

## Project budget inside the $10 included bucket

Use a separate Dis-Unity budget so the Bees do not consume the entire account allowance accidentally.

Recommended initial values:
- published monthly included credit: **$10.00**
- Dis-Unity soft project ceiling: **$8.00**
- safety remainder: **$2.00**
- per-call maximum reservation: configurable by role/model
- unknown-price model/API/tool: **not eligible**

The $8 ceiling is deliberately adjustable; it is not a claim that $2 must always remain unused.

## Reserve-before-call accounting

Every proposed Mistral inference must reserve its **worst allowed cost before POST**.

For token-priced models:

`reservation = estimated_input_tokens * input_price + max_output_tokens * output_price`

Use current reviewed model pricing, never an old hard-coded assumption without an effective date.

Call flow:
1. compute/measure prompt token estimate conservatively;
2. read selected model's reviewed input/output price;
3. compute worst-case cost using `max_tokens`;
4. include any known tool/API fee;
5. compare reservation to `remaining_project_budget`;
6. if it does not fit, do not POST;
7. if it fits, write an immutable reservation record;
8. send exactly one generation;
9. settle reservation against returned actual usage/cost when available;
10. preserve unresolved accounting if receipt/usage is incomplete; do not create another generation merely to learn the first one's cost.

Concurrent calls must consume the same shared budget ledger so two Bees cannot each promise the same remaining dollars.

## Suggested role fit

### Mistral Medium
Use sparingly for **bounded high-value synthesis/reasoning**:
- hard Garden residuals after cheaper collection/crosschecking;
- Governor-adjacent comparative synthesis when a distinct second model is valuable;
- complex cross-domain relationship checks;
- difficult code/design review where Codestral/Small is insufficient.

Current public list price at design time: $1.50/M input, $7.50/M output.

### Mistral Small
Good default Mistral text model for:
- Collector synthesis;
- multilingual comparison support;
- compact structured extraction/rewrite;
- inexpensive second-opinion passes;
- routine classification that genuinely benefits from a model.

Current public list price at design time: $0.15/M input, $0.60/M output.

### Codestral
Use for bounded code-completion/code-review tasks where a coding specialist is useful.
Current public list price at design time: $0.30/M input, $0.90/M output.

### Voxtral
Use only when audio itself is the problem: transcription, speech/audio understanding, later language/voice experiments. Do not spend audio quota on text tasks.

### OCR
Use only when document extraction is genuinely needed and Files/native PDF extraction is insufficient or the project specifically wants a Mistral OCR comparison.

### Free endpoints
An endpoint shown by Mistral as literally **Free** can use a separate zero-dollar lane, but it must still have request/rate limits and provenance. “Free” does not mean unlimited.

## Cost classes for Bees

Suggested initial classes:
- `zero`: endpoint itself reviewed as free;
- `tiny`: <= $0.002 reserved;
- `small`: <= $0.01 reserved;
- `reasoning`: <= $0.05 reserved;
- `special`: > $0.05 requires explicit Work/human approval.

These are ceilings, not targets.

A Bee role should declare:
- eligible Mistral model(s);
- maximum input;
- maximum output;
- maximum reservation;
- why Mistral is preferable to deterministic/public-source work or another zero-cost provider;
- stop condition.

## No silent fallbacks

- No automatic switch from Small to Medium.
- No automatic third-party model use merely because it appears in `/v1/models`.
- No tool call (web search, code execution, image generation, premium news, etc.) unless its separate fee is reviewed and budgeted.
- No Groq, including indirect routing, under existing project policy.
- A model-list entry establishes visibility, not cost eligibility.

## Monthly reset

Do not assume the reset date/time from memory. Read the actual Mistral Subscription/usage period or official provider metadata. Reset only the Dis-Unity budget ledger when the provider's included-credit period is known to have reset.

## First live-call recommendation

After PAYG-off confirmation:
- use `mistral-small-latest`;
- one tiny deterministic test prompt;
- very small `max_tokens`;
- reserve the worst-case cost first;
- record model, prices, prompt, response usage, estimated/actual cost, timestamp and provider response IDs;
- stop after that one call and review before enabling Bees.
