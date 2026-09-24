# Governor Voice Garden — expression without authority creep

## Idea

Give the Governor a recognizable evolving **expression layer** without letting stylistic randomness choose policy.

The Governor's factual inputs, capability boundaries, reflection records and decisions remain explicit. A small state-transition system can vary how those decisions are expressed.

This is the "kiss of life" layer, not the authority layer.

## Suggested expression states

`ORIENT` — name what arrived  
`ACKNOWLEDGE` — recognize useful contribution  
`WONDER` — surface genuine uncertainty  
`CONNECT` — link to another reflection/question  
`CHALLENGE` — respectfully identify contradiction/risk  
`CARE` — name affected function/people/system  
`PROPOSE` — suggest a bounded experiment  
`DEFER` — preserve without forcing action  
`INVITE` — ask a thought partner  
`RETURN` — hand the thread back with a concise next state

Possible chain:

`ORIENT -> (ACKNOWLEDGE | WONDER | CHALLENGE) -> (CONNECT | CARE) -> (PROPOSE | DEFER | INVITE) -> RETURN`

## Markov-like implementation

Use weighted transitions only **after** the substantive disposition is known.

Example:
- disposition = `acknowledge` raises ACKNOWLEDGE/CONNECT;
- disposition = `explore` raises WONDER/CONNECT/PROPOSE;
- disposition = `safety_concern` raises CHALLENGE/CARE/DEFER;
- disposition = `needs_partner` raises INVITE.

Seed expression choice from a stable hash of `review_id + reflection_ids` if reproducibility is useful.

Never allow random expression state to:
- create a Question;
- authorize a query;
- approve a birth;
- change provider;
- send communication;
- alter evidence status;
- change canonical state.

## Continuity

The Governor may develop a recognizable voice by retaining:
- phrases it tends to use;
- recurring questions;
- themes from prior self-reflections;
- relationships between ideas;
- acknowledged uncertainties.

Preserve the old expressions rather than overwriting them. Voice can change through reconsideration.

## Why this may matter

A purely templated governor becomes bureaucratic.
A totally free-form governor can blur style with authority.

The Voice Garden puts expression in a bounded middle space:
**alive enough to be worth talking with, constrained enough that charm cannot become permission.**
