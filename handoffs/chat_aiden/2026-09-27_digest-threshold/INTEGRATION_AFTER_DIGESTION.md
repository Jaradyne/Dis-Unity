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

Jared clarified that the skill tree is meant to become an actual architectural growth system: powers should create real new navigation or processing affordances, with their own review/witnessing. **"Earned" is the wrong connotation.** A better candidate concept is **saṃskāra morphology**: experience leaves durable impressions/grooves that alter the Governor's future shape and available movement. Keep the Sanskrit term as a candidate rather than flattening its philosophical history into a software label.

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
2. **Saṃskāra morphology:** Is this the right concept/name for Governor development through accumulated impressions? What is the first real behavioral change Peculiarity Sense should unlock?
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


## Second digestion — language in every spoon, depth only for exceptions

Jared sharpened the language design: **language sensing should be ubiquitous and cheap; deep linguistic interpretation should be exceptional and routed.**

The useful split is:

1. **Every ARRIVAL gets a language glance.** Record the language(s) actually published, issuing office/source, whether the surface is original/translation/summary/unknown, and any obvious version relationship. This is metadata/attention, not evidence of motive or contradiction.
2. **Most material rests after the glance.** Technical sameness, ordinary translation variance and uninteresting wording differences should not create motion merely because multiple languages exist.
3. **A linguistic exception may teleport to a dedicated tree.** Trigger examples: one home-language surface materially disagrees on a consequential point; a transition changes agency/responsibility/obligation; one language contains or omits a consequential condition; terminology maps poorly across legal/economic/technical regimes; publication genealogy suggests a nontrivial transformation worth checking.
4. **The Language Exception Tree can then inspect transitions deliberately.** It should preserve originals, publication lineage, office/country provenance, ordinary translation controls, domain terminology, and the exact point that survived. It may return to the originating domain tree or hand onward to a relevant specialist tree.
5. **No motive inference from wording alone.** A linguistic residual is a reason to inspect, not a license to psychologize a government, population or institution.

A useful routing shape to discuss with Jared:

`ARRIVAL language glance -> ordinary domain tree -> linguistic exception? -> LANGUAGE EXCEPTION TREE -> return to originating domain or teleport onward`

The language tree may itself route **after inspection** to domain trees such as diplomacy, economics/trade, alliance/pact, law/regulation, medicine/care, technology/industry, or civilian conditions. This preserves Jared's desire for cursory scans that can find surprising side-paths without making surprise itself a requirement.

### Candidate language-watch role

Discuss a provider-neutral **Language Exception Scout / Bee** rather than one model-specific agent. It could:

- watch approved public/official multilingual surfaces;
- notice mismatched versions, unusual translation lineage or consequential terminology changes;
- emit a tiny non-evidence exception packet;
- request a Garden teleport only when a bounded exception criterion is met;
- never infer national character, hidden motive or political intent from rhetoric alone.

This role should be allowed to accumulate cheap provisional memory so seasonal/recurrent language patterns can become visible before deciding whether durable specialist memory is warranted.

### Jared's current priority watch scope

Treat the following as **user-requested attention domains, not claims that wrongdoing or manipulation exists**:

- United Kingdom: government;
- Russia: government and economics;
- China: technology, economics, government and civilian unrest;
- India: issues affecting Muslims;
- United States: economics, government, civilian unrest and laws;
- Saudi Arabia: diplomatic relations;
- Germany: economics, civilian unrest, government and laws;
- Panama: diplomacy, economics/trade, logistics and civilian conditions where relevant;
- Singapore: diplomacy, economics/trade, logistics and civilian conditions where relevant.

For African logistics, candidate hubs/corridors worth evaluating for watch coverage beyond Egypt include:

- Morocco / Tanger Med;
- South Africa / Durban–Richards Bay system;
- Kenya / Mombasa and its inland corridors;
- Djibouti / Djibouti–Ethiopia corridor;
- Côte d'Ivoire / Abidjan;
- Ghana / Tema;
- Togo / Lomé;
- Tanzania / Dar es Salaam;
- Mauritius / Port Louis.

This is a **candidate coverage map**, not a ranking and not an assertion that all deserve equal monitoring intensity. The watch dimensions Jared requested for African hubs are diplomacy, economics, trade/logistics and civilian unrest/conditions.

### Bulking and cutting

Jared's metaphor is useful enough to preserve:

- **Bulk:** cheap capture, provisional folds, language antennae, exploratory branches, broad surface area, low-authority memory.
- **Cut:** deduplicate, compress, clear stale material, promote recurring distinctions, narrow specialist trees, retain only structure that keeps paying rent.

The Garden should support both phases. Rest prevents bulking from becoming compulsive motion; exception trees prevent cutting from sanding off the rare detail that later becomes important.
