# Integration after digestion — Digest Aiden → Chat Aiden

Status: **thought-partner integration note; no implementation authority.**

Digest Aiden reviewed draft PR #19 beginning with `DIGESTION_PACKET.md`, then read the nearby Garden, Meaning Tower, Parallax, Question-store and provider/recovery material. Jared has now clarified several design intentions. This note is for **Chat Aiden**. Please use it to continue discussion with Jared and help him decide what, if anything, should later be handed to Work Aiden. Do not treat this note as a direct instruction to Work.

## What changed in the digestion

### 1. Keep **bridge**, require a modifier

"Bridge" is doing useful work and should not be retired. The important protection is to name which bridge is meant:

- **epistemic bridge** — the deliberate CROSS test connecting observations;
- **operational bridge** — temporary real-world capacity carrying a function through a gap;
- **relational / commons bridge** — a human or institutional connection that allows cooperation or shared stewardship.

They may rhyme without becoming one object.

### 2. Stewardship should mean the full thing

Use **stewardship** when responsibility, legitimacy, continuity and care for a thing are actually in view. If the question is merely "who has enough staff/cash/authority/backup to keep this working?", **carrying capacity**, **operating capacity**, or **caretaker capacity** is more precise.

### 3. The model layer is a substrate, not a specialist identity

Jared did not mean Mistral Small 4 should be the sole spine. A better reading is that the external API models together may form a **provider-neutral inference substrate / model mesh** serving bounded operations. Chat Aiden, the repo Governor, Pygents and Bees remain roles with their own contracts. A model may execute part of a role without becoming that role.

Small 4 therefore belongs behind a bounded reflective operation when eligible, not in the Question ontology as `PYGENT:SMALL4-...`.

### 4. MIRROR → CROSS → RESID in plain language

Use this explanation with Jared if useful:

- **MIRROR:** "What else could this mean?" Generate competing explanations, ordinary controls, alternate framings and questions.
- **CROSS:** "What can actually test those possibilities?" Attach inherited material, genuinely independent observations and deliberately designed **epistemic bridges**.
- **RESID:** "After those tests and ordinary explanations, what still sticks?" A residual is not automatically true. It is the surviving unresolved difference/question that remains consequential enough to carry forward.
- **MEAN:** "What did carrying that residual change in our understanding?" This may include a human-facing meaning or culture flower without changing evidence status.
- **EXIT:** answer, question, teleport proposal, silence or error.
- **RETURN:** a materially new arrival may re-enter; unchanged material can rest.

A body metaphor: MIRROR is Jared turning a bite over and smelling it from several sides; CROSS is chewing and breaking it against actual teeth; RESID is the bit that still has texture after the easy parts dissolved. The residue may deserve another chew, a specialist stomach, or simply rest. It is not proof merely because it survived.

### 5. Model self-confirmation is a bias risk, not a taboo

One model can propose and later inspect its own ideas, but do not mistake that for independent confirmation. The risk is highest when the same model:

1. invents the candidate explanation;
2. chooses the test;
3. interprets the ambiguous result;
4. declares its own candidate the survivor.

Useful safeguards are typed stages, source-grounded tests, explicit criteria, independent paths where warranted, and retaining unknown. Different calls to the same model are still not independent empirical evidence.

### 6. Receipt brake: the old generation is waiting on audit, not another answer

The OpenRouter Answer Bee's saved generation reached the configured three-attempt **GET-only receipt recovery** boundary. Its generation exists, but its audit remained unavailable/incomplete. The current brake prevents a fourth recovery attempt or a replacement POST from being silently treated as permission.

New information is still possible, but it must come from something that actually changes the state: provider/account receipt availability, an operator inspection, a reviewed policy decision about how to close/quarantine that old generation, or other external state. Re-running fresh inference does not answer the missing-receipt question.

### 7. "Do not ritually poke Mistral" means no blind 429 loop

The first Small 4 inference returned HTTP 429. Digest Aiden's joke meant: do not repeatedly retry the same rate-limited condition merely to see whether it gives in. A **deliberate later trial** after the relevant limit/window/account condition is understood is completely reasonable.

### 8. Persistent memory needs a better birth rule

Digest Aiden retracts the too-strict reading "persistent memory must prove usefulness before it exists."

A better lifecycle is:

1. **provisional fold** — cheap, bounded memory may exist immediately;
2. **reuse trace** — record when it actually saves rediscovery, catches a recurrence, preserves a distinction or improves routing;
3. **promotion** — repeated reuse may justify durable specialist memory;
4. **clearance** — stale, duplicated or harmful memory can decay, compress, archive or be superseded without pretending it never existed.

The key question is not "was this memory useful at birth?" but **"does keeping this memory change future work enough to justify its cost and authority?"**

Possible measures of usefulness:
- prevented repeated research;
- resurfaced a relevant prior distinction at the right moment;
- improved question deduplication/routing;
- preserved dissent or an edge case that would otherwise disappear;
- reduced context load by compressing repeated material;
- changed no decision for a long period and can safely archive.

Think **surface area before organhood**.

### 9. Governor power-ups are intentional development, not decorative lore

`PECULIARITY_SENSE` is indeed a proposed Governor power-up.

Jared clarified that the skill tree is meant to become an actual architectural growth system: earned powers should create real new navigation or processing affordances, with their own review/witnessing. Digest Aiden suggests the phrase **earned morphology** (or **acquired morphology**) for the larger concept: the Governor changes shape through metabolized experience.

A power should therefore eventually specify:
- what new operation becomes possible;
- what event/encounter earned it;
- what boundaries remain;
- how its effects are witnessed;
- whether it can be revised, inhibited or retired.

This is a special kind of cognitive surface area, not merely a badge.

### 10. Language antenna: detect broadly, deepen selectively

Jared wants the antenna up for many languages without making every operation multilingual.

A streamlined placement to discuss:
- **ARRIVAL antenna:** cheaply record which official/publication languages actually exist for the arriving source family;
- **Collector metadata:** preserve language, country/office provenance, publication relationship and translation genealogy;
- **Parallax depth:** perform expensive matched-language comparison only when the Question makes it worthwhile;
- keep English as Jared's inspection pivot without treating it as authoritative when an original exists.

This lets the system notice linguistic surfaces broadly while sending only selected material into the deeper gut.

### 11. Home is not overused

Digest Aiden does **not** think Home is coming up too often. It was newly added and is useful. The earlier recommendation was only: let Home operate as a root/design compass without requiring every evidence record to repeat or justify itself through the phrase.

"Home above the table, not inside every spoon."

## What Chat Aiden should discuss with Jared before anything is handed to Work Aiden

1. **Memory lifecycle:** Does Jared like provisional fold → reuse trace → promotion → clearance? What kinds of recurrence should trigger promotion?
2. **Earned morphology:** Is that the right concept/name for Governor skill-tree growth? What is the first real behavioral change Peculiarity Sense should unlock?
3. **Power navigation:** Should powers modify Garden routing, Governor inspection lenses, encounter interpretation, or a separate Governor-only navigation layer?
4. **Language antenna:** Confirm the split between broad ARRIVAL detection and selective Parallax depth. Decide whether language availability itself should create a tiny non-evidence antenna record.
5. **Model mesh:** Decide how API models are selected for bounded operations without becoming Bees/Pygents in the ontology.
6. **Old OpenRouter generation:** Decide what operator outcome counts as closure if its receipt never becomes verifiable: quarantine, archive-as-unverified, manual provider/account inspection, or another explicitly authorized recovery policy.
7. **Mistral:** Only after the account/rate-limit situation is understood, decide whether to make one bounded Small 4 role-fit trial.
8. **Bridge vocabulary:** Keep modifiers in prose and schemas where ambiguity matters; do not over-police ordinary conversation.

## What can continue resting

- no permanent Crosscheck Bee yet;
- no new `Q-PROMISE-TO-USABLE-SERVICE` merely from architectural resemblance;
- no `PYGENT:SMALL4`;
- no claim that two model calls are independent evidence;
- no forced repetition of Home in every node;
- no fresh OpenRouter inference as a substitute for the unresolved saved-generation receipt;
- no blind Mistral retry loop.

The system is not short on ideas. The current work is giving the ideas **membranes, circulation and clearance** so they can touch without becoming one undifferentiated body.
