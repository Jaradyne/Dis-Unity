#!/usr/bin/env python3
"""Local, resumable research-cycle bookkeeping. No network or agent launcher.

Only commit writes canonical state. Reviews are explicit declarations by a named
reviewer, not proof of independence or verification of the underlying research.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

if os.name == "nt":
    import msvcrt
else:
    import fcntl

from validate_state import validate

CANONICAL = "Resilience_Cascade_STATE.json"
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
DECISIONS = {"passed", "accepted_with_limitations", "changes_requested"}


class CycleError(Exception):
    """A state conflict or incomplete operation; safe to report without traceback."""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def digest(value):
    """Semantic JSON hash: whitespace and dictionary order do not cause conflicts."""
    return hashlib.sha256(encoded(value)).hexdigest()


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"),
                          parse_constant=lambda x: (_ for _ in ()).throw(
                              ValueError(f"Non-finite JSON value: {x}")))
    except (OSError, ValueError) as exc:
        raise CycleError(f"Cannot read JSON {path}: {exc}") from exc


def check_name(value, field="identifier"):
    if not NAME.fullmatch(value) or value in {".", ".."}:
        raise CycleError(f"Invalid {field}: use letters, digits, dots, underscores or hyphens")
    return value


def validated(value):
    try:
        errors = validate(value)
        encoded(value)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise CycleError(f"Invalid state structure: {exc}") from exc
    if errors:
        raise CycleError("State validation failed:\n" + "\n".join(errors))
    return value


def fsync_dir(path):
    if os.name == "nt":
        # Python cannot portably open a directory handle for FlushFileBuffers.
        # File data are still flushed before the atomic rename.
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_bytes(path, payload, *, replace=False):
    """Durable same-directory write; immutable by default, atomic on replacement."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(payload)
            out.flush()
            os.fsync(out.fileno())
        if replace:
            os.replace(temporary, path)
        else:
            try:
                os.link(temporary, path)
            except FileExistsError:
                if path.read_bytes() != payload:
                    raise CycleError(f"Refusing to change immutable record: {path}")
        fsync_dir(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_json(path, value, *, replace=False):
    write_bytes(path, encoded(value), replace=replace)


@contextmanager
def locked(root):
    """All cooperating cycle processes serialize writes; OS releases lock on exit."""
    root = Path(root).resolve()
    if not (root / CANONICAL).is_file():
        raise CycleError(f"No canonical state at {root / CANONICAL}")
    with (root / ".cycle.lock").open("a+b") as handle:
        if os.name == "nt":
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield root
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def location(root, cycle_id):
    return root / "cycles" / check_name(cycle_id, "cycle ID")


def load_cycle(root, cycle_id):
    folder = location(root, cycle_id)
    manifest = read_json(folder / "manifest.json")
    baseline_path = folder / "baseline.json"
    baseline = validated(read_json(baseline_path))
    if (manifest["cycle_id"] != cycle_id or digest(baseline) != manifest["base_hash"]
            or hashlib.sha256(baseline_path.read_bytes()).hexdigest()
            != manifest["baseline_bytes_sha256"]):
        raise CycleError("Baseline or manifest changed; refusing to continue")
    return folder, manifest, baseline


def journal(folder):
    entries = []
    previous = None
    for number, path in enumerate(sorted((folder / "events").glob("*.json")), 1):
        event = read_json(path)
        claimed_hash = event.get("hash")
        body = {key: value for key, value in event.items() if key != "hash"}
        if (event.get("sequence") != number or event.get("previous_hash") != previous
                or digest(body) != claimed_hash):
            raise CycleError(f"Operational journal integrity failure: {path.name}")
        if path.name != f"{number:06d}-{event['event_id']}.json":
            raise CycleError(f"Unexpected journal filename: {path.name}")
        previous = claimed_hash
        entries.append(event)
    return entries


def append_event(folder, event_type, payload, key):
    entries = journal(folder)
    event_id = digest({"kind": event_type, "key": key})[:24]
    for event in entries:
        if event["event_id"] == event_id:
            if event["event_type"] != event_type or event["payload"] != payload:
                raise CycleError("Idempotency key was reused with a different payload")
            return event
    event = {"sequence": len(entries) + 1, "event_id": event_id,
             "event_type": event_type, "cycle_id": folder.name,
             "at": now(), "previous_hash": entries[-1]["hash"] if entries else None,
             "payload": payload}
    event["hash"] = digest(event)
    write_json(folder / "events" / f"{event['sequence']:06d}-{event_id}.json", event)
    return event


def field_changes(before, after, prefix=""):
    if before == after:
        return []
    if isinstance(before, dict) and isinstance(after, dict):
        changes = []
        for key in sorted(set(before) | set(after)):
            path = f"{prefix}.{key}" if prefix else key
            if key not in before or key not in after:
                changes.append(path)
            else:
                changes.extend(field_changes(before[key], after[key], path))
        return changes
    return [prefix or "(entire record)"]


def collections(value, prefix=""):
    """Find keyed record lists without pretending unkeyed lists have stable IDs."""
    found = {}
    if isinstance(value, dict):
        for key, item in value.items():
            found.update(collections(item, f"{prefix}.{key}" if prefix else key))
    elif isinstance(value, list) and value and all(
            isinstance(item, dict) and isinstance(item.get("id"), str) for item in value):
        found[prefix] = {item["id"]: item for item in value}
    return found


def audit(before, after):
    old, new = collections(before), collections(after)
    result = {}
    for key in sorted(set(old) | set(new)):
        left, right = old.get(key, {}), new.get(key, {})
        changed = {rid: field_changes(left[rid], right[rid])
                   for rid in sorted(set(left) & set(right)) if left[rid] != right[rid]}
        added, removed = sorted(set(right) - set(left)), sorted(set(left) - set(right))
        if added or removed or changed:
            result[key] = {"added": added, "removed": removed, "changed": changed}
    return {"changed_sections": sorted(key for key in set(before) | set(after)
                                        if before.get(key) != after.get(key)),
            "changed_paths": field_changes(before, after),
            "record_changes": result,
            "source_changes": result.get("SOURCE_LEDGER", {
                "added": [], "removed": [], "changed": {}}),
            "note": "Diff records changes, not their truth or importance. Unkeyed list changes are reported at list level."}


def ensure_open(folder):
    if (folder / "commit.json").exists():
        raise CycleError("Cycle is committed; begin a new cycle for further work")
    if (folder / "commit_intent.json").exists():
        raise CycleError("Commit is pending; resume commit before further changes")


def begin(root, cycle_id, cutoff=None):
    with locked(root) as root:
        folder = location(root, cycle_id)
        if (folder / "manifest.json").exists():
            folder, manifest, _ = load_cycle(root, cycle_id)
            if cutoff and cutoff != manifest["research_cutoff"]:
                raise CycleError("Existing cycle cutoff differs; use a new cycle")
        else:
            current = validated(read_json(root / CANONICAL))
            chosen_cutoff = cutoff or current["meta"]["research_cutoff"]
            try:
                datetime.strptime(chosen_cutoff, "%Y-%m-%d")
            except ValueError as exc:
                raise CycleError("Cutoff must be YYYY-MM-DD") from exc
            folder.mkdir(parents=True, exist_ok=True)
            baseline_path = folder / "baseline.json"
            if baseline_path.exists():
                baseline = validated(read_json(baseline_path))
                if digest(baseline) != digest(current):
                    raise CycleError("Precreated baseline differs from canonical state; not overwriting it")
            else:
                write_bytes(baseline_path, (root / CANONICAL).read_bytes())
            manifest = {"format_version": 1, "cycle_id": cycle_id, "created_at": now(),
                        "research_cutoff": chosen_cutoff, "base_hash": digest(current),
                        "baseline_bytes_sha256": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
                        "canonical_filename": CANONICAL,
                        "mode": "Local active-session records; no agents, network or schedule launched"}
            write_json(folder / "manifest.json", manifest)
        append_event(folder, "cycle_begun", manifest, "begin")
        return {"status": "ready", "cycle_id": cycle_id, "base_hash": manifest["base_hash"],
                "baseline": str(folder / "baseline.json")}


def submit(root, cycle_id, agent, path, phase="submitted"):
    check_name(agent, "agent name")
    if phase not in {"checkpoint", "submitted"}:
        raise CycleError("Phase must be checkpoint or submitted")
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise CycleError("Agent submission must be a JSON object")
    declared_cycle = payload.get("cycle_id", payload.get("cycle"))
    if declared_cycle and declared_cycle != cycle_id:
        raise CycleError("Submission declares a different cycle")
    if payload.get("agent") and payload["agent"] != agent:
        raise CycleError("Submission declares a different agent")
    payload_hash = digest(payload)
    with locked(root) as root:
        folder, manifest, _ = load_cycle(root, cycle_id)
        ensure_open(folder)
        submission_id = digest({"agent": agent, "phase": phase, "payload_hash": payload_hash})
        destination = folder / "submissions" / agent / f"{submission_id}.json"
        if destination.exists():
            record = read_json(destination)
        else:
            record = {"submission_id": submission_id, "cycle_id": cycle_id, "agent": agent,
                      "phase": phase, "at": now(), "base_hash": manifest["base_hash"],
                      "payload_hash": payload_hash, "payload": payload}
            write_json(destination, record)
        if digest(record["payload"]) != record["payload_hash"]:
            raise CycleError("Stored submission failed its content hash")
        append_event(folder, "agent_submission", {
            "agent": agent, "phase": phase, "submission_id": submission_id,
            "payload_hash": payload_hash}, submission_id)
        return {"status": "saved", "submission_id": submission_id, "snapshot": str(destination)}


def review(root, cycle_id, candidate_path, reviewer, role, decision, note,
           limitations=None, materiality="material", evidence=None):
    check_name(reviewer, "reviewer")
    limitations = limitations or []
    if role not in {"coordinator", "independent"} or decision not in DECISIONS:
        raise CycleError("Unknown reviewer role or decision")
    if materiality not in {"minor", "material"} or not note.strip():
        raise CycleError("Materiality and a substantive review note are required")
    if decision == "accepted_with_limitations" and not any(x.strip() for x in limitations):
        raise CycleError("Acceptance with limitations requires at least one named limitation")
    candidate = validated(read_json(candidate_path))
    with locked(root) as root:
        folder, manifest, baseline = load_cycle(root, cycle_id)
        ensure_open(folder)
        candidate_hash = digest(candidate)
        if candidate["meta"]["cycle_id"] != cycle_id:
            raise CycleError("Candidate meta.cycle_id must match the open cycle")
        if candidate["meta"]["research_cutoff"] != manifest["research_cutoff"]:
            raise CycleError("Candidate cutoff must match the open cycle")
        details = {"cycle_id": cycle_id, "base_hash": manifest["base_hash"],
                   "candidate_hash": candidate_hash, "reviewer": reviewer, "role": role,
                   "decision": decision, "materiality": materiality, "note": note.strip(),
                   "limitations": limitations, "evidence": evidence or []}
        review_id = digest(details)
        destination = folder / "reviews" / f"{review_id}.json"
        snapshot = folder / "candidates" / f"{candidate_hash}.json"
        write_json(snapshot, candidate)
        if destination.exists():
            record = read_json(destination)
        else:
            review_status = ("independent_pass" if role == "independent" else "coordinator_pass") \
                if decision == "passed" else f"{role}_{decision}"
            record = {**details, "review_id": review_id, "at": now(),
                      "review_status": review_status, "audit": audit(baseline, candidate),
                      "independence_note": "Role is a reviewer declaration, not authentication or automatic evidence verification."}
            write_json(destination, record)
        append_event(folder, "candidate_reviewed", {
            "review_id": review_id, "candidate_hash": candidate_hash,
            "review_status": record["review_status"], "materiality": materiality}, review_id)
        return {"status": "recorded", "review_id": review_id,
                "review_status": record["review_status"], "candidate_hash": candidate_hash,
                "audit": record["audit"]}


def latest_review(folder, candidate_hash):
    records = [read_json(path) for path in (folder / "reviews").glob("*.json")]
    matching = [record for record in records if record["candidate_hash"] == candidate_hash]
    if not matching:
        raise CycleError("Commit requires an explicit review of this exact candidate hash")
    return sorted(matching, key=lambda record: (record["at"], record["review_id"]))[-1]


def commit(root, cycle_id, candidate_path=None):
    with locked(root) as root:
        folder, manifest, baseline = load_cycle(root, cycle_id)
        receipt_path, intent_path = folder / "commit.json", folder / "commit_intent.json"
        current = validated(read_json(root / CANONICAL))
        current_hash = digest(current)
        candidate = validated(read_json(candidate_path)) if candidate_path else None
        if receipt_path.exists():
            receipt = read_json(receipt_path)
            if candidate is not None and digest(candidate) != receipt["candidate_hash"]:
                raise CycleError("Cycle already committed a different candidate")
            append_event(folder, "commit_applied", receipt, "commit")
            return {"status": "already_committed", "receipt": receipt,
                    "canonical_matches_commit": current_hash == receipt["candidate_hash"]}
        if intent_path.exists():
            intent = read_json(intent_path)
            snapshot = read_json(folder / "candidates" / f"{intent['candidate_hash']}.json")
            if candidate is not None and digest(candidate) != intent["candidate_hash"]:
                raise CycleError("A different candidate has a pending commit; resume it first")
            candidate = validated(snapshot)
            if digest(candidate) != intent["candidate_hash"] or intent["base_hash"] != manifest["base_hash"]:
                raise CycleError("Pending commit snapshot or base hash changed")
            recovered = True
        else:
            if candidate is None:
                raise CycleError("Initial commit requires --candidate; resume may omit it")
            candidate_hash = digest(candidate)
            if current_hash != manifest["base_hash"]:
                raise CycleError("Lost-update protection: canonical state changed after this cycle began; rebase into a new cycle")
            decision = latest_review(folder, candidate_hash)
            if decision["decision"] == "changes_requested":
                raise CycleError("Latest review requests changes; candidate is not approved")
            if decision["base_hash"] != manifest["base_hash"]:
                raise CycleError("Review was made against a different baseline")
            if (candidate["meta"]["cycle_id"] != cycle_id
                    or candidate["meta"]["research_cutoff"] != manifest["research_cutoff"]):
                raise CycleError("Candidate cycle or cutoff differs from its reviewed cycle")
            write_json(folder / "candidates" / f"{candidate_hash}.json", candidate)
            intent = {"cycle_id": cycle_id, "prepared_at": now(),
                      "base_hash": manifest["base_hash"], "candidate_hash": candidate_hash,
                      "review_id": decision["review_id"], "review_status": decision["review_status"],
                      "reviewer": decision["reviewer"], "materiality": decision["materiality"],
                      "limitations": decision["limitations"], "audit": audit(baseline, candidate)}
            write_json(intent_path, intent)
            recovered = False
        if current_hash not in {intent["base_hash"], intent["candidate_hash"]}:
            raise CycleError("Lost-update protection: pending commit conflicts with current state")
        append_event(folder, "commit_prepared", intent, "commit")
        if current_hash != intent["candidate_hash"]:
            write_json(root / CANONICAL, candidate, replace=True)
        receipt = {**intent, "completed_at": now()}
        write_json(receipt_path, receipt)
        append_event(folder, "commit_applied", receipt, "commit")
        return {"status": "recovered" if recovered else "committed", "receipt": receipt,
                "canonical_matches_commit": True}


def status(root, cycle_id):
    with locked(root) as root:
        folder, manifest, _ = load_cycle(root, cycle_id)
        events = journal(folder)
        current_hash = digest(validated(read_json(root / CANONICAL)))
        submissions = []
        for path in (folder / "submissions").glob("*/*.json"):
            record = read_json(path)
            if digest(record["payload"]) != record["payload_hash"]:
                raise CycleError(f"Submission hash mismatch: {path}")
            submissions.append({key: record[key] for key in (
                "agent", "phase", "at", "submission_id", "payload_hash")})
        submissions.sort(key=lambda item: item["at"])
        latest = {item["agent"]: item for item in submissions}
        receipt = read_json(folder / "commit.json") if (folder / "commit.json").exists() else None
        intent = read_json(folder / "commit_intent.json") if (folder / "commit_intent.json").exists() else None
        review_records = [read_json(path) for path in (folder / "reviews").glob("*.json")]
        return {"cycle_id": cycle_id, "status": "committed" if receipt else
                "recovery_required" if intent else "open", "research_cutoff": manifest["research_cutoff"],
                "base_hash": manifest["base_hash"], "current_hash": current_hash,
                "canonical_changed_from_baseline": current_hash != manifest["base_hash"],
                "latest_agent_snapshots": latest, "submission_count": len(submissions),
                "reviews": [{key: item[key] for key in ("review_id", "candidate_hash", "reviewer",
                            "review_status", "materiality", "limitations")}
                            for item in sorted(review_records, key=lambda item: item["at"])],
                "commit": receipt, "pending_commit": intent if not receipt else None,
                "journal_entries": len(events),
                "mode": "Local records only; no background agents, network or schedule"}


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    commands = result.add_subparsers(dest="command", required=True)
    for name in ["begin", "status", "submit", "review", "commit"]:
        command = commands.add_parser(name)
        command.add_argument("cycle_id")
        if name == "begin":
            command.add_argument("--cutoff")
        if name == "submit":
            command.add_argument("--agent", required=True)
            command.add_argument("--file", dest="path", type=Path, required=True)
            command.add_argument("--phase", choices=["checkpoint", "submitted"], default="submitted")
        if name == "review":
            command.add_argument("--candidate", dest="candidate_path", type=Path, required=True)
            command.add_argument("--reviewer", required=True)
            command.add_argument("--role", choices=["coordinator", "independent"], required=True)
            command.add_argument("--decision", choices=sorted(DECISIONS), required=True)
            command.add_argument("--materiality", choices=["minor", "material"], default="material")
            command.add_argument("--note", required=True)
            command.add_argument("--limitation", dest="limitations", action="append", default=[])
            command.add_argument("--evidence", action="append", default=[])
        if name == "commit":
            command.add_argument("--candidate", dest="candidate_path", type=Path)
    return result


def main():
    arguments = vars(parser().parse_args())
    command = arguments.pop("command")
    try:
        output = globals()[command](**arguments)
    except (CycleError, OSError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
