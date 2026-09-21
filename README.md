# Dis-Unity — Resilience Cascade

**Stress → interaction → opportunity → adaptation → resilience.**

A public-source research system for understanding how dependent systems carry one another's load. It follows stresses, tests conditional cascades, finds usable buffers and transitions, and develops cooperative responses from neighborhood to international scale.

Start with the [executive briefing](Resilience_Cascade_Briefing.md), [commons proposals](Resilience_Cascade_Commons.md), or [system map](state/SYSTEM_MAP.md).

## Current deployment

Research cycle **RC-003** was completed on **21 September 2026**, with a **21 September evidence cutoff**. It contains 42 signals, 21 dependency links, nine clusters and 77 source records, including explicitly logged gaps. Ten readable state sections are generated from one canonical JSON file. A cutoff is not a claim that every domain was refreshed that day.

Four specialist threads completed focused research on nutrients, maritime networks, food/electrification and durable commons. A Bayer specialist saved only an initial checkpoint; the coordinator completed a bounded evidence watch. Three claims received independent source checks. Closing review covered seven new edges and four reserve records, with nutrient-input authorship limiting independence. Final admission is coordinator acceptance with limitations, not a whole-state independent pass. See the [review record](reports/RC-003/REVIEW.md).

The new work tests whether a fallback shrinks under the same shock that creates demand for it. Food assistance, public-space opening hours, electricity imports and fuel backup all receive this test. Diesel replacement is the first structured transition case, with new dependencies and useful coproducts tracked. Sulfur/phosphate processing, Venezuela conversion gates and regional piracy evidence are distinguished from available rescue capacity. Improving maritime reports remain alongside specific hijackings and input constraints.

## Operation

The multi-agent research runs during active assistant sessions. The Python utilities preserve, validate and commit that work; they do not launch models, browse autonomously or run a scheduled digest. Git provides durable history and reviewable differences, not background execution.

| Path | Purpose |
| --- | --- |
| `Resilience_Cascade_STATE.json` | Canonical shared state; coordinator is sole writer |
| `state/` | Ten generated, source-linked views |
| `inbox/RC-003/` | Attributed specialist checkpoints, including incomplete work |
| `cycles/RC-003/` | Immutable baseline, submission snapshots, review, change audit and commit receipt |
| `reports/RC-003/` | Food/replacement, commons, maritime, nutrient/network and review detail |
| `scripts/cycle.py` | Begin, checkpoint, review, commit and resume a cycle |
| `scripts/validate_state.py` | Required fields, graph references, source references and date checks |
| `scripts/render_state.py` | Regenerate the readable views |
| `tests/test_cycle.py` | Data-loss and evidence-admission boundary tests |
| `AGENTS.md` | Instructions for continuing research and maintaining the repository |
| `reports/RC-002/WORKFLOW.md` | Commands, recovery procedure and implementation limits |

Requires Python 3.9 or later and its standard library. The completed verification used Linux. Windows locking support is included but has not been exercised on Windows.

```bash
python scripts/validate_state.py Resilience_Cascade_STATE.json
python scripts/cycle.py status RC-003
python -m unittest discover -s tests -v
```

## Reasoning contract

FACT, PLAUSIBLE MECHANISM, EARLY SIGNAL, UNKNOWN and SPECULATION remain separate. Observations, forecasts, announcements, construction, commissioning and demonstrated service are different stages. Multiple articles about one event do not become multiple shocks.

Each consequential cascade records mechanism, evidence, thresholds, buffers, substitutions, time horizon, uncertainty, confirming evidence and a falsifier. No opaque collapse score is used. Separate gauges track load, reserve, recovery, dependency, substitutability, shedding, growth, lifeboats, social temperature and confidence.

Every substantial decline gets a transition analysis. Preserve necessary function; distinguish destructive loss, managed shedding, creative transition and healthy replacement. A producer preserving cash through furloughs may shift harm onto workers. That is not automatically a successful transition.

A donor's usable contribution is bounded by verified capacity after existing commitments and its protected contingency floor, then by transport, staffing, compatibility and replenishment. Unknown surplus is not committed rescue. An interconnected power system on another continent is not a direct local electricity donor.

Every reserve also records how the initiating shock could damage it. Several suppliers can share one factory, route, grid or funder. Food-waste prevention remains desirable; dependable nutrition should survive the loss of avoidable surplus. Technology replacement must preserve necessary service and account for commissioning, staffing, new inputs and useful coproducts.

Social analysis separates rhetoric, organization, capacity, behavior and violence. It also examines mediation and cooperation. Identity, affiliation, ordinary anger and activism do not establish dangerousness. Simultaneous failures do not establish malicious intent.

## Geography and scope

Context is nested across San Francisco, the Bay Area, California, the United States, North America, the Caribbean, relevant European/NATO and Commonwealth-linked networks, and major resource/trade nodes. Coverage is deliberately uneven and gaps are recorded. Pajaro Valley is treated as a neighboring California context, not silently included in the nine-county Bay Area.

Public, lawful, nonintrusive sources only. No private account data, outbound contacts, resource commitments or facility targeting are part of this deployment. Commons cards are proposals unless an operational status is explicitly verified.

## License

The project uses [The Unlicense](LICENSE), as selected by its creator. Linked third-party publications retain their own terms; this repository records source references and research findings rather than republishing source articles.
