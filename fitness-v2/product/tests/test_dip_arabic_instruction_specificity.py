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
    "Dips_-_Triceps_Version": {
        "setup_ar": "أمسك عارضتي المتوازي بقبضة ثابتة، وارفع جسمك إلى أعلى مع تثبيت لوحي الكتف والرسغين.",
        "steps_ar": [
            "ابدأ من أعلى المتوازي بذراعين شبه ممدودتين، واجعل الكتفين بعيدين عن الأذنين.",
            "خذ شهيقًا وانزل ببطء مع إبقاء الجذع منتصبًا والمرفقين قريبين من الجسم؛ توقف عند عمق مريح للكتفين.",
            "ازفر وادفع عبر راحتي اليدين لمد المرفقين والعودة إلى أعلى دون قفل عنيف.",
            "كرر العدد المحدد دون ارتداد، مع ثبات الرسغين والتحكم في كل نزول."
        ]
    },
    "Parallel_Bar_Dip": {
        "setup_ar": "قف بين عارضتين ثابتتين، أمسك كل عارضة بقبضة كاملة، وتأكد من ثباتهما قبل رفع القدمين.",
        "steps_ar": [
            "ارفع جسمك إلى أعلى المتوازي بذراعين ممدودتين، مع تثبيت الكتفين والجذع.",
            "اثنِ المرفقين وانزل بتحكم حتى يقترب العضدان من الموازي للأرض، دون تأرجح أو دفع الكتفين للأمام.",
            "ادفع عبر راحتي اليدين ومد المرفقين للعودة إلى أعلى، مع بقاء الجذع ثابتًا.",
            "كرر العدد المحدد، وتوقف إذا فقدت القبضة أو ظهر ألم بالكتف."
        ]
    }
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


class DipArabicInstructionSpecificityTests(unittest.TestCase):
    def test_generated_runtime_catalog_and_manifest_stay_in_sync(self):
        generated = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
        self.assertEqual(load_runtime_catalog(), generated)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["exerciseCount"], len(generated))
        self.assertEqual(hashlib.sha256(CATALOG_JSON.read_bytes()).hexdigest(), manifest["catalogSha256"])

    def test_dip_variants_have_specific_four_step_arabic_guidance(self):
        catalog = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
        for source_id, expected in EXPECTED.items():
            with self.subTest(source_id=source_id):
                item = next((x for x in catalog if x["sourceItemId"] == source_id), None)
                self.assertIsNotNone(item)
                self.assertEqual(item["setup"]["ar"], expected["setup_ar"])
                self.assertEqual(item["steps"]["ar"], expected["steps_ar"])
                self.assertEqual(len(item["steps"]["ar"]), len(item["steps"]["en"]))
                self.assertEqual(len(item["steps"]["ar"]), 4)
                self.assertNotIn("اخفض الحمل أو الجسم بتحكم حتى مدى مريح.", item["steps"]["ar"])

    def test_builder_keeps_the_dip_overrides_reproducible(self):
        builder = BUILDER.read_text(encoding="utf-8")
        self.assertIn("ARABIC_INSTRUCTION_OVERRIDES", builder)
        self.assertIn('instruction_override.get("setup_ar", family["setup_ar"])', builder)
        self.assertIn('instruction_override.get("steps_ar", family["steps_ar"])', builder)
        for source_id in EXPECTED:
            self.assertIn(f'"{source_id}": {{', builder)


if __name__ == "__main__":
    unittest.main()
