#!/usr/bin/env python3
"""Deterministic Meaning Tower packets and Governor deliveries; no execution or writes."""
import copy
from datetime import date, datetime
import ipaddress
import re
from urllib.parse import urlsplit

import cycle
import garden

PACKET_VERSION = "meaning-tower-boss-packet-1"
RESULT_VERSION = "meaning-tower-boss-result-1"
QUESTION = "Q-MEANING-TRANSLATION-BOSS"
ROUTE = ("INIT:RESID-0007", "PYGENT:PARALLAX-0001", "INIT:RETURN-0010")
EVIDENCE_STATUSES = {"source_statement", "inference", "question", "unknown"}


def record(value, required, optional=()):
    garden.require(isinstance(value, dict), "Expected a named record")
    missing = set(required) - value.keys()
    unknown = value.keys() - set(required) - set(optional)
    garden.require(not missing and not unknown,
                   "Missing or unknown fields: " + ", ".join(sorted(missing | unknown)))


def bounded_json(value, maximum):
    try:
        size = len(cycle.encoded(value))
    except (TypeError, ValueError) as exc:
        raise cycle.CycleError("Supply a finite JSON value") from exc
    garden.require(size <= maximum, f"Keep this record at or below {maximum} bytes")


def words(value, maximum=1600):
    garden.require(isinstance(value, str) and value.strip() and len(value) <= maximum,
                   f"Expected nonempty text at or below {maximum} characters")


def sequence(value, minimum=0, maximum=12):
    garden.require(isinstance(value, list) and minimum <= len(value) <= maximum,
                   f"Expected a list with {minimum}..{maximum} items")


def text_list(value, minimum=0, maximum=12):
    sequence(value, minimum, maximum)
    for item in value:
        words(item)


def instant(value):
    words(value, 40)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise cycle.CycleError("Expected an ISO timestamp with a timezone") from exc
    garden.require(parsed.tzinfo is not None and parsed.utcoffset() is not None,
                   "Timestamp needs a timezone")
    return parsed


def calendar_day(value):
    if value is None:
        return
    garden.require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value),
                   "Use an ISO calendar day or null for an unknown date")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise cycle.CycleError("Invalid calendar day") from exc


def public_url(value):
    words(value, 2048)
    try:
        url = urlsplit(value)
        hostname = url.hostname or ""
        port = url.port
    except ValueError as exc:
        raise cycle.CycleError("Invalid source URL") from exc
    garden.require(url.scheme == "https" and "." in hostname and url.username is None
                   and url.password is None and port in (None, 443)
                   and not any(char.isspace() for char in value)
                   and not hostname.endswith((".localhost", ".local", ".internal")),
                   "Sources need public HTTPS URLs without credentials")
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        return
    raise cycle.CycleError("Use the public source's named HTTPS host, not an IP address")


def actor(value, model=False):
    record(value, ("name", "runtime", "model") if model else ("name", "runtime"))
    for item in value.values():
        words(item, 160)


def refs(value, source_ids, minimum=0):
    sequence(value, minimum, 3)
    garden.require(all(isinstance(item, str) and item in source_ids for item in value)
                   and len(value) == len(set(value)), "Source references must be unique known IDs")


def validate_packet(packet, registry):
    """Validate structure/provenance, not the truth or official status of source text."""
    bounded_json(packet, 98304)
    record(packet, ("schema_version", "packet_id", "boss_id", "packet_status", "question_id", "epoch",
                    "title", "created_at", "actor", "source_ledger", "comparison", "cross", "rounds"),
           ("power_candidate",))
    garden.require(packet["schema_version"] == PACKET_VERSION and packet["boss_id"] == "THE-UNRESOLVED"
                   and packet["packet_status"] == "evidence_backed", "Expected an evidence-backed Unresolved packet")
    garden.identifier(packet["question_id"])
    question = registry.get("questions", {}).get(packet["question_id"])
    garden.require(packet["question_id"] == QUESTION and isinstance(question, dict)
                   and type(packet["epoch"]) is int and packet["epoch"] == question.get("epoch"),
                   "Use the existing Translation Boss Question and its current epoch")
    seen = set()

    def unique(value):
        garden.identifier(value)
        garden.require(value not in seen, "All packet record IDs must be unique")
        seen.add(value)

    unique(packet["packet_id"])
    words(packet["title"], 240)
    instant(packet["created_at"])
    actor(packet["actor"], model=True)
    sequence(packet["source_ledger"], 2, 3)
    source_ids = set()
    urls = set()
    for source in packet["source_ledger"]:
        record(source, ("source_id", "url", "title", "language", "publication_date",
                        "observation_date", "retrieved_at", "access_limitations"))
        unique(source["source_id"])
        source_ids.add(source["source_id"])
        public_url(source["url"])
        garden.require(source["url"] not in urls, "Repeated URLs are not separate sources")
        urls.add(source["url"])
        words(source["title"], 400)
        words(source["language"], 80)
        calendar_day(source["publication_date"])
        calendar_day(source["observation_date"])
        instant(source["retrieved_at"])
        text_list(source["access_limitations"])
        garden.require(all(source[key] is not None for key in ("publication_date", "observation_date"))
                       or source["access_limitations"], "Explain unknown source dates in access limitations")
    comparison = packet["comparison"]
    record(comparison, ("kind", "summary", "ordinary_explanations", "limitations"))
    garden.require(comparison["kind"] == "official_notice_and_summary", "Expected a matched notice and summary comparison")
    words(comparison["summary"])
    text_list(comparison["ordinary_explanations"], minimum=1)
    text_list(comparison["limitations"], minimum=1)
    cross = packet["cross"]
    record(cross, ("inherited", "independent", "bridge"))
    refs(cross["inherited"], source_ids, minimum=1)
    refs(cross["independent"], source_ids)
    text_list(cross["bridge"])
    sequence(packet["rounds"], 1, 4)
    kinds = []
    for round_record in packet["rounds"]:
        record(round_record, ("id", "kind", "title", "prompt", "context", "originals", "pieces"))
        unique(round_record["id"])
        garden.require(isinstance(round_record["kind"], str)
                       and round_record["kind"] in {"control", "residual", "question"}, "Invalid encounter round kind")
        kinds.append(round_record["kind"])
        words(round_record["title"], 240)
        for key in ("prompt", "context"):
            words(round_record[key])
        sequence(round_record["originals"], 1, 3)
        original_refs = []
        for original in round_record["originals"]:
            record(original, ("source_id", "text", "english_pivot"))
            original_refs.append(original["source_id"])
            words(original["text"])
            words(original["english_pivot"])
        refs(original_refs, source_ids, minimum=1)
        sequence(round_record["pieces"], 2, 4)
        for piece in round_record["pieces"]:
            record(piece, ("id", "text", "note", "evidence_status", "source_refs"))
            unique(piece["id"])
            words(piece["text"], 400)
            words(piece["note"])
            garden.require(isinstance(piece["evidence_status"], str)
                           and piece["evidence_status"] in EVIDENCE_STATUSES, "Unrecognized evidence status")
            refs(piece["source_refs"], source_ids, minimum=1 if piece["evidence_status"] == "source_statement" else 0)
    garden.require("control" in kinds and kinds.count("residual") <= 3,
                   "Include a control and at most three residuals")
    power = packet.get("power_candidate")
    if power is not None:
        record(power, ("id", "text", "canonical_status"))
        unique(power["id"])
        garden.require(power["id"] == "PECULIARITY_SENSE" and power["canonical_status"] == "proposed",
                       "Only the proposed Peculiarity Sense candidate is registered")
        words(power["text"])
    return copy.deepcopy(packet)


def validate_result(packet, result, registry):
    """A validated browser report remains a client report, not verified human identity."""
    validate_packet(packet, registry)
    bounded_json(result, 8192)
    record(result, ("schema_version", "packet_id", "packet_sha256", "play_id", "actor", "completed_at",
                    "completion_status", "choices", "power_decision", "evidence_changed"))
    garden.require(result["schema_version"] == RESULT_VERSION and result["packet_id"] == packet["packet_id"]
                   and result["packet_sha256"] == cycle.digest(packet), "Result must bind the original packet and its hash")
    garden.identifier(result["play_id"])
    actor(result["actor"])
    instant(result["completed_at"])
    garden.require(result["completion_status"] == "completed" and result["power_decision"] == "pending_review"
                   and result["evidence_changed"] is False, "Play completion cannot award powers or change evidence")
    sequence(result["choices"], len(packet["rounds"]), len(packet["rounds"]))
    for choice, round_record in zip(result["choices"], packet["rounds"]):
        record(choice, ("round_id", "preserved_id", "held_ms", "input_method"))
        garden.require(choice["round_id"] == round_record["id"]
                       and isinstance(choice["preserved_id"], str)
                       and choice["preserved_id"] in {piece["id"] for piece in round_record["pieces"]},
                       "Supply one valid choice for each round in packet order")
        garden.require(type(choice["held_ms"]) is int and 1900 <= choice["held_ms"] <= 600000,
                       "The reported hold must be 1900..600000 milliseconds")
        garden.require(isinstance(choice["input_method"], str)
                       and choice["input_method"] in {"pointer", "keyboard", "assist"}, "Unknown input method")
    return copy.deepcopy(result)


def make_delivery(packet, result, registry, garden_config):
    """Always deliver a valid completed play, after the explicit no-power step."""
    validated = validate_result(packet, result, registry)
    garden.require(all(garden.resolve(garden_config, address)["status"] == "resolved" for address in ROUTE),
                   "Register the complete stable Parallax route before delivery")
    selections = []
    for round_record, choice in zip(packet["rounds"], validated["choices"]):
        preserved = next(piece for piece in round_record["pieces"] if piece["id"] == choice["preserved_id"])
        sunk = [{**copy.deepcopy(piece), "attention_status": "not_selected_not_false"}
                for piece in round_record["pieces"] if piece["id"] != choice["preserved_id"]]
        selections.append({"round_id": round_record["id"], "kind": round_record["kind"],
                           "title": round_record["title"], "prompt": round_record["prompt"],
                           "context": round_record["context"], "originals": copy.deepcopy(round_record["originals"]),
                           "preserved": copy.deepcopy(preserved), "sunk": sunk})
    return {"schema_version": "governor-boss-input-1", "kind": "governor_boss_input",
            "delivery_id": "BOSS-" + cycle.digest(validated)[:24],
            "packet_id": packet["packet_id"], "packet_sha256": cycle.digest(packet),
            "play_id": validated["play_id"], "result_sha256": cycle.digest(validated),
            "question_id": packet["question_id"], "epoch": packet["epoch"],
            "actor": copy.deepcopy(validated["actor"]), "completed_at": validated["completed_at"],
            "input_origin": "client_report", "human_identity_verified": False,
            "validation_scope": "Structure, packet binding and choices; source truth and human identity are not verified by this validator.",
            "route": {"from": ROUTE[1], "to": ROUTE[2], "status": "resolved", "automatic_execution": False},
            "event_order": ["attention_selection", "power_application", "governor_delivery"],
            "applied_powers": [], "power_status": "no_canonical_powers",
            "power_candidate": copy.deepcopy(packet.get("power_candidate")),
            "selection_before_powers": copy.deepcopy(validated["choices"]),
            "selection_after_powers": copy.deepcopy(validated["choices"]),
            "rounds": selections, "source_ledger": copy.deepcopy(packet["source_ledger"]),
            "comparison": copy.deepcopy(packet["comparison"]), "cross": copy.deepcopy(packet["cross"]),
            "evidence_changed": False, "canonical_admission": False,
            "evidence_treatment": "Preserved means selected for attention. Sunk means unselected, never false. Every original evidence status remains unchanged."}
