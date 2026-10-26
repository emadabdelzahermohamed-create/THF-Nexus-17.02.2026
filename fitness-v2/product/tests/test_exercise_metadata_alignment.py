import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"
SPEC = importlib.util.spec_from_file_location("thf_build_catalog", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


EXPECTED_MOVEMENTS = {
    "Leg_Extensions": "isolation",
    "Incline_Dumbbell_Press": "horizontal_push",
    "Side_Bridge": "core",
    "Flutter_Kicks": "core",
    "Downward_Facing_Balance": "core",
    "Superman": "core",
    "Mountain_Climbers": "core",
    "Linear_Acceleration_Wall_Drill": "locomotion",
    "Straight-Arm_Dumbbell_Pullover": "horizontal_pull",
    "One-Arm_Medicine_Ball_Slam": "core",
    "Overhead_Slam": "core",
}


class ExerciseMetadataAlignmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog = json.loads((PULSE / "data" / "exercises.json").read_text())
        cls.by_source_id = {item["sourceItemId"]: item for item in catalog}

    def test_displayed_movement_matches_the_corrected_exercise_family(self):
        for source_id, movement in EXPECTED_MOVEMENTS.items():
            with self.subTest(source_id=source_id):
                self.assertEqual(movement, self.by_source_id[source_id]["movement"]["id"])
                self.assertEqual(
                    movement,
                    BUILDER.pattern_for({"id": source_id}),
                    "the generator must preserve the corrected classification",
                )

    def test_hold_drill_and_throw_prescriptions_match_how_they_are_performed(self):
        for source_id in ("Side_Bridge", "Downward_Facing_Balance"):
            prescription = self.by_source_id[source_id]["prescription"]
            self.assertIsNone(prescription["reps"])
            self.assertGreaterEqual(prescription["durationSeconds"], 20)

        for source_id in ("Mountain_Climbers", "Linear_Acceleration_Wall_Drill"):
            prescription = self.by_source_id[source_id]["prescription"]
            self.assertLessEqual(prescription["durationSeconds"] or 0, 60)
            self.assertGreaterEqual(prescription["sets"], 3)

        for source_id in BUILDER.THROW_GUIDANCE_IDS:
            prescription = self.by_source_id[source_id]["prescription"]
            self.assertEqual("5–8", prescription["reps"])
            self.assertIn("explosive", prescription["tempo"])

    def test_bodyweight_core_corrections_do_not_request_load_tracking(self):
        loadless = {
            "Side_Bridge", "Flutter_Kicks", "Downward_Facing_Balance",
            "Superman", "Mountain_Climbers", "Linear_Acceleration_Wall_Drill",
        }
        for source_id in loadless:
            with self.subTest(source_id=source_id):
                self.assertFalse(self.by_source_id[source_id]["tracking"]["load"])


if __name__ == "__main__":
    unittest.main()
