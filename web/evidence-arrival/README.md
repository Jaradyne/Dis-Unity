# Follow the evidence — The Garden

Open [index.html](index.html) locally in a browser. It is a complete static file with embedded data, styling and interaction: no server, external dependencies, source retrieval or model call. GitHub's ordinary file view displays code; download the file to explore it.

Four stages explain the actual October 14 Camp East Montana receipt: receipt, detection, separate review and preserved assessment. The simulation lab exposes all six saved examples, including unchanged responses, fictional closure without verification, conflicting accounts and incomplete response. Every lab view stays explicitly labeled simulated.

The assessment remains UNKNOWN for TB correction. This is a dated saved case, not a current facility-status display. Source, evidence-review, assessment-history and unsent FOIA links point to the exact PR #40 evidence commit, `cb4ac6a79075f92fcdef9492428d9d307661b6f2`. Links open only when selected; loading or operating the viewer makes no source requests. The original evidence and generated Garden records are not modified.

The [October 15 reporting cross-check](../../reports/reporting-audit/camp-east-montana/AUDIT.md) makes the broad inspection assessment distinct from the TB-specific result. Assessment now labels its historical scope and explains that `partial` inspection capacity does not establish sampled TB compliance. Review includes dated, GAO-attributed TB findings and the contractor-response limitations, with a pinned historical-case link. The viewer's Digest link still opens the preserved October 14 version; the audit and current handoff carry the dated clarification.

Build/check from the repository root:

```bash
python scripts/build_evidence_viewer.py
python scripts/build_evidence_viewer.py --check
```

The builder reconstructs and checks the existing arrival outputs before embedding a small presentation projection. It rejects changes to the assessment/fixture states that would require reviewing the explanatory narrative. Source-derived strings are rendered as text, and the embedded JSON escapes HTML delimiters. `template.html` is the build source; open the generated `index.html` to use the viewer.

The viewer supports narrow screens, keyboard-operable stages and tabs, and reduced-motion preferences. No evidence admission, research expansion, outbound request or runtime activation is part of this addition.

Verification: exact build/replay checks passed. A local DOM execution check exercised all four stages, six simulation choices, the UNKNOWN result, hash display, keyboard tabs and pinned links with no external assets. Full browser layout/screenshot verification remains unperformed: the available browser installation returned an invalid download. Responsive CSS is present; actual desktop/mobile rendering is not claimed as verified.
