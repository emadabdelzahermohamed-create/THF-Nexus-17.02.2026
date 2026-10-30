import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
EXERCISES = json.loads((PULSE / "data" / "exercises.json").read_text(encoding="utf-8"))
PROGRAMS = json.loads((PULSE / "data" / "programs.json").read_text(encoding="utf-8"))
PROGRAMS_JS = (PULSE / "data" / "programs.js").read_text(encoding="utf-8")
APP_JS = (PULSE / "app.js").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "fitness-v2" / "product" / "PROGRAMS_MANIFEST.json").read_text(encoding="utf-8"))

BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_programs.py"
SPEC = importlib.util.spec_from_file_location("thf_build_programs", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class ProgramDurationCatalogParityTest(unittest.TestCase):
    def test_catalog_timed_exercises_remain_timed_in_every_program_reference(self):
        by_id = {item["id"]: item for item in EXERCISES}
        mismatches = []
        for program in PROGRAMS:
            for session in program["sessions"]:
                for reference in session["exercises"]:
                    exercise = by_id[reference["exerciseId"]]
                    duration = exercise["prescription"].get("durationSeconds")
                    if duration:
                        if reference.get("durationSeconds") != duration or reference.get("reps") is not None:
                            mismatches.append((program["id"], session["id"], reference["exerciseId"]))
        self.assertEqual(mismatches, [])

    def test_program_only_superman_holds_are_explicit_and_preserved(self):
        expected = {
            ("home-progressive-strength", 3, "superman"): 30,
            ("home-progressive-strength", 4, "superman"): 30,
            ("calisthenics-foundations", 1, "superman"): 30,
            ("calisthenics-foundations", 2, "superman"): 30,
            ("calisthenics-skills", 1, "superman"): 30,
            ("boxing-power-core", 4, "superman"): 30,
        }
        self.assertEqual(BUILDER.PROGRAM_DURATION_OVERRIDES, expected)
        for (program_id, session_number, exercise_id), duration in expected.items():
            program = next(item for item in PROGRAMS if item["id"] == program_id)
            session = program["sessions"][session_number - 1]
            reference = next(item for item in session["exercises"] if item["exerciseId"] == exercise_id)
            self.assertEqual(reference["durationSeconds"], duration)
            self.assertIsNone(reference["reps"])

    def test_catalog_rep_doses_match_every_non_timed_program_reference(self):
        by_id = {item["id"]: item for item in EXERCISES}
        mismatches = []
        for program in PROGRAMS:
            for session in program["sessions"]:
                for reference in session["exercises"]:
                    exercise = by_id[reference["exerciseId"]]
                    if reference.get("durationSeconds") is not None:
                        continue  # Explicit timed holds are covered by the duration tests above.
                    expected_reps = exercise["prescription"].get("reps")
                    if expected_reps is not None and reference.get("reps") != expected_reps:
                        mismatches.append((
                            program["id"], session["id"], reference["exerciseId"],
                            reference.get("reps"), expected_reps,
                        ))
        self.assertEqual([], mismatches)

    def test_program_builder_preserves_catalog_rep_doses(self):
        generated = BUILDER.build()
        by_id = {item["id"]: item for item in EXERCISES}
        mismatches = []
        for program in generated:
            for session in program["sessions"]:
                for reference in session["exercises"]:
                    if reference.get("durationSeconds") is not None:
                        continue
                    expected_reps = by_id[reference["exerciseId"]]["prescription"].get("reps")
                    if expected_reps is not None and reference.get("reps") != expected_reps:
                        mismatches.append((
                            program["id"], session["id"], reference["exerciseId"],
                            reference.get("reps"), expected_reps,
                        ))
        self.assertEqual([], mismatches)

    def test_program_builder_keeps_catalog_timed_doses(self):
        generated = BUILDER.build()
        by_id = {item["id"]: item for item in EXERCISES}
        for program in generated:
            for session in program["sessions"]:
                for reference in session["exercises"]:
                    duration = by_id[reference["exerciseId"]]["prescription"].get("durationSeconds")
                    if duration:
                        self.assertEqual(reference["durationSeconds"], duration)
                        self.assertIsNone(reference["reps"])

    def test_runtime_js_and_json_payloads_match(self):
        runtime = json.loads(PROGRAMS_JS.split("=", 1)[1].strip().removesuffix(";"))
        self.assertEqual(runtime, PROGRAMS)

    def test_manifest_hash_matches_exact_program_json_bytes(self):
        digest = hashlib.sha256((PULSE / "data" / "programs.json").read_bytes()).hexdigest()
        self.assertEqual(MANIFEST["programsSha256"], digest)
        self.assertEqual(MANIFEST["programCount"], len(PROGRAMS))

    def test_timed_prescriptions_do_not_publish_repetitions_in_reserve(self):
        timed = [
            reference
            for program in PROGRAMS
            for session in program["sessions"]
            for reference in session["exercises"]
            if reference.get("durationSeconds") is not None
        ]
        repetition_based = [
            reference
            for program in PROGRAMS
            for session in program["sessions"]
            for reference in session["exercises"]
            if reference.get("durationSeconds") is None
        ]
        self.assertGreater(len(timed), 0)
        self.assertTrue(all(reference.get("targetRir") is None for reference in timed))
        self.assertTrue(all(reference.get("targetRir") is not None for reference in repetition_based))

    def test_builder_only_assigns_rir_to_repetition_based_prescriptions(self):
        generated = BUILDER.build()
        for program in generated:
            for session in program["sessions"]:
                for reference in session["exercises"]:
                    if reference.get("durationSeconds") is not None:
                        self.assertIsNone(reference.get("targetRir"))
                    else:
                        self.assertIsNotNone(reference.get("targetRir"))

    def test_program_detail_formats_rir_only_for_repetition_based_work(self):
        self.assertIn("const timed = Number(reference.durationSeconds) > 0;", APP_JS)
        self.assertIn("const rir = !timed && reference.targetRir !== null", APP_JS)
        self.assertIn("const rest = Number(reference.sets) > 1 && Number(reference.restSeconds) > 0", APP_JS)

if __name__ == "__main__":
    unittest.main()
