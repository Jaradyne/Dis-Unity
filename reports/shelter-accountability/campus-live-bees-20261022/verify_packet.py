"""Offline byte/lineage verification of this research packet; no evidence admission."""
import base64
import gzip
import hashlib
import json
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    packet = Path(__file__).resolve().parent
    root = packet.parents[2]
    manifest = json.loads((packet / "PUBLICATION.json").read_text())
    for entry in manifest["published_files"]:
        path = root / entry["path"]
        data = path.read_bytes()
        if len(data) != entry["bytes"] or digest(data) != entry["sha256"]:
            raise ValueError(f"Published byte mismatch: {entry['path']}")
        if path.suffix == ".json":
            json.loads(data)

    for path, expected in manifest["preserved_inputs"].items():
        if digest((root / path).read_bytes()) != expected:
            raise ValueError(f"Preserved input mismatch: {path}")

    dispatch = json.loads((packet / "DISPATCH.json").read_text())
    for task in dispatch["tasks"]:
        if digest((root / task["prompt_path"]).read_bytes()) != task["prompt_sha256"]:
            raise ValueError(f"Prompt mismatch: {task['task_name']}")
        for path, expected in task["role_sha256"].items():
            if digest((root / path).read_bytes()) != expected:
                raise ValueError(f"Inherited role mismatch: {path}")
        name = task["task_name"].rsplit("/", 1)[1]
        if (packet / "returns" / (name + ".json")).read_bytes() != (
            root / "cycles/RC-009/inbox" / (name + "-final.json")
        ).read_bytes():
            raise ValueError(f"Return/inbox mismatch: {name}")

    archive = json.loads((packet / "receipts/manifest.json").read_text())
    compressed = (root / archive["archive_path"]).read_bytes()
    original = gzip.decompress(compressed)
    if digest(compressed) != archive["archive_sha256"] or digest(original) != archive["original_sha256"]:
        raise ValueError("Budget HTTP archive mismatch")
    receipt = json.loads(original)
    body = receipt["response"]["body"]
    pdf = base64.b64decode(body["content"], validate=True)
    if (receipt["response"]["http_status"] != 200 or not body["complete"]
            or digest(pdf) != archive["source_body_sha256"]
            or digest(pdf) != body["saved_sha256"]
            or len(pdf) != archive["source_body_bytes"]):
        raise ValueError("Budget origin-body mismatch")

    for omission in manifest["excluded_originals"]:
        replacement = root / omission["publication_path"]
        if digest(replacement.read_bytes()) != omission["publication_sha256"]:
            raise ValueError(f"Publication replacement mismatch: {replacement}")

    print(json.dumps({
        "status": "pass",
        "published_files_verified": len(manifest["published_files"]),
        "attributed_work_session_tasks": len(dispatch["tasks"]),
        "canonical_and_original_case_unchanged": True,
        "budget_receipt_losslessly_reconstructed": True,
        "budget_source_body_bytes": len(pdf),
        "excluded_incidental_material_reconstructed": False,
        "network_requests": 0,
        "canonical_admission": False,
        "meaning": "Byte and recorded-lineage integrity; not empirical corroboration or a new Garden assessment."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
