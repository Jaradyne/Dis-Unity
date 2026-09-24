#!/usr/bin/env python3
"""Provider-neutral Dis-Unity worker.

This worker is intentionally small:
- reads a declarative JSON role plus selected repository context;
- records an immutable request before computation; real providers defer;
- runs a deterministic mock or preserves a policy-blocked request;
- writes one attributed checkpoint under operations/;
- can optionally submit that checkpoint through scripts/cycle.py.

It does not browse, send mail, mutate canonical state, spawn child workers, or
commit to Git. Those are later capabilities that should be added explicitly.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import hashlib

import cycle
import questions
import reflections


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
        path = (root / name).resolve()
        if root.resolve() not in path.parents or any(
                part in {"private", ".git"} or part.startswith(".env") for part in path.parts):
            raise WorkerError("Context must be a public repository file")
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
reflections: array of brief shareable observations about this work: what helped, what failed, a mistaken assumption, uncertainty, or something worth trying. Each may be a string or an object with summary, observations, suggestions, questions, uncertainties, and source_refs.

Reflection is welcome from every participant, including the governor and each application-level subcall. A short honest note or an empty array is valid. Do not manufacture a lesson, expose private reasoning, or make extra calls just to fill this field. The runtime records missing reflection coverage honestly. The governor can develop ideas with Chat Aiden, ask Work Aiden to implement them, and invite the human or other thought partners. Suggestions are contributions, not authorization to act.

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
        "reflections": [{"summary": "Mock fixture: checkpoint and reflection paths can be exercised without a model call.",
                         "uncertainties": ["This is deterministic test content, not model self-reflection or research."]}],
        "limitations": ["Mock provider performs no research or inference."],
    }


def gemini_response(prompt, model, api_key, timeout):
    if not api_key:
        raise WorkerError("GEMINI_API_KEY is required for provider=gemini")
    raise WorkerError("Real providers paused: resolve model policy and verify eligibility first")


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
            "worker_version": "0.3",
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
        "reflections": result.get("reflections", []),
    }


def write_checkpoint(path, checkpoint):
    path = Path(path)
    cycle.write_json(path, checkpoint)


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
    p.add_argument("--model", default=None, help="Explicit candidate ID; real providers currently paused")
    p.add_argument("--question", help="Existing shared Question ID; otherwise register task text")
    p.add_argument("--run-id", help="Shared identifier for an application-level call tree")
    p.add_argument("--parent-call-id", help="Recorded parent call, when this invocation is a subcall")
    p.add_argument("--reflection-level", choices=["worker", "neuron", "subcall", "governor"], default="worker")
    p.add_argument("--context", action="append", default=[])
    p.add_argument("--max-context-chars", type=int, default=90000)
    p.add_argument("--timeout", type=int, default=120)
    p.add_argument("--output", type=Path)
    p.add_argument("--submit", action="store_true")
    return p


def main():
    args = parser().parse_args()
    root = args.root.resolve()
    attempt = None
    qid = None
    try:
        cycle.check_name(args.cycle, "cycle ID")
        if args.submit:
            folder, _, _ = cycle.load_cycle(root, args.cycle)
            cycle.ensure_open(folder)
        role_path = args.role if args.role.is_absolute() else root / args.role
        role = load_json(role_path)
        if not isinstance(role, dict) or not isinstance(role.get("id"), str):
            raise WorkerError("Role definition requires a non-empty id")
        cycle.check_name(role["id"], "role ID")
        if args.max_context_chars < 1 or not 1 <= args.timeout <= 300:
            raise WorkerError("Use positive context size and a timeout of 1–300 seconds")
        qid = args.question
        if qid:
            item = questions.question(questions.load(root), qid)
            task = item["question"]
        else:
            task = args.task
            qid = questions.ask(root, task, role["id"], context_refs=[f"cycle:{args.cycle}"])["question_id"]
        context_paths = args.context or DEFAULT_CONTEXT
        context = read_context(root, context_paths, args.max_context_chars)
        prompt = role_prompt(role, args.cycle, task, context)
        lease = questions.claim(root, qid, role["id"], seconds=args.timeout + 60)
        if lease["status"] != "claimed":
            print(json.dumps(lease))
            return 0
        git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True,
                             capture_output=True, check=False)
        model = "deterministic-mock" if args.provider == "mock" else args.model or "unselected"
        attempt = questions.begin_attempt(root, qid, lease["token"], {
            "actor": role["id"], "runtime": "python_worker_0.3", "provider": args.provider,
            "model": model, "role": role, "role_sha256": cycle.digest(role),
            "prompt": prompt, "context_refs": context_paths,
            "context_sha256": hashlib.sha256(context.encode("utf-8")).hexdigest(),
            "base_commit": git.stdout.strip() if git.returncode == 0 else "unknown",
            "evidence_cutoff": cycle.read_json(root / cycle.CANONICAL).get("meta", {}).get("research_cutoff"),
            "settings": {"timeout_seconds": args.timeout, "response_format": "json"},
            "call_context": {"run_id": args.run_id, "parent_call_id": args.parent_call_id,
                             "reflection_level": args.reflection_level},
        })
        aid = attempt["attempt_id"]
        if args.provider == "mock":
            result = mock_response(role, task)
            outcome = "mock_only"
        else:
            result = {"summary": "Deferred before network access; prompt retained.",
                      "questions": [task], "limitations": [
                          "Provider policy remains unresolved; no real model called."]}
            outcome = "policy_blocked"
        checkpoint = build_checkpoint(role, args.cycle, args.provider, model, task, result)
        checkpoint.update(question_id=qid, attempt_id=aid, attempt_result=outcome)
        checkpoint.update(run_id=args.run_id or aid, parent_call_id=args.parent_call_id,
                          reflection_level=args.reflection_level)
        output = (args.output or root / "operations" / "checkpoints" / f"{aid}.json").resolve()
        if root in output.parents and output.relative_to(root).parts[0] != "operations":
            raise WorkerError("Repository checkpoints must stay under operations/; closed cycles are protected")
        # Save the complete result to shared memory even if later checkpoint export fails.
        questions.finish_attempt(root, qid, aid, outcome, details={"checkpoint": checkpoint})
        # Projection is separate from research completion and can be replayed from
        # the durable attempt if interrupted or temporarily unable to write.
        try:
            reflection_status = {"status": "recorded", "ids": reflections.from_checkpoint(root, checkpoint)}
        except (cycle.CycleError, OSError, ValueError, KeyError, TypeError) as exc:
            reflection_status = {"status": "pending_projection", "reason": str(exc),
                                 "recovery": {"question_id": qid, "attempt_id": aid}}
        write_checkpoint(output, checkpoint)
        response = {"status": "checkpoint_written" if outcome == "mock_only" else "deferred_policy",
                    "path": str(output), "question_id": qid, "attempt_id": aid,
                    "reflection_mailbox": reflection_status}
        if args.submit:
            if outcome != "mock_only":
                raise WorkerError("Deferred provider requests cannot be submitted as research")
            response["submission"] = submit_checkpoint(root, args.cycle, role["id"], output)
    except (WorkerError, cycle.CycleError, OSError, ValueError) as exc:
        if attempt:
            # Do not strand a claim after an ordinary local error. Hard interruption
            # still leaves result=None, which requires explicit recovery.
            try:
                saved = questions.question(questions.load(root), qid)["attempts"][attempt["attempt_id"]]
                if saved["result"] is None:
                    questions.finish_attempt(root, qid, attempt["attempt_id"], "invalid_response",
                                            details={"local_error": str(exc)})
            except (cycle.CycleError, OSError, ValueError):
                pass  # The prewritten request remains the recovery point.
        print(json.dumps({"status": "blocked", "reason": str(exc)}), file=sys.stderr)
        return 2

    print(json.dumps(response, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
