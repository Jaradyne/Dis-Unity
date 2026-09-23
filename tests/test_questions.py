import concurrent.futures
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cycle
import questions


class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / cycle.CANONICAL).write_text('{"meta": {"research_cutoff": "2026-09-21"}}')
        self.qid = questions.ask(self.root, "How much reserve is usable?", "work")["question_id"]

    def begin(self, provider="mock"):
        lease = questions.claim(self.root, self.qid, "bee")
        request = {"actor": "bee", "provider": provider, "model": "test", "prompt": "exact prompt\n",
                   "role": {"id": "bee"}, "context_refs": [], "base_commit": "unknown",
                   "evidence_cutoff": "2026-09-21", "settings": {}}
        return questions.begin_attempt(self.root, self.qid, lease["token"], request)

    def payload(self):
        return {"summary": "An attributed answer", "status": "ready_for_review",
                "evidence_refs": [], "counterevidence": [], "limitations": ["Illustrative test only"]}

    def test_duplicate_registration_and_concurrent_claim_have_one_owner(self):
        q = questions.ask(self.root, "HOW MUCH  reserve is usable?", "chat")
        self.assertEqual(self.qid, q["question_id"])
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda n: questions.claim(self.root, self.qid, str(n)), range(4)))
        self.assertEqual(sum(x["status"] == "claimed" for x in results), 1)

    def test_interruption_retains_request_and_blocks_blind_retry(self):
        attempt = self.begin()
        restored = questions.load(self.root)["questions"][self.qid]["attempts"][attempt["attempt_id"]]
        self.assertEqual(restored["request"]["prompt"], "exact prompt\n")
        self.assertIsNone(restored["result"])
        self.assertEqual(questions.claim(self.root, self.qid, "next")["status"], "unfinished_attempt")
        questions.finish_attempt(self.root, self.qid, attempt["attempt_id"], "interrupted")
        self.assertEqual(questions.claim(self.root, self.qid, "next")["status"], "claimed")

    def test_failed_attempt_is_immutable_and_idempotent(self):
        attempt = self.begin()
        first = questions.finish_attempt(self.root, self.qid, attempt["attempt_id"], "policy_blocked")
        self.assertEqual(first, questions.finish_attempt(self.root, self.qid, attempt["attempt_id"], "policy_blocked"))
        with self.assertRaises(cycle.CycleError):
            questions.finish_attempt(self.root, self.qid, attempt["attempt_id"], "usable_answer")

    def test_chat_answer_stops_duplicates_and_resolves_same_ticket(self):
        ticket = questions.escalate(self.root, self.qid, "work", "chat_research_requested", "Bounded lookup")
        again = questions.escalate(self.root, self.qid, "work", "chat_research_requested", "Bounded lookup")
        self.assertEqual(ticket, again)
        reply = questions.answer(self.root, self.qid, "chat", self.payload(), epoch=1)
        self.assertEqual(reply, questions.answer(self.root, self.qid, "chat", self.payload(), epoch=1))
        q = questions.load(self.root)["questions"][self.qid]
        self.assertEqual(q["tickets"][ticket["ticket_id"]]["status"], "resolved")
        self.assertEqual(questions.claim(self.root, self.qid, "bee")["status"], "already_answered_or_closed")

    def test_stale_attempt_and_answer_cannot_resolve_new_epoch(self):
        attempt = self.begin("test_provider")
        questions.reopen(self.root, self.qid, "work", "New inventory release")
        questions.finish_attempt(self.root, self.qid, attempt["attempt_id"], "usable_answer")
        questions.answer(self.root, self.qid, "bee", self.payload(), epoch=1, attempt_id=attempt["attempt_id"])
        q = questions.load(self.root)["questions"][self.qid]
        self.assertEqual(q["epoch"], 2)
        self.assertEqual(q["status"], "needs_refresh")

    def test_mock_cannot_be_promoted_to_research_answer(self):
        attempt = self.begin()
        questions.finish_attempt(self.root, self.qid, attempt["attempt_id"], "mock_only")
        with self.assertRaises(cycle.CycleError):
            questions.answer(self.root, self.qid, "bee", self.payload(), epoch=1, attempt_id=attempt["attempt_id"])
        self.assertEqual(questions.load(self.root)["questions"][self.qid]["status"], "open")

    def test_links_preserve_two_geographic_questions(self):
        other = questions.ask(self.root, "How much reserve is usable?", "chat", geography="Oakland")["question_id"]
        questions.link(self.root, self.qid, other, "child", "work")
        store = questions.load(self.root)
        self.assertEqual(len(store["questions"]), 2)
        self.assertEqual(store["questions"][other]["relations"][0]["kind"], "parent")


if __name__ == "__main__":
    unittest.main()
