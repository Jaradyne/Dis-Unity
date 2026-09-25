from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cycle
import daily_scroll
import garden
import governor
import questions
import reflections
import worker


class ReflectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / cycle.CANONICAL).write_text('{"meta":{}}')

    def test_fifty_subcalls_and_parent_survive_retry_and_paging(self):
        notes = [{"actor": "bee", "level": "subcall", "summary": "Repeated lesson",
                  "context": {"run_id": "run-1", "call_id": f"call-{i}", "parent_call_id": "parent"}}
                 for i in range(50)]
        ids = reflections.post(self.root, notes)
        self.assertEqual(len(set(ids)), 50)
        before = (self.root / reflections.STORE).read_bytes()
        self.assertEqual(reflections.post(self.root, notes), ids)
        page = reflections.attend(self.root, 30)
        remainder = reflections.attend(self.root, 30, page["next_offset"])
        self.assertEqual((page["pending_count"], remainder["returned_count"]), (50, 20))
        self.assertEqual({r["context"]["parent_call_id"] for r in remainder["entries"]}, {"parent"})
        self.assertEqual((self.root / reflections.STORE).read_bytes(), before)

    def test_invalid_batch_writes_nothing_and_preserves_existing_notes(self):
        valid = {"actor": "human", "level": "human", "summary": "A small useful observation"}
        reflections.post(self.root, valid)
        before = (self.root / reflections.STORE).read_bytes()
        invalid = {"actor": "bee", "level": "subcall", "summary": "No call identity"}
        with self.assertRaises(cycle.CycleError):
            reflections.post(self.root, [{**valid, "summary": "Should not be inserted"}, invalid])
        self.assertEqual((self.root / reflections.STORE).read_bytes(), before)

    def test_governor_can_choose_reconsider_and_include_other_partners(self):
        rid = reflections.post(self.root, {"actor": "bee", "level": "worker", "summary": "An observation"})[0]
        response = {"review_id": "review-1", "actor": "Chat Aiden acting as governor",
                    "reflection_ids": [rid], "disposition": "Explore a surprising connection",
                    "summary": "Ask others to develop the idea", "keep_open": False,
                    "followups": [{"recipient": "Work Aiden", "question": "Can this be tried reversibly?"},
                                  {"recipient": "human", "question": "Optional: does this fit your experience?"}],
                    "self_reflection": "I should consider dissent before recommending implementation."}
        first = reflections.respond(self.root, response)
        self.assertEqual(reflections.respond(self.root, response), first)
        self.assertEqual(reflections.attend(self.root)["pending_count"], 1)
        with self.assertRaises(cycle.CycleError):
            reflections.respond(self.root, {**response, "summary": "Silent rewrite"})
        reflections.respond(self.root, {**response, "review_id": "review-2", "keep_open": True,
                                       "self_reflection": None, "summary": "Reconsider after counterevidence"})
        data = reflections.load(self.root)
        self.assertEqual(len(data["decisions"]), 2)
        self.assertEqual(data["entries"][rid]["summary"], "An observation")
        self.assertEqual(reflections.attend(self.root)["pending_count"], 2)
        self.assertFalse((self.root / questions.STORE).exists())

    def test_runtime_provenance_wins_and_missing_reflection_is_not_fabricated(self):
        checkpoint = {"agent": "bee", "question_id": "Q-1", "attempt_id": "ATT-1", "runtime": {"provider": "mock"},
                      "attempt_result": "mock_only", "reflections": [{"summary": "Fixture", "actor": "pretend",
                         "origin": "self_report", "context": {"call_id": "pretend"}}]}
        rid = reflections.from_checkpoint(self.root, checkpoint)[0]
        entry = reflections.load(self.root)["entries"][rid]
        self.assertEqual((entry["actor"], entry["origin"], entry["context"]["call_id"]), ("bee", "mock", "ATT-1"))
        checkpoint.update(attempt_id="ATT-2", reflections=[], attempt_result="policy_blocked", runtime={"provider": "gemini"})
        rid = reflections.from_checkpoint(self.root, checkpoint)[0]
        self.assertEqual(reflections.load(self.root)["entries"][rid]["origin"], "runtime_observation")

    def test_worker_projection_failure_can_recover_from_saved_attempt(self):
        (self.root / "role.json").write_text('{"id":"bee"}')
        command = ["worker.py", "--root", str(self.root), "--role", "role.json", "--cycle", "runtime-check",
                   "--run-id", "colony-run", "--parent-call-id", "parent-1", "--reflection-level", "subcall"]
        with patch.object(sys, "argv", command), patch.object(reflections, "from_checkpoint", side_effect=OSError("fixture disk failure")), patch("builtins.print"):
            self.assertEqual(worker.main(), 0)
        question = next(iter(questions.load(self.root)["questions"].values()))
        aid = next(iter(question["attempts"]))
        ids = reflections.from_attempt(self.root, question["question_id"], aid)
        self.assertEqual(reflections.from_attempt(self.root, question["question_id"], aid), ids)
        entry = reflections.load(self.root)["entries"][ids[0]]
        self.assertEqual(entry["level"], "subcall")
        self.assertEqual(entry["context"]["run_id"], "colony-run")
        self.assertEqual(entry["context"]["parent_call_id"], "parent-1")
        self.assertFalse((self.root / "inbox").exists())

    def test_governor_packet_observes_without_consuming_or_executing(self):
        roles = self.root / "agents"
        roles.mkdir()
        (roles / "governor.json").write_text('{"id":"governor"}')
        reflections.post(self.root, {"actor": "bee", "level": "worker", "summary": "Consider a change"})
        before = (self.root / reflections.STORE).read_bytes()
        packet = governor.prepare(self.root)
        self.assertEqual(packet["attention"]["pending_count"], 1)
        self.assertIn("Work Aiden", packet["request"])
        self.assertEqual(before, (self.root / reflections.STORE).read_bytes())

    def test_daily_scroll_dates_order_and_chair_feedback_preserve_sources(self):
        (self.root / 'agents').mkdir()
        (self.root / 'agents/governor.json').write_text('{"id":"governor"}')
        state = {'runs': {name: {'started_at': date, 'status': 'complete', 'result': 'partial_answer'}
                         for name, date in [('z-old', '2026-09-24T01:00:00Z'), ('a-new', '2026-09-25T01:00:00Z')]}}
        manifest = self.root / daily_scroll.BASE / 'run-manifest.json'
        cycle.write_json(manifest, state)
        folder = self.root / daily_scroll.BASE / 'runs/a-new'
        cycle.write_json(folder / 'outcome.json', {'answer_summary': 'Usable reserve is unknown.'})
        cycle.write_json(folder / 'sources.json', {'retrieved_at': '2026-09-25T00:59:00Z', 'new_or_changed_ids': ['s1']})
        reflections.post(self.root, {'actor': 'test', 'level': 'worker', 'summary': 'Read recorded work.'})
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        scroll = daily_scroll.snapshot(self.root, limit=1)
        self.assertEqual([r['run_id'] for r in scroll['recent_runs']], ['a-new'])
        self.assertEqual(scroll['recent_runs'][0]['retrieved_at'], '2026-09-25T00:59:00Z')
        imagination = garden.attach_imagination(garden.generate_chair([
            {'id': 'ONE', 'word': 'care'}, {'id': 'TWO', 'word': 'care'}], 'fixture'),
            'Who needs rest?', {'name': 'test fixture', 'runtime': 'unit test'})
        packet = governor.prepare(self.root, imagination=imagination)
        self.assertEqual(packet['inputs']['chair_imagination'], imagination)
        self.assertEqual([r['run_id'] for r in packet['inputs']['daily_scroll']['recent_runs']], ['z-old', 'a-new'])
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        imagination['chair']['text'] = 'altered sequence'
        with self.assertRaises(cycle.CycleError):
            governor.prepare(self.root, imagination=imagination)


if __name__ == "__main__":
    unittest.main()
