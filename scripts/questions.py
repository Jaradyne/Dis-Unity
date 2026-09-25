#!/usr/bin/env python3
"""Shared question/attempt/answer records. No network or canonical-state writes."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid

import cycle

STORE = "operations/questions.json"
RESULTS = {
    "usable_answer", "partial_answer", "mock_only", "policy_blocked",
    "transient_capacity", "short_rate_limit", "daily_quota_exhausted",
    "auth_or_configuration_error", "model_unavailable", "transport_timeout",
    "invalid_response", "interrupted", "audit_pending", "spend_detected",
}
REASONS = {
    "provider_ring_exhausted", "chat_research_requested", "work_integration_required",
    "human_review_required", "credentials_or_access_required", "consequential_review",
    "long_lived_deferred_action",
}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def stamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise cycle.CycleError("Timestamps require a timezone")
    return parsed


def identifier(value, prefix):
    if not isinstance(value, str) or not re.fullmatch(prefix + r"-[A-Z0-9-]{1,90}", value):
        raise cycle.CycleError(f"Invalid {prefix} identifier")
    return value


def text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise cycle.CycleError(f"{name} must be non-empty text")
    return value


def load(root):
    path = Path(root) / STORE
    data = cycle.read_json(path) if path.exists() else {"schema_version": "0.1", "questions": {}}
    if data.get("schema_version") != "0.1" or not isinstance(data.get("questions"), dict):
        raise cycle.CycleError("Unsupported question store")
    return data


def mutate(root, action):
    with cycle.locked(root) as root:
        data = load(root)
        before = cycle.digest(data)
        result = action(data)
        if cycle.digest(data) != before:
            cycle.write_json(root / STORE, data, replace=True)
        return result


def question(data, qid):
    identifier(qid, "Q")
    if qid not in data["questions"]:
        raise cycle.CycleError(f"Unknown question: {qid}")
    return data["questions"][qid]


def ask(root, wording, actor, *, qid=None, geography=None, context_refs=None):
    text(wording, "question")
    text(actor, "actor")
    key = cycle.digest([" ".join(wording.casefold().split()), geography])
    qid = identifier(qid or "Q-" + key[:16].upper(), "Q")

    def action(data):
        if qid in data["questions"] and data["questions"][qid]["identity_key"] != key:
            raise cycle.CycleError("Question ID already refers to different wording/scope")
        for existing in data["questions"].values():
            if existing["identity_key"] == key:
                return existing
        item = {
            "question_id": qid, "question": wording, "identity_key": key,
            "status": "open", "epoch": 1, "created_at": now(), "created_by": actor,
            "geography": geography, "context_refs": context_refs or [], "relations": [],
            "claim": None, "attempts": {}, "answers": {}, "tickets": {}, "history": [],
        }
        data["questions"][qid] = item
        return item
    return mutate(root, action)


def link(root, qid, other, kind, actor):
    reverse = {"parent": "child", "child": "parent", "sibling": "sibling", "related": "related"}
    if kind not in reverse or qid == other:
        raise cycle.CycleError("Use parent/child/sibling/related between different questions")

    def action(data):
        left, right = question(data, qid), question(data, other)
        for item, target, relation in [(left, other, kind), (right, qid, reverse[kind])]:
            if not any(x["question_id"] == target and x["kind"] == relation for x in item["relations"]):
                item["relations"].append({"question_id": target, "kind": relation, "actor": actor})
        return left
    return mutate(root, action)


def claim(root, qid, actor, seconds=900):
    text(actor, "actor")
    if not 1 <= seconds <= 3600:
        raise cycle.CycleError("Claim duration must be 1–3600 seconds")

    def action(data):
        item = question(data, qid)
        if item["status"] in {"answered", "superseded", "closed_no_answer"}:
            return {"status": "already_answered_or_closed", "question_id": qid}
        if any(a["epoch"] == item["epoch"] and a["result"] is None for a in item["attempts"].values()):
            return {"status": "unfinished_attempt", "question_id": qid}
        if item["claim"] and stamp(item["claim"]["expires_at"]) > stamp(now()):
            return {"status": "claimed_elsewhere", "question_id": qid}
        lease = {"token": uuid.uuid4().hex, "actor": actor, "epoch": item["epoch"],
                 "expires_at": (stamp(now()) + timedelta(seconds=seconds)).isoformat()}
        item["claim"] = lease
        item["status"] = "answering"
        return {"status": "claimed", "question_id": qid, **lease}
    return mutate(root, action)


def begin_attempt(root, qid, token, request):
    required = {"actor", "provider", "model", "prompt", "role", "context_refs", "base_commit",
                "evidence_cutoff", "settings"}
    if not isinstance(request, dict) or required - request.keys():
        raise cycle.CycleError("Attempt request is missing provenance/prompt fields")
    text(request["prompt"], "prompt")
    aid = "ATT-" + uuid.uuid4().hex.upper()

    def action(data):
        item = question(data, qid)
        lease = item["claim"]
        if (not lease or lease["token"] != token or lease["epoch"] != item["epoch"]
                or stamp(lease["expires_at"]) <= stamp(now()) or item["status"] != "answering"):
            raise cycle.CycleError("Valid question claim required")
        if any(a["epoch"] == item["epoch"] and a["result"] is None for a in item["attempts"].values()):
            raise cycle.CycleError("Recover the unfinished attempt before trying again")
        attempt = {"attempt_id": aid, "question_id": qid, "epoch": item["epoch"],
                   "created_at": now(), "request": request, "request_sha256": cycle.digest(request),
                   "result": None}
        item["attempts"][aid] = attempt
        return attempt
    return mutate(root, action)


def finish_attempt(root, qid, aid, result, *, details=None):
    if result not in RESULTS:
        raise cycle.CycleError("Unknown attempt result")
    payload = {"category": result, "details": details or {}}

    def action(data):
        item = question(data, qid)
        attempt = item["attempts"].get(aid)
        if not attempt:
            raise cycle.CycleError("Unknown attempt")
        if cycle.digest(attempt["request"]) != attempt["request_sha256"]:
            raise cycle.CycleError("Retained prompt/provenance changed")
        if attempt["result"]:
            if {k: attempt["result"][k] for k in payload} != payload:
                raise cycle.CycleError("Attempt result is immutable; create a new attempt")
            return attempt
        attempt["result"] = {**payload, "recorded_at": now()}
        if attempt["epoch"] == item["epoch"]:
            item["claim"] = None
            if item["status"] == "answering":
                item["status"] = "open"
        return attempt
    return mutate(root, action)


def answer(root, qid, actor, payload, *, epoch, attempt_id=None):
    text(actor, "actor")
    if not isinstance(payload, dict):
        raise cycle.CycleError("Answer must be an object")
    text(payload.get("summary"), "answer summary")
    for name in ("evidence_refs", "counterevidence", "limitations"):
        if not isinstance(payload.get(name), list):
            raise cycle.CycleError(f"Answer requires {name} as an array (can be empty)")
    if payload.get("status") not in {"provisional", "ready_for_review"}:
        raise cycle.CycleError("Answer status must be provisional or ready_for_review")
    body = {"question_id": qid, "actor": actor, "epoch": epoch, "attempt_id": attempt_id, "payload": payload}
    answer_id = "ANS-" + cycle.digest(body)[:24].upper()

    def action(data):
        item = question(data, qid)
        if not isinstance(epoch, int) or not 1 <= epoch <= item["epoch"]:
            raise cycle.CycleError("Invalid evidence epoch")
        if attempt_id:
            attempt = item["attempts"].get(attempt_id)
            if (not attempt or attempt["epoch"] != epoch or not attempt["result"]
                    or attempt["result"]["category"] not in {"usable_answer", "partial_answer"}):
                raise cycle.CycleError("Only a recorded answer-producing attempt can support an answer")
            if attempt["request"]["provider"] == "mock":
                raise cycle.CycleError("A mock result cannot answer research")
        if answer_id not in item["answers"]:
            item["answers"][answer_id] = {**body, "answer_id": answer_id, "created_at": now()}
        if epoch == item["epoch"] and payload["status"] == "ready_for_review":
            item["status"] = "answered"
            item["claim"] = None
            for ticket in item["tickets"].values():
                if ticket["epoch"] == epoch and ticket["status"] not in {"resolved", "superseded"}:
                    ticket.update(status="resolved", answer_id=answer_id, resolved_at=now())
        return item["answers"][answer_id]
    return mutate(root, action)


def reopen(root, qid, actor, reason):
    text(reason, "reopen reason")

    def action(data):
        item = question(data, qid)
        item["history"].append({"event": "reopened", "actor": actor, "reason": reason,
                                "previous_epoch": item["epoch"], "at": now()})
        for ticket in item["tickets"].values():
            if ticket["status"] not in {"resolved", "superseded"}:
                ticket["status"] = "superseded"
        item.update(epoch=item["epoch"] + 1, status="needs_refresh", claim=None)
        return item
    return mutate(root, action)


def escalate(root, qid, actor, reason, note):
    if reason not in REASONS:
        raise cycle.CycleError("Unknown escalation reason")
    text(note, "ticket note")

    def action(data):
        item = question(data, qid)
        if item["status"] == "answered":
            raise cycle.CycleError("Question already answered; reopen explicitly if stale")
        tid = "TKT-" + cycle.digest([qid, item["epoch"], reason])[:20].upper()
        if tid not in item["tickets"]:
            item["tickets"][tid] = {"ticket_id": tid, "question_id": qid, "epoch": item["epoch"],
                "status": "open", "created_at": now(), "created_by": actor, "reason": reason, "notes": note}
        return item["tickets"][tid]
    return mutate(root, action)


def overview(root):
    with cycle.locked(root):
        return [{"question_id": q["question_id"], "question": q["question"], "status": q["status"],
                 "epoch": q["epoch"], "attempts": len(q["attempts"]), "answers": len(q["answers"]),
                 "open_tickets": sum(t["status"] == "open" for t in q["tickets"].values())}
                for q in load(root)["questions"].values()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    p = commands.add_parser("ask")
    p.add_argument("question")
    p.add_argument("--id")
    p.add_argument("--geography")
    p.add_argument("--actor", required=True)
    for name in ["answer", "reopen", "escalate", "recover"]:
        p = commands.add_parser(name)
        p.add_argument("question_id")
        p.add_argument("--actor", required=True)
        if name == "answer":
            p.add_argument("--file", type=Path, required=True)
            p.add_argument("--epoch", type=int, required=True)
        elif name == "recover":
            p.add_argument("--attempt", required=True)
            p.add_argument("--reason", required=True)
        else:
            p.add_argument("--reason", required=True)
            if name == "escalate":
                p.add_argument("--note", required=True)
    args = parser.parse_args()
    try:
        if args.command == "status":
            result = overview(args.root)
        elif args.command == "ask":
            result = ask(args.root, args.question, args.actor, qid=args.id, geography=args.geography)
        elif args.command == "answer":
            result = answer(args.root, args.question_id, args.actor, cycle.read_json(args.file), epoch=args.epoch)
        elif args.command == "reopen":
            result = reopen(args.root, args.question_id, args.actor, args.reason)
        elif args.command == "escalate":
            result = escalate(args.root, args.question_id, args.actor, args.reason, args.note)
        else:
            result = finish_attempt(args.root, args.question_id, args.attempt, "interrupted",
                                    details={"actor": args.actor, "reason": args.reason})
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (cycle.CycleError, OSError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
