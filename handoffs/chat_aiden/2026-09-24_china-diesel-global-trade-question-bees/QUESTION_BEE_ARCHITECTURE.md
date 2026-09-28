# Question Bee architecture

## Principle

A Python "Bee" is not automatically a chatbot.

Python supplies orchestration, state, source retrieval, deduplication, schemas and rules. It becomes semantically generative only when:
- it calls an LLM/provider;
- a human/Chat/Work supplies a Question;
- or deterministic logic can form a narrow Question from a known pattern.

A spreadsheet is likewise data/state, not an LLM. It can feed an LLM through an API/Apps Script/connector, or be read by a Python worker that then calls an approved model.

## Separate organs

### Collector Bee
Cheap/deterministic where possible.
- fetch;
- parse;
- normalize;
- timestamp;
- dedupe;
- classify source/access;
- emit observations.
It does **not** decide what the world means.

### Question Bee
LLM-backed when semantic judgment is useful.

Input:
- new observations;
- unresolved Questions;
- culture;
- source/fidelity registry;
- recent reflections;
- graph neighborhood;
- user-muted/sample genres.

It first reflects:
1. What changed?
2. Why might this matter?
3. Is there already a Question for this?
4. What shared dependency could be touched?
5. What is the mundane explanation?
6. What evidence would distinguish interpretations?
7. Is this worth spending an Answer attempt on?

Output:
- no question;
- relate to existing Question;
- narrower child Question;
- broader parent Question proposal;
- new Question proposal;
- human/Governor sample only.

Question creation remains schema-bound and deduplicated.

### Evidence Planner Bee
Takes a Question and emits an answer plan before searching.

It identifies:
- proposition(s) that would answer the Question;
- best primary source classes;
- geography/time/product codes;
- expected source latency;
- likely counterevidence;
- falsifier;
- minimum sufficient evidence;
- stop condition.

Then it asks Collectors/Search adapters for those evidence classes.

### Answer Bee
Receives the Question plus collected evidence and must reflect on source fit before answering.

### Governor
Reviews recurring Questions, source gaps, weird associations, culture, births and human-facing samples.

## How a Question Bee decides where to look

Do not let an LLM invent arbitrary URLs first.

Use a **source capability registry** such as:

- China customs → product/month/destination customs flows;
- MOFCOM → licensing/allocation policy;
- JODI → country monthly product balance;
- PortWatch → port/chokepoint movement;
- UN Comtrade → bilateral HS trade;
- NWS → active U.S. weather warnings;
- EIA → U.S. petroleum inventories/prices;
- Global Fishing Watch → AIS presence/identity.

The planner maps the Question's needed evidence type to the registry, then fills query parameters. Open-web search is a fallback/discovery lane, not the first reflex.

## Selection power

Use a layered rule:
- deterministic hard gates: safety, cost, duplicate, freshness, source eligibility;
- LLM semantic fit: why this Question matters and which evidence types bear on it;
- Governor reflection: recurring blind spots, associations and births;
- Jared/Chat/Work: consequential direction and culture.

This lets the ecology become more discerning without making every collector a miniature unrestricted agent.
