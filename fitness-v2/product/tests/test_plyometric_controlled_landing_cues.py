import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG_JSON = ROOT / "fitness-v2/android/app/src/main/assets/pulse/data/exercises.json"
CATALOG_JS = ROOT / "fitness-v2/android/app/src/main/assets/pulse/data/exercises.js"
MANIFEST = ROOT / "fitness-v2/product/CATALOG_MANIFEST.json"
BUILDER_PATH = ROOT / "fitness-v2/product/tools/build_catalog.py"

EXPECTED = {
  "Fast_Skipping": {
    "en": [
      "Stand tall with feet under the hips and one foot slightly forward; keep the knees soft and the area clear.",
      "Use an alternating step-hop pattern—right-right-step, then left-left-step—with small, quiet contacts and relaxed arms.",
      "Begin at a cadence you can control; increase it only while contacts stay quiet and balance remains steady. Stop if coordination or landing quality slips."
    ],
    "ar": [
      "قف باستقامة والقدمان تحت الوركين مع تقديم إحدى القدمين قليلًا؛ أبقِ الركبتين مرتخيتين والمساحة خالية.",
      "نفّذ نمط خطوة وقفزة بالتبادل: يمين–يمين–خطوة انتقال، ثم يسار–يسار–خطوة انتقال، بملامسات قصيرة وهادئة وذراعين مرتخيتين.",
      "ابدأ بإيقاع تتحكم فيه، وزده فقط ما دامت الملامسات هادئة والتوازن ثابتًا. توقف إذا اختل التناسق أو جودة الهبوط."
    ]
  },
  "Box_Skip": {
    "en": [
      "Use a low, stable box on a nonslip surface with clear space around it; begin with one box before adding more.",
      "Stand facing the box in a staggered stance, with soft knees and eyes on the landing surface.",
      "Push from the back foot to hop onto the box; choose a height that allows a controlled landing rather than reaching for maximum height.",
      "Land softly with the whole foot and the knee tracking over the toes; pause until balance returns.",
      "Step down carefully and reset; add another box or speed only after every landing is controlled. Stop if balance is lost."
    ],
    "ar": [
      "استخدم صندوقًا منخفضًا وثابتًا على سطح غير زلق، مع مساحة خالية حوله؛ ابدأ بصندوق واحد قبل إضافة غيره.",
      "قف أمام الصندوق بوقفة متدرجة، مع ثني بسيط للركبتين والنظر إلى سطح الهبوط.",
      "ادفع بالقدم الخلفية للوثب إلى الصندوق؛ اختر ارتفاعًا يسمح بهبوط متحكم فيه بدل السعي إلى أقصى ارتفاع.",
      "اهبط بهدوء بكامل القدم مع توجيه الركبة نحو أصابع القدم، ثم انتظر حتى يستعيد الجسم توازنه.",
      "انزل خطوة خطوة وأعد ضبط الوقفة؛ لا تضف صندوقًا آخر أو تسرّع التسلسل إلا بعد ثبات كل هبوط. توقف إذا اختل التوازن."
    ]
  },
  "Front_Cone_Hops_or_hurdle_hops": {
    "en": [
      "Set low cones or soft barriers at a spacing you can clear comfortably; keep the landing area open.",
      "Stand facing the first barrier with feet about hip-width apart and knees soft.",
      "Hop over the first barrier with both feet, using a small, controlled clearance and a natural arm swing.",
      "Land quietly with knees tracking over the toes; pause to regain balance before the next hop.",
      "Continue only while each landing stays quiet and stable; stop if knee alignment or balance slips."
    ],
    "ar": [
      "رتّب أقماعًا منخفضة أو حواجز لينة بمسافة تسمح بتجاوزها براحة، وأخلِ منطقة الهبوط.",
      "قف أمام أول حاجز والقدمان بعرض الوركين تقريبًا مع ثني بسيط للركبتين.",
      "اقفز فوق الحاجز بكلتا القدمين مع ارتفاع صغير ومتحكم فيه وحركة طبيعية للذراعين.",
      "اهبط بهدوء مع توجيه الركبتين نحو أصابع القدم، وانتظر حتى تستعيد توازنك قبل القفزة التالية.",
      "واصل فقط ما دام كل هبوط هادئًا وثابتًا؛ توقف إذا اختلت محاذاة الركبتين أو التوازن."
    ]
  },
  "Lateral_Cone_Hops": {
    "en": [
      "Set low cones with enough side-to-side clearance and keep both landing sides open.",
      "Stand side-on to the direction of travel with feet hip-width apart and knees soft.",
      "Hop laterally over one cone with a small, controlled height; keep the trunk steady and knees aligned.",
      "Land softly, regain balance before the next cone, and stop if foot placement or knee alignment breaks down."
    ],
    "ar": [
      "ضع أقماعًا منخفضة مع مسافة كافية للقفز الجانبي، وأخلِ جانبي منطقة الهبوط.",
      "قف بجانب الصف وجسمك متعامد مع اتجاه الحركة، والقدمان بعرض الوركين والركبتان مرتخيتان.",
      "اقفز جانبيًا فوق قمع واحد بارتفاع صغير ومتحكم فيه، مع ثبات الجذع ومحاذاة الركبتين.",
      "اهبط بهدوء واستعد توازنك قبل القمع التالي، وتوقف إذا اختل موضع القدم أو محاذاة الركبة."
    ]
  },
  "Side_Hop-Sprint": {
    "en": [
      "Place a low cone or hurdle beside you and clear a short sprint lane; begin in a balanced stance.",
      "Hop sideways over and back with quiet landings; pause and reset between directions instead of rebounding immediately.",
      "After the prescribed hops, accelerate into a short sprint only when the final landing is stable. Stop if balance or coordination deteriorates."
    ],
    "ar": [
      "ضع قمعًا أو حاجزًا منخفضًا بجانبك وأخلِ مسار انطلاق قصيرًا؛ ابدأ بوقفة متوازنة.",
      "اقفز جانبيًا فوق الحاجز ثم عد بهبوط هادئ، وتوقف لحظة لإعادة ضبط الوقفة بين الاتجاهين بدل الارتداد الفوري.",
      "بعد عدد القفزات المحدد، انطلق لمسافة قصيرة فقط بعد ثبات الهبوط الأخير. توقف إذا تدهور التوازن أو التناسق."
    ]
  },
  "Freehand_Jump_Squat": {
    "en": [
      "Stand with feet shoulder-width apart, arms crossed over the chest, and knees soft.",
      "Brace the trunk and squat to a comfortable depth with the hips back and knees tracking over the toes.",
      "Push through the whole foot to jump vertically with a height you can control; exhale on takeoff.",
      "Land quietly with hips and knees flexed to absorb impact, keeping the knees aligned.",
      "Pause to regain balance and reset your stance; do not rebound immediately.",
      "Repeat the prescribed reps and stop if landings become loud or alignment slips."
    ],
    "ar": [
      "قف والقدمان بعرض الكتفين والذراعان متقاطعتان أمام الصدر، مع ثني بسيط للركبتين.",
      "شد الجذع واخفض الوركين إلى سكوات بعمق مريح، مع توجيه الركبتين نحو أصابع القدم.",
      "ادفع بكامل القدم للقفز عموديًا بارتفاع تستطيع التحكم فيه، وازفر عند الدفع.",
      "اهبط بهدوء مع ثني الوركين والركبتين لامتصاص الصدمة، مع الحفاظ على محاذاة الركبتين.",
      "توقف لاستعادة التوازن وأعد ضبط الوقفة؛ لا ترتد فورًا إلى القفزة التالية.",
      "كرر العدد المحدد وتوقف إذا أصبح الهبوط صاخبًا أو اختلت المحاذاة."
    ]
  },
  "Lateral_Bound": {
    "en": [
      "Start in a half squat facing perpendicular to the travel direction; clear space on both sides.",
      "Shift weight to the outside leg with a small, controlled countermovement; keep the knee aligned.",
      "Push off laterally only as far as you can land under control, not for maximum distance.",
      "Land on the opposite foot with the knee tracking over the toes; flex the hip and knee to absorb impact, then pause.",
      "Return only after balance is restored; alternate while landings stay quiet and stop if alignment slips."
    ],
    "ar": [
      "ابدأ بنصف سكوات وجسمك متعامد مع اتجاه الحركة، وأخلِ المساحة على الجانبين.",
      "انقل الوزن إلى الساق الخارجية بحركة تمهيدية صغيرة ومتحكم فيها، مع الحفاظ على محاذاة الركبة.",
      "ادفع جانبيًا لمسافة تستطيع الهبوط بعدها بتحكم، لا لأقصى مسافة ممكنة.",
      "اهبط على القدم المقابلة مع توجيه الركبة نحو أصابع القدم وثني الورك والركبة لامتصاص الصدمة، ثم توقف لحظة.",
      "لا تعد إلا بعد استعادة التوازن؛ بدّل الجهة ما دام الهبوط هادئًا، وتوقف إذا اختلت المحاذاة."
    ]
  }
}
BANNED_ENGLISH_CUES = (
    "as quickly as possible",
    "as high as possible",
    "as far as possible",
    "rebounding out of your landing",
    "immediately squat down and jump again",
)

SPEC = importlib.util.spec_from_file_location("thf_build_catalog_plyometric_cues", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


def load_runtime_catalog():
    source = CATALOG_JS.read_text(encoding="utf-8")
    payload = source.split("=", 1)[1].strip().removesuffix(";")
    return json.loads(payload)


class PlyometricControlledLandingCueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
        cls.runtime = load_runtime_catalog()
        cls.by_source = {item["sourceItemId"]: item for item in cls.catalog}
        cls.runtime_by_source = {item["sourceItemId"]: item for item in cls.runtime}
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_seven_bilingual_sequences_match_builder_json_and_runtime(self):
        self.assertEqual(7, len(EXPECTED))
        self.assertEqual(112, len(self.catalog))
        self.assertEqual(self.catalog, self.runtime)
        for source_id, steps in EXPECTED.items():
            with self.subTest(source_id=source_id):
                self.assertEqual(steps, BUILDER.STEP_OVERRIDES[source_id])
                self.assertEqual(steps, self.by_source[source_id]["steps"])
                self.assertEqual(steps, self.runtime_by_source[source_id]["steps"])
                self.assertEqual(len(steps["en"]), len(steps["ar"]))
                self.assertTrue(all(step.strip() for step in steps["en"] + steps["ar"]))

    def test_plyometric_cues_avoid_unbounded_effort_and_immediate_rebounds(self):
        for source_id in EXPECTED:
            with self.subTest(source_id=source_id):
                english = " ".join(self.by_source[source_id]["steps"]["en"]).lower()
                for phrase in BANNED_ENGLISH_CUES:
                    self.assertNotIn(phrase, english)
                self.assertIn("stop", english)
                arabic = " ".join(self.by_source[source_id]["steps"]["ar"])
                self.assertTrue("توقف" in arabic or "توقّف" in arabic)

    def test_catalog_manifest_digest_matches_exact_json_bytes(self):
        digest = hashlib.sha256(CATALOG_JSON.read_bytes()).hexdigest()
        self.assertEqual(digest, self.manifest["catalogSha256"])


if __name__ == "__main__":
    unittest.main()
