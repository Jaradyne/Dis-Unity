import json
from pathlib import Path
import tempfile
import unittest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import worker


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
            worker.gemini_response("prompt", "gemini-3.8-flash", "", 1)


if __name__ == "__main__":
    unittest.main()
