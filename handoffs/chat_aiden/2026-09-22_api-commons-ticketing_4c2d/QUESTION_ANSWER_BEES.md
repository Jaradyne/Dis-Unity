# Two-bee-per-role architecture — Question Bee + Answer Bee

## Why split them?

The skills for noticing **what deserves asking** are not the same as the skills for proving **what the answer is**.

Each domain role can expose two modes without duplicating all domain knowledge.

## Question Bee / Scout

Purpose:
- watch sensors and local context;
- compare new observations with current state;
- detect contradictions, missing denominators, hidden local detail and possible cascade links;
- deduplicate against existing questions;
- create or update a Question object;
- propose births when the local question has become too specific to average away.

It should **not** force an answer.

Example output:
```json
{
  "question_id": "Q-US-RURAL-DIESEL-014",
  "question": "Can this county reach a rail transload point before its local diesel buffer becomes limiting?",
  "why_now": ["local truck-rate spike", "no rail line in county"],
  "related_questions": ["Q-US-RURAL-DIESEL-003"],
  "evidence_refs": ["SRC-..."],
  "freshness": "fast",
  "answer_needed_by": null
}
```

## Answer Bee / Solver

Purpose:
- take one unresolved Question;
- assemble evidence;
- run the configured provider attempt ring if useful;
- distinguish fact/inference/unknown;
- answer, partially answer, or return a precise missing-data statement;
- create counterquestions only when necessary.

## Question identity before ticket identity

User preference: the **question** is the durable semantic object because the same or nearly the same question may recur at different scales.

Recommended objects:

`Question` = enduring research concept  
`Attempt` = one actor/provider trying to answer  
`Answer` = one evidence-backed response  
`Ticket` = escalation/work-order object only when work must survive/coordinate beyond an ordinary attempt ring

So a new question first checks semantic neighbors:
- exact duplicate -> reuse existing question
- narrower/broader version -> link `parent_question` / `child_question`
- same mechanism, different geography -> sibling relation
- new evidence makes old answer stale -> reopen same question with new evidence epoch

Example: "Is the Strait of Hormuz passable for sulfur cargo?" and "Can sulfur cross the Gulf system?" should be linked, not blindly collapsed.

## Full attempt ring before escalation ticket

For an ordinary Answer Bee:

1. Try preferred eligible provider/model.
2. On transient failure, repeat according to retry policy.
3. Move to next eligible provider/model and record the attempt.
4. Complete one bounded circuit of the configured provider group.
5. If none returns a usable answer, then create/escalate a durable ticket for deferred provider capacity, Chat Aiden, Work Aiden or human review.

A successful answer ends the ring unless independent review was requested.

Provider quota/capacity belongs on the Attempt/Provider state; it should not imply the Question is blocked if another eligible provider remains.

## Relationship to birth

Question Bee notices the need for a child.
Answer Bee may confirm that the parent role cannot resolve it.
Orchestrator validates the birth request.
No child launches merely because a model wrote `birth_requests`.
