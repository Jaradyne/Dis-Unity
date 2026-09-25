#!/usr/bin/env python3
"""Prepare a reflection review for any thought partner; no provider call or automatic action."""
from pathlib import Path
import argparse
import json
import sys

import cycle
import daily_scroll
import garden
import meaning_boss
import reflections


def prepare(root, limit=50, offset=0, imagination=None, boss_packet=None, boss_result=None):
    attention = reflections.attend(root, limit, offset)
    if imagination is not None:
        if (not isinstance(imagination, dict) or imagination.get('kind') != 'chair_imagination'
                or imagination.get('evidence') is not False or len(cycle.encoded(imagination)) > 24000):
            raise cycle.CycleError('Governor imagination input must be a bounded non-evidence Chair response')
        expected = garden.attach_imagination(imagination.get('chair', {}), imagination.get('response'),
                                             imagination.get('actor'), imagination.get('destination'))
        if imagination != expected:
            raise cycle.CycleError('Chair input differs from its preserved sequence and response envelope')
    boss_input = None
    if boss_packet is not None or boss_result is not None:
        if boss_packet is None or boss_result is None:
            raise cycle.CycleError('Supply both the Boss Packet and its completed result')
        boss_input = meaning_boss.make_delivery(
            boss_packet, boss_result, cycle.read_json(Path(root) / 'operations/questions.json'),
            cycle.read_json(Path(root) / 'config/garden.json'))
    def optional_config(name):
        path = Path(root) / 'config' / name
        return cycle.read_json(path) if path.exists() else None
    return {
        "kind": "governor_reflection_review", "prepared_at": cycle.now(),
        "role": cycle.read_json(Path(root) / "agents/governor.json"),
        "attention": attention,
        "inputs": {"daily_scroll": daily_scroll.snapshot(root), "chair_imagination": imagination,
                   "boss_encounter": boss_input, "weekly_series": optional_config('meaning-tower-series.json'),
                   "voice": optional_config('governor-voice.json')},
        "input_treatment": "Daily Scroll is a projection of dated records. Chair sequence and AI interpretation are imagination, never evidence. Boss choices preserve attention, not truth; all unselected pieces retain their evidence status. A completed encounter arrives even without powers. Read as context; choose a response or silence. No followup executes automatically.",
        "request": "Consider these contributions and choose your own response. Share brief conclusions and lessons, not private reasoning. When voice context is present, a short Tamarian-style shared-story allusion may accompany a plain-language meaning; source claims and uncertainty stay explicit. You may propose the weekly order and final boss from actual available encounters, explaining their thematic fit; Jared may rearrange them. Collaborate with Chat Aiden, Work Aiden, the human, or other thought partners as useful. Record a response with scripts/reflections.py respond. Followups are recorded invitations, not sent messages or executed tasks.",
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
    p.add_argument("--imagination", type=Path, help="Optional saved Chair + attributed AI response; non-evidence")
    p.add_argument("--boss-packet", type=Path, help="Reviewed Boss Packet used for the encounter")
    p.add_argument("--boss-result", type=Path, help="Completed browser result, validated against the packet")
    p.add_argument("--boss-bundle", type=Path, help="Exported browser bundle; its claimed Governor input is rederived")
    p.add_argument("--output", type=Path, help="Optional immutable review packet under operations/")
    args = p.parse_args()
    try:
        root = args.root.resolve()
        imagination = cycle.read_json(args.imagination) if args.imagination else None
        boss_packet = cycle.read_json(args.boss_packet) if args.boss_packet else None
        boss_result = cycle.read_json(args.boss_result) if args.boss_result else None
        if args.boss_bundle:
            if args.boss_packet or args.boss_result:
                raise cycle.CycleError('Use a bundle or the separate packet/result paths')
            if args.boss_bundle.stat().st_size > 300000:
                raise cycle.CycleError('Boss bundle exceeds its bounded size')
            bundle = cycle.read_json(args.boss_bundle)
            if not isinstance(bundle, dict) or not {'packet', 'result'} <= bundle.keys():
                raise cycle.CycleError('Boss bundle needs packet and result')
            boss_packet, boss_result = bundle['packet'], bundle['result']
        result = prepare(root, args.limit, args.offset, imagination, boss_packet, boss_result)
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
