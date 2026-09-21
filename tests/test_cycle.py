"""Exercise data-loss and false-admission boundaries using temporary projects."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import cycle


class CycleIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        baseline = ROOT / "cycles/RC-002/baseline.json"
        self.base = json.loads(baseline.read_text(encoding="utf-8"))
        self.state_path = self.root / cycle.CANONICAL
        self.write(self.state_path, self.base)
        cycle.begin(self.root, "TEST-002", "2026-09-20")
        self.candidate = copy.deepcopy(self.base)
        self.candidate["meta"]["cycle_id"] = "TEST-002"
        self.candidate_path = self.root / "candidate.json"
        self.write(self.candidate_path, self.candidate)

    def write(self, path, value):
        path.write_text(json.dumps(value), encoding="utf-8")

    def approve(self):
        return cycle.review(self.root, "TEST-002", self.candidate_path,
                            "coordinator", "coordinator", "accepted_with_limitations",
                            "Reviewed candidate with documented coverage gap.",
                            ["Independent closing review incomplete"])

    def test_missing_review_and_changed_candidate_are_blocked(self):
        with self.assertRaisesRegex(cycle.CycleError, "explicit review"):
            cycle.commit(self.root, "TEST-002", self.candidate_path)
        self.approve()
        self.candidate["meta"]["status"] = "Different material candidate"
        self.write(self.candidate_path, self.candidate)
        with self.assertRaisesRegex(cycle.CycleError, "explicit review"):
            cycle.commit(self.root, "TEST-002", self.candidate_path)
        self.assertEqual(json.loads(self.state_path.read_text()), self.base)

    def test_orphan_source_cannot_be_reviewed(self):
        self.candidate["ACTIVE_SIGNALS"][0]["source_ids"].append("NO-SUCH-SOURCE")
        self.write(self.candidate_path, self.candidate)
        with self.assertRaisesRegex(cycle.CycleError, "unresolved source"):
            self.approve()

    def test_fragmented_narrative_cannot_be_admitted(self):
        edge = self.candidate["CASCADE_GRAPH"]["edges"][0]
        edge["thresholds"] += " Source independence must be checked."
        self.write(self.candidate_path, self.candidate)
        with self.assertRaisesRegex(cycle.CycleError, "fragmented narrative"):
            self.approve()
        self.assertEqual(json.loads(self.state_path.read_text()), self.base)
        edge["thresholds"] = ["Source independence must be checked."]
        self.write(self.candidate_path, self.candidate)
        self.approve()
        cycle.commit(self.root, "TEST-002", self.candidate_path)
        self.assertEqual(json.loads(self.state_path.read_text()), self.candidate)

    def test_lost_update_preserves_newer_state(self):
        self.approve()
        newer = copy.deepcopy(self.base)
        newer["meta"]["status"] = "Another valid writer's change"
        self.write(self.state_path, newer)
        with self.assertRaisesRegex(cycle.CycleError, "Lost-update"):
            cycle.commit(self.root, "TEST-002", self.candidate_path)
        self.assertEqual(json.loads(self.state_path.read_text()), newer)

    def test_stricter_validation_repairs_immutable_legacy_baseline(self):
        legacy = copy.deepcopy(self.base)
        legacy["CASCADE_GRAPH"]["edges"][0]["thresholds"] += " Legacy broken narrative."
        self.write(self.state_path, legacy)
        # Model a cycle admitted before the fragmented-narrative rule existed.
        with patch.object(cycle, "validate", return_value=[]):
            cycle.begin(self.root, "MIGRATION", "2026-09-20")
        baseline_path = self.root / "cycles/MIGRATION/baseline.json"
        original_bytes = baseline_path.read_bytes()
        candidate = copy.deepcopy(legacy)
        candidate["meta"]["cycle_id"] = "MIGRATION"
        self.write(self.candidate_path, candidate)
        with self.assertRaisesRegex(cycle.CycleError, "fragmented narrative"):
            cycle.review(self.root, "MIGRATION", self.candidate_path,
                         "coordinator", "coordinator", "passed", "Review migration")
        candidate["CASCADE_GRAPH"]["edges"][0]["thresholds"] = ["Legacy repaired narrative."]
        self.write(self.candidate_path, candidate)
        cycle.review(self.root, "MIGRATION", self.candidate_path,
                     "coordinator", "coordinator", "passed", "Review migration")
        cycle.commit(self.root, "MIGRATION", self.candidate_path)
        self.assertEqual(baseline_path.read_bytes(), original_bytes)
        self.assertEqual(json.loads(self.state_path.read_text()), candidate)
        self.assertEqual(cycle.status(self.root, "MIGRATION")["status"], "committed")

    def test_duplicate_commit_is_idempotent_and_review_honest(self):
        self.approve()
        result = cycle.commit(self.root, "TEST-002", self.candidate_path)
        count = cycle.status(self.root, "TEST-002")["journal_entries"]
        again = cycle.commit(self.root, "TEST-002", self.candidate_path)
        self.assertEqual(result["receipt"]["review_status"],
                         "coordinator_accepted_with_limitations")
        self.assertEqual(again["status"], "already_committed")
        self.assertEqual(cycle.status(self.root, "TEST-002")["journal_entries"], count)

    def test_interruption_after_state_replace_recovers(self):
        self.approve()
        original = cycle.write_json
        def interrupted(path, value, **kwargs):
            if Path(path).name == "commit.json":
                raise OSError("Simulated interruption after canonical replacement")
            return original(path, value, **kwargs)
        with patch.object(cycle, "write_json", side_effect=interrupted):
            with self.assertRaises(OSError):
                cycle.commit(self.root, "TEST-002", self.candidate_path)
        self.assertEqual(cycle.status(self.root, "TEST-002")["status"], "recovery_required")
        result = cycle.commit(self.root, "TEST-002")
        self.assertEqual(result["status"], "recovered")
        self.assertEqual(json.loads(self.state_path.read_text()), self.candidate)

    def test_baseline_and_journal_tampering_detected(self):
        folder = self.root / "cycles/TEST-002"
        baseline = folder / "baseline.json"
        baseline.write_text(baseline.read_text() + " ")
        with self.assertRaisesRegex(cycle.CycleError, "Baseline"):
            cycle.status(self.root, "TEST-002")
        baseline.write_text(baseline.read_text()[:-1])
        event = next((folder / "events").glob("*.json"))
        body = json.loads(event.read_text())
        body["event_type"] = "altered"
        self.write(event, body)
        with self.assertRaisesRegex(cycle.CycleError, "journal integrity"):
            cycle.status(self.root, "TEST-002")

    def test_checkpoint_is_preserved_and_wrong_cycle_rejected(self):
        path = self.root / "agent.json"
        self.write(path, {"agent": "fuel", "cycle_id": "TEST-002", "findings": ["one"]})
        one = cycle.submit(self.root, "TEST-002", "fuel", path, "checkpoint")
        self.write(path, {"agent": "fuel", "cycle_id": "TEST-002", "findings": ["two"]})
        cycle.submit(self.root, "TEST-002", "fuel", path, "checkpoint")
        self.assertEqual(json.loads(Path(one["snapshot"]).read_text())["payload"]["findings"], ["one"])
        self.write(path, {"agent": "fuel", "cycle_id": "OTHER"})
        with self.assertRaisesRegex(cycle.CycleError, "different cycle"):
            cycle.submit(self.root, "TEST-002", "fuel", path)


if __name__ == "__main__":
    unittest.main()
