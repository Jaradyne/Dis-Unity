#!/usr/bin/env python3
"""Build a portable Meaning Tower encounter from a reviewed, validated packet."""
import argparse
import json
from pathlib import Path

import cycle
import meaning_boss


DEFAULT_PACKET = "examples/meaning-tower/parallax-trucks-2026-09-25.json"


def build(root, packet_path=None, output=None):
    root = Path(root)
    packet = cycle.read_json(packet_path or root / DEFAULT_PACKET)
    meaning_boss.validate_packet(packet, cycle.read_json(root / "operations/questions.json"))
    series = cycle.read_json(root / "config/meaning-tower-series.json")
    voice = cycle.read_json(root / "config/governor-voice.json")
    data = {"packet": packet, "packet_sha256": cycle.digest(packet),
            "series": series, "voice": voice, "approved_powers": []}
    folder = root / "web/meaning-tower"
    html = (folder / "template.html").read_text()
    replacements = {
        "__TOWER_DATA__": json.dumps(data, ensure_ascii=False, sort_keys=True).replace("<", "\\u003c"),
        "__BOSS_CSS__": (folder / "boss.css").read_text(),
        "__BOSS_JS__": (folder / "boss.js").read_text(),
    }
    for token, value in replacements.items():
        if html.count(token) != 1:
            raise cycle.CycleError("Expected exactly one template token: " + token)
        html = html.replace(token, value)
    destination = Path(output) if output else folder / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html)
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    print(build(args.root, args.packet, args.output))
