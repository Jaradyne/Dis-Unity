# Clinical Reconsideration and Second Opinions

A first opinion must remain open to meaningful reconsideration. This Garden wing keeps the original assessment, a person's reported burden, requests for another review and any later correction inspectable together. It does not decide a diagnosis or require an adjudicated clinical error before preserving a report of harm.

Started November 21; completed and checked November 22, 2026 Pacific. [Readable demonstration](generated/RECONSIDERATION.md) · [Chat/Digest handoff](HANDOFF_CHAT_DIGEST.md) · [published routes and limits](POLICY_BOUNDARIES.md) · [review](REVIEW.md) · [validation](VALIDATION.md).

## One fictional case

The supplied case contains no private medical history or real provider incident. A provisional initial assessment is disputed; the fictional patient reports distress. One service explicitly declines a review, citing capacity. Another referral's receipt is initially unknown. A later revision records receipt, authorization, booking, attendance and a reasoned reconsideration of primary material. The later reviewer agrees with the provisional explanation while preserving uncertainty and corrects a description of available records.

That correction is sent to the continuing-care team. Receipt, changed care and clinical benefit remain UNKNOWN. Clinical error, causal responsibility and reviewer independence also remain UNKNOWN. The earlier refusal and report of distress remain visible. The first opinion's certainty can be recorded as provisional, definitive or unspecified; those terms describe the opinion, not its accuracy.

## Evidence boundaries

| Observation | Separate question that remains |
| --- | --- |
| A person reports psychological harm | What caused it, and who is responsible? The report itself is retained. |
| A formal second-review route exists | Was a usable review obtained? |
| An opinion is repeated or a second clinician appears | Was primary material reconsidered, and what supports independence? |
| Another review agrees or disagrees | Is either clinical opinion accurate? |
| A review discusses possible error | Does its scoped conclusion affirm error, reject it or remain inconclusive? |
| A correction is authored or dispatched | Did the intended care team receive and use that specific correction? |
| Care changes | Is there a separately documented benefit? |

This is a small typed extension of [Patient Care Continuity](../../medical-access/20261113/README.md). It composes the existing care schema with a [reconsideration lens](../../../schemas/clinical-reconsideration.schema.json), reuses its source resolver and journal replay, and passes the result through the existing Garden reducer. The core runtimes and earlier medical demonstration are unchanged. One supplied tree extension adds a bounded ten-node pass; it is not an active clinical service or autonomous collector.

The [records](../../../operations/clinical-reconsideration/20261121/records.json) and [shared reference bindings](../../../operations/clinical-reconsideration/20261121/references.json) retain dates and one fictional source family. The [journal](../../../operations/clinical-reconsideration/20261121/journal.json) keeps two revisions, their authorship and hash chain. Later assessments retain earlier evidence, opinions, harm reports and contrary records. Conflicting scoped reviews cannot be hidden by selecting only the favorable reference. Complete rewriting and rehashing by an authorized editor is not prevented cryptographically; Git history and review preserve the published baseline.

## Reproduce

From the repository root:

```bash
python scripts/clinical_reconsideration.py validate
python scripts/clinical_reconsideration.py replay
python scripts/clinical_reconsideration.py check
python -m unittest discover -s tests -p test_clinical_reconsideration.py -v
```

`check` reconstructs the Garden output twice in temporary directories and compares each file byte for byte against the saved output. `build` regenerates this supplied example after an intentional reviewed change. Neither command contacts a provider or public source. Fixed November 21 fixture timestamps are simulated assessment/replay dates, not observations of a real patient; November 22 is the completion date.

One proposed next test asks whether a dated acknowledgement identifies receipt of the correction by the continuing-care team. It remains a fictional test, not an authorization to collect private records. Stop at that transfer; receipt would not establish benefit.

The separate public policy note retains its November 21 inspection date and retrieval limits. It establishes published routes only. No Governor change, new runtime Bee, recurring program, outreach or canonical admission is included.
