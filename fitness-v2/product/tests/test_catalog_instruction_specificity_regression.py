import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.json"
RUNTIME_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.js"
MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "CATALOG_MANIFEST.json"
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"

SOURCE_ID = "Medicine_Ball_Full_Twist"
EXPECTED_MEDICINE_BALL_FULL_TWIST_STEPS = {
    "en": [
        "Stand back-to-back with your partner about 2–3 feet apart, feet hip-width and knees soft. Hold a light medicine ball at chest height.",
        "Brace gently and turn your shoulders and hips together toward the agreed passing side. Let your feet pivot as needed, keep the range comfortable, and avoid twisting only through the lower back.",
        "Pass the ball at chest height without throwing it. Your partner receives it with both hands, then turns smoothly to bring the ball around to the next passing side.",
        "Alternate the passing side on each exchange so both partners rotate to each side. Keep the ball close and your balance steady; stop if either partner feels pain or loses control.",
    ],
    "ar": [
        "قف مع شريكك وظهركما متقابل، على مسافة نحو 60–90 سم، والقدمان بعرض الحوض والركبتان مرتخيتان. أمسك كرة طبية خفيفة عند مستوى الصدر.",
        "شدّ عضلات الجذع برفق وأدر الكتفين والوركين معًا نحو جهة التمرير المتفق عليها. اسمح للقدمين بالدوران عند الحاجة، واختر مدى مريحًا، ولا تحصر الالتواء في أسفل الظهر.",
        "مرّر الكرة عند مستوى الصدر دون قذفها. يستقبلها الشريك بكلتا اليدين، ثم يدور بسلاسة لجلب الكرة إلى جهة التمرير التالية.",
        "بدّلا جهة التمرير في كل تبادل حتى يدور كلاكما إلى الجهتين. أبقيا الكرة قريبة وحافظا على التوازن؛ وتوقفا إذا شعر أحدكما بألم أو فقد السيطرة.",
    ],
}

GENERIC_ENGLISH_FILLER = (
    re.compile(r"\brepeat the procedure\b", re.IGNORECASE),
    re.compile(r"\bperform the (?:amount|number) of repetitions\b", re.IGNORECASE),
    re.compile(r"\bfor a number of repetitions\b", re.IGNORECASE),
)


SPEC = importlib.util.spec_from_file_location("thf_build_catalog_instruction_specificity", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class CatalogInstructionSpecificityRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        raw = RUNTIME_PATH.read_text(encoding="utf-8")
        prefix = "window.THF_EXERCISES = "
        if not raw.startswith(prefix) or not raw.rstrip().endswith(";"):
            raise AssertionError("Runtime catalog wrapper is invalid")
        cls.runtime = json.loads(raw[len(prefix):raw.rfind(";")])
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.by_source_id = {item["sourceItemId"]: item for item in cls.catalog}

    def test_medicine_ball_full_twist_has_coordinated_bilingual_partner_pass_cues(self):
        item = self.by_source_id[SOURCE_ID]
        self.assertEqual(EXPECTED_MEDICINE_BALL_FULL_TWIST_STEPS, item["steps"])
        self.assertEqual(item["steps"], BUILDER.STEP_OVERRIDES[SOURCE_ID])
        self.assertEqual(4, len(item["steps"]["en"]))
        self.assertEqual(len(item["steps"]["en"]), len(item["steps"]["ar"]))
        self.assertIn("feet pivot as needed", item["steps"]["en"][1])
        self.assertIn("اسمح للقدمين بالدوران", item["steps"]["ar"][1])
        self.assertIn("without throwing it", item["steps"]["en"][2])
        self.assertIn("دون قذفها", item["steps"]["ar"][2])
        self.assertNotIn("counter-clockwise", " ".join(item["steps"]["en"]).lower())
        self.assertNotIn("ثبّت القدمين", " ".join(item["steps"]["ar"]))

    def test_generic_repetition_filler_is_absent_from_english_catalog_steps(self):
        offenders = [
            (item["sourceItemId"], index, step)
            for item in self.catalog
            for index, step in enumerate(item["steps"]["en"], start=1)
            if any(pattern.search(step) for pattern in GENERIC_ENGLISH_FILLER)
        ]
        self.assertEqual([], offenders)

    def test_runtime_javascript_payload_matches_generated_json(self):
        self.assertEqual(self.catalog, self.runtime)

    def test_catalog_manifest_digest_matches_exact_json_bytes(self):
        digest = hashlib.sha256(CATALOG_PATH.read_bytes()).hexdigest()
        self.assertEqual(digest, self.manifest["catalogSha256"])


    def test_dancers_stretch_steps_are_bilingual_and_do_not_force_the_knee(self):
        item = self.by_source_id[DANCERS_STRETCH_SOURCE_ID]
        self.assertEqual(EXPECTED_DANCERS_STRETCH_STEPS, item["steps"])
        self.assertEqual(item["steps"], BUILDER.STEP_OVERRIDES[DANCERS_STRETCH_SOURCE_ID])
        self.assertEqual(len(item["steps"]["en"]), len(item["steps"]["ar"]))
        self.assertEqual(len(item["steps"]["en"]), 4)
        self.assertIn("do not pull the knee", item["steps"]["en"][2])
        self.assertIn("لا تسحب الركبة", item["steps"]["ar"][2])
        self.assertIn("Return to center", item["steps"]["en"][3])
        self.assertIn("عد للوسط", item["steps"]["ar"][3])

    def test_standing_hip_circles_uses_controlled_timed_bilingual_steps(self):
        item = self.by_source_id[STANDING_HIP_CIRCLES_SOURCE_ID]
        self.assertEqual(EXPECTED_STANDING_HIP_CIRCLES_STEPS, item["steps"])
        self.assertEqual(item["steps"], BUILDER.STEP_OVERRIDES[STANDING_HIP_CIRCLES_SOURCE_ID])
        self.assertEqual(30, item["prescription"]["durationSeconds"])
        self.assertIsNone(item["prescription"]["reps"])
        self.assertIn("comfortable range", item["steps"]["en"][2])
        self.assertIn("مدى مريح", item["steps"]["ar"][2])
        self.assertNotIn("as far as possible", item["steps"]["en"][2])
        self.assertNotIn("number of repetitions", item["steps"]["en"][3])
        self.assertIn("بدّل الساق", item["steps"]["ar"][3])

    def test_overhead_slam_has_controlled_bilingual_rebound_cues(self):
        item = self.by_source_id[OVERHEAD_SLAM_SOURCE_ID]
        self.assertEqual(EXPECTED_OVERHEAD_SLAM_STEPS, item["steps"])
        self.assertEqual(item["steps"], BUILDER.STEP_OVERRIDES[OVERHEAD_SLAM_SOURCE_ID])
        self.assertEqual(4, len(item["steps"]["en"]))
        self.assertEqual(len(item["steps"]["en"]), len(item["steps"]["ar"]))
        self.assertIn("intended for slams", item["steps"]["en"][0])
        self.assertIn("controlled rather than chasing maximum force", item["steps"]["en"][2])
        self.assertIn("designed to bounce", item["steps"]["en"][3])
        self.assertIn("let it settle", item["steps"]["en"][3])
        self.assertIn("مخصصة للرمي الأرضي", item["steps"]["ar"][0])
        self.assertIn("قوة مضبوطة", item["steps"]["ar"][2])
        self.assertIn("مصممة للارتداد", item["steps"]["ar"][3])
        self.assertIn("اتركها تستقر", item["steps"]["ar"][3])
        self.assertNotIn("as hard as you can", " ".join(item["steps"]["en"]).lower())
        self.assertNotIn("repeat the movement", " ".join(item["steps"]["en"]).lower())

    def test_heavy_bag_thrust_has_controlled_bilingual_thrust_and_recovery_cues(self):
        item = self.by_source_id[HEAVY_BAG_THRUST_SOURCE_ID]
        self.assertEqual(EXPECTED_HEAVY_BAG_THRUST_STEPS, item["steps"])
        self.assertEqual(item["steps"], BUILDER.STEP_OVERRIDES[HEAVY_BAG_THRUST_SOURCE_ID])
        self.assertEqual(len(item["steps"]["en"]), 3)
        self.assertEqual(len(item["steps"]["en"]), len(item["steps"]["ar"]))
        self.assertIn("allowing the feet to pivot naturally", item["steps"]["en"][1])
        self.assertIn("السماح للقدمين بالدوران الطبيعي", item["steps"]["ar"][1])
        self.assertIn("Stop if you feel wrist, shoulder, or back pain.", item["steps"]["en"][2])
        self.assertIn("توقف إذا شعرت بألم في الرسغ أو الكتف أو الظهر", item["steps"]["ar"][2])
        self.assertNotIn("as hard as possible", " ".join(item["steps"]["en"]).lower())

if __name__ == "__main__":
    unittest.main()
