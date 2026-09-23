import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import worker
import cycle
import questions


class WorkerTests(unittest.TestCase):
    def test_mock_checkpoint_is_attributed_and_recoverable(self):
        role = {
            "id": "bee",
            "beat": {"include": ["test"], "open_ended": True},
        }
        result = worker.mock_response(role, "look around")
        checkpoint = worker.build_checkpoint(
            role, "RC-004", "mock", "deterministic-mock", "look around", result
        )
        self.assertEqual(checkpoint["agent"], "bee")
        self.assertEqual(checkpoint["cycle_id"], "RC-004")
        self.assertEqual(checkpoint["phase"], "checkpoint")
        self.assertIn("questions", checkpoint)
        self.assertIn("birth_requests", checkpoint)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "inbox.json"
            worker.write_checkpoint(path, checkpoint)
            restored = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(restored["agent"], "bee")
        self.assertEqual(restored["runtime"]["provider"], "mock")

    def test_role_prompt_requests_attributed_outputs(self):
        prompt = worker.role_prompt({"id": "bee"}, "RC-004", "task", "context")
        self.assertIn("birth_requests", prompt)
        self.assertIn("correspondence", prompt)
        self.assertIn("Do not invent source IDs", prompt)

    def test_missing_gemini_key_is_blocked(self):
        with self.assertRaisesRegex(worker.WorkerError, "GEMINI_API_KEY"):
            worker.gemini_response("prompt", "unverified-candidate", "", 1)

    def test_real_adapter_cannot_bypass_policy_with_a_key(self):
        with self.assertRaisesRegex(worker.WorkerError, "paused"):
            worker.gemini_response("prompt", "unverified-candidate", "test-secret", 1)

    def test_cli_defers_and_saves_exact_request_without_model_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / cycle.CANONICAL).write_text('{"meta":{"research_cutoff":"2026-09-21"}}')
            (root / "role.json").write_text('{"id":"bee"}')
            command = ["worker.py", "--root", str(root), "--role", "role.json", "--cycle", "runtime-check",
                       "--provider", "gemini", "--task", "How much reserve?"]
            with patch.object(sys, "argv", command), patch.object(worker, "gemini_response") as api, patch("builtins.print"):
                self.assertEqual(worker.main(), 0)
                api.assert_not_called()
            q = next(iter(questions.load(root)["questions"].values()))
            attempt = next(iter(q["attempts"].values()))
            self.assertEqual(attempt["result"]["category"], "policy_blocked")
            self.assertIn("How much reserve?", attempt["request"]["prompt"])
            self.assertEqual(attempt["request"]["model"], "unselected")
            self.assertEqual(q["status"], "open")
            self.assertFalse((root / "inbox").exists())

    def test_existing_answer_skips_worker_and_context_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / cycle.CANONICAL).write_text('{"meta":{}}')
            (root / "role.json").write_text('{"id":"bee"}')
            qid = questions.ask(root, "Question already answered", "chat")["question_id"]
            questions.answer(root, qid, "chat", {"summary":"Answer", "status":"ready_for_review",
                "evidence_refs":[], "counterevidence":[], "limitations":["Fixture"]}, epoch=1)
            command = ["worker.py", "--root", str(root), "--role", "role.json", "--cycle", "runtime-check", "--question", qid]
            with patch.object(sys, "argv", command), patch.object(worker, "mock_response") as api, patch("builtins.print"):
                self.assertEqual(worker.main(), 0)
                api.assert_not_called()
            with self.assertRaises(worker.WorkerError):
                worker.read_context(root, ["../outside.txt"], 100)

    def test_checkpoint_cannot_replace_prior_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "checkpoint.json"
            worker.write_checkpoint(target, {"original": True})
            with self.assertRaises(cycle.CycleError):
                worker.write_checkpoint(target, {"original": False})
            self.assertEqual(json.loads(target.read_text()), {"original": True})


if __name__ == "__main__":
    unittest.main()
