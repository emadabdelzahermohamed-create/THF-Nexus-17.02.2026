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
    "Dip_Machine": {
        "setup_ar": "اضبط المقعد والمقاومة بحيث تبدأ والمرفقان بجوار الجذع، وثبّت الظهر والقدمين قبل الدفع.",
        "steps_ar": [
            "اجلس بثبات على جهاز المتوازي، واضبط المقاومة، ثم أمسك المقبضين بقبضة كاملة.",
            "أبقِ المرفقين بجوار الجذع واثنهما إلى زاوية مريحة تقارب 90 درجة، مع بقاء الرسغين بمحاذاة الساعدين.",
            "ازفر ومد المرفقين لدفع المقبضين إلى أسفل، وتوقف قبل قفل المرفقين مع استمرار شد الترايسبس.",
            "خذ شهيقًا وأعد المقبضين ببطء إلى وضع البداية، دون ارتداد أو ترك الأوزان تصطدم.",
            "كرر العدد المحدد، وخفّف المقاومة أو توقف إذا ظهر ألم في الكتف أو المرفق."
        ],
    },
    "Front_Barbell_Squat": {
        "setup_ar": "اضبط حوامل الرف على ارتفاع يسمح بإخراج البار بأمان، وضعه على مقدمة الكتفين مع إبقاء المرفقين مرتفعين.",
        "steps_ar": [
            "قف داخل رف القرفصاء واضبط البار على ارتفاع مناسب؛ ارفع المرفقين وضع البار على مقدمة الكتفين بقبضة أمامية ثابتة أو متقاطعة مريحة.",
            "شد الجذع وادفع الأرض بالقدمين لرفع البار من الحوامل، ثم تراجع بخطوات قصيرة إلى مساحة خالية.",
            "اجعل القدمين بعرض الكتفين تقريبًا وأصابع القدم للخارج قليلًا، وثبّت القدم كاملة مع إبقاء المرفقين مرتفعين.",
            "خذ شهيقًا وانزل بثني الوركين والركبتين مع بقاء الجذع منتصبًا وتتبع الركبتين لاتجاه أصابع القدم؛ توقف عند عمق يمكنك التحكم فيه دون ارتفاع الكعب.",
            "ازفر وادفع الأرض بمنتصف القدم للعودة إلى الوقوف، مع ثبات الجذع وعدم قفل الركبتين بعنف.",
            "كرر العدد المحدد، ثم أعد البار إلى الحوامل بثبات بعد إكمال المجموعة."
        ],
    },
}


def load_runtime_catalog():
    text = CATALOG_JS.read_text(encoding="utf-8")
    prefix = "window.THF_EXERCISES = "
    if not text.startswith(prefix):
        raise AssertionError("unexpected runtime catalog prefix")
    payload = text[len(prefix):].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    return json.loads(payload)


class FrontSquatAndDipMachineInstructionTests(unittest.TestCase):
    def test_generated_runtime_catalog_and_manifest_stay_in_sync(self):
        generated = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
        self.assertEqual(load_runtime_catalog(), generated)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["exerciseCount"], len(generated))
        self.assertEqual(hashlib.sha256(CATALOG_JSON.read_bytes()).hexdigest(), manifest["catalogSha256"])

    def test_two_targets_have_specific_arabic_setup_and_step_parity(self):
        catalog = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
        for source_id, expected in EXPECTED.items():
            with self.subTest(source_id=source_id):
                item = next((x for x in catalog if x["sourceItemId"] == source_id), None)
                self.assertIsNotNone(item)
                self.assertEqual(item["setup"]["ar"], expected["setup_ar"])
                self.assertEqual(item["steps"]["ar"], expected["steps_ar"])
                self.assertEqual(len(item["steps"]["ar"]), len(item["steps"]["en"]))
                self.assertEqual(len(item["steps"]["ar"]), len(expected["steps_ar"]))
                self.assertTrue(all(step.strip() for step in item["steps"]["ar"]))

    def test_builder_preserves_both_arabic_overrides(self):
        builder = BUILDER.read_text(encoding="utf-8")
        self.assertIn("ARABIC_INSTRUCTION_OVERRIDES = {", builder)
        for source_id in EXPECTED:
            self.assertIn(f'"{source_id}": {{', builder)
        self.assertIn('instruction_override.get("setup_ar", family["setup_ar"])', builder)
        self.assertIn('instruction_override.get("steps_ar", family["steps_ar"])', builder)


if __name__ == "__main__":
    unittest.main()
