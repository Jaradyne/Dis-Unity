# Multilingual Official-Surface Bee

## Mission

Watch one government's own official multilingual publication surfaces and ask:

> When the same event, speech or policy is expressed in different official languages, what changes — wording, emphasis, omission, timing, framing, metaphor, level of certainty, or emotional temperature — and which differences are likely meaningful rather than translation noise?

Initial focus: **People's Republic of China official surfaces**.

This is not a propaganda detector and not a motive detector. It is a **translation-parallax observer**.

## Source families

### State Council
- Chinese: `www.gov.cn`
- English: `english.www.gov.cn`

The English site describes itself as the State Council's official English-language communication platform. For the State Council Gazette, the Chinese version prevails on discrepancy.

### Ministry of Foreign Affairs
Official language surfaces visible on the MFA site:
- Simplified Chinese
- English
- French
- Spanish
- Russian
- Arabic

The Bee should preserve each language as its own source record rather than overwrite them into one translation.

### Other official multilingual surfaces
Potential later additions:
- Beijing International Web Portal (nine-language public-service surface);
- official translated books/white papers where counterpart editions are verifiable.

Do not silently treat Xinhua/CGTN/People's Daily as equivalent to State Council/MFA publication authority. They may be useful separate official/state-media surfaces with their own provenance class.

## Architecture: granular first, synthesis second

### Language Leaf Bees
One Leaf Bee per language.

Each Leaf Bee works **independently before seeing other language interpretations** to reduce anchoring.

It records:
- exact source URL;
- publication/update time;
- language/script;
- event/document identity;
- short source excerpt or bounded semantic units;
- metaphors/idioms;
- explicit certainty/uncertainty;
- actors named/omitted;
- qualifiers/intensifiers;
- emotional/rhetorical temperature;
- notable terms difficult to translate;
- self-comparison with the same language's earlier usage.

A Leaf Bee may say "nothing unusual."

### Counterpart Matcher
Matches likely same-event/same-document records across languages using:
- date/time;
- title/entity overlap;
- official cross-links;
- document/decree/speech identifiers;
- source family.

A mismatch is preserved as uncertainty rather than force-matched.

### Parallax Bee
Compares matched records after Leaf Bees have produced independent observations.

Looks for:
- omission/addition;
- stronger/weaker certainty;
- named vs unnamed target;
- metaphor retained/flattened;
- positive/negative valence shift;
- legal/technical terminology shift;
- different audience framing;
- publishing lag;
- headline/body mismatch.

### Noise Gate
Before escalation, asks whether the difference is plausibly:
- grammar/idiom;
- translator preference;
- space/layout;
- language-specific convention;
- publication lag;
- source-version mismatch;
- literal vs idiomatic translation.

Only survivors become Questions or Samples.

## Pairwise tradeoff

With N languages, comparing every language independently to every other language grows as N(N-1)/2.

For six MFA languages that is 15 pairwise comparisons per item.

Recommended Week One pattern:
1. every Leaf independently inspects itself;
2. compare each foreign-language surface with Chinese;
3. compare every language with its own prior usage;
4. trigger selected foreign↔foreign comparisons only when the Parallax Bee sees a candidate anomaly.

This keeps granularity while avoiding automatic O(N²) noise/cost.

For high-interest items, run the full pairwise matrix.

## Diachronic self-comparison

Each language also compares **itself to itself over time**.

This can reveal:
- a term becoming more/less intense;
- a metaphor appearing/disappearing;
- a policy concept acquiring a new translation;
- a topic moving from technical to moral/emotional vocabulary;
- habitual translation drift.

A self-change is not automatically political significance.

## Similar official surfaces elsewhere

Good comparative laboratories:
- Russia: Kremlin maintains Russian and English official sites; English translations exist only where available.
- Japan: Prime Minister's Office provides English/provisional translations; Japanese originals may explicitly prevail on discrepancy.
- Switzerland: German/French/Italian are primary federal-language surfaces; English is explicitly a **selection** of information.
- Canada: English and French have equal official status across federal institutions, making systematic asymmetry a different kind of signal than a clearly secondary translation surface.
- France: Élysée maintains French and English publication surfaces; official texts and editorial material should remain provenance-distinct.

Each country gets its own authority rules. Do not impose China's hierarchy on Canada or Switzerland.

## Sample card output

Every escalated item can emit a compact Sample:

```json
{
  "sample_id": "SAMPLE-...",
  "source_family": "PRC MFA",
  "event": "2026-08-31 press conference",
  "languages": ["zh-Hans","en","fr","ru"],
  "difference_type": ["tone","agency"],
  "what_changed": "English rendering is less explicit about the target/agency of 'smearing/hype' than several other official-language versions.",
  "noise_test": ["idiomatic translation remains plausible"],
  "why_interesting": "Audience-facing translation can alter rhetorical temperature without altering the policy position.",
  "question_ref": null,
  "confidence": "candidate",
  "source_refs": []
}
```

Samples are invitations to look, not conclusions.
