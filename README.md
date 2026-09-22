# Dis-Unity — Resilience Cascade

**Stress → interaction → opportunity → adaptation → resilience.**

A public-source research system for understanding how dependent systems carry one another's load. It follows stresses, tests conditional cascades, finds usable buffers and transitions, and develops cooperative responses from neighborhood to international scale.

Start with the [executive briefing](Resilience_Cascade_Briefing.md), [commons proposals](Resilience_Cascade_Commons.md), or [system map](state/SYSTEM_MAP.md).

## Current deployment

Research cycle **RC-004** was completed on **22 September 2026**, with an empirical evidence cutoff of **21 September**. It contains **52 signals, 26 conditional links, nine clusters and 109 source records**, including one separately labelled user-supplied design input. Ten readable state sections are generated from one canonical JSON file. Counts measure recorded work, not severity or independent confirmations. The [complete RC-003 inventory](reports/RC-004/RC003_INVENTORY.md) explains the earlier 42/21/77 totals.

Six bounded specialist threads examined fuel, rail, sulfur, food/soil, commons access and maritime response. Five saved complete packets; the coordinator recovered the rail specialist's delivered findings and preserved its original initial checkpoint. A separate reviewer checked new integration and source mapping; this was not independent replication of every source. Final admission is coordinator acceptance with limitations. See the [review record](reports/RC-004/REVIEW.md).

Every reserve now distinguishes shelf life, turnover, accessible service cover, activation, replenishment and replacement. Fuel stocks and Japan's import counterevidence sit alongside price and physical-flow stress. Exact current diesel futures settlements, locomotive counts, local stock cover and exportable donor reserves remain unknown.

The supplied **15 Years Til Utopia** is incorporated as [a commons growth direction](ideas/COMMONS_GROWTH_PATH.md), with a [page-labelled source transcription](ideas/15_YEARS_TIL_UTOPIA_SOURCE.md). Begin with modifiable space and useful presence; grow tools, learning, food, essential services and reciprocal networks. The concept's technology and income aspirations are not treated as proven operating capacity. This design intake occurred on September 22 and does not silently extend the empirical cutoff.

## Operation

The multi-agent research runs during active assistant sessions. The cycle utilities preserve, validate and admit that work. A separately merged `scripts/worker.py` can produce one attributed checkpoint using a deterministic mock or an explicitly invoked provider. It does not browse, send mail, edit canonical state, commit Git or recursively spawn agents. **Real Gemini execution is paused** under the user's best-model-only policy until reviewed selection and prompt-retention safeguards are integrated; its existing Flash default is not approved. Mock verification remains available. No unattended research loop or scheduled digest is configured.

Read [HANDOFF_FOR_CHAT_AIDEN.md](HANDOFF_FOR_CHAT_AIDEN.md) for the division of work: Chat prepares research, analysis, prompts, drafts and proposed patches; Work integrates and verifies consequential changes. [Retained Gemini prompt materials](handoffs/deferred_prompts/GEMINI_RESEARCH_PROMPTS.md) remain ready for a future eligible run. Git preserves shared history and contributions; it does not make an agent run merely because a role file exists.

| Path | Purpose |
| --- | --- |
| `Resilience_Cascade_STATE.json` | Canonical shared state; coordinator is sole writer |
| `state/` | Ten generated, source-linked views |
| `inbox/RC-004/` | Attributed specialist checkpoints, including incomplete work |
| `cycles/RC-004/` | Immutable baseline, submission snapshots, review, change audit and commit receipt |
| `reports/RC-004/` | Fuel, rail, food/soil, sulfur, maritime, commons, proposed emails and review detail |
| `scripts/cycle.py` | Begin, checkpoint, review, commit and resume a cycle |
| `scripts/validate_state.py` | Required fields, graph references, source references and date checks |
| `scripts/render_state.py` | Regenerate the readable views |
| `tests/test_cycle.py` | Data-loss and evidence-admission boundary tests |
| `AGENTS.md` | Instructions for continuing research and maintaining the repository |
| `HANDOFF_FOR_CHAT_AIDEN.md` | Chat preparation queue, contribution rules and best-Gemini-only policy |
| `WORK_AIDEN_HANDOFF.md` | Received runtime/geography handoff with current integration note |
| `agents/` | Declarative roles, geography coordination and shared thinking mailbox |
| `scripts/worker.py` | One-checkpoint external-worker prototype; Gemini paused, mock available |
| `reports/RC-002/WORKFLOW.md` | Commands, recovery procedure and implementation limits |

Requires Python 3.9 or later and its standard library. The completed verification used Linux. Windows locking support is included but has not been exercised on Windows.

```bash
python scripts/validate_state.py Resilience_Cascade_STATE.json
python scripts/cycle.py status RC-004
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

Public, lawful, nonintrusive research plus a user-supplied concept explicitly authorized for Git incorporation. No private account data, outbound contacts, resource commitments or facility targeting are part of this deployment. Commons cards are proposals unless an operational status is explicitly verified.

## License

The project uses [The Unlicense](LICENSE), as selected by its creator. Linked third-party publications retain their own terms; this repository records source references and research findings rather than republishing source articles.
