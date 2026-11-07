import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CATALOG_JSON = ROOT / "fitness-v2/android/app/src/main/assets/pulse/data/exercises.json"
CATALOG_JS = ROOT / "fitness-v2/android/app/src/main/assets/pulse/data/exercises.js"
MANIFEST = ROOT / "fitness-v2/product/CATALOG_MANIFEST.json"
BUILDER = ROOT / "fitness-v2/product/tools/build_catalog.py"

EXPECTED = {
    "One-Arm_Medicine_Ball_Slam": {
        "setup_ar": "أخلِ منطقة الرمي، وقف بوقفة متدرجة ثابتة، وأمسك كرة طبية مناسبة بيد واحدة.",
        "steps_ar": [
            "قف بوقفة متدرجة ثابتة، وأمسك الكرة بيد واحدة على جهة الساق الخلفية.",
            "ارفع الكرة فوق الرأس مع مد الوركين والركبتين، ثم اضربها في الأرض أمامك بثني الوركين والجذع بتحكم.",
            "التقط ارتداد الكرة فقط إذا كان آمنًا، ثم كرر من دون فقدان التوازن.",
        ],
    },
    "Pallof_Press_With_Rotation": {
        "setup_ar": "ثبّت الكابل عند مستوى الصدر، وقف بجانب الجهاز بقدمين بعرض الورك، وأمسك المقبض بكلتا اليدين.",
        "steps_ar": [
            "اسحب المقبض إلى الصدر ثم مد الذراعين أمامك مع شد الجذع.",
            "أدر الجذع ببطء بعيدًا عن البكرة نحو ربع دورة، مع بقاء القدمين والحوض ثابتين.",
            "عد إلى مواجهة الأمام بتحكم، ثم أعد المقبض إلى الصدر وكرر للجهة الأخرى.",
        ],
    },
    "Hanging_Leg_Raise": {
        "setup_ar": "تأكد من ثبات العقلة والقبضة، وتعلّق بذراعين ممدودتين مع إرخاء الكتفين بعيدًا عن الأذنين.",
        "steps_ar": [
            "ابدأ من تعليق ثابت، مع شد البطن ومنع التأرجح.",
            "ارفع الساقين أمامك حتى يرتفع الفخذان إلى مستوى الورك تقريبًا، من دون تقويس أسفل الظهر.",
            "اخفض الساقين ببطء إلى وضع البداية، وحافظ على التحكم قبل التكرار التالي.",
        ],
    },
    "Air_Bike": {
        "setup_ar": "استلقِ على ظهرك، اثنِ الركبتين وارفع الكتفين قليلًا، وضع اليدين بخفة بجانب الرأس.",
        "steps_ar": [
            "قرّب المرفق الأيمن نحو الركبة اليسرى مع مد الساق اليمنى، من دون سحب الرقبة باليدين.",
            "بدّل الجانبين كحركة بدّال: قرّب المرفق الأيسر من الركبة اليمنى ومد الساق اليسرى.",
            "حافظ على أسفل الظهر ملامسًا للأرض بقدر مريح، وخفّض المدى إذا فقدت التحكم.",
        ],
    },
}


class ArabicMovementCueRegression(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
        self.by_source = {item["sourceItemId"]: item for item in self.catalog}

    def test_four_movements_have_specific_arabic_setup_and_steps(self):
        for source_id, expected in EXPECTED.items():
            with self.subTest(source_id=source_id):
                item = self.by_source[source_id]
                self.assertEqual(item["setup"]["ar"], expected["setup_ar"])
                self.assertEqual(item["steps"]["ar"], expected["steps_ar"])
                self.assertEqual(len(item["steps"]["ar"]), 3)
                self.assertTrue(all(step.strip() for step in item["steps"]["ar"]))
                self.assertNotEqual(item["steps"]["ar"], [
                    "ابدأ من جذع ثابت وتنفس دون حبس طويل.",
                    "نفّذ الحركة ببطء ومن دون شد الرقبة.",
                    "توقف قبل فقدان وضع الحوض أو أسفل الظهر.",
                ])

    def test_runtime_javascript_payload_matches_json(self):
        source = CATALOG_JS.read_text(encoding="utf-8")
        prefix = "window.THF_EXERCISES = "
        self.assertTrue(source.startswith(prefix))
        runtime = json.loads(source[len(prefix):].strip().rstrip(";"))
        self.assertEqual(runtime, self.catalog)

    def test_catalog_manifest_matches_exact_json_bytes(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        digest = hashlib.sha256(CATALOG_JSON.read_bytes()).hexdigest()
        self.assertEqual(manifest["catalogSha256"], digest)
        self.assertEqual(manifest["exerciseCount"], len(self.catalog))
        self.assertEqual(len({item["id"] for item in self.catalog}), len(self.catalog))

    def test_builder_keeps_overrides_durable_and_validated(self):
        builder = BUILDER.read_text(encoding="utf-8")
        self.assertIn("ARABIC_INSTRUCTION_OVERRIDES = {", builder)
        self.assertIn("instruction_override = ARABIC_INSTRUCTION_OVERRIDES.get(source_id, {})", builder)
        self.assertIn('instruction_override.get("setup_ar", family["setup_ar"])', builder)
        self.assertIn('instruction_override.get("steps_ar", family["steps_ar"])', builder)
        self.assertIn("validate_arabic_instruction_overrides()", builder)


if __name__ == "__main__":
    unittest.main()
