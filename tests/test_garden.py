from pathlib import Path
import copy
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cycle
import garden

ROOT = Path(__file__).resolve().parents[1]


class GardenTests(unittest.TestCase):
    def setUp(self):
        self.config = garden.load_config(ROOT)
        self.packet = cycle.read_json(ROOT / "examples/garden/q18-pass.json")
        self.registry = {"questions": {"Q-RESEARCH-Q18": {"epoch": 1}}}

    def test_stable_destination_survives_presentation_reordering(self):
        self.config["trees"]["INIT"]["nodes"].reverse()
        self.assertEqual(garden.resolve(self.config, "INIT:MEAN-0008")["status"], "resolved")
        self.assertEqual(garden.resolve(self.config, "PYGENT:OPERATING-0001")["status"], "proposed")
        for destination in ("tab!43", "INIT:43", "INIT:ROOT:0001", "../INIT:ROOT-0001"):
            with self.subTest(destination=destination), self.assertRaises(cycle.CycleError):
                garden.resolve(self.config, destination)

    def test_unknown_is_not_false_and_groups_are_explicit(self):
        check = lambda op, values: garden.evaluate_group({"op": op, "members": ["a", "b"]}, values)
        self.assertIsNone(check("AND", {"a": True}))
        self.assertIsNone(check("OR", {"a": False, "b": None}))
        self.assertIs(check("AND", {"a": False}), False)
        self.assertIs(check("OR", {"a": True}), True)
        self.assertIs(check("AND", {"a": True, "b": True}), True)
        self.assertIs(check("OR", {"a": False, "b": False}), False)
        with self.assertRaises(cycle.CycleError):
            check("AND", {"a": "unknown"})
        with self.assertRaises(cycle.CycleError):
            garden.evaluate_group({"op": "AND", "members": []}, {})

    def test_pass_preserves_input_and_current_question_epoch(self):
        before = copy.deepcopy(self.packet)
        output = garden.prepare_pass(self.config, self.packet, self.registry)
        self.assertEqual(output["record"], before)
        self.assertEqual(self.packet, before)
        self.assertEqual(output["return"]["status"], "rest")
        self.assertEqual(output["trace"][0], "INIT:ROOT-0001")
        self.assertEqual(output["specialist_return"]["status"], "resolved")
        self.packet["epoch"] = 2
        with self.assertRaises(cycle.CycleError):
            garden.prepare_pass(self.config, self.packet, self.registry)
        self.packet["question_id"] = "Q-INVENTED"
        with self.assertRaises(cycle.CycleError):
            garden.prepare_pass(self.config, self.packet, self.registry)

    def test_exit_teleport_can_be_only_a_proposal_and_error_is_not_default(self):
        self.packet["steps"][8].update(kind="teleport", destination="PYGENT:OPERATING-0001")
        output = garden.prepare_pass(self.config, self.packet, self.registry)
        self.assertEqual(output["teleport"]["status"], "proposed")
        self.assertEqual(output["exit"]["kind"], "teleport")
        for kind in ("answer", "question", "silence", "error"):
            self.packet["steps"][8]["kind"] = kind
            self.assertEqual(garden.prepare_pass(self.config, self.packet, self.registry)["exit"]["kind"], kind)

    def test_missing_cross_attachment_and_evidence_flower_are_rejected(self):
        del self.packet["steps"][5]["bridge"]
        with self.assertRaises(cycle.CycleError):
            garden.prepare_pass(self.config, self.packet, self.registry)
        self.packet["steps"][5]["bridge"] = []
        self.packet["steps"][7]["culture_flower"]["evidence"] = True
        with self.assertRaises(cycle.CycleError):
            garden.prepare_pass(self.config, self.packet, self.registry)

    def test_specialist_needs_numeric_budget_ceilings(self):
        self.packet["steps"][6]["specialist"]["budget"] = "as much as needed"
        with self.assertRaises(cycle.CycleError):
            garden.prepare_pass(self.config, self.packet, self.registry)

    def test_return_preserves_origin_and_does_not_reenter_unchanged_work(self):
        arrival = self.packet["steps"][1]["arrival"]
        new = {**arrival, "id": "Q18-VOYAGE-2", "payload": {"ref": "new-operating-record"}}
        routed = garden.route_return(arrival, new, "New dated service record")
        self.assertEqual(routed["arrival"]["origin"], arrival)
        self.assertEqual(routed["arrival"]["parent_arrival_id"], arrival["id"])
        third = {**new, "id": "Q18-VOYAGE-3", "payload": {"ref": "third-operating-record"}}
        next_route = garden.route_return(routed["arrival"], third, "More service evidence")
        self.assertEqual(next_route["arrival"]["origin"], arrival)
        self.assertNotIn("origin", new)
        self.assertEqual(garden.route_return(arrival, {**arrival, "id": "NEW-ID"}, "Same data")["status"], "rest")
        self.assertEqual(garden.route_return(arrival, new, "Seen", [new["id"]])["status"], "rest")
        with self.assertRaises(cycle.CycleError):
            garden.route_return(arrival, new)

    def test_word_instances_reproducible_complete_and_separately_preserved(self):
        bank = cycle.read_json(ROOT / "examples/garden/chair-bank.json")
        before = copy.deepcopy(bank)
        first = garden.generate_chair(bank, "jared-1")
        self.assertEqual(first, garden.generate_chair(bank, "jared-1"))
        self.assertEqual(bank, before)
        self.assertEqual(first["bank"], before)
        self.assertEqual({x["id"] for x in first["sequence"]}, {x["id"] for x in bank})
        self.assertEqual(sum(x["word"] == "care" for x in first["sequence"]), 2)
        first["sequence"][0]["word"] = "changed"
        self.assertEqual(bank, before)
        self.assertEqual(first["bank"], before)
        for bad in ([{"id": "SAME", "word": "a"}, {"id": "SAME", "word": "b"}], [{"word": "missing id"}]):
            with self.assertRaises(cycle.CycleError):
                garden.generate_chair(bad, "seed")

    def test_imagination_is_attributed_non_evidence_and_changed_sequence_rejected(self):
        chair = garden.generate_chair([{"id": "WORD-1", "word": "voyage"}], "seed")
        actor = {"name": "Fixture author", "runtime": "test fixture", "model": "none"}
        result = garden.attach_imagination(chair, "Who gets carried?", actor)
        self.assertFalse(result["evidence"])
        self.assertEqual(result["actor"], actor)
        self.assertEqual(result["automatic_actions"], [])
        self.assertEqual(result["chair_sha256"], cycle.digest(chair))
        chair["text"] = "silently changed"
        with self.assertRaises(cycle.CycleError):
            garden.attach_imagination(chair, "Response", actor)

    def test_saved_sequence_cannot_be_overwritten_with_a_new_seed(self):
        bank = [{"id": "WORD-1", "word": "voyage"}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chair.json"
            first = garden.generate_chair(bank, "first")
            garden.save_packet(path, first)
            garden.save_packet(path, first)
            with self.assertRaises(cycle.CycleError):
                garden.save_packet(path, garden.generate_chair(bank, "second"))
            self.assertEqual(cycle.read_json(path), first)


if __name__ == "__main__":
    unittest.main()
