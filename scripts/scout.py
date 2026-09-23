#!/usr/bin/env python3
"""One bounded public RSS/Atom retrieval. Metadata discovery, not causal research."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import cycle

MAX_BYTES = 1_000_000


def checked_url(url, hosts):
    parts = urllib.parse.urlsplit(url)
    if (parts.scheme != "https" or parts.hostname not in hosts or parts.port not in (None, 443)
            or parts.username or parts.password):
        raise cycle.CycleError("Sensor URL must use HTTPS on an explicitly approved public host")
    return url


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise cycle.CycleError("Sensor redirect needs review; no alternate URL was fetched")


def fetch(source):
    url = checked_url(source["url"], source["allowed_hosts"])
    request = urllib.request.Request(url, headers={"User-Agent": "Dis-Unity-Public-Scout/0.1",
                                                   "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"})
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=20) as response:
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise cycle.CycleError("Feed exceeded the bounded response size")
    return body


def parse_feed(body, source_url):
    if len(body) > MAX_BYTES:
        raise cycle.CycleError("Oversize feed")
    # Restrict decoding before checking declarations, including UTF-16 null-byte bypasses.
    try:
        xml = body.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise cycle.CycleError("Feed encoding requires a reviewed decoder") from exc
    if "\x00" in xml or "<!DOCTYPE" in xml.upper() or "<!ENTITY" in xml.upper():
        raise cycle.CycleError("Oversize feed or XML entity declarations are not accepted")
    try:
        tree = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise cycle.CycleError("Source did not return valid RSS/Atom XML") from exc
    local = lambda tag: tag.rsplit("}", 1)[-1]
    if local(tree.tag) not in {"rss", "feed", "RDF"}:
        raise cycle.CycleError("Source did not return a recognized feed")
    records = []
    for entry in tree.iter():
        if local(entry.tag) not in {"item", "entry"}:
            continue
        fields = {}
        for child in entry:
            tag = local(child.tag)
            if tag == "link":
                if child.get("rel", "alternate") == "alternate":
                    fields[tag] = child.get("href") or child.text or ""
            elif tag in {"title", "guid", "id", "pubDate", "published", "updated"}:
                fields[tag] = "".join(child.itertext()).strip()
        link = urllib.parse.urljoin(source_url, fields.get("link", ""))
        parts = urllib.parse.urlsplit(link)
        if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
            continue
        title = fields.get("title", "")[:240]
        published = fields.get("pubDate") or fields.get("published")
        updated = fields.get("updated")
        identifier = fields.get("guid") or fields.get("id") or link
        item = {"title": title, "url": link, "source_item_id": identifier[:1000],
                "publication_date_raw": published, "updated_date_raw": updated,
                "observation_period": "unknown; inspect the linked source",
                "access": "feed_metadata_only", "status": "unreviewed_lead"}
        item["fingerprint"] = cycle.digest(item)
        records.append(item)
        if len(records) >= 100:
            break
    return records


def run(root, source_id, fetcher=fetch):
    root = Path(root).resolve()
    cycle.check_name(source_id, "sensor ID")
    config = cycle.read_json(root / "config" / "sensors.json")
    if source_id not in config["sources"]:
        raise cycle.CycleError("Unknown sensor")
    source = config["sources"][source_id]
    path = root / "operations" / "sensors" / f"{source_id}.json"
    started_at = cycle.now()
    try:
        body = fetcher(source)
        items = parse_feed(body, source["url"])
        result = {"status": "retrieved", "started_at": started_at, "finished_at": cycle.now(),
                  "body_sha256": hashlib.sha256(body).hexdigest(), "items": items}
    except (OSError, ValueError, cycle.CycleError) as exc:
        result = {"status": "unavailable", "started_at": started_at, "finished_at": cycle.now(),
                  "error_type": type(exc).__name__, "http_status": getattr(exc, "code", None),
                  "note": "No interpretation or missing-data inference; retry only in a later bounded run."}
    with cycle.locked(root):
        prior = cycle.read_json(path) if path.exists() else {"sensor_id": source_id, "last_success": None}
        if "attempt_history" not in prior:
            prior["attempt_history"] = [{k: v for k, v in prior["latest_attempt"].items()
                                         if k not in {"items", "new_or_changed_items"}}] if "latest_attempt" in prior else []
        known = set(prior.get("seen_fingerprints", []))
        if result["status"] == "retrieved":
            result["new_or_changed_items"] = [i for i in result["items"] if i["fingerprint"] not in known]
            prior["seen_fingerprints"] = sorted(known | {i["fingerprint"] for i in result["items"]})
            prior["last_success"] = {k: v for k, v in result.items() if k != "new_or_changed_items"}
        prior.update(source_url=source["url"], latest_attempt=result,
                     interpretation="Discovery only; publication time is not event time. No canonical admission.")
        prior["attempt_history"].append({k: v for k, v in result.items() if k not in {"items", "new_or_changed_items"}})
        cycle.write_json(path, prior, replace=True)
    return {"sensor_id": source_id, "status": result["status"],
            "new_or_changed_items": len(result.get("new_or_changed_items", [])), "record": str(path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source", required=True)
    args = parser.parse_args()
    try:
        result = run(args.root, args.source)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "retrieved" else 2
    except (OSError, ValueError, cycle.CycleError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
