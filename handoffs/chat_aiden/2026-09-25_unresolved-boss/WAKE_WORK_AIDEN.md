# Wake Work Aiden — The Unresolved / Parallax Bee

Good morning again. Jared asked Chat to make the first Meaning Tower boss encounter interactive and to set up the Bee that can eventually feed it.

Please review this branch rather than treating it as merged design.

## Jared's current direction

- **The Unresolved** may be a recurring Meaning Tower boss.
- Visually he is an original retro pixel-art sea sovereign: aqua-hued, tentacled, Poseidon-adjacent without using external game assets.
- He fights by summoning whirlpools full of flotsam.
- Jared clears a whirlpool by **holding one piece of flotsam steady** until the water calms.
- What survives is preserved for attention; what sinks is not declared false.
- No score.
- A Boss Result should carry the preserved pieces back to the Garden/Governor with provenance.
- The first proposed power-up remains **Peculiarity Sense**.

Chat staged:
- `handoffs/chat_aiden/2026-09-25_unresolved-boss/UNRESOLVED_BOSS.html`
- `agents/parallax_collector_bee.json`
- the accompanying README.

## Bee proposal

The **Parallax Collector Bee** is the first concrete specialized Collector candidate for `Q-MEANING-TRANSLATION-BOSS`.

Please review whether it should become the first registered Garden teleport destination:

`INIT:RESID-0007 -> PYGENT:PARALLAX-0001 -> INIT:RETURN-0010`

Its intended bounded pass is one matched official multilingual source family, ordinary translation/weather controls, inherited/independent/bridge CROSS attachments, at most three surviving residuals and one boring control, then a Boss Packet or a valid silent/question exit.

Do **not** schedule it merely because the role file exists.

## Integration questions for Work

1. Should the boss HTML replace/upgrade the existing Meaning Tower translation-boss room, or become a reusable boss component that can be given different packets?
2. Can the live Boss Packet schema be kept data-driven so later bosses reuse the whirlpool mechanic without hard-coding translation content?
3. Please preserve the distinction: the game records Jared's attention choice; it does not change evidence status.
4. If the Bee becomes runnable, give it a real narrow budget/stop condition and a deterministic packet validator before any model-backed execution.
5. Do not award the Governor power in canonical state until Jared actually completes a real encounter and we decide what his method of defeat taught the Governor.

## Provider note

Jared is separately exploring Mistral Free mode. Do not add a Mistral adapter or secret solely because signup is available. If/when Jared provides the key and asks to integrate it, verify Free-mode/PAYG-off account state and role fit first. Preserve zero-spend and NO GROQ boundaries.
