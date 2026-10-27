import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_programs.py"
SPEC = importlib.util.spec_from_file_location("thf_build_programs", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class ProgramProgressionTest(unittest.TestCase):
    def test_four_week_plan_uses_a_single_week_label(self):
        progression = BUILDER.progression_for("mobility", 4, "beginner")

        self.assertIn("Week 2:", progression["en"][1])
        self.assertNotIn("Weeks 2–2", progression["en"][1])
        self.assertIn("الأسبوع 2:", progression["ar"][1])
        self.assertNotIn("الأسابيع 2–2", progression["ar"][1])

    def test_progression_matches_the_program_training_family(self):
        strength = BUILDER.progression_for("gym", 6, "beginner")
        endurance = BUILDER.progression_for("running", 6, "beginner")
        conditioning = BUILDER.progression_for("hiit", 6, "intermediate")
        mobility = BUILDER.progression_for("recovery", 4, "beginner")

        self.assertIn("2–5% load", " ".join(strength["en"]))
        self.assertIn("الحمل 2–5%", " ".join(strength["ar"]))

        self.assertIn("10%", " ".join(endurance["en"]))
        self.assertIn("الزمن أو المسافة", " ".join(endurance["ar"]))

        self.assertIn("one round or interval", " ".join(conditioning["en"]))
        self.assertIn("جولة أو فترة واحدة", " ".join(conditioning["ar"]))

        self.assertIn("5–10 seconds", " ".join(mobility["en"]))
        self.assertIn("الألم", " ".join(mobility["ar"]))

        for progression in (endurance, conditioning, mobility):
            self.assertNotIn("load", " ".join(progression["en"]).lower())
            self.assertNotIn("الحمل", " ".join(progression["ar"]))

    def test_long_source_duration_blocks_fit_session_time_budgets(self):
        source_catalog = json.loads(BUILDER.EXERCISES_PATH.read_text(encoding="utf-8"))
        source_by_id = {item["id"]: item["prescription"] for item in source_catalog}
        adjusted = 0

        for program in BUILDER.build():
            for session in program["sessions"]:
                planned_timed_seconds = 0
                for entry in session["exercises"]:
                    source_duration = source_by_id[entry["exerciseId"]].get("durationSeconds")
                    if source_duration is not None and int(source_duration) >= 600:
                        adjusted += 1
                        self.assertEqual(1, entry["sets"])
                        self.assertEqual(
                            300 if entry["role"] == "warmup" else 600,
                            entry["durationSeconds"],
                        )
                    if entry["durationSeconds"] is not None:
                        planned_timed_seconds += int(entry["sets"]) * int(entry["durationSeconds"])

                self.assertLessEqual(
                    planned_timed_seconds,
                    int(session["estimatedMinutes"]) * 60,
                    f"{program['id']}/{session['id']} timed work exceeds its advertised session estimate",
                )

        self.assertGreater(adjusted, 0)

    def test_checked_in_program_json_js_and_manifest_stay_in_sync(self):
        json_text = BUILDER.PROGRAMS_PATH.read_text(encoding="utf-8")
        checked_in = json.loads(json_text)
        generated = BUILDER.build()
        self.assertEqual(generated, checked_in)

        js_text = BUILDER.PROGRAMS_JS_PATH.read_text(encoding="utf-8")
        js_payload = js_text.partition("=")[2].strip()
        self.assertTrue(js_payload.endswith(";"))
        self.assertEqual(checked_in, json.loads(js_payload[:-1].rstrip()))

        manifest = json.loads(BUILDER.MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            hashlib.sha256(json_text.encode("utf-8")).hexdigest(),
            manifest["programsSha256"],
        )

    def test_every_program_uses_its_section_progression(self):
        programs = BUILDER.build()

        for program in programs:
            with self.subTest(program=program["id"]):
                self.assertEqual(
                    BUILDER.progression_for(
                        program["section"]["id"],
                        program["weeks"],
                        program["level"]["id"],
                    ),
                    program["progression"],
                )


if __name__ == "__main__":
    unittest.main()
