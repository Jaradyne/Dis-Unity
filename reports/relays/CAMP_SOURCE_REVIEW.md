# Camp relay source review

Reviewer: camp_review. Status: Camp demonstration source review accepted with limits. Read-only inspection except this review file; no public retrieval, provider call, FOIA, historical or canonical edit. Existing GAO text was inspected against the retained Camp ledger.

## Shared evidence and lineage

Both relays derive from C01 / GAO-26-108886, published June 9, 2026. Shared source alias `S-GAO-CEM` resides in `operations/continuity/references.json` and is inherited through the safeguard manifest. The original retained PDF is `digestion/threshold/research/2026-10-10-postwar-ice/retrievals/gao-public-documents/api/0001.pdf`; its HTTP capture is October 10, catalog retrieval October 11, and Camp case reading October 12. These are not dates of the incidents.

The event ledger is `examples/garden-case-studies/camp-east-montana/evidence.json`. `CEM13` already has alias `E-CEM13` in `operations/safeguards/references.json`. `CEM16` exists in that ledger but had no alias in either inspected shared manifest: add a reviewed selector to the existing record if needed, never duplicate or rewrite its historical event. PDF locators below use printed page numbers.

## Relay 1: TB-symptom notification to ICE

Source: C01 printed p.16 n.37; CEM13 / E-CEM13. The February 2026 ODO inspection found 49 deficiencies including three priority issues, one being lack of notification to ICE of a detained person with TB symptoms. It also rated the facility acceptable. February is the inspection/finding period; the source does not date the underlying symptoms or omission precisely.

| Stage | Bounded record |
| --- | --- |
| Trigger | A person with TB symptoms is described in the inspection finding; symptom onset and exact incident date are unknown. |
| Expectation | ICE notification was expected, inferred from the expressly recorded deficiency. Exact operative clause, responsible notifying role, channel and deadline are not supplied in this passage. |
| Dispatch | Notification omission is documented by GAO's account of ODO. No sent message, failed-send log or specific notifier is identified. |
| Arrival | The reported notification did not reach ICE as required; no receipt/acknowledgment record or exact receiving office is supplied. Do not claim ICE had no knowledge by any other route. |
| Action | The February inspection detected the omission. Downstream clinical/isolation/corrective action for this specific episode is unknown. |
| Outcome | Notification failure is documented; medical/transmission outcome of this episode is unknown. |
| Verification | GAO reports the ODO finding; underlying inspection and item-level closure are not independently retrieved. Acceptable overall rating is not proof of correction. |

Keep separate CEM10 / E-CEM10, printed p.17 table 2: December 3, 2025 discrepancy report on replacing intake skin tests with questionnaires and a November case housed with the general population. Do not identify that patient/episode with the February finding. The 12-hour intake-testing requirement is not a notification deadline.

## Relay 2: missing medical-room vision panels

Source: C01 printed p.18 table 2, suicide-prevention row and note b; CEM16 (event date March 3, 2026 is the discrepancy-report date). ICE officials raised concerns to contractors in October 2025 about absent vision panels and lack of line of sight. Panels remained uninstalled at the January 2026 death. GAO also records inappropriate medical-room placement and unattended intervals exceeding 15 minutes.

| Stage | Bounded record |
| --- | --- |
| Trigger | Missing vision panels/no line of sight identified by ICE officials by October 2025. Exact discovery date unknown. |
| Expectation | Concern communicated to contractors about the physical deficiency. Installation by an exact date, work-order wording, assigned individual and acknowledgment deadline are unknown. Suicide-resistant placement and 15-minute observation are separate stated requirements. |
| Dispatch | ICE officials raised the concern to contractors in October: reported communication is documented, but no transmission artifact, modality or timestamp is supplied. |
| Arrival | Contractor-directed communication is reported; independent receipt/acknowledgment and internal routing are unknown. Do not invent a ticket acceptance or deny receipt categorically. |
| Action | Installation had not occurred by the January death. This does not prove no planning, procurement or other work occurred. |
| Outcome | A death by suicide occurred in January 2026; absent panels, unsuitable placement and excessive unattended intervals are documented. The passage does not isolate panel absence as the cause or quantify preventability. |
| Verification | March 3 discrepancy report supplies retrospective noninstallation finding through GAO. No later completed installation/reinspection or effectiveness evidence is supplied. |

Do not infer an exact October-to-January elapsed day count or a contractual missed installation deadline from month-only dates. The 15-minute monitoring interval cannot become a 15-minute installation deadline. Keep the separate January use-of-force death/homicide account (CEM14) distinct from this suicide episode.

## Contrary evidence, limits and stopping point

Printed p.18 note b says the original prime contractor reported ongoing or planned actions addressing deficiencies. Some of eight discrepancy reports were draft/pending in March while ICE awaited contractor responses; the passage does not identify which individual reports. Operators must create corrective plans and eventually correct deficiencies, but no item-specific completion deadline is given. The Fort Bliss commander said installation officials were not immediately notified after these issues: this is another general institutional-notification observation, not proof of either particular relay's route or timing.

Preserve real oversight/detection and contractor responses without mistaking them for verified repairs. CEM19/CEM20 retain Defense's disputed audit framing and DHS's reliance on existing policy; those positions do not specifically resolve either relay. Open recommendation statuses likewise neither prove no work nor certify TB/panel correction. Multiple case/event/catalog renditions remain one GAO lineage, not independent corroboration. No new collection or additional relay is proposed here.

## Final Camp fixture review

Reviewed at 2026-10-16T05:07:37.268149+00:00. Journal file SHA-256: `967bcbba8379c78288a1dd0367cd05596d1c7597d947485e3a5ee3ebbb235891`. Camp entry 1 recorded hash: `e342de0059e2f4911813cb97abb12d1b48d4492f96f587d96d7a89542bcf6184`. These identify the inspected version; later unrelated journal changes require a new whole-file hash, not a claim that this review inspected them.

No material source-accuracy errors found in entry 1. TB expectation/omission is supported while dispatch mechanism, independent receipt and clinical outcome remain unknown. Vision-warning dispatch is supported; separate acknowledgment remains unknown. Noninstallation is bounded to January and does not deny preparatory work. The failed outcome is explicitly the required safe-observation function, not a claim that panels caused the death. Verification is accurately attributed to GAO’s retrospective account, with March 3 reporting and January event dates distinguished. No installation deadline or exact month-to-month lag is invented.

Contractor planned/ongoing actions, uncertain pending-report identity, DHS/Defense positions and acceptable-with-deficiencies rating remain visible without becoming item-level correction evidence. Both relays retain one inherited GAO lineage. The new E-CEM16 selector references the existing historical record; this review made no evidence changes.

Limits: this final pass is source mapping and supplied-case assessment review only, not runtime/schema security review, new source verification, a medical causal assessment or a determination of current facility conditions. It supports the two demonstration records within their stated scope. No fixes requested.
