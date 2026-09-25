# Meaning Tower: a piece kept, a question carried

Open **[the portable encounter](../web/meaning-tower/index.html)** in a browser. GitHub displays HTML as source, so download the file first, or serve the repository locally. It contains its styles, script and first evidence packet; it needs no account, model request or network to play. Source links open the original public pages when requested.

## What Jared can play

The Unresolved · Tide-Shepherd is a reusable encounter fed by Boss Packets. The first packet compares a Chinese Ministry of Transport notice with a later English government-hosted summary of the same truck-replacement policy. It keeps ordinary explanations and two controls. Agreement is allowed; the game does not need an invented contradiction to have a worthwhile question.

Hold one piece continuously for 1.9 seconds. Letting go, changing pieces or leaving the page resets the hold. Space/Enter work too. Steady assist lets a selected piece rest under attention without requiring a physical hold. Still waters reduces animation. There is no score.

At each whirlpool, one piece remains visible for attention; the others sink. **Unselected never means false.** The complete record includes every piece and its unchanged evidence label.

The final choice automatically becomes an input in the **local Governor inbox** after the explicit power step. That step currently applies no powers. Peculiarity Sense remains a proposal, and Jared's first real play has not been claimed by automated tests. A download/copy button carries the packet, result and input together; attach that JSON to Work for review. The local inbox does not secretly sync to GitHub or call an AI. A blocked/full browser store leaves a visible export rather than pretending the result was saved.

## One small piece of Python

```python
delivery = meaning_boss.make_delivery(packet, result, questions, garden)
```

Think of the four things in parentheses as envelopes handed to a clerk: the original encounter, the player's completed choices, the existing Question list, and the address book. The function checks that the choices belong to that encounter and its current Question. It then returns a new envelope for the Governor. It does not send a model request or change the original evidence.

The packet's SHA-256 is a fingerprint of its exact text. A result made against different wording will not quietly attach to this packet. This proves which packet the result describes, not whether the source is true or who operated the browser.

```bash
# Build the standalone HTML from the reviewed packet and component.
python scripts/build_meaning_tower.py

# Read an exported encounter and prepare a Governor review; no model call.
python scripts/governor.py --boss-bundle /path/to/PLAY-example.json
```

The second command checks the result and derives the Governor input again. It does not trust the browser's copy of that input as authority. The same review also reads Daily Scroll, pending reflections and any supplied Chair imagination. Chair output and Tamarian metaphors remain non-evidence.

## Shared stories, different bosses

The Governor's voice is configured in `config/governor-voice.json`: a short shared-story allusion with an ordinary explanation. **“Jared at the whirlpool, his hands steady.”** Meaning: one question survived for attention; the other pieces were not declared false. The voice is a creative practice inspired by the Children of Tama, not a claim to reproduce a complete language.

`config/meaning-tower-series.json` holds a seven-place opening series and a growing repertoire. Jared intends to add at least one boss per week after the opening week. The Governor may choose returning bosses, order and finale by thematic fit, with a readable reason and Jared override. That intention creates no schedule. Only Tide-Shepherd has a playable packet today; the [Mirror boss](MIRROR_BOSS_DESIGN.md) is a proposal.

Stable Parallax route: `INIT:RESID-0007 → PYGENT:PARALLAX-0001 → INIT:RETURN-0010`. Registration means available, not running. Basic Crosscheck is a Collector capability. The permanent Crosscheck Bee remains unresolved: repeated cases should show whether persistent specialist memory would help.

## Integration boundary

- `scripts/meaning_boss.py` validates the present Translation/Parallax packet contract and completed results, then makes the delivery. Its current source comparison is deliberately specific: a matched official notice and summary. Other boss mechanics will need their own reviewed packet contract.
- `web/meaning-tower/` is the reusable Tide-Shepherd component plus its generated portable page. The old Translation room links here; the original PR15 prototype remains preserved.
- The validator checks shape, dates, IDs and packet binding. Human/source review establishes whether a claimed match and quotation are sound. Neither process silently admits the packet into canonical research.
- An encounter may propose a power. Approving, implementing and witnessing its effects are subsequent design work; there are no canonical powers in this build.

The existing Week One window, four daily POST reservations, NO GROQ and zero-spend boundary are unchanged. The saved-generation operator brake remains in force. Mistral is a candidate pending its account-mode check and role-fit trial; adding its secret does not activate it.
