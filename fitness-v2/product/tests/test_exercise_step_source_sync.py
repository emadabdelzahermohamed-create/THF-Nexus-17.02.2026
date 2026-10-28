import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.json"
MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "CATALOG_MANIFEST.json"
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"

SPEC = importlib.util.spec_from_file_location("thf_build_catalog_step_sync", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)

EXPECTED_SOURCE_IDS = {
    "Medicine_Ball_Full_Twist",
    "One-Arm_Medicine_Ball_Slam",
    "Pallof_Press_With_Rotation",
    "Handstand_Push-Ups",
    "Hanging_Leg_Raise",
    "Pullups",
    "Barbell_Bench_Press_-_Medium_Grip",
    "Barbell_Deadlift",
    "Barbell_Shoulder_Press",
    "Pallof_Press",
    "Romanian_Deadlift",
    "Front_Box_Jump",
    "Mountain_Climbers",
    "Overhead_Slam",
    "Air_Bike",
    "Fast_Skipping",
    "Box_Skip",
    "Front_Cone_Hops_or_hurdle_hops",
    "Lateral_Cone_Hops",
    "Side_Hop-Sprint",
    "Freehand_Jump_Squat",
    "Lateral_Bound",
    "Side_to_Side_Box_Shuffle",
    "Bicycling",
    "Bicycling_Stationary",
    "Recumbent_Bike",
    "Linear_Acceleration_Wall_Drill",
    "Single-Cone_Sprint_Drill",
    "Elliptical_Trainer",
    "Rowing_Stationary",
    "Bodyweight_Walking_Lunge",
    "Jogging_Treadmill",
    "Prowler_Sprint",
    "Running_Treadmill",
    "Trail_Running_Walking",
    "Walking_Treadmill",
    "Crunches",
    "Plank",
    "Russian_Twist",
    "Side_Bridge",
    "Superman",
    "Flutter_Kicks",
    "Downward_Facing_Balance",
    "Barbell_Squat",
    "Bent_Over_Barbell_Row",
    "Dumbbell_Bench_Press",
    "Dumbbell_Bicep_Curl",
    "Dumbbell_Shoulder_Press",
    "Parallel_Bar_Dip",
    "Barbell_Hip_Thrust",
    "Dumbbell_Step_Ups",
    "Seated_Cable_Rows",
    "Leg_Press",
    "Dips_-_Triceps_Version",
    "Barbell_Step_Ups",
    "Platform_Hamstring_Slides",
    "Standing_Dumbbell_Calf_Raise",
    "Cable_Crossover",
    "Close-Grip_Front_Lat_Pulldown",
    "Dip_Machine",
    "Face_Pull",
    "Front_Barbell_Squat",
    "Hammer_Curls",
    "Standing_Calf_Raises",
    "Tricep_Dumbbell_Kickback",
    "Triceps_Pushdown_-_Rope_Attachment",
    "Pushups",
    "Single_Leg_Glute_Bridge",
    "90_90_Hamstring",
    "Inchworm",
    "Standing_Hip_Circles",
    "Calves-SMR",
    "Latissimus_Dorsi-SMR",
    "Incline_Dumbbell_Press",
    "Lateral_Raise_-_With_Bands",
    "Leg_Extensions",
    "Leverage_High_Row",
    "Lying_Leg_Curls",
    "Machine_Bench_Press",
    "One-Arm_Dumbbell_Row",
    "Side_Lateral_Raise",
    "Smith_Machine_Bench_Press",
    "Smith_Machine_Squat",
    "Piriformis-SMR",
    "Quadriceps-SMR",
    "External_Rotation_with_Band",
    "Full_Range-Of-Motion_Lat_Pulldown",
    "One_Arm_Lat_Pulldown",
    "Straight-Arm_Dumbbell_Pullover",
    "Medicine_Ball_Chest_Pass",
    "Single-Leg_Lateral_Hop",
    "Dancers_Stretch",
    "Spinal_Stretch",
    "Heavy_Bag_Thrust",
    "Ankle_Circles",
    "Standing_Gastrocnemius_Calf_Stretch",
    "Worlds_Greatest_Stretch",
    "Hamstring-SMR",
    "Iliotibial_Tract-SMR",
    "Runners_Stretch",
    "Dumbbell_Scaption",
    "Cat_Stretch",
    "Childs_Pose",
    "Pelvic_Tilt_Into_Bridge",
    "Step-up_with_Knee_Raise",
    "Medicine_Ball_Scoop_Throw",
}


EXPECTED_ARABIC_NAMES = {
    "Fast_Skipping": "قفز متناوب سريع",
    "Box_Skip": "قفز متتابع بين الصناديق",
    "Barbell_Step_Ups": "صعود الصندوق بالبار",
    "Platform_Hamstring_Slides": "انزلاق الكعبين لثني خلفية الفخذ",
    "Standing_Dumbbell_Calf_Raise": "رفع السمانة واقفًا بالدمبل",
}


class ExerciseStepSourceSyncTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.by_source_id = {item["sourceItemId"]: item for item in cls.catalog}
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_reviewed_step_overrides_are_complete_and_match_generated_catalog(self):
        self.assertEqual(EXPECTED_SOURCE_IDS, set(BUILDER.STEP_OVERRIDES))
        for source_id, expected_steps in BUILDER.STEP_OVERRIDES.items():
            with self.subTest(source_id=source_id):
                self.assertIn(source_id, self.by_source_id)
                self.assertEqual(expected_steps, self.by_source_id[source_id]["steps"])
                self.assertEqual(len(expected_steps["en"]), len(expected_steps["ar"]))
                self.assertGreaterEqual(len(expected_steps["en"]), 2)
                self.assertTrue(all(step.strip() for step in expected_steps["en"]))
                self.assertTrue(all(step.strip() for step in expected_steps["ar"]))

    def test_catalog_manifest_digest_matches_the_checked_in_json(self):
        digest = hashlib.sha256(CATALOG_PATH.read_bytes()).hexdigest()
        self.assertEqual(digest, self.manifest["catalogSha256"])

    def test_reviewed_arabic_titles_match_generated_catalog(self):
        for source_id, expected_name in EXPECTED_ARABIC_NAMES.items():
            with self.subTest(source_id=source_id):
                self.assertEqual(expected_name, self.by_source_id[source_id]["name"]["ar"])

    def test_two_step_core_drills_remain_supported_without_generic_filler(self):
        mountain_climbers = self.by_source_id["Mountain_Climbers"]["steps"]
        self.assertEqual(2, len(mountain_climbers["en"]))
        self.assertEqual(2, len(mountain_climbers["ar"]))
        self.assertNotIn("ابدأ من جذع ثابت وتنفس دون حبس طويل.", mountain_climbers["ar"])
        self.assertNotIn("نفّذ الحركة ببطء ومن دون شد الرقبة.", mountain_climbers["ar"])


if __name__ == "__main__":
    unittest.main()
