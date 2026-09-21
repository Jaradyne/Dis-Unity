# Dis-Unity — Resilience Cascade

**Stress → interaction → opportunity → adaptation → resilience.**

A public-source research system for understanding how dependent systems carry one another's load. It follows stresses, tests conditional cascades, finds usable buffers and transitions, and develops cooperative responses from neighborhood to international scale.

Start with the [executive briefing](Resilience_Cascade_Briefing.md), [commons proposals](Resilience_Cascade_Commons.md), or [system map](state/SYSTEM_MAP.md).

## Current deployment

Research cycle **RC-002** was completed on **21 September 2026**, retaining a **20 September evidence cutoff**. It contains 30 signals, 14 dependency links, six clusters and 40 source records, including explicitly logged gaps. Ten readable state sections are generated from one canonical JSON file.

Five specialist threads saved research/review/code checkpoints. A shared usage limit interrupted their closing work. The coordinator completed the bounded cycle, source admission and implementation. Six independent checks reproduced material first-cycle claims; final independent peer review of the second-cycle additions remains open. The review record distinguishes these scopes.

The strongest new findings concern phosphate production curtailments, uneven regional fuel and produce-transport capacity, and the separation between usable service reserve, restricted capital and announced funding. Improving grain movements and completed local infrastructure remain alongside the stress signals.

## Operation

The multi-agent research runs during active assistant sessions. The Python utilities preserve, validate and commit that work; they do not launch models, browse autonomously or run a scheduled digest. Git provides durable history and reviewable differences, not background execution.

| Path | Purpose |
| --- | --- |
| `Resilience_Cascade_STATE.json` | Canonical shared state; coordinator is sole writer |
| `state/` | Ten generated, source-linked views |
| `inbox/RC-002/` | Attributed specialist checkpoints, including incomplete work |
| `cycles/RC-002/` | Immutable baseline, submission snapshots, review, change audit and commit receipt |
| `scripts/cycle.py` | Begin, checkpoint, review, commit and resume a cycle |
| `scripts/validate_state.py` | Required fields, graph references, source references and date checks |
| `scripts/render_state.py` | Regenerate the readable views |
| `tests/test_cycle.py` | Data-loss and evidence-admission boundary tests |
| `AGENTS.md` | Instructions for continuing research and maintaining the repository |
| `reports/RC-002/WORKFLOW.md` | Commands, recovery procedure and implementation limits |

Requires Python 3.9 or later and its standard library. The completed verification used Linux. Windows locking support is included but has not been exercised on Windows.

```bash
python scripts/validate_state.py Resilience_Cascade_STATE.json
python scripts/cycle.py status RC-002
python -m unittest discover -s tests -v
```

## Reasoning contract

FACT, PLAUSIBLE MECHANISM, EARLY SIGNAL, UNKNOWN and SPECULATION remain separate. Observations, forecasts, announcements, construction, commissioning and demonstrated service are different stages. Multiple articles about one event do not become multiple shocks.

Each consequential cascade records mechanism, evidence, thresholds, buffers, substitutions, time horizon, uncertainty, confirming evidence and a falsifier. No opaque collapse score is used. Separate gauges track load, reserve, recovery, dependency, substitutability, shedding, growth, lifeboats, social temperature and confidence.

Every substantial decline gets a transition analysis. Preserve necessary function; distinguish destructive loss, managed shedding, creative transition and healthy replacement. A producer preserving cash through furloughs may shift harm onto workers. That is not automatically a successful transition.

A donor's usable contribution is bounded by verified capacity after existing commitments and its protected contingency floor, then by transport, staffing, compatibility and replenishment. Unknown surplus is not committed rescue. An interconnected power system on another continent is not a direct local electricity donor.

Social analysis separates rhetoric, organization, capacity, behavior and violence. It also examines mediation and cooperation. Identity, affiliation, ordinary anger and activism do not establish dangerousness. Simultaneous failures do not establish malicious intent.

## Geography and scope

Context is nested across San Francisco, the Bay Area, California, the United States, North America, the Caribbean, relevant European/NATO and Commonwealth-linked networks, and major resource/trade nodes. Coverage is deliberately uneven and gaps are recorded. Pajaro Valley is treated as a neighboring California context, not silently included in the nine-county Bay Area.

Public, lawful, nonintrusive sources only. No private account data, outbound contacts, resource commitments or facility targeting are part of this deployment. Commons cards are proposals unless an operational status is explicitly verified.

## License

The project uses [The Unlicense](LICENSE), as selected by its creator. Linked third-party publications retain their own terms; this repository records source references and research findings rather than republishing source articles.
