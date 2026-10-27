import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUNTIME_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.js"
CATALOG_PATH = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.json"
BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"

SPEC = importlib.util.spec_from_file_location("thf_build_catalog_core_cues", BUILDER_PATH)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)

EXPECTED = json.loads("{\"Crunches\":{\"id\":\"crunches\",\"steps\":{\"en\":[\"Lie on your back with knees bent and feet flat; keep your lower back gently in contact with the floor.\",\"Place fingertips beside your ears with elbows open; do not pull on your head.\",\"Exhale and curl your shoulder blades a few inches off the floor by tightening your abdominal muscles.\",\"Pause briefly at the top without swinging or straining your neck.\",\"Inhale and lower your shoulders slowly to the starting position.\"],\"ar\":[\"استلقِ على ظهرك واثنِ الركبتين مع تثبيت القدمين على الأرض، وأبقِ أسفل الظهر ملامسًا للأرض برفق.\",\"ضع أطراف الأصابع بجانب الأذنين واترك المرفقين مفتوحين، ولا تسحب الرأس باليدين.\",\"ازفر وارفع لوحي الكتف بضعة سنتيمترات عن الأرض بشد عضلات البطن.\",\"توقف لحظة في الأعلى دون تأرجح أو إجهاد الرقبة.\",\"خذ شهيقًا وأنزل الكتفين ببطء إلى وضع البداية.\"]}},\"Plank\":{\"id\":\"plank\",\"steps\":{\"en\":[\"Start face down with forearms on the floor and elbows directly beneath your shoulders; tuck your toes under.\",\"Lift your torso and hips into a straight line from head to heels, bracing your abdomen and glutes.\",\"Breathe steadily and keep your hips from sagging or rising; hold only while alignment remains controlled.\",\"Lower your knees and hips carefully to finish, or use a shorter hold or knee plank if alignment breaks.\"],\"ar\":[\"ابدأ ووجهك إلى الأرض، وضع الساعدين عليها والمرفقين أسفل الكتفين مباشرة، مع تثبيت أصابع القدمين.\",\"ارفع الجذع والحوض حتى يصنع الجسم خطًا مستقيمًا من الرأس إلى الكعبين، مع شد البطن والألوية.\",\"تنفس بانتظام وامنع هبوط الحوض أو ارتفاعه؛ استمر فقط ما دامت المحاذاة ثابتة.\",\"أنزل الركبتين والحوض بتحكم لإنهاء الثبات، أو استخدم مدة أقصر أو بلانك على الركبتين إذا اختل الوضع.\"]}},\"Russian_Twist\":{\"id\":\"russian-twist\",\"steps\":{\"en\":[\"Sit with knees bent and heels on the floor, then lean back slightly while keeping your spine long.\",\"Hold your hands together in front of your chest and brace your abdomen without rounding your lower back.\",\"Rotate your rib cage to one side within a comfortable range while keeping your hips and knees steady.\",\"Return through the center and rotate to the other side; move under control instead of swinging your arms.\",\"Keep your feet grounded; for an easier version sit more upright and use a smaller rotation, and stop if your lower back hurts.\"],\"ar\":[\"اجلس والركبتان مثنيتان والكعبان على الأرض، ثم أمل الجذع قليلًا للخلف مع إطالة العمود الفقري.\",\"ضم اليدين أمام الصدر وشد عضلات البطن دون تدوير أسفل الظهر.\",\"أدر القفص الصدري إلى أحد الجانبين ضمن مدى مريح مع تثبيت الحوض والركبتين.\",\"عد إلى المنتصف ثم أدر الجذع إلى الجهة الأخرى بتحكم بدل تأرجح الذراعين.\",\"أبقِ القدمين على الأرض؛ ولتسهيل الحركة اجلس أكثر انتصابًا وقلل الدوران، وتوقف إذا ظهر ألم أسفل الظهر.\"]}},\"Side_Bridge\":{\"id\":\"side-bridge\",\"steps\":{\"en\":[\"Lie on your side with the elbow directly under the shoulder; keep the legs straight or bend the knees for an easier version.\",\"Brace your abdomen and lift your hips until your shoulder, hip, and ankle form one line.\",\"Breathe steadily, keep the top hip stacked over the lower hip, and avoid rolling your chest toward the floor.\",\"Lower your hips with control and repeat on the other side; stop if the shoulder becomes painful.\"],\"ar\":[\"استلقِ على جانبك وضع المرفق أسفل الكتف مباشرة؛ أبقِ الساقين مستقيمتين أو اثنِ الركبتين لتسهيل الحركة.\",\"شد عضلات البطن وارفع الحوض حتى يصطف الكتف والحوض والكاحل في خط واحد.\",\"تنفس بانتظام وأبقِ الورك العلوي فوق السفلي، وتجنب تدوير الصدر نحو الأرض.\",\"أنزل الحوض بتحكم وكرر على الجانب الآخر، وتوقف إذا ظهر ألم في الكتف.\"]}},\"Superman\":{\"id\":\"superman\",\"steps\":{\"en\":[\"Lie face down on a mat with arms extended overhead and legs straight; look down to keep your neck neutral.\",\"Gently brace your abdomen and squeeze your glutes before lifting.\",\"Raise the opposite arm and leg a small distance, or lift both sides only if comfortable; do not force an arch in the lower back.\",\"Pause briefly, lower slowly, and alternate sides or repeat as prescribed; stop if back pain appears.\"],\"ar\":[\"استلقِ على بطنك فوق بساط مع مد الذراعين أمام الرأس والساقين للخلف، وانظر إلى الأرض لإبقاء الرقبة محايدة.\",\"شد عضلات البطن برفق واضغط الألوية قبل الرفع.\",\"ارفع الذراع والساق المتعاكستين مسافة صغيرة، أو ارفع الطرفين معًا فقط إذا كان ذلك مريحًا، دون المبالغة في تقويس أسفل الظهر.\",\"توقف لحظة ثم اخفض الطرفين ببطء وبدّل الجهة أو كرر حسب البرنامج؛ توقف إذا ظهر ألم بالظهر.\"]}},\"Flutter_Kicks\":{\"id\":\"flutter-kicks\",\"steps\":{\"en\":[\"Lie face down on a sturdy flat bench with your hips near the edge, grip the front securely, and let straight legs hover clear of the floor.\",\"Brace your abdomen and glutes while keeping your pelvis steady and lower back neutral.\",\"Alternate small leg lifts, raising one leg slightly as the other lowers without swinging or arching your back.\",\"Continue evenly for the prescribed repetitions or time; stop if your lower back hurts or the bench feels unstable.\"],\"ar\":[\"استلقِ على بطنك فوق مقعد مسطح وثابت مع اقتراب الوركين من الحافة، وأمسك مقدمة المقعد بإحكام واترك الساقين مستقيمتين فوق الأرض.\",\"شد عضلات البطن والألوية مع تثبيت الحوض والحفاظ على وضع محايد لأسفل الظهر.\",\"ارفع إحدى الساقين مسافة صغيرة بينما تنخفض الأخرى، بالتبادل دون تأرجح أو تقويس الظهر.\",\"واصل بإيقاع منتظم حسب التكرارات أو المدة المحددة، وتوقف إذا ظهر ألم أسفل الظهر أو لم يكن المقعد ثابتًا.\"]}},\"Downward_Facing_Balance\":{\"id\":\"downward-facing-balance\",\"steps\":{\"en\":[\"Place your abdomen and hips on a stable exercise ball and set both hands on a clear, non-slip floor in front of you.\",\"Walk your hands forward until your torso is supported and aligned, keeping the ball centered under your pelvis and abdomen.\",\"Brace your core and lift both legs only to hip height while keeping the elbows and knees straight; avoid over-arching your back.\",\"Breathe steadily, lower your legs, and walk your hands back; use assistance or skip the move if you cannot balance securely.\"],\"ar\":[\"ضع البطن والوركين فوق كرة تمرين ثابتة، وثبّت اليدين على أرضية غير زلقة وخالية من العوائق أمامك.\",\"حرّك اليدين إلى الأمام حتى يستند الجذع وتصبح محاذاته مستقيمة، مع إبقاء الكرة تحت الحوض والبطن.\",\"شد عضلات الجذع وارفع الساقين حتى مستوى الورك فقط، مع إبقاء المرفقين والركبتين مستقيمين وتجنب تقويس الظهر.\",\"تنفس بانتظام ثم اخفض الساقين وأعد اليدين للخلف؛ اطلب المساعدة أو اترك التمرين إذا تعذر الحفاظ على التوازن.\"]}}}")

GENERIC_ARABIC = {
    "ابدأ من جذع ثابت وتنفس دون حبس طويل.",
    "نفّذ الحركة ببطء ومن دون شد الرقبة.",
    "توقف قبل فقدان وضع الحوض أو أسفل الظهر.",
}


class CoreInstructionSpecificityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runtime_source = RUNTIME_PATH.read_text(encoding="utf-8")
        cls.runtime = json.loads(runtime_source.split("=", 1)[1].strip().removesuffix(";"))
        cls.generated = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.runtime_by_id = {item["id"]: item for item in cls.runtime}
        cls.generated_by_source = {item["sourceItemId"]: item for item in cls.generated}

    def test_seven_core_and_back_exercises_have_specific_bilingual_steps(self):
        self.assertEqual(112, len(self.runtime))
        self.assertEqual(112, len(self.generated))
        for source_id, expected in EXPECTED.items():
            with self.subTest(source_id=source_id):
                self.assertIn(source_id, BUILDER.STEP_OVERRIDES)
                self.assertEqual(expected["steps"], BUILDER.STEP_OVERRIDES[source_id])
                self.assertEqual(expected["steps"], self.generated_by_source[source_id]["steps"])
                self.assertEqual(expected["steps"], self.runtime_by_id[expected["id"]]["steps"])
                self.assertEqual(len(expected["steps"]["en"]), len(expected["steps"]["ar"]))
                self.assertGreaterEqual(len(expected["steps"]["en"]), 4)
                self.assertTrue(all(step.strip() for lang in ("en", "ar") for step in expected["steps"][lang]))
                self.assertFalse(set(expected["steps"]["ar"]) & GENERIC_ARABIC)


if __name__ == "__main__":
    unittest.main()
