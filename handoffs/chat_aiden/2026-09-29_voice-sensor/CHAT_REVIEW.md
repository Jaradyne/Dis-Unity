# Chat review of the Voice design

## What is already strong

The Voice proposal fits the current architecture unusually well.

1. **Do not spend inference merely detecting change.** A deterministic process should answer "did the permitted source change?" before any model call.
2. **Preserve lineage.** Multiple summaries of one upstream source remain one evidentiary lineage.
3. **Keep speculation separate from verification.** Sensors report observations and changes; they do not promote claims.
4. **Prefer the least invasive official interface.** API/dataset → RSS/Atom/iCal → official email alert → other explicitly permitted feed → human review is a good default preference order.
5. **Temporal validity deserves first-class treatment.** A facility location and today's spare capacity should not decay on the same schedule.
6. **Paid data should follow a demonstrated blind spot.** Build the darkness map first, then spend only where a paid source closes a real observational gap.

## What needs sharpening before implementation

### 1. Dedupe is not enough; preserve change history

A stable item can later be corrected, amended, superseded, or withdrawn. The sensor should distinguish at least:

- `new`
- `changed`
- `unchanged`
- `corrected_or_retracted` when the source exposes that meaning
- `gone_or_unobservable` only when the interface makes that distinction safe

Identity and content are separate. Prefer a source's stable item/event ID where available; otherwise use a canonical URL or documented key. Content hashes detect revisions but should not become the identity itself.

### 2. "No change" should have a receipt without storing needless duplicate bodies

If a source supports ETag / Last-Modified / cursor semantics, use conditional requests. A 304 or equivalent can be retained as a lightweight poll receipt with:

- source/endpoint identity;
- checked_at;
- HTTP/result status;
- ETag/Last-Modified/cursor if available;
- prior item-set/content hash;
- bytes received;
- outcome.

Do not copy the same full feed body forever just to prove it was unchanged.

### 3. "Wake a Bee" should initially mean **queue work**, not automatically spend cognition

For the first proof, a relevant new item should emit a bounded Garden/threshold handoff packet. It should **not** automatically make a model call.

That keeps the sensor proof independent of provider capacity and lets the existing Garden candidate/permission machinery decide whether Chat, Digest, a deterministic path, or an approved model should handle it.

### 4. Temporal validity should be a profile, not one universal TTL

Suggested fields:

- `event_at` / `effective_at` when supplied;
- `published_at`;
- `updated_at`;
- `retrieved_at`;
- `last_verified_at`;
- `expected_update_cadence` (if known);
- `freshness_class` or `freshness_hint`;
- `stale_after` only when there is a defensible basis;
- `observability` (direct / delayed / partial / inferred);
- `staleness_consequence` (what goes wrong if this is old).

Do not manufacture precision when a source has irregular cadence.

### 5. Source registry should separate a source family from one endpoint

A useful registry record should eventually distinguish:

- source family / institution;
- endpoint/feed;
- source type (API/RSS/Atom/iCal/email/manual);
- officiality / publisher;
- permission/terms basis and `checked_at`;
- allowed host(s);
- authentication needs;
- expected cadence / rate limits;
- stable-ID strategy;
- correction/update semantics;
- language/geographic scope;
- source-family lineage key;
- adapter name/version;
- known limitations.

This prevents one URL from silently standing in for an institution.

### 6. Email should wait

Dedicated-inbox ingestion is reasonable, but it brings credentials, attachments, duplicate alerts, threading, and sender-authentication concerns. It should be a later adapter after one public no-secret interface works cleanly.

### 7. The first proof should minimize variables

The Voice handoff used Ship & Bunker RSS as an example. The architecture is good; the specific **first** source is not sacred.

Chat's preference is:

- first prove sensor state/dedupe/provenance on an already permitted official machine-readable source the repo knows (NWS or EIA are candidates);
- then add an RSS/Atom adapter such as Ship & Bunker **after** verifying its current official feed and automation terms.

That way the first failure, if any, is in our code rather than licensing/endpoint ambiguity.

## Non-goals for this build

Do not:
- add every source family from the Voice list;
- add email credentials;
- buy data;
- auto-wake paid or first-use model paths;
- turn temporal validity into automatic evidence deletion;
- infer source independence from different URLs;
- create a general scheduler/crawler platform before one sensor works.

The goal is one small sensor that proves the nervous system can notice without thinking.
