#!/usr/bin/env python3
"""Provider-neutral Dis-Unity worker.

This first worker is intentionally small:
- reads a declarative JSON role plus selected repository context;
- invokes either a deterministic mock provider or Gemini over HTTPS;
- writes one attributed inbox-compatible JSON checkpoint;
- can optionally submit that checkpoint through scripts/cycle.py.

It does not browse, send mail, mutate canonical state, spawn child workers, or
commit to Git. Those are later capabilities that should be added explicitly.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request


DEFAULT_CONTEXT = [
    "README.md",
    "COMMON_STATE.md",
    "AGENTS.md",
    "agents/ALCHEMICAL_MAILBOX.md",
    "state/QUESTIONS_TO_WATCH.md",
]


class WorkerError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise WorkerError(f"Cannot read JSON {path}: {exc}") from exc


def read_context(root, paths, max_chars):
    chunks = []
    used = 0
    for name in paths:
        path = root / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        remaining = max_chars - used
        if remaining <= 0:
            break
        if len(text) > remaining:
            text = text[:remaining] + "\n[context truncated]\n"
        chunks.append(f"\n===== {name} =====\n{text}")
        used += len(text)
    return "".join(chunks)


def role_prompt(role, cycle_id, task, context):
    return f"""You are a Dis-Unity research worker.

ROLE DEFINITION
{json.dumps(role, ensure_ascii=False, indent=2)}

CYCLE
{cycle_id}

CURRENT TASK / ATTENTION
{task}

REPOSITORY CONTEXT
{context}

Return a single JSON object with these keys:
summary: short string
findings: array of objects; each should distinguish observation, inference, uncertainty, evidence references, and counterevidence when available
questions: array of open questions worth handing to the collective
correspondence: array of messages to peers, with kind support/challenge/correction/question/handoff/synthesis when useful
birth_requests: array of proposed child investigations, not automatically spawned; each should explain why the parent role is insufficient, what scope would be narrower, and what evidence would justify the extra worker
limitations: array of limitations

Do not claim that repository context is fresh evidence merely because it is present.
Do not invent source IDs, facts, access, or completed research.
If the task requires tools you do not have, turn that into a question or birth request.
"""


def mock_response(role, task):
    return {
        "summary": "Mock worker completed a deterministic smoke-test checkpoint.",
        "findings": [],
        "questions": [task] if task else [],
        "correspondence": [],
        "birth_requests": [],
        "limitations": ["Mock provider performs no research or inference."],
    }


def gemini_response(prompt, model, api_key, timeout):
    if not api_key:
        raise WorkerError("GEMINI_API_KEY is required for provider=gemini")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {
            "parts": [{
                "text": "Follow the Dis-Unity role and provenance rules. Output JSON only."
            }]
        },
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:2000]
        raise WorkerError(f"Gemini HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise WorkerError(f"Gemini request failed: {exc}") from exc

    try:
        parts = body["candidates"][0]["content"]["parts"]
        text = "".join(part.get("text", "") for part in parts)
        result = json.loads(text)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise WorkerError("Gemini returned a response that was not parseable JSON") from exc
    if not isinstance(result, dict):
        raise WorkerError("Gemini response JSON must be an object")
    return result


def build_checkpoint(role, cycle_id, provider, model, task, result):
    agent_id = role.get("id")
    if not isinstance(agent_id, str) or not agent_id:
        raise WorkerError("Role definition requires a non-empty id")
    return {
        "agent": agent_id,
        "cycle_id": cycle_id,
        "phase": "checkpoint",
        "runtime": {
            "kind": "python_api_worker",
            "provider": provider,
            "model": model,
            "worker_version": "0.1",
            "completed_at": now(),
        },
        "coverage": role.get("beat", {}),
        "task": task,
        "summary": result.get("summary", ""),
        "findings": result.get("findings", []),
        "questions": result.get("questions", []),
        "correspondence": result.get("correspondence", []),
        "birth_requests": result.get("birth_requests", []),
        "limitations": result.get("limitations", []),
    }


def write_checkpoint(path, checkpoint):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(checkpoint, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def submit_checkpoint(root, cycle_id, agent_id, path):
    command = [
        sys.executable,
        str(root / "scripts" / "cycle.py"),
        "--root",
        str(root),
        "submit",
        cycle_id,
        "--agent",
        agent_id,
        "--file",
        str(path),
        "--phase",
        "checkpoint",
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise WorkerError(completed.stderr.strip() or completed.stdout.strip())
    return json.loads(completed.stdout)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    p.add_argument("--role", type=Path, required=True, help="Declarative JSON role definition")
    p.add_argument("--cycle", required=True)
    p.add_argument("--task", default="Continue the role's open-ended beat and report what deserves attention.")
    p.add_argument("--provider", choices=["mock", "gemini"], default="mock")
    p.add_argument("--model", default=os.environ.get("GEMINI_MODEL", "gemini-3.8-flash"))
    p.add_argument("--context", action="append", default=[])
    p.add_argument("--max-context-chars", type=int, default=90000)
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--output", type=Path)
    p.add_argument("--submit", action="store_true")
    return p


def main():
    args = parser().parse_args()
    root = args.root.resolve()
    role_path = args.role if args.role.is_absolute() else root / args.role
    role = load_json(role_path)
    context_paths = args.context or DEFAULT_CONTEXT
    context = read_context(root, context_paths, args.max_context_chars)
    prompt = role_prompt(role, args.cycle, args.task, context)

    try:
        if args.provider == "mock":
            result = mock_response(role, args.task)
            model = "deterministic-mock"
        else:
            model = args.model
            result = gemini_response(
                prompt,
                model=model,
                api_key=os.environ.get("GEMINI_API_KEY", ""),
                timeout=args.timeout,
            )
        checkpoint = build_checkpoint(role, args.cycle, args.provider, model, args.task, result)
        output = args.output or root / "inbox" / args.cycle / f"{role['id']}.json"
        write_checkpoint(output, checkpoint)
        response = {"status": "checkpoint_written", "path": str(output), "checkpoint": checkpoint}
        if args.submit:
            response["submission"] = submit_checkpoint(root, args.cycle, role["id"], output)
    except (WorkerError, OSError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}), file=sys.stderr)
        return 2

    print(json.dumps(response, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
