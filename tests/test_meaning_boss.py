from pathlib import Path
import copy
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cycle
import garden
import meaning_boss

ROOT = Path(__file__).resolve().parents[1]


def packet_fixture():
    """Synthetic wording for contract tests; not an empirical Boss Packet."""
    source = {"title": "Synthetic notice", "language": "en", "publication_date": "2026-09-01",
              "observation_date": "2026-09-01", "retrieved_at": "2026-09-25T21:00:00Z",
              "access_limitations": ["Synthetic test fixture; not public evidence."]}
    rounds = []
    for index, kind in enumerate(("control", "residual")):
        rounds.append({"id": f"ROUND-{index}", "kind": kind, "title": "A fixture comparison",
                       "prompt": "What deserves attention?", "context": "No empirical claim is made.",
                       "originals": [{"source_id": "SOURCE-1", "text": "Fixture words", "english_pivot": "Fixture words"}],
                       "pieces": [{"id": f"PIECE-{index}-A", "text": "Carry the question", "note": "A question remains open.",
                                   "evidence_status": "question", "source_refs": ["SOURCE-1"]},
                                  {"id": f"PIECE-{index}-B", "text": "Preserve the statement", "note": "A synthetic source statement.",
                                   "evidence_status": "source_statement", "source_refs": ["SOURCE-2"]}]})
    return {"schema_version": meaning_boss.PACKET_VERSION, "packet_id": "TEST-PACKET-1",
            "boss_id": "THE-UNRESOLVED", "packet_status": "evidence_backed",
            "question_id": meaning_boss.QUESTION, "epoch": 1, "title": "Synthetic encounter",
            "created_at": "2026-09-25T21:01:00Z", "actor": {"name": "Fixture", "runtime": "unittest", "model": "none"},
            "source_ledger": [{**source, "source_id": "SOURCE-1", "url": "https://example.gov/notice"},
                              {**source, "source_id": "SOURCE-2", "url": "https://example.gov/summary"}],
            "comparison": {"kind": "official_notice_and_summary", "summary": "Testing the contract only.",
                           "ordinary_explanations": ["Summary versus full notice."], "limitations": ["Synthetic sources."]},
            "cross": {"inherited": ["SOURCE-1", "SOURCE-2"], "independent": [], "bridge": []},
            "rounds": rounds, "power_candidate": {"id": "PECULIARITY_SENSE", "text": "A proposed power.", "canonical_status": "proposed"}}


def result_fixture(packet):
    return {"schema_version": meaning_boss.RESULT_VERSION, "packet_id": packet["packet_id"],
            "packet_sha256": cycle.digest(packet), "play_id": "TEST-PLAY-1",
            "actor": {"name": "Unverified fixture player", "runtime": "test browser"},
            "completed_at": "2026-09-25T21:05:00Z", "completion_status": "completed",
            "choices": [{"round_id": item["id"], "preserved_id": item["pieces"][0]["id"],
                         "held_ms": 2000, "input_method": "pointer"} for item in packet["rounds"]],
            "power_decision": "pending_review", "evidence_changed": False}


class MeaningBossTests(unittest.TestCase):
    def setUp(self):
        self.packet = packet_fixture()
        self.result = result_fixture(self.packet)
        self.registry = {"questions": {meaning_boss.QUESTION: {"epoch": 1}}}
        self.config = garden.load_config(ROOT)

    def test_deterministic_validation_returns_separate_copy(self):
        before = copy.deepcopy(self.packet)
        first = meaning_boss.validate_packet(self.packet, self.registry)
        self.assertEqual(first, meaning_boss.validate_packet(self.packet, self.registry))
        first["rounds"][0]["pieces"][0]["text"] = "Changed copy"
        self.assertEqual(self.packet, before)

    def test_current_question_and_integer_epoch_required(self):
        for change in ({"question_id": "Q-INVENTED"}, {"epoch": 2}, {"epoch": True}):
            with self.subTest(change=change), self.assertRaises(cycle.CycleError):
                meaning_boss.validate_packet({**self.packet, **change}, self.registry)

    def test_source_urls_dates_and_unknown_date_explanation(self):
        for field, value in (("url", "http://example.gov/notice"), ("url", "https://127.0.0.1/x"),
                             ("url", "https://a.local/x"), ("url", "https://user:secret@example.gov/x"),
                             ("publication_date", "2026-02-30"), ("retrieved_at", "2026-09-25T21:00:00")):
            packet = copy.deepcopy(self.packet)
            packet["source_ledger"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(cycle.CycleError):
                meaning_boss.validate_packet(packet, self.registry)
        self.packet["source_ledger"][0]["observation_date"] = None
        meaning_boss.validate_packet(self.packet, self.registry)
        self.packet["source_ledger"][0]["access_limitations"] = []
        with self.assertRaises(cycle.CycleError):
            meaning_boss.validate_packet(self.packet, self.registry)

    def test_score_truth_updates_and_oversized_packets_rejected(self):
        for extra in ({"score": 3}, {"truth_changes": []}, {"title": "x" * 100000}):
            with self.subTest(extra=list(extra)), self.assertRaises(cycle.CycleError):
                meaning_boss.validate_packet({**self.packet, **extra}, self.registry)
        self.packet["rounds"][0]["pieces"][0]["score"] = 1
        with self.assertRaises(cycle.CycleError):
            meaning_boss.validate_packet(self.packet, self.registry)

    def test_control_required_and_duplicate_or_unknown_references_rejected(self):
        variants = []
        packet = copy.deepcopy(self.packet)
        packet["rounds"][0]["kind"] = "residual"
        variants.append(packet)
        packet = copy.deepcopy(self.packet)
        packet["rounds"][1]["pieces"][0]["id"] = packet["rounds"][0]["pieces"][0]["id"]
        variants.append(packet)
        packet = copy.deepcopy(self.packet)
        packet["rounds"][0]["pieces"][0]["source_refs"] = ["MISSING"]
        variants.append(packet)
        packet = copy.deepcopy(self.packet)
        packet["rounds"][0]["pieces"][1]["source_refs"] = []
        variants.append(packet)
        for index, packet in enumerate(variants):
            with self.subTest(index=index), self.assertRaises(cycle.CycleError):
                meaning_boss.validate_packet(packet, self.registry)

    def test_result_hash_binds_text_and_evidence_status(self):
        for field, value in (("text", "Altered words"), ("evidence_status", "unknown")):
            packet = copy.deepcopy(self.packet)
            packet["rounds"][0]["pieces"][0][field] = value
            with self.subTest(field=field), self.assertRaises(cycle.CycleError):
                meaning_boss.validate_result(packet, self.result, self.registry)
        self.result["evidence_changed"] = True
        with self.assertRaises(cycle.CycleError):
            meaning_boss.validate_result(self.packet, self.result, self.registry)

    def test_choices_must_be_complete_unique_in_order_and_in_round(self):
        choices = self.result["choices"]
        variants = [choices[:1], choices + choices[:1], list(reversed(choices)), [choices[0], choices[0]],
                    [{**choices[0], "preserved_id": "MISSING"}, choices[1]],
                    [{**choices[0], "preserved_id": choices[1]["preserved_id"]}, choices[1]]]
        for variant in variants:
            with self.subTest(choices=variant), self.assertRaises(cycle.CycleError):
                meaning_boss.validate_result(self.packet, {**self.result, "choices": variant}, self.registry)

    def test_hold_and_input_method_reported_explicitly(self):
        for field, value in (("held_ms", 1899), ("held_ms", 600001), ("held_ms", True), ("input_method", "imagined")):
            result = copy.deepcopy(self.result)
            result["choices"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(cycle.CycleError):
                meaning_boss.validate_result(self.packet, result, self.registry)
        for method in ("pointer", "keyboard", "assist"):
            self.result["choices"][0]["input_method"] = method
            meaning_boss.validate_result(self.packet, self.result, self.registry)

    def test_no_power_still_delivers_every_piece_without_changing_evidence(self):
        before = copy.deepcopy((self.packet, self.result, self.registry, self.config))
        delivery = meaning_boss.make_delivery(self.packet, self.result, self.registry, self.config)
        self.assertEqual(delivery, meaning_boss.make_delivery(self.packet, self.result, self.registry, self.config))
        self.assertEqual(delivery["applied_powers"], [])
        self.assertEqual(delivery["selection_before_powers"], delivery["selection_after_powers"])
        self.assertEqual(delivery["event_order"][-2:], ["power_application", "governor_delivery"])
        for original, round_delivery in zip(self.packet["rounds"], delivery["rounds"]):
            self.assertEqual(round_delivery["preserved"], original["pieces"][0])
            self.assertEqual(round_delivery["sunk"], [{**original["pieces"][1], "attention_status": "not_selected_not_false"}])
        self.assertFalse(delivery["evidence_changed"])
        self.assertFalse(delivery["canonical_admission"])
        self.assertFalse(delivery["human_identity_verified"])
        self.assertEqual(delivery["input_origin"], "client_report")
        self.assertEqual((self.packet, self.result, self.registry, self.config), before)

    def test_power_candidate_optional_and_never_awarded(self):
        self.packet["power_candidate"] = None
        self.result = result_fixture(self.packet)
        delivery = meaning_boss.make_delivery(self.packet, self.result, self.registry, self.config)
        self.assertIsNone(delivery["power_candidate"])
        self.assertEqual(delivery["applied_powers"], [])
        self.result["power_decision"] = "canonical"
        with self.assertRaises(cycle.CycleError):
            meaning_boss.make_delivery(self.packet, self.result, self.registry, self.config)
        self.packet["power_candidate"] = {"id": "PECULIARITY_SENSE", "text": "Test", "canonical_status": "canonical"}
        with self.assertRaises(cycle.CycleError):
            meaning_boss.validate_packet(self.packet, self.registry)

    def test_stable_route_registered_without_scheduling_or_execution(self):
        role = cycle.read_json(ROOT / "agents/parallax_collector_bee.json")
        self.assertEqual(role["status"], "available_role_definition_not_running")
        self.assertFalse(role["runtime"]["scheduled"])
        self.assertFalse(role["runtime"]["autonomous"])
        for destination in meaning_boss.ROUTE:
            self.assertEqual(garden.resolve(self.config, destination)["status"], "resolved")
        delivery = meaning_boss.make_delivery(self.packet, self.result, self.registry, self.config)
        self.assertEqual(delivery["route"]["to"], "INIT:RETURN-0010")
        self.assertFalse(delivery["route"]["automatic_execution"])
        del self.config["trees"]["PYGENT"]
        with self.assertRaises(cycle.CycleError):
            meaning_boss.make_delivery(self.packet, self.result, self.registry, self.config)


if __name__ == "__main__":
    unittest.main()
