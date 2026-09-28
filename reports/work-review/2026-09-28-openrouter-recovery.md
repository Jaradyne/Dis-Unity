# OpenRouter record and recovery repair

Recorded 28 September UTC / 27 September Pacific. Jared reported viewing the OpenRouter dashboard with no charge and explicitly authorized moving on even if the historical receipt remains unknown. The separate Week One Governor automation was already disabled when inspected; it remains paused until the repo Governor is ready.

## What the stored record shows

| Event | Saved observation |
| --- | --- |
| September 24, 09:23 UTC | One completion request produced ID `gen-1790241783-S8W2Vc6pfpCKlAE4OrBL`. The stored response has no choices, no usage, no model and no routing metadata. |
| September 24–25 | Two additional GET-only recovery attempts followed the original attempt. The latest recovery reached the configured three-attempt boundary. No completed answer was recovered from this ID. |
| September 25, 09:07 UTC | A different generation, `gen-1790327195-43t7Cg064sAzTva87I4u`, returned a provisional answer with Nvidia identity, `is_byok:false` and cost **0**. Its recorded token counts are 9,032 prompt and 1,544 completion tokens. |
| September 27 audit | PR #20 recorded HTTP 404 for both metadata and stored-content GET endpoints for the incomplete September 24 generation. |
| September 27 Pacific, user dashboard inspection | Jared reports no charge and authorizes retiring the unresolved interaction and continuing bounded work. This is an attributed account observation; Work did not independently inspect the dashboard. |

The original request, filtered response, outcomes and recovery chain remain on `week-one-state:operations/week-one/runs/`. The original incomplete request is `gh-35980783938-2`; subsequent recoveries are `gh-35981423237-2` and `gh-36166138616-1`. The verified zero-cost answer is `gh-36116582032-1`.

## Two implementation faults

1. `public_response()` retained the generation ID but dropped top-level and choice-level errors before the adapter examined them. OpenRouter documents that a non-streaming failure can arrive as **HTTP 200 with a generation ID and error object but no choices**. This is consistent with the incomplete saved shape. It is an explanation to consider, not proof of the original cause: the historical raw error was not retained.
2. Exhausted receipt recovery became a permanent barrier to future work without an operator disposition path. A missing receipt and a detected charge require different treatment. Jared has now supplied the missing decision for this particular old interaction.

Official references, inspected 28 September UTC:

- [Errors and debugging](https://openrouter.ai/docs/api/reference/errors-and-debugging), especially non-streaming responses and typed errors.
- [Generation metadata](https://openrouter.ai/docs/api/api-reference/generations/get-request-&-usage-metadata-for-a-generation).
- [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection), including the maximum-price filter.

## Changes

- Preserve HTTP status and bounded numeric/typed error diagnostics before classifying failures. Raw provider messages, echoed request data and hidden reasoning are excluded. Explicit error responses remain failed attempts; they do not enter completion-receipt recovery. Positive cost and known route conflicts still take priority.
- `config/provider-dispositions.json` records Jared's decision for the exact generation, three runs and saved-response hash. The runtime marks those records `retired_unverified`, records the account observation and clears only that exhausted-recovery brake. Original outcome/status/attempt history is preserved. Changed responses, other brakes, closed windows and daily budgets are not overridden.
- New free-route attempts may proceed under the existing zero-price Nvidia route, NO GROQ, four-POST daily ceiling and one-generation/one-POST behavior. No receipt is fabricated and the old generation is not reissued as a recovery operation.
- The Answer Bee now supplies `peer_reflection` as a worker contribution. It no longer makes Governor decisions. The legacy response field is readable for recovery but is also treated as a worker contribution. The separate scheduled Governor remains disabled; play and digestion inputs can wait in the inbox.

## Practical conclusion

OpenRouter has already worked for this project at verified zero cost. The evidence supports repairing our integration and the stuck recovery lifecycle, rather than declaring the entire provider unusable. Actual free-route capacity remains subject to the next request's outcome. The missing original error cannot be reconstructed from the current filtered record.

## Work reflection

Preserving the ID while discarding the error made the record look more mysterious than it was entitled to look. Store the reason for failure before classifying it, and provide a narrow, attributed way to retire unresolved historical work. This lesson and Jared's disposition are projected into the reflection mailbox when the decision is applied.

## Verification

All 97 Python tests pass, including HTTP-200/HTTP-error diagnostics, positive-cost precedence, historical retirement, retained daily budget, and worker-only reflection behavior. The browser-component contract checks, canonical-state validation and whitespace check pass. Applying the decision to an isolated copy of live state `e2a39d54caea2ddc32b82d4e9b4b7fe139e96a28` clears the named brake and marks exactly three historical run records, while leaving their saved responses and historical Governor decisions unchanged. No API request was made by these local checks; the next hosted outcome must be inspected separately.
