import importlib.util
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
