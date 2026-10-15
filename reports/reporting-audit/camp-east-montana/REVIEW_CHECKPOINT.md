# Camp East Montana reporting review checkpoint

Reviewer: Work in-session independent reviewer `reporting_review`.
Started: 2026-10-15 UTC.

Scope: one bounded audit of the saved Camp East Montana evidence-arrival Digest handoff and evidence viewer, against retained receipts, review history and the original Camp case. This is a review of source support and reporting, not an independent observation of facility conditions.

No new source retrieval, provider dispatch, recurring monitoring, worker activation, canonical evidence edit or external communication is authorized or performed by this reviewer. Only this reviewer's checkpoint and review files will be written.

Review questions: exact source/date/attribution support; whether general inspection operational dimensions are conflated with TB compliance; whether the original medical failures retain their original attribution and date; preservation of uncertainty, contrary evidence, scope and source lineage. Open recommendations and absent verification cannot establish that no corrective action occurred.

Status: review started; no conclusion yet. Final review will identify the exact reviewed file hashes, findings, limits and disposition.

## Preliminary findings

1. **Needs narrower wording — viewer scope.** The Assessment stage presents `SG-CEM-INSPECTIONS`'s broad operational `partial / partial / partial` values inside a TB-correction narrative without displaying the safeguard scope. The journal describes inspectors and inspection activity after occupancy, a skipped opening procedure, and limited stop authority. These values do not establish sampled post-transition TB compliance. Show the broader historical scope and keep the TB-specific compliance question explicitly UNKNOWN.
2. **Needs clearer attribution and dates — original medical failures.** The arrival handoff and viewer refer generically to the original deficiencies. GAO's retained report separately describes the December 3, 2025 ICE discrepancy report (questionnaires substituted for required skin tests; a November 2025 TB case in general population) and the February 2026 ODO notification finding. Report date and underlying event date must remain separate. Neither item was independently reread in the underlying ICE file in this audit.
3. **Preserve contrary evidence.** GAO p. 18 Table 2 note b preserves pending/draft reports as of March 2026 and contractor-reported ongoing/planned corrective actions. No inference that correction never occurred is warranted.
4. **Preserve temporal scope of formal requirements.** GAO describes the 2025 contract/standards baseline. This review does not independently establish all replacement-contract TB terms after April 18, 2026. The journal's historical formal status need not change.

Sources checked directly from retained local files:

- `digestion/threshold/research/2026-10-10-postwar-ice/retrievals/gao-public-documents/api/0001.pdf`, SHA-256 `7d5316dff4f3abd0c385a22d7a7a300ae40ceec358c16ca3ee39def202f17e85`: printed pp. 15–18 (PDF pages 19–22), especially p. 16 n. 37; p. 17 Table 2; p. 18 Table 2 note b. Read by local text extraction; no remote retrieval.
- October 14 receipt `examples/evidence-arrival/camp-east-montana/live/operations/week-one/runs/CEM-FIRST-ARRIVAL/api/0001.json`, file SHA-256 `833e55615f49292f3456cd16e1c131883fa5b6cb48c089321b0cce2b2982b1d7`, body SHA-256 `99309dd5d28cf2f12ae8a9c762ffaebdabef7f6c792bdc918330b67d2410d945`: Recommendations for Executive Action, four numbered recommendations, May responses and August Army milestones.
- `operations/safeguards/journal.json`, `/entries/4/safeguard/{scope,formal,operational,effectiveness,failure,evidence,contrary_evidence,residuals}`.
- `examples/garden-case-studies/camp-east-montana/evidence.json`, events CEM06, CEM10, CEM13, CEM17–20; `status-recheck.json`'s explicit paraphrase limitation.

All other consequential arrival-handoff conclusions inspected are supported within the one-page limit: four Open recommendations, future milestones not overdue at retrieval, no item-specific TB verification supplied there, first version for this sensor rather than a verified historical source change, simulations kept separate, and no inference of absent correction or absent records elsewhere.

Status: preliminary findings sent to coordinator. Awaiting the bounded presentation patch for exact-hash final review. No software pass or current facility-compliance conclusion is claimed.
