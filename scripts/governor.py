#!/usr/bin/env python3
"""Prepare a reflection review for any thought partner; no provider call or automatic action."""
from pathlib import Path
import argparse
import json
import sys

import cycle
import reflections


def prepare(root, limit=50, offset=0):
    attention = reflections.attend(root, limit, offset)
    return {
        "kind": "governor_reflection_review", "prepared_at": cycle.now(),
        "role": cycle.read_json(Path(root) / "agents/governor.json"),
        "attention": attention,
        "request": "Consider these contributions and choose your own response. Share brief conclusions and lessons, not private reasoning. Collaborate with Chat Aiden, Work Aiden, the human, or other thought partners as useful. Record a response with scripts/reflections.py respond. Followups are recorded invitations, not sent messages or executed tasks.",
        "response_fields": {"review_id": "unique ID", "actor": "actual reviewer/runtime",
            "reflection_ids": "IDs actually considered", "disposition": "your chosen response",
            "summary": "what you decided and why, briefly", "keep_open": "boolean",
            "followups": [{"recipient": "thought partner", "question": "bounded question or proposal"}],
            "self_reflection": "optional brief observation about your review"},
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--output", type=Path, help="Optional immutable review packet under operations/")
    args = p.parse_args()
    try:
        root = args.root.resolve()
        result = prepare(root, args.limit, args.offset)
        if args.output:
            path = args.output.resolve()
            if root in path.parents and path.relative_to(root).parts[0] != "operations":
                raise cycle.CycleError("Repository review packets must stay under operations/")
            cycle.write_json(path, result)
            print(json.dumps({"path": str(path), "pending_count": result["attention"]["pending_count"]}))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (cycle.CycleError, OSError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
