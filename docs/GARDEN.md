# The initiating Garden, one small working slice

The Garden now has an **on-demand grammar prototype**. It checks and preserves a supplied pass through the ten initiating nodes, resolves named destinations, and makes a reproducible Chair sequence. It does not run a researcher, issue search queries, call an AI, or schedule another pass. Recorded answers must be supplied by the actual participant who obtained them.

Jared's current Bee choice is part of `config/garden.json`: basic Crosscheck belongs to a Collector. A consequential residual may justify a bounded Pygent Collector/specialist request. A permanent Crosscheck Bee remains unresolved until repeated cases show that persistent specialist memory helps.

## Read one pass with Jared

Python's `def` gives a little mechanism a name. Its arguments are the things handed to it; `return` is what it hands back. A **dictionary** is a labelled record, written with braces. A **list** is an ordered collection, written with square brackets.

```python
result = prepare_pass(config, packet, registry)
```

Here `config` holds the Garden's addresses, `packet` contains the supplied observations and stage records, and `registry` supplies existing Question IDs and their current epochs. The function validates those relationships and hands back a new record. It leaves the three inputs unchanged.

`examples/garden/q18-pass.json` follows the vessel example without repeating its research. Its MIRROR queries are explicitly proposed and its independent CROSS list is empty. That emptiness records missing work; the code does not fill it with invented evidence.

| Stable address | What the record carries |
| --- | --- |
| `INIT:ROOT-0001` | Pass name and identity |
| `INIT:ARRIVAL-0002` | What arrived, from where and sent where |
| `INIT:EPIST-0003` | Question/prompt and starting epistemic state |
| `INIT:FUNC-0004` | Task and function being investigated |
| `INIT:MIRROR-0005` | Competing explanations, proposed or actual queries, recorded answers |
| `INIT:CROSS-0006` | Inherited, independently derived and deliberate bridge attachments |
| `INIT:RESID-0007` | Surviving residual, if any; optional bounded specialist proposal |
| `INIT:MEAN-0008` | What changed in meaning; optional non-evidence culture flower |
| `INIT:EXIT-0009` | Answer, question, teleport, silence or error |
| `INIT:RETURN-0010` | New linked arrival or rest |

The validated trace means these records are present in that order. It does not certify that research was performed, that a claim is true, or that an answer has been admitted. A bridge can be a test connecting two observations; its mere presence adds no corroboration. Two independent search paths can still lead to the same underlying source.

A named teleport such as `PYGENT:OPERATING-0001` stays **proposed** until that tree and node exist in the configuration. `INIT:MEAN-0008` resolves now. Neither result executes code. Spreadsheet row numbers and tab names are presentation only; moving a row does not change its stable address. No Governor-only tree or specialist runtime is created by this slice.

EXIT includes errors as one possible result. Audit failure is an error case, not the purpose of EXIT. RETURN preserves the original arrival and parent link. An already-seen arrival ID or identical payload rests. A changed payload with a new ID also needs an explicit reason for renewed attention; a human/worker must assess whether that change is meaningful. The code cannot judge semantic novelty merely from a hash.

## AND, OR and unknown

In Python `True` means yes, `False` means no and `None` means unknown here. We name a group explicitly rather than interpreting free text as a condition.

```python
group = {"op": "AND", "members": ["arrived", "usable"]}
result = evaluate_group(group, {"arrived": True, "usable": None})
# result is None: arrival alone does not establish usable capacity.
```

For AND, one false member establishes false; otherwise an unknown member keeps the group unknown. For OR, one true member establishes true; otherwise unknown stays unknown. Missing predicates are unknown. This helper does not yet make scheduling decisions or automatically traverse branches. Empty groups and text pretending to be a Boolean are rejected.

## The Chair: every deposited instance gets a seat

The current Chair is a **seeded word-instance sequence generator**. It is not a trained Markov model. Each deposited word has its own ID, so two deposits of “care” remain two instances:

```python
bank = [{"id": "WORD-1", "word": "care"},
        {"id": "WORD-2", "word": "care"}]
chair = generate_chair(bank, "jared-1")
```

The seed is a reproducible starting label. The mechanism gives each seed/instance-ID pair a SHA-256 ordering value, then sorts by that value. Every valid deposited instance therefore appears exactly once. There is no retrying until the sentence seems meaningful. A different seed may give a different order; it is not guaranteed to do so, especially with few words.

The packet preserves the original bank, instance IDs and words in generated order, seed, algorithm/version, hashes and coverage. Maximum size is 256 instances. Empty banks are valid and yield an empty sequence. Missing or duplicate instance IDs are rejected; repeated words are welcome. Hashes detect content changes and support reproduction; they are not proof of authorship or meaning.

The generated `imagination_prompt` can then be given to an AI in an authorized session. Its response is a separate attributed record:

```python
imagination = attach_imagination(
    chair, "Who gets carried, and who needs rest?",
    {"name": "actual participant", "runtime": "actual session", "model": "unknown"})
```

That example string illustrates the API, not a claim that an AI was called. `attach_imagination` preserves the exact Chair packet, checks its bank/sequence/seed hashes and records actual supplied output, actor and proposed Garden destination. Sequence and response both remain **non-evidence**. An empty response records silence. The Governor can use the association as a question or culture input; any resulting factual claim still needs ordinary source work.

An actual Work-session response is preserved in [chair-imagination.json](../examples/garden/chair-imagination.json), including the exact sequence **care care vessel voyage rest needs** and both care-instance IDs. Work's association asks what rest margin makes a voyage dependable. [chair-feedback-pass.json](../examples/garden/chair-feedback-pass.json) routes that non-evidence question through INIT and then rests. It was supplied and validated in this ChatGPT session; it is not a separate autonomous Governor run. Its CROSS evidence lists are empty.

## Bounded inputs and saved output

A pass can retain `input_refs`, including the Daily Scroll projection, mailbox, Meaning Tower and Chair imagination. References describe context; they do not import it by themselves or grant execution authority. The Governor's review packet is the adjacent integration point; see `scripts/governor.py` for its current supported input projection.

These commands inspect the supplied examples and print JSON:

```bash
python scripts/garden.py pass --file examples/garden/q18-pass.json
python scripts/garden.py chair --file examples/garden/chair-bank.json --seed jared-1
python scripts/garden.py pass --file examples/garden/chair-feedback-pass.json
python scripts/governor.py --imagination examples/garden/chair-imagination.json
```

Add `--output /path/to/a/unique-packet.json` to preserve a result. `save_packet(path, packet)` uses the repository's existing immutable writer: retrying identical content is safe; different content at the same path is refused. Supplied inputs, exact configuration and record hashes make a saved pass inspectable. Pass size is capped at 64 KiB. Operational outputs belong on the designated operational branch through its coordinated workflow; these commands do not publish or modify canonical research.

The next design decision is how explicit AND/OR groups should control a **real** branch: for example, whether an unknown operating measure requests another observation or ends with a question. This prototype makes those choices visible without silently choosing them for Jared.
