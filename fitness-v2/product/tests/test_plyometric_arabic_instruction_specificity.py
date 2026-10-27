import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "fitness-v2/android/app/src/main/assets/pulse/data/exercises.js"

EXPECTED_NAMES = {
    "fast-skipping": "قفز متناوب سريع",
    "box-skip": "قفز متتابع بين الصناديق",
}

EXPECTED_AR = {
    "fast-skipping": [
        "ابدأ في وضع مريح مع تقديم إحدى القدمين قليلًا.",
        "نفّذ نمط خطوة وقفزة بالتبادل: يمين–يمين–خطوة انتقال، ثم يسار–يسار–خطوة انتقال.",
        "زد سرعة القفز مع إبقاء زمن الطيران قصيرًا والقدمين قريبين من الأرض."
    ],
    "box-skip": [
        "رتّب عدة صناديق ثابتة في صف، واترك نحو 2.4 متر بين كل صندوق وآخر.",
        "قف أمام الصندوق الأول مع وضع إحدى القدمين خلف الأخرى قليلًا.",
        "ادفع بالأرض من القدم الخلفية لرفع الورك واكتساب ارتفاع نحو الصندوق.",
        "عند الهبوط على الصندوق، ادفع الرجل الأخرى للأمام والأعلى ثم اقفز نحو الصندوق التالي؛ اهبط بين الصندوقين على القدم نفسها التي هبطت بها على الأول.",
        "انتقل إلى الصندوق التالي وكرر التسلسل، مع التأكد من ثبات الهبوط قبل القفزة التالية."
    ],
    "front-cone-hops-or-hurdle-hops": [
        "رتّب صفًا من الأقماع أو الحواجز المنخفضة، مع ترك بضعة أقدام بين كل حاجز وآخر.",
        "قف أمام أول حاجز والقدمان بعرض الكتفين.",
        "اقفز بكلتا القدمين معًا فوق الحاجز، وحرّك الذراعين للمساعدة في الدفع.",
        "امتص الهبوط بثني الركبتين ثم ارتدّ للقفز فوق الحاجز التالي.",
        "واصل حتى تتجاوز الصف كاملًا، وتوقف إذا أصبح الهبوط صلبًا أو اختل اتجاه الركبتين."
    ],
    "lateral-cone-hops": [
        "ضع عدة أقماع في صف يفصل بينها بضعة أقدام.",
        "قف بجانب طرف الصف واجعل جسمك متعامدًا مع اتجاه الانتقال.",
        "اثنِ الركبتين قليلًا ثم ادفع الأرض فورًا للقفز جانبيًا فوق القمع.",
        "امتص الهبوط بالساقين ثم انتقل مباشرة إلى القفزة التالية حتى نهاية الصف."
    ],
    "side-hop-sprint": [
        "قف إلى جانب قمع أو حاجز منخفض.",
        "اقفز جانبيًا فوق الحاجز ثم استخدم الهبوط للارتداد والعودة إلى نقطة البداية.",
        "كرر العدد المحدد بأسرع إيقاع يمكن التحكم فيه، ثم انطلق لمسافة قصيرة بعد آخر هبوط."
    ],
    "freehand-jump-squat": [
        "اعقد الذراعين أمام الصدر.",
        "قف والقدمان بعرض الكتفين، والرأس مرفوع والظهر مستقيم.",
        "اخفض الوركين في سكوات مع الشهيق حتى يصبح الفخذان موازيين للأرض أو أدنى، مع إبقاء الصدر مرفوعًا.",
        "ادفع بمقدمة القدمين واقفز عموديًا بأعلى ارتفاع يمكنك التحكم فيه، مع الزفير.",
        "عند ملامسة الأرض، اثنِ الوركين والركبتين لامتصاص الهبوط والعودة فورًا إلى وضع السكوات.",
        "كرر العدد المطلوب مع الحفاظ على محاذاة الركبتين وهبوط هادئ؛ توقف إذا فقدت السيطرة."
    ],
    "lateral-bound": [
        "ابدأ بنصف سكوات، واجعل جسمك متعامدًا مع اتجاه الوثب.",
        "حرّك الساق القائدة قليلًا إلى الداخل وانقل وزنك إلى الساق الخارجية.",
        "ادفع الأرض وامدد الورك والركبة للوثب جانبيًا إلى أبعد مسافة تستطيع التحكم بها.",
        "عند الهبوط، ادفع فورًا بالاتجاه المعاكس للعودة إلى موضع البداية.",
        "واصل الوثب ذهابًا وإيابًا لعدة تكرارات، مع امتصاص الهبوط والحفاظ على اتجاه الركبتين."
    ]
}

GENERIC_CUES = (
    "حمّل الورك والركبتين بسرعة متحكم فيها",
    "ادفع الأرض وحافظ على اتجاه الركبتين",
    "اهبط بهدوء واثبت قبل التكرار التالي",
    "اخفض الحمل أو الجسم بتحكم حتى مدى مريح",
    "ادخل المدى ببطء حتى شد خفيف لا ألم",
    "حافظ على الوضع والتنفس من دون ارتداد",
    "اخرج من الوضع تدريجيًا وكرر على الجهة الأخرى عند الحاجة",
)


class PlyometricArabicInstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = CATALOG.read_text(encoding="utf-8")
        payload = source.split("=", 1)[1].strip().removesuffix(";")
        cls.exercises = json.loads(payload)
        cls.by_id = {item["id"]: item for item in cls.exercises}

    def test_seven_plyometric_sequences_are_specific_and_step_aligned(self):
        self.assertEqual(7, len(EXPECTED_AR))
        for exercise_id, expected_steps in EXPECTED_AR.items():
            with self.subTest(exercise_id=exercise_id):
                item = self.by_id[exercise_id]
                arabic = item["steps"]["ar"]
                english = item["steps"]["en"]
                self.assertEqual(expected_steps, arabic)
                self.assertEqual(len(english), len(arabic))
                self.assertTrue(all(step.strip() for step in arabic))
                joined = " ".join(arabic)
                for generic in GENERIC_CUES:
                    self.assertNotIn(generic, joined)

    def test_skipping_and_box_skip_titles_match_the_actual_drill(self):
        for exercise_id, expected_name in EXPECTED_NAMES.items():
            with self.subTest(exercise_id=exercise_id):
                self.assertEqual(expected_name, self.by_id[exercise_id]["name"]["ar"])

    def test_catalog_size_and_target_identity_remain_stable(self):
        self.assertEqual(112, len(self.exercises))
        self.assertEqual(set(EXPECTED_AR), {key for key in EXPECTED_AR if key in self.by_id})


if __name__ == "__main__":
    unittest.main()
