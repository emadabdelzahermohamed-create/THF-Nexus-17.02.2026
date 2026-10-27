import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "fitness-v2/android/app/src/main/assets/pulse/data/exercises.js"

EXPECTED = {
    "side-to-side-box-shuffle": {
        "en": [
            "Stand beside a stable box with one foot centered on it and the other foot on the floor; keep your knees soft.",
            "Hop laterally across the box and switch which foot lands on the box and which lands on the floor, using your arms for balance.",
            "Continue shuffling from side to side with quiet, controlled landings and a clear path.",
        ],
        "ar": [
            "قف بجانب صندوق ثابت، وضع قدمًا في منتصفه والأخرى على الأرض مع ثني الركبتين قليلًا.",
            "اقفز جانبيًا فوق الصندوق وبدّل موضع القدمين؛ استخدم الذراعين للموازنة.",
            "واصل الانتقال من جانب إلى آخر بهبوط هادئ ومتحكم فيه مع إبقاء المسار خاليًا.",
        ],
    },
    "bicycling": {
        "en": [
            "Adjust the saddle so your knee remains slightly bent when the pedal is at its lowest point.",
            "Start with easy resistance and a smooth cadence; keep your shoulders relaxed and hands secure on the bars.",
            "Increase effort gradually, then reduce resistance and slow your cadence before dismounting.",
        ],
        "ar": [
            "اضبط ارتفاع المقعد بحيث تبقى الركبة مثنية قليلًا عندما تكون الدواسة في أدنى نقطة.",
            "ابدأ بمقاومة خفيفة ودوران سلس للدواسات، مع إرخاء الكتفين وثبات اليدين على المقود.",
            "زد الجهد تدريجيًا، ثم خفّض المقاومة والإيقاع قبل النزول عن الدراجة.",
        ],
    },
    "bicycling-stationary": {
        "en": [
            "Adjust the seat so your knee stays slightly bent at the bottom of the pedal stroke, then secure your feet if straps are provided.",
            "Choose a manual setting or suitable program and begin with low resistance; do not treat console calorie estimates as measured results.",
            "Pedal smoothly and raise resistance gradually only while you can keep a steady cadence and relaxed posture.",
        ],
        "ar": [
            "اضبط المقعد بحيث تبقى الركبة مثنية قليلًا عند أسفل دورة الدواسة، وثبّت القدمين إذا توفرت أحزمة.",
            "اختر الوضع اليدوي أو برنامجًا مناسبًا وابدأ بمقاومة منخفضة؛ تقدير السعرات على الشاشة ليس قياسًا فعليًا.",
            "بدّل الدواسات بسلاسة وزد المقاومة تدريجيًا فقط مع الحفاظ على إيقاع ثابت ووضع مريح.",
        ],
    },
    "recumbent-bike": {
        "en": [
            "Move the seat until your knee remains slightly bent when the pedal is farthest away, and sit with your back supported.",
            "Secure your feet and start at low resistance with an even pedal stroke.",
            "Increase effort gradually, then lower resistance and slow down before getting off.",
        ],
        "ar": [
            "حرّك المقعد حتى تبقى الركبة مثنية قليلًا عند أبعد نقطة للدواسة، واجلس مع إسناد الظهر.",
            "ثبّت القدمين وابدأ بمقاومة منخفضة ودورة دواسة منتظمة.",
            "زد الجهد تدريجيًا، ثم خفّض المقاومة وأبطئ الإيقاع قبل النزول.",
        ],
    },
    "linear-acceleration-wall-drill": {
        "en": [
            "Lean into a wall at about 45 degrees with your body aligned and glutes engaged.",
            "Drive one knee up quickly, then strike the foot down beneath your hips without letting the trunk collapse.",
            "Switch legs and repeat with the same forward lean and controlled foot placement.",
            "Once the rhythm is stable, alternate the legs rapidly for the prescribed interval; stop if your posture breaks down.",
        ],
        "ar": [
            "استند إلى الحائط بزاوية تقارب 45 درجة، مع محاذاة الجسم وشد عضلات الألوية.",
            "ارفع ركبة واحدة بسرعة ثم اضرب الأرض بالقدم أسفل الحوض دون انهيار الجذع.",
            "بدّل الساق وكرر مع الحفاظ على الميل الأمامي وموضع قدم متحكم فيه.",
            "بعد ثبات الإيقاع، بدّل الساقين بسرعة خلال المدة المحددة، وتوقف إذا اختل وضع الجسم.",
        ],
    },
    "single-cone-sprint-drill": {
        "en": [
            "Place one cone on a clear, non-slip surface and stand beside it with your arms in a running position.",
            "Take quick, short steps around the cone while driving your arms and lifting your knees without crossing your feet.",
            "Rest after three controlled circuits, or sooner if you lose footing or coordination.",
        ],
        "ar": [
            "ضع قمعًا واحدًا على سطح ثابت غير زلق وخالٍ من العوائق، وقف بجانبه بوضعية الجري.",
            "نفّذ خطوات قصيرة وسريعة حول القمع مع تحريك الذراعين ورفع الركبتين دون تشابك القدمين.",
            "استرح بعد ثلاث دورات متحكم فيها، أو قبل ذلك إذا اختل التوازن أو التناسق.",
        ],
    },
    "elliptical-trainer": {
        "en": [
            "Step onto the pedals, hold the handles securely, and select an easy program or low resistance before starting.",
            "Move through a smooth stride with an upright torso and relaxed shoulders; use moving handles only if they feel stable.",
            "Increase resistance or incline gradually, then reduce the effort and let the machine slow before stepping off.",
        ],
        "ar": [
            "اصعد إلى الدواسات وأمسك المقابض بثبات، واختر برنامجًا سهلًا أو مقاومة منخفضة قبل البدء.",
            "تحرك بخطوة سلسة مع جذع منتصب وكتفين مرتاحين، واستخدم المقابض المتحركة فقط إذا كانت مستقرة.",
            "زد المقاومة أو الميل تدريجيًا، ثم خفّض الجهد واترك الجهاز يبطئ قبل النزول.",
        ],
    },
    "rowing-stationary": {
        "en": [
            "Secure your feet in the straps, sit tall, and hinge slightly forward from the hips with a neutral back.",
            "Drive through the legs first, then swing the torso slightly back and pull the handle toward the upper abdomen.",
            "Return the arms first, hinge forward, and then bend the knees to slide toward the starting position.",
            "Repeat in that order with a smooth rhythm; stop if you feel back pain or cannot maintain control.",
        ],
        "ar": [
            "ثبّت القدمين بالأحزمة، واجلس منتصبًا مع ميل بسيط للأمام من الورك وظهر محايد.",
            "ادفع بالقدمين أولًا، ثم أمل الجذع قليلًا للخلف واسحب المقبض نحو أعلى البطن.",
            "أعد الذراعين أولًا، ثم أمل الجذع للأمام واثنِ الركبتين للعودة إلى وضع البداية.",
            "كرر التسلسل بإيقاع سلس، وتوقف إذا ظهر ألم بالظهر أو تعذر الحفاظ على التحكم.",
        ],
    },
    "bodyweight-walking-lunge": {
        "en": [
            "Stand with feet about hip-width apart, torso upright, and hands on your hips or by your sides.",
            "Step forward and lower until the rear knee approaches the floor while the front knee tracks in line with the foot.",
            "Push through the whole front foot to stand without bouncing or letting the knee collapse inward.",
            "Bring the rear foot forward into the next lunge and alternate sides with a controlled stride.",
        ],
        "ar": [
            "قف والقدمان بعرض الورك تقريبًا، والجذع منتصب، واليدان على الحوض أو بجانب الجسم.",
            "تقدم خطوة إلى الأمام وانزل حتى تقترب الركبة الخلفية من الأرض مع بقاء الركبة الأمامية في اتجاه القدم.",
            "ادفع بالأرض بكامل القدم الأمامية للوقوف دون ارتداد أو انهيار الركبة إلى الداخل.",
            "قدّم القدم الخلفية إلى الاندفاع التالي وبدّل الجانبين بخطوة متحكم فيها.",
        ],
    },
    "jogging-treadmill": {
        "en": [
            "With the belt stopped, stand on the side rails, choose a low starting speed, and begin only when the belt is moving safely.",
            "Jog with a tall posture, short controlled steps, and relaxed shoulders; avoid holding the rails during normal running.",
            "Reduce the belt to a walk and wait for it to stop before stepping off.",
        ],
        "ar": [
            "والحزام متوقف، قف على الجانبين واختر سرعة بداية منخفضة، ولا تبدأ إلا بعد تحرك الحزام بأمان.",
            "اهرول بجذع منتصب وخطوات قصيرة متحكم فيها وكتفين مرتاحين؛ لا تتمسك بالمقابض أثناء الجري الطبيعي.",
            "اخفض السرعة إلى المشي وانتظر توقف الحزام قبل النزول.",
        ],
    },
    "prowler-sprint": {
        "en": [
            "Choose a sled load that creates resistance but still allows quick, short steps without losing posture.",
            "Grip the upright or low handles, extend the arms, brace the trunk, and lean forward from the ankles.",
            "Drive through the floor with alternating short steps for a short distance while keeping the sled path clear.",
            "Stop before technique breaks down; reduce the load if your steps slow sharply or your back rounds.",
        ],
        "ar": [
            "اختر وزنًا للزلاجة يوفر مقاومة مع السماح بخطوات قصيرة وسريعة دون فقدان الوضع.",
            "أمسك بالمقابض المرتفعة أو المنخفضة، ومد الذراعين، وشد الجذع، ومل للأمام من الكاحلين.",
            "ادفع الأرض بخطوات قصيرة متبادلة لمسافة قصيرة مع إبقاء مسار الزلاجة خاليًا.",
            "توقف قبل انهيار التقنية؛ خفّض الوزن إذا تباطأت الخطوات بشدة أو تقوس الظهر.",
        ],
    },
    "running-treadmill": {
        "en": [
            "With the belt stopped, stand on the side rails, set a conservative speed and incline, and start the belt before stepping on.",
            "Run with controlled strides, eyes forward, and a stable torso; use the rails only for balance or dismounting.",
            "Lower the speed to a walk, wait for the belt to stop, and then step off.",
        ],
        "ar": [
            "والحزام متوقف، قف على الجانبين واضبط سرعة وميلًا مناسبين، ثم شغّل الحزام قبل الصعود إليه.",
            "اجرِ بخطوات متحكم فيها ونظرك للأمام وجذع ثابت؛ استخدم المقابض للتوازن أو عند النزول فقط.",
            "اخفض السرعة إلى المشي، وانتظر توقف الحزام ثم انزل.",
        ],
    },
    "trail-running-walking": {
        "en": [
            "Wear shoes with suitable grip, scan the trail ahead, and choose a pace that matches the surface and visibility.",
            "On climbs, shorten your stride and keep effort steady rather than overreaching.",
            "On descents, take shorter steps, bend the knees, and slow down to manage impact and avoid slipping.",
            "Walk technical, loose, or slippery sections and stop if footing becomes unsafe.",
        ],
        "ar": [
            "ارتدِ حذاءً مناسبًا للتشبث بالأرض، وراقب المسار أمامك واختر سرعة تناسب السطح ومدى الرؤية.",
            "في الصعود، قصّر الخطوة وحافظ على جهد ثابت بدل المبالغة في مدها.",
            "في النزول، قصّر الخطوات واثنِ الركبتين وأبطئ لتقليل الصدمة وتجنب الانزلاق.",
            "امشِ في المقاطع الوعرة أو المفككة أو الزلقة، وتوقف إذا أصبح تثبيت القدم غير آمن.",
        ],
    },
    "walking-treadmill": {
        "en": [
            "With the belt stopped, stand on the side rails, select a comfortable starting speed, and start the belt before stepping on.",
            "Walk upright with eyes forward and a natural arm swing; avoid leaning on the rails throughout the session.",
            "Reduce the speed to zero and wait for the belt to stop before stepping off.",
        ],
        "ar": [
            "والحزام متوقف، قف على الجانبين واختر سرعة بداية مريحة، ثم شغّل الحزام قبل الصعود إليه.",
            "امشِ بجذع منتصب ونظرك للأمام وحركة ذراعين طبيعية؛ تجنب الاتكاء المستمر على المقابض.",
            "اخفض السرعة إلى الصفر وانتظر توقف الحزام قبل النزول.",
        ],
    },
}

GENERIC = {
    "ابدأ من جذع ثابت وتنفس دون حبس طويل.",
    "نفّذ الحركة ببطء ومن دون شد الرقبة.",
    "توقف قبل فقدان وضع الحوض أو أسفل الظهر.",
    "ارفع الإيقاع تدريجيًا مع وضع جسم مريح.",
    "حافظ على خطوات أو دورات سلسة ويمكنك التحدث بجمل قصيرة.",
    "اخفض السرعة تدريجيًا قبل التوقف.",
}

class CardioInstructionSpecificityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = CATALOG.read_text(encoding="utf-8")
        prefix = "window.THF_EXERCISES = "
        cls.exercises = json.loads(source[len(prefix):].strip().removesuffix(";"))
        cls.by_id = {item["id"]: item for item in cls.exercises}

    def test_fourteen_cardio_and_locomotion_drills_have_specific_bilingual_steps(self):
        self.assertEqual(14, len(EXPECTED))
        self.assertEqual(112, len(self.exercises))
        for exercise_id, expected in EXPECTED.items():
            with self.subTest(exercise_id=exercise_id):
                item = self.by_id[exercise_id]
                self.assertEqual(expected["en"], item["steps"]["en"])
                self.assertEqual(expected["ar"], item["steps"]["ar"])
                self.assertEqual(len(item["steps"]["en"]), len(item["steps"]["ar"]))
                self.assertTrue(all(step.strip() for lang in ("en", "ar") for step in item["steps"][lang]))
                joined_ar = " ".join(item["steps"]["ar"])
                self.assertTrue(all(cue not in joined_ar for cue in GENERIC))
                joined_en = " ".join(item["steps"]["en"]).lower()
                self.assertNotIn("150 lb", joined_en)
                self.assertNotIn("calories", joined_en)

    def test_only_step_arrays_changed_for_target_records(self):
        self.assertEqual(112, len(self.exercises))
        self.assertTrue(set(EXPECTED).issubset(self.by_id))
        for exercise_id, expected in EXPECTED.items():
            self.assertEqual(expected, self.by_id[exercise_id]["steps"])

if __name__ == "__main__":
    unittest.main()
