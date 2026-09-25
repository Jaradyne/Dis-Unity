# Mistral safe API probe — 25 September 2026

Chat Aiden performed one explicitly authorized, non-inference connectivity probe using the repository secret `MISTRAL_API_KEY`.

## Request

- Method: `GET`
- Endpoint: `https://api.mistral.ai/v1/models`
- Authentication: GitHub Actions secret, masked in logs
- Chat/completion inference: **none**
- Prompt tokens generated: **none**
- Billing action requested: **none**

Official Mistral documentation identifies this endpoint as the model-list/key verification call.

## Result

- HTTP status: **200**
- The key authenticated successfully.
- The workspace returned a substantial model catalog, including `mistral-small-latest`, `mistral-medium-latest`, `magistral-small-latest`, Codestral, Voxtral, embedding, moderation and OCR model IDs.

This establishes that the stored key can access the Mistral API model-list endpoint despite the Studio banner saying “Upgrade to Pro to use your API keys and access the full API.”

It **does not establish**:
- that every listed model is usable under Free mode;
- the free quota for any individual model;
- that a chat/completion request would be zero-cost;
- that PAYG is disabled;
- that a provider adapter should be enabled.

Do not make a model inference until Work/Chat verifies the workspace's current Free/PAYG state, the selected model's eligibility and a fail-closed zero-spend boundary.

## Run

GitHub Actions run: https://github.com/Jaradyne/Dis-Unity/actions/runs/36198127186
