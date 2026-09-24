#!/usr/bin/env python3
"""Shared reflection mailbox. Stores contributions and governor responses, never executes them."""
from __future__ import annotations

import argparse
from pathlib import Path
import json
import sys

import cycle

STORE = "operations/reflections/mailbox.json"
ORIGINS = {"self_report", "human_contribution", "coordinator_note", "runtime_observation", "mock"}


def load(root):
    path = Path(root) / STORE
    data = cycle.read_json(path) if path.exists() else {
        "schema_version": "0.1", "entries": {}, "decisions": {},
    }
    if (not isinstance(data, dict) or data.get("schema_version") != "0.1" or not isinstance(data.get("entries"), dict)
            or not isinstance(data.get("decisions"), dict)):
        raise cycle.CycleError("Unsupported reflection mailbox")
    return data


def required_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise cycle.CycleError(f"{name} requires non-empty text")
    return value


def strings(value, name):
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
        raise cycle.CycleError(f"{name} must be an array of non-empty strings")
    return value


def entry_body(payload):
    if not isinstance(payload, dict):
        raise cycle.CycleError("A reflection must be an object")
    body = {key: required_text(payload.get(key), key) for key in ("actor", "level", "summary")}
    origin = payload.get("origin", "self_report")
    if origin not in ORIGINS:
        raise cycle.CycleError("Unknown reflection origin")
    context = payload.get("context", {})
    if not isinstance(context, dict):
        raise cycle.CycleError("Reflection context must be an object")
    if body["level"] in {"neuron", "subcall"}:
        for key in ("run_id", "call_id"):
            required_text(context.get(key), key)
    for key in ("run_id", "call_id", "parent_call_id", "question_id", "attempt_id"):
        if context.get(key) is not None:
            required_text(context[key], key)
    body.update(origin=origin, context=context)
    for key in ("observations", "suggestions", "questions", "uncertainties", "source_refs", "related_reflection_ids"):
        body[key] = strings(payload.get(key, []), key)
    cycle.encoded(body)
    return body


def insert(data, body):
    rid = "REFL-" + cycle.digest(body)[:24].upper()
    if rid not in data["entries"]:
        data["entries"][rid] = {"reflection_id": rid, "created_at": cycle.now(), **body}
    elif any(data["entries"][rid].get(k) != v for k, v in body.items()):
        raise cycle.CycleError("Reflection identity conflict; original entry is preserved")
    return rid


def post(root, payloads):
    if isinstance(payloads, dict):
        payloads = [payloads]
    if not isinstance(payloads, list) or not payloads:
        raise cycle.CycleError("Supply one reflection or a non-empty array")
    bodies = [entry_body(p) for p in payloads]
    with cycle.locked(root) as root:
        data = load(root)
        before = cycle.digest(data)
        ids = [insert(data, body) for body in bodies]
        if cycle.digest(data) != before:
            cycle.write_json(root / STORE, data, replace=True)
    return ids


def attend(root, limit=50, offset=0):
    """Reading never consumes a message. Explicit responses decide what remains open."""
    if not isinstance(limit, int) or limit < 1:
        raise cycle.CycleError("Attention limit must be positive")
    if not isinstance(offset, int) or offset < 0:
        raise cycle.CycleError("Attention offset must be nonnegative")
    with cycle.locked(root):
        data = load(root)
        latest = {}
        for decision in sorted(data["decisions"].values(), key=lambda d: d["sequence"]):
            for rid in decision["reflection_ids"]:
                latest[rid] = decision
        pending = [r for rid, r in data["entries"].items()
                   if rid not in latest or latest[rid]["keep_open"]]
        pending.sort(key=lambda r: (r["created_at"], r["reflection_id"]))
        chosen = pending[offset:offset + limit]
        chosen_ids = {r["reflection_id"] for r in chosen}
        # Include the whole response history relevant to this page, including handoffs.
        responses = [d for d in data["decisions"].values() if chosen_ids.intersection(d["reflection_ids"])]
        return {"pending_count": len(pending), "returned_count": len(chosen),
                "offset": offset, "remaining_count": max(0, len(pending) - offset - len(chosen)),
                "next_offset": offset + len(chosen) if offset + len(chosen) < len(pending) else None,
                "entries": chosen,
                "prior_responses": responses,
                "instruction": "Reflect with other thought partners as useful. Choose and record your response; this mailbox executes no actions."}


def respond(root, payload):
    """Governor chooses a response; no ranking, action routing or policy change is automatic."""
    if not isinstance(payload, dict):
        raise cycle.CycleError("Governor response must be an object")
    body = {k: required_text(payload.get(k), k) for k in ("review_id", "actor", "disposition", "summary")}
    refs = strings(payload.get("reflection_ids"), "reflection_ids")
    if not refs:
        raise cycle.CycleError("A response must identify the reflections considered")
    keep_open = payload.get("keep_open", True)
    if not isinstance(keep_open, bool):
        raise cycle.CycleError("keep_open must be boolean")
    followups = payload.get("followups", [])
    if not isinstance(followups, list):
        raise cycle.CycleError("followups must be an array")
    for item in followups:
        if not isinstance(item, dict):
            raise cycle.CycleError("Each followup must name a recipient and question")
        required_text(item.get("recipient"), "recipient")
        required_text(item.get("question"), "question")
    self_reflection = payload.get("self_reflection")
    if self_reflection is not None:
        required_text(self_reflection, "self_reflection")
    body.update(reflection_ids=refs, keep_open=keep_open, followups=followups,
                self_reflection=self_reflection)
    did = "REVIEW-" + cycle.digest(body)[:24].upper()
    with cycle.locked(root) as root:
        data = load(root)
        if any(rid not in data["entries"] for rid in refs):
            raise cycle.CycleError("Response references an unknown reflection")
        if did in data["decisions"]:
            return data["decisions"][did]
        # A reused review ID cannot quietly replace a prior response.
        if any(d["review_id"] == body["review_id"] for d in data["decisions"].values()):
            raise cycle.CycleError("Review ID already used; append a new response for a changed decision")
        own_id = None
        if self_reflection:
            own_id = insert(data, entry_body({"actor": body["actor"], "level": "governor",
                "origin": "self_report", "summary": self_reflection,
                "context": {"review_id": body["review_id"]}, "related_reflection_ids": refs}))
        record = {"decision_id": did, "sequence": len(data["decisions"]) + 1,
                  "created_at": cycle.now(), "own_reflection_id": own_id, **body}
        data["decisions"][did] = record
        cycle.write_json(root / STORE, data, replace=True)
        return record


def from_checkpoint(root, checkpoint):
    """Project already-saved worker output into the mailbox; safe to repeat after interruption."""
    runtime = checkpoint.get("runtime", {})
    origin = "mock" if runtime.get("provider") == "mock" else "self_report"
    common = {"actor": checkpoint["agent"], "level": checkpoint.get("reflection_level", "worker"), "origin": origin,
              "context": {"question_id": checkpoint["question_id"], "attempt_id": checkpoint["attempt_id"],
                          "run_id": checkpoint.get("run_id", checkpoint["attempt_id"]),
                          "call_id": checkpoint["attempt_id"], "parent_call_id": checkpoint.get("parent_call_id"),
                          "provider": runtime.get("provider"), "model": runtime.get("model"),
                          "result": checkpoint.get("attempt_result")}}
    supplied = checkpoint.get("reflections", [])
    if not isinstance(supplied, list):
        raise cycle.CycleError("Worker reflections must be an array; raw output remains in the attempt")
    entries = []
    for note in supplied:
        if isinstance(note, str):
            note = {"summary": note}
        if not isinstance(note, dict):
            raise cycle.CycleError("Each worker reflection must be text or an object")
        # Identity and call provenance come from the runtime, not model-authored fields.
        entries.append({**note, **common})
    if not entries:
        entries = [{**common, "origin": "runtime_observation",
                    "summary": "No self-reflection was supplied for this recorded worker call.",
                    "observations": [f"Recorded result: {checkpoint.get('attempt_result', 'unknown')}."],
                    "uncertainties": ["This is a coverage note, not an inferred account of a model's thoughts."]}]
    return post(root, entries)


def from_attempt(root, question_id, attempt_id):
    import questions
    item = questions.question(questions.load(root), question_id)
    attempt = item["attempts"].get(attempt_id)
    if not attempt or not attempt.get("result"):
        raise cycle.CycleError("Attempt has no saved result to project")
    checkpoint = attempt["result"].get("details", {}).get("checkpoint")
    if not checkpoint:
        raise cycle.CycleError("Attempt has no saved worker checkpoint")
    return from_checkpoint(root, checkpoint)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("post", "respond", "project-checkpoint"):
        sub.add_parser(name).add_argument("--file", type=Path, required=True)
    pending = sub.add_parser("pending")
    pending.add_argument("--limit", type=int, default=50)
    pending.add_argument("--offset", type=int, default=0)
    recover = sub.add_parser("recover-attempt")
    recover.add_argument("--question", required=True)
    recover.add_argument("--attempt", required=True)
    args = p.parse_args()
    try:
        if args.command == "pending":
            result = attend(args.root, args.limit, args.offset)
        elif args.command == "recover-attempt":
            result = from_attempt(args.root, args.question, args.attempt)
        else:
            payload = cycle.read_json(args.file)
            operation = {"post": post, "respond": respond, "project-checkpoint": from_checkpoint}[args.command]
            result = operation(args.root, payload)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (cycle.CycleError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
