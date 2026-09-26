# Mistral Small 4 one-shot evaluation result

Date: 25 September 2026

Jared confirmed in the Mistral Admin UI:
- Free plan;
- $10 included monthly API usage;
- API pay-as-you-go is OFF (the UI offers an **Enable** button);
- monthly allowance resets on the first day of each calendar month.

## Intended test

Model: `mistral-small-latest` (Mistral Small 4)

Task: one short conservative multilingual semantic comparison using the WHO accountability/responsibility wording already in the Parallax packet.

Maximum completion: 500 tokens.

No fallback model and no retry were authorized.

## Result

The request returned:

- HTTP **429**
- `rate_limited`
- service message: **Rate limit exceeded**

No successful model answer was generated, so this run provides **no quality signal about Small 4**.

Mistral documents 429 as a rate-limit response governed by organization-level requests/sec, tokens/minute and tokens/month limits. Free mode has the lowest limits. The next safe diagnostic is the Mistral Admin **Limits** page; do not repeatedly POST until the exact limit is visible.

GitHub Actions run:
https://github.com/Jaradyne/Dis-Unity/actions/runs/36217398550
