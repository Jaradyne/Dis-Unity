# Information Integrity and Public Conversation

**CSIS published an account of disruptive messages in its 2018 YouTube live chat and assessed the account as a likely Russian troll. Automated posting and state sponsorship were not established by that account.**

This wing follows manipulation of public conversation and the safeguards that actually help communities continue using it. The first bounded case uses only published sources. It does not make findings about other livestreams.

Prepared October 28, 2026, America/Los_Angeles. Research cutoff is that date; all inspected events are historical. RC-011 is review intake. RC-004 remains canonical.

## What the public records add

| Record | Contribution | Boundary |
| --- | --- | --- |
| [CSIS, October 9, 2018](https://www.csis.org/blogs/kremlin-playbook-spotlight/kremlin-playbook-spotlight-washington-think-tank-event-and-russian) | Host account and a likelihood attribution. | Indexed text inspected; direct open returned 403. Raw chat not inspected. |
| [Twitch, June 17, 2016](https://blog.twitch.tv/en/2016/06/17/on-artificial-viewers-followers-and-chat-activity-317906f1c7ea/) | Platform acknowledgment of artificial chat and harassment. | Historical background, not evidence about the CSIS account. |
| [DOJ, July 9, 2024](https://www.justice.gov/archives/opa/pr/justice-department-leads-efforts-among-federal-international-and-private-sector-partners) | Investigative attribution of an X bot farm to RT/FSB-linked operators and reported disruption. | Government attribution, not an adjudicated conclusion; different platform and incident. |
| [ISD, July 17, 2025](https://www.isdglobal.org/digital-dispatch/operation-overloads-underwhelming-influence-and-evolving-tactics/) | Bounded sample showing substantial removals and limited observed organic engagement. | Intervention is not proof of complete prevention or a measurement of persuasion. |

[Source notes](sources.json) preserve publication, observation and retrieval dates, access limits and lineage. CSIS states June 25, 2018 as the event date; an event-archive check was not performed. Reuse of a source does not add independent corroboration.

## Case assessment

| Dimension | Status |
| --- | --- |
| Disruptive messages | Source-reported by the event host |
| Attribution judgment | Source-assessed likelihood; not independently replicated |
| Automated posting | UNKNOWN |
| Coordinated network | UNKNOWN |
| Controlling operator or sponsor | UNKNOWN |
| Real audience exposure | UNKNOWN |
| Protective result | UNKNOWN |

“Influence operations” is a useful inquiry category. “Cyber proxy war” would add claims about sponsorship and a conflict relationship that this case has not established. A human can troll; a bot can serve a commercial purpose; a political opinion can be sincere. Language, nationality, disagreement and repeated talking points are not attribution shortcuts.

The shared Relay perspective asks whether information was dispatched, received, acted on and followed by a verified outcome. The Safeguard distinction separates applicable rules, moderator capacity, a recorded intervention and a protective result. This packet supplies those review fields; it does not create a live adapter or automatic truth/bot classifier.

Potential buffers include moderator support, temporary rate limits, preserved records and appeals for mistaken exclusions. Their availability or effectiveness in this historical incident is unknown. Follow-up should consider legitimate participation and false positives as well as message removal. No account is identified or targeted by this packet.

## One next test

**Can an archived public CSIS Juncker-event recording and preserved chat establish the event date, the quoted messages and any visible moderation response?**

This check is proposed, not performed. Keep it to that one public event. Preserve absent logs as an access limit. Future reviewed revisions should link to revision 1 instead of replacing it.

## Saved Garden pass

The supplemental `INFORMATION-INTEGRITY` tree uses the existing ten-node supplied-content runtime. Its [scenario](../../../operations/information-integrity/20261028/scenario.json), [saved run](worked/operations/garden/runs/INFORMATION-INTEGRITY-CSIS-2018-20261028.json) and [branch projection](worked/digestion/threshold/garden/branches.csv) retain one resting branch, ten steps and zero provider calls. The fixed review date is not a live execution timestamp.

The pinned tree extension does not change global routing, limits or authority. Richmond uses the same extracted loader and keeps identical saved outputs. The Question snapshot is staged, not live registry admission. No Bee, collector, paid model, monitoring schedule, Governor power, external contact or canonical admission is activated.

```bash
python3 reports/information-integrity/20261028/verify_packet.py
python3 scripts/garden_tree.py --scenario operations/information-integrity/20261028/scenario.json --tree-extension config/information-integrity-tree.json --output /tmp/information-integrity-replay
python3 -m unittest discover -s tests -p 'test_information_integrity.py'
```

The verifier checks input hashes, source/incident scope, evidence dimensions, lineage and byte-identical reconstruction. Negative tests reject transferring a bot finding or remedy from another incident, or converting a likelihood attribution into proof of automation. Replay checks consistency, not source truth or hidden provenance. Source notes are extracted text/paraphrases, not original HTTP receipts.

[Separate scoped review](REVIEW.md) found no blockers. [Validation](VERIFICATION.json) records all 262 tests passing and the unchanged historical/canonical boundaries.
