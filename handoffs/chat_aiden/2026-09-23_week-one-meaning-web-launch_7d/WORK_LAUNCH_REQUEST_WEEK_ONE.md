# WORK LAUNCH REQUEST — Week One Meaning Web

**Requested actor:** Work Aiden  
**Base commit:** `9cddb4bdc0a730d11d42769066fa89464457fc2d`  
**Desired outcome:** deploy one real, bounded autonomous system that performs useful public-source research for seven days and leaves a body of work that can be digested across later Chat sessions.

## User intent

The user is nearing the final Work reset they expect to spend heavily on this project. Use that Work session to **launch something that actually runs**, rather than only extending architecture.

The system should embody:
- root reflection;
- care for people and dependent systems;
- stability without stasis;
- search for "Titanic pressure points" crossing political, national, economic, cultural, linguistic and other frames;
- meaning-centric synthesis;
- a soft/strong spiderweb architecture that is locally breakable and repairable.

Read `ROOT_MEANING_AND_DESIGN_PRINCIPLES.md` before implementation.

## Launch the smallest system that can honestly work for one week

Do not wait for every proposed organ to be complete.

### Minimum viable autonomous organism

1. **Real public scouts**
   - existing RSS/Atom scouts;
   - at least one additional useful public structured source if bounded and safe;
   - deduplicate and retain discovery provenance;
   - no source item becomes admitted evidence merely by being discovered.

2. **Question selection**
   - reuse `operations/questions.json`;
   - prefer unresolved Questions and newly discovered Questions that expose cross-domain/cross-relative pressure junctions;
   - do not create a question storm;
   - semantic duplicates and narrower/broader questions remain linked.

3. **One real Answer path**
   - integrate the current user provider policy from Chat PR #5:
     - role-fit free models are allowed after verification;
     - actual provider/model identity must be recorded;
     - no silent downgrade;
     - **NO GROQ**, including hidden aggregator routing.
   - enable at least **one reviewed real provider adapter**.
   - if practical within this Work session, enable a bounded role-fit ring using Gemini + Cloudflare Workers AI + OpenRouter.
   - if the full ring would delay launch, ship one verified real provider plus the provider-neutral interface and launch. Real useful work outranks architectural completeness.

4. **Reflection**
   - preserve existing worker reflection;
   - require capability-transition reflection where it can change behavior;
   - use deterministic checks rather than extra LLM calls for tiny Touch/Query operations;
   - project meaningful notes into the reflection mailbox;
   - do not require busywork reflection.

5. **Governor review**
   - run a bounded governor review on accumulated reflections and research outputs;
   - it may connect, defer, question, quarantine or suggest followup;
   - suggestions do not automatically execute consequential actions.

6. **Safe capability boundary**
   - public lawful read-only research;
   - no autonomous email sending;
   - no purchases;
   - no account/permission changes;
   - no partner commitments;
   - no canonical research admission without normal review;
   - no recursive privilege escalation;
   - no Groq.

7. **Scheduled operation**
   - enable a GitHub Actions schedule or equivalent bounded unattended trigger for **seven days**;
   - stay at zero paid spend;
   - use provider-specific quota/reset knowledge;
   - preserve all attempt outcomes;
   - avoid needless retry storms.

## Suggested cadence

Choose an operational cadence based on verified free quotas and GitHub/runtime limits rather than blindly following this suggestion.

A reasonable first-week shape would be:
- light public scouting several times per day;
- one or two bounded Answer-Bee batches per day;
- one daily governor/reflection review;
- prepare a human-facing candidate packet before the Pacific evening Human Window when useful;
- final weekly synthesis after seven days.

If current quotas make this too aggressive, reduce frequency rather than lowering provenance/safety standards.

## Research attention

The first autonomous week should prioritize **junctions, not headlines**.

Look for cases where a stress or reserve crosses several domains, for example:
- fuel ↔ food ↔ logistics ↔ emergency services;
- sulfur/phosphate ↔ agriculture ↔ finance ↔ international shipping;
- rail/transload ↔ rural access ↔ diesel elasticity;
- power ↔ communications ↔ medicine/cold chain;
- commons ↔ local productive capacity ↔ reciprocal logistics;
- public narratives ↔ actual operational constraints.

Do not force every run to find catastrophe. Improving conditions, spare capacity and boring continuity are equally valid findings.

## Meaning packet

For any high-interest Question, add a compact meaning layer when supported:

- **material function:** what actually has to keep working;
- **human/system meaning:** why it matters;
- **frames:** materially relevant differences in how groups/institutions describe it;
- **shared dependency:** what remains common across those frames;
- **buffers/adaptations:** what bends;
- **pressure point:** what could propagate;
- **growth opening:** what new capability could emerge;
- **unknowns/falsifier:** what would change the interpretation.

This is synthesis metadata, not permission to speculate about motives.

## Week-one outputs

Create a durable directory/collection with:

### Daily
- source-discovery records;
- Questions touched/created/reopened;
- every model attempt and actual result;
- provisional/ready answers;
- reflection records;
- provider/quota/cooldown state;
- governor review;
- compact human-readable daily note when warranted.

### End of week
Produce:

`WEEK_ONE_DIGEST.md`

with:
- what the system actually ran;
- uptime/failures/recovery;
- Questions asked;
- Questions answered/partially answered;
- most important cross-domain junctions found;
- stabilizing/improving signals;
- reserves/adaptations/growth openings;
- unresolved Questions;
- provider/model role-fit observations;
- reflection themes that materially changed behavior;
- false alarms/misleading leads;
- what should be changed before Week Two;
- links to all underlying packets.

Also produce a **Chat-friendly index** so future Chat Aiden sessions can take one bounded piece at a time rather than reading the whole week.

## Stop conditions / emergency brake

Pause autonomous model work if:
- provider cost could exceed zero-spend intent;
- credentials/auth behave unexpectedly;
- repeated prompt-injection/adversarial inputs escape containment;
- provider routing cannot enforce NO GROQ;
- birth/worker count grows unexpectedly;
- writes begin affecting external systems;
- repeated retries consume quotas without useful output;
- provenance or attempt identity cannot be preserved.

Public scouts may continue only if independently safe.

## Definition of "launched"

Do not call this launched merely because code exists.

Launched means:
1. at least one scheduled unattended run is enabled;
2. at least one real public scout successfully retrieves;
3. at least one real approved AI provider successfully completes a bounded worker attempt **or** leaves a correctly classified provider failure that the scheduler can recover from without human repair;
4. reflection is preserved;
5. the output is durable/reviewable;
6. the next scheduled run can proceed without the user being present.

If a provider cannot be enabled safely in the available Work window, launch the autonomous public-scout + Question/reflection/governor pipeline and leave the live Answer stage explicitly pending rather than pretending.

## Handoff to future Chat

Future Chat Aiden should be able to open one daily packet or one Question ID and continue meaningfully without re-running the week.

The week is intended to create **material for many later conversations**, not one enormous report the user must digest at once.
