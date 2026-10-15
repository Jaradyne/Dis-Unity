# Camp East Montana reporting cross-check

Work Aiden, October 15, 2026. Audited baseline: `cd8adf78a5386ac291558b6e547dcb1e737a3cf6` (merged PR #41). Empirical observation cutoff remains October 14 at 17:45:15 UTC. The audit date is not a new facility observation.

**Result:** The inspected claims support the bounded UNKNOWN conclusion. Two presentation problems needed correction: the viewer could make general inspection activity look like TB-specific compliance, and the short arrival handoff omitted the dates and attribution of the separate TB findings. The fixes expose those distinctions without changing the underlying assessment. No unsupported substantive conclusion was identified within this scoped review.

## Scope and source lineage

Reviewed the [original Camp Digest handoff](../../../examples/garden-case-studies/camp-east-montana/DIGEST_HANDOFF.md), [arrival handoff](../../evidence-arrival/DIGEST_HANDOFF.md), [viewer](../../../web/evidence-arrival/README.md) and selected supporting case records. Work Aiden performed the source/claim audit and patch; `reporting_review` independently challenged the presentation in this active session. Its [initial checkpoint](REVIEW_CHECKPOINT.md) and [final review](REVIEW.md) retain attribution and limits. This uses the existing cross-check function; no repository Bee, application model route, schedule or Governor power was activated.

Source labels below reuse the archive:

- **C01:** [GAO-26-108886 retained PDF](../../../digestion/threshold/research/2026-10-10-postwar-ice/retrievals/gao-public-documents/api/0001.pdf), published June 9, 2026. Printed pages 7–9, 12, 14–19 and 21–22 were checked for the claims below; the page 8 timeline was also visually inspected. Printed pages 1–31 follow four front-matter PDF pages.
- **C02:** [GAO-26-108663 retained PDF](../../../digestion/threshold/research/2026-10-10-postwar-ice/retrievals/gao-public-documents/api/0002.pdf), published September 24, 2026; printed pages 7–8. C02 cites C01 and adds a dated pricing observation, not independent replication of the medical findings.
- **R14:** [October 14 full HTTP receipt](../../../examples/evidence-arrival/camp-east-montana/live/operations/week-one/runs/CEM-FIRST-ARRIVAL/api/0001.json), `/response/body/content`, especially “Recommendations for Executive Action,” recommendations 1–4. Work read the complete normalized main text and verified the retained body hash. This is the same GAO product family as C01, not an independent medical inspection.
- **J3:** [safeguard journal](../../../operations/safeguards/journal.json), `/entries/4/safeguard`: Camp revision 3, with its own historical scope, evidence attribution and contrary evidence.

The PDF receipt was captured October 10; the source catalog was reviewed October 11; the original case and paraphrased status check are dated October 12. R14 is a distinct October 14 receipt. The underlying ICE inspection reports, contractor records and replacement contract were not separately obtained. Hashes identify retained material; they do not certify its factual truth.

## Claim audit

“Supported” means supported within the cited record's date, attribution and scope. “Needs narrower wording” identifies a presentation repair, not an adverse empirical reassessment. An “unsupported” result would require withdrawing or qualifying that claim; none was identified among the claims below.

| ID / consequential claim | Disposition at baseline | Exact support and limits | Action |
| --- | --- | --- | --- |
| A01 Army awarded the WEXMAC task order July 18, 2025; administration passed to ICE October 1. | Supported | C01 pp. 7–9, especially p. 8 Figure 2. ICE's operational/oversight role preceded the administration transfer. Contracting relationship, not a finding on every action's legal validity. | Preserve. |
| A02 About 1,600 people at February 2026 end versus paid meals/services at the 5,000-person quantity. | Supported | C01 p. 12 and n. 29; about 5,000 physical capacity as of April on p. 2. ICE cited separation/isolation needs; GAO noted subdividable units. Meals paid for are distinct from meals prepared. | Preserve dates, competing explanations and UNKNOWN current safely usable capacity. |
| A03 A pre-occupancy inspection was required but skipped at the August 2025 opening. | Supported | C01 pp. 15–16 and n. 36; opening date in p. 8 Figure 2. ICE cited expedited timing and reported an informal later inspection (n. 37). | Preserve specific historical failure; do not extend it to every later inspection. |
| A04 The TB failure baseline is documented. | Needs narrower wording in the short arrival presentation | C01 p. 17 Table 2: ICE's December 3, 2025 report describes questionnaires replacing required skin tests and a November 2025 TB case in general population. C01 p. 16 n. 37 separately reports a February 2026 TB-symptom notification failure. Both reach this case through GAO. | Add dates, separate the events, and identify the attribution. Do not claim a newly observed outbreak or measured transmission. |
| A05 The February inspection was rated acceptable despite 49 deficiencies, including three priority issues. | Supported | C01 p. 16 n. 37. A rating and documented deficiencies coexist; detection does not establish remediation. | Retain both in the viewer's historical detail. |
| A06 “Formal: documented” establishes the required procedure. | Needs narrower wording in the TB-focused presentation | J3 `/scope`, `/formal` and evidence `CEM-POLICY`; C01 p. 15 Table 1 note a and p. 18 Table 2 note a describe the historical policy/2025 contract. The replacement contract's full terms were not independently checked. | Label the table as the historical inspection assessment; do not imply independently checked current contract terms. |
| A07 “Operational: partial / partial / partial” describes people, procedures and authority. | Needs narrower wording in the viewer | J3 `/operational/people`, `/procedures`, `/authority`: later inspectors and oversight operated, but the opening gate failed. These are broad inspection claims, not sampled TB intake/notification compliance after April 18. | Separate the broad assessment from the TB-specific UNKNOWN result. |
| A08 Some corrective activity occurred or was reported, despite incomplete verification. | Supported; make the short presentation explicit | C01 p. 15 recreation row documents a yard opened but inadequate at the September visit; p. 18 Table 2 note b retains contractor-reported ongoing/planned actions and draft/pending discrepancy reports as of March 2026. | Preserve observed partial improvement versus contractor response; neither proves TB correction. |
| A09 Replacement procurement does not establish correction. | Supported | C01 pp. 14 and 19: March 12 award for operation from April 18, mid-April termination, and outcome too early to assess during that audit. | Preserve as dated action, without promoting it to effectiveness. |
| A10 Later pricing nonimplementation was documented, not merely inferred from Open status. | Supported | C02 pp. 7–8 says the cost-saving measures still were not incorporated as of August 2026. C02 n. 26 cites C01. | Preserve August pricing scope; no inference about October pricing or medical conditions. |
| A11 Four recommendations were Open; agency responses and planned milestones remained visible. | Supported | R14, recommendations 1–4: May DHS positions and August Army milestones, including a December 30, 2026 completion estimate. C01 pp. 21–22 also preserves DHS/Defense responses and GAO's disagreement. | Keep Open separate from inactivity; future targets were not overdue on October 14. |
| A12 The arrival supplied no qualifying post-April 18 TB correction verification. | Supported within this one surface | Full R14 main text; retained review `/dimension_assessment` and `/question_result`. It supplies neither requirement-specific sampled compliance nor a protective result. | Retain UNKNOWN. Absence here is not evidence that no correction occurred or no record exists elsewhere. |
| A13 One actual receipt and the six examples represent different kinds of work. | Supported | Observation ledger contains one live receipt; fixture ledger has separate simulated new/repeat/304/changed/conflicting/incomplete inputs. The October 12 paraphrase is not a comparable byte baseline. | Preserve simulation labels. Neither a detected change nor successful replay is a new medical finding. |
| A14 Separate review and replay add scrutiny and record checks, with no independent facility corroboration. | Supported | All empirical paths still lead to the retained GAO family. Reviewers independently scrutinize the same material; deterministic replay checks preservation and runtime consistency. | State review independence separately from source independence. |

## Corrections and history

The viewer now names the broad historical inspection scope and gives the narrower post-April 18 TB question its own UNKNOWN result. Its review detail separates the December and February findings and preserves contractor responses. The arrival Digest handoff has an October 15 addendum; its October 14 text remains intact. The viewer still links to the pinned October 14 handoff; the current handoff and this audit carry the dated clarification.

RC-005, RC-006, the original Camp case, raw receipts, source catalogs, Continuity/Safeguard journals and their generated passes are unchanged. No new empirical assessment revision is warranted because no new empirical material arrived. This review does not assert absence of correction, prevalence of harm, or current facility conditions.

## Reproduce the checks

[SOURCE_PINS.json](SOURCE_PINS.json) identifies the exact unchanged inputs. From the repository root, verify them and replay the existing case without network access:

```bash
python - <<'PY'
import hashlib, json
from pathlib import Path
pins = json.loads(Path('reports/reporting-audit/camp-east-montana/SOURCE_PINS.json').read_text())
for item in pins['files']:
    assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
print('PASS: retained audit input hashes')
PY
python examples/garden-case-studies/camp-east-montana/replay.py --check
python scripts/continuity.py check
python scripts/safeguards.py check
python scripts/evidence_arrival.py check
python scripts/build_evidence_viewer.py --check
```

These checks establish byte preservation and deterministic reconstruction. They do not independently establish facility conditions. Final patch verification and review limits are recorded in [REVIEW.md](REVIEW.md). Browser layout verification remains unperformed; a DOM interaction check is not a rendered desktop/mobile inspection.

## Handoff for Chat and Digest

**Chat:** The saved viewer and short handoff now expose the scope and attribution that were already present in the detailed records. Formal policy, broad inspection activity, TB-specific compliance and protective outcomes remain distinct. No new mechanism or activation is needed for this repair.

**Digest:** Keep `Q-CEM-TB-CORRECTION` UNKNOWN. The established historical record includes separate December 2025 testing and February 2026 notification findings, with contractor responses and an acceptable overall rating preserved. The single most useful missing record remains a dated post-April 18 final medical reinspection/corrective verification identifying the requirement, completed action, verification method/period and observed results. A responsive record could support compliance within its scope; protective effectiveness would still need its own evidence. A no-records response would establish only the search outcome.

The [FOIA draft](../../evidence-arrival/FOIA_DRAFT.md) remains unsent. Submitting it is optional and was not a prerequisite for this completed local review. No new public-source retrieval occurred; the one-retrieval proof budget was not extended. Stop after this one audited case and the reviewed presentation fixes.
