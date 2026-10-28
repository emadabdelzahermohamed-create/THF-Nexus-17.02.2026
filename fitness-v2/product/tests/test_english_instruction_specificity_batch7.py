import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PULSE_DATA = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data"
CATALOG_PATH = PULSE_DATA / "exercises.json"
RUNTIME_PATH = PULSE_DATA / "exercises.js"

GENERIC_ENGLISH_FILLER = {
    "Repeat for the recommended amount of repetitions.",
    "Repeat the movement for the prescribed amount of repetitions.",
}

EXPECTED_ENGLISH_STEPS = {
    "dips---triceps-version": [
        "Start above the parallel bars with your elbows nearly extended and shoulders set.",
        "Inhale and lower slowly, keeping your torso upright and elbows close to your sides.",
        "Stop at a comfortable elbow depth; do not descend into shoulder pain.",
        "Exhale and press back up through the triceps without forcefully locking the elbows.",
    ],
    "handstand-push-ups": [
        "Face a wall and place your hands shoulder-width apart, leaving clear space for your head; use a spotter if this is new.",
        "Bring your feet to the wall and extend your arms, keeping your body straight and your head neutral rather than looking down.",
        "Bend your elbows slowly until your head approaches a stable pad; stop before loading your neck.",
        "Press the floor away as you exhale until your elbows are nearly extended, without a hard lockout.",
        "Repeat only through a controlled range; come down with assistance if you lose balance or feel pain.",
    ],
    "hanging-leg-raise": [
        "Hang from a secure bar with your arms extended and a firm grip; let your body settle without swinging.",
        "Lift your legs from the hips toward a comfortable angle near 90 degrees without driving your torso forward.",
        "Exhale as you lift and keep your pelvis slightly tucked without straining your neck.",
        "Lower your legs slowly to the start position before beginning the next repetition.",
    ],
    "barbell-bench-press---medium-grip": [
        "Lie on a flat bench, take a medium grip, and lift the bar from the rack over your chest with your feet and shoulder blades set.",
        "Inhale and lower the bar slowly to the middle of your chest, keeping your wrists stacked over your elbows.",
        "Pause briefly, then exhale and press the bar up without bouncing; keep the bar path steady.",
        "Repeat the controlled descent and press, lowering more slowly than you lift; avoid forcefully locking your elbows.",
        "After the final repetition, return the bar to the rack using the safety catches or a spotter when needed.",
    ],
    "barbell-shoulder-press": [
        "Sit with back support, set the bar in a rack just above head height, and take an overhand grip.",
        "Bring the bar to shoulder level slightly in front of your head; brace your abdomen and keep your feet stable.",
        "Inhale as you lower the bar slowly to your shoulders.",
        "Exhale and press the bar overhead without arching your lower back.",
        "Repeat through a comfortable range; stop if your ribs flare forward or shoulder pain develops.",
    ],
    "dip-machine": [
        "Adjust the seat and load, sit securely, and grip the handles firmly.",
        "Keep your elbows close to your torso and your shoulders down.",
        "Exhale and extend your elbows to press the handles down without forcefully locking the joints.",
        "Inhale as you return slowly to a comfortable elbow angle without shrugging your shoulders.",
        "Repeat without swinging; reduce the load if you cannot control the movement.",
    ],
    "front-barbell-squat": [
        "Inside a squat rack, set the safety pins below your deepest controlled position; rest the bar on your front shoulders with your elbows high.",
        "Stand to lift the bar from the rack, step back once or twice, and set your feet about shoulder-width apart.",
        "Inhale and brace your trunk, then lower your hips between your knees while keeping your torso upright and elbows high.",
        "Keep your knees tracking toward your toes and your whole foot grounded; do not descend beyond a controllable depth.",
        "Exhale and drive through the floor to stand, preventing your knees from collapsing inward.",
        "After the final rep, rerack the bar safely; reduce the load if your elbows drop or your torso folds.",
    ],
    "hammer-curls": [
        "Stand tall with dumbbells at your sides, palms facing inward, and elbows close to your torso.",
        "Keep your upper arms still and exhale as you curl the dumbbells without swinging your torso.",
        "Stop when the dumbbells approach shoulder level; keep your wrists straight and do not shrug.",
        "Pause briefly without jerking the weights or moving your elbows forward.",
        "Inhale and lower the dumbbells slowly to a comfortable arm extension.",
    ],
    "incline-dumbbell-press": [
        "Lie back on an incline bench and hold a dumbbell over each thigh, with your palms facing each other.",
        "Use your thighs to help raise the dumbbells to shoulder level one at a time.",
        "Rotate your wrists so your palms face forward, and keep your feet and shoulder blades set on the bench.",
        "Exhale and press the dumbbells over your chest along a controlled path without arching your lower back.",
        "Pause briefly at the top without letting the weights collide, then lower them slowly, taking longer on the descent than the ascent.",
        "Repeat through a range you can control; reduce the load if your shoulder stability deteriorates.",
    ],
    "lateral-raise---with-bands": [
        "Stand on the middle of the band with your feet hip-width apart; hold the handles by your thighs with a slight bend in your elbows.",
        "Exhale and raise your arms out to the sides to near shoulder height without leaning or shrugging.",
        "Pause briefly with neutral wrists and controlled arms; do not lift above a comfortable range.",
        "Lower the handles slowly with an inhale to the start while maintaining band tension.",
    ],
    "romanian-deadlift": [
        "Hold the bar in front of your thighs with an overhand grip slightly wider than shoulder-width; use a stable platform if needed.",
        "Bend your knees slightly and push your hips back, keeping your shins nearly vertical and your spine neutral.",
        "Drive your hips forward to stand as you exhale, keeping your arms straight and the bar close to your body.",
        "Push your hips back and lower the bar slowly with an inhale; do not turn the movement into a squat.",
        "Repeat with control; stop if you lose a neutral back position or your knees bend excessively.",
    ],
    "side-lateral-raise": [
        "Stand tall with dumbbells beside your thighs, palms facing inward, and your elbows slightly bent.",
        "Raise the dumbbells out to the sides toward shoulder height while keeping your torso still and avoiding a swing.",
        "Pause briefly with your neck relaxed, shoulders down, and wrists steady.",
        "Lower the dumbbells slowly with an inhale, then repeat through a controlled range.",
    ],
    "smith-machine-bench-press": [
        "Place a flat bench under the Smith machine, set the bar height and load, then lie back and grip slightly wider than your shoulders.",
        "Unhook the bar and hold it over the middle of your chest with your wrists aligned above your elbows.",
        "Inhale and lower the bar slowly to the middle of your chest with a comfortable elbow angle.",
        "Exhale and press up without bouncing the bar off your chest or forcefully locking your elbows.",
        "After the final repetition, return the bar to the safety hooks and confirm it is secure before sitting up.",
    ],
    "smith-machine-squat": [
        "Set the bar height and place it across your upper back, not your neck; make sure your feet are stable beneath it.",
        "Hold the bar on both sides, unlock the hooks, stand securely, and set your feet about shoulder-width apart.",
        "Brace your trunk and inhale, then lower your hips by bending your knees in line with your toes.",
        "Descend only as far as you can control, keeping your heels grounded and your torso steady.",
        "Exhale and drive through the floor to stand without letting your knees collapse inward or over-arching your lower back.",
        "After the set, lock the bar back onto the hooks; reduce the load if your movement path breaks down.",
    ],
    "standing-calf-raises": [
        "Adjust the calf-raise machine pad height so it rests securely across your shoulders.",
        "Place the balls of your feet on the calf platform with your heels beyond the edge; keep your knees slightly bent, not locked.",
        "Exhale and raise your heels by extending your ankles while keeping your knees still.",
        "Pause briefly at the top, then lower your heels slowly to a comfortable stretch as you inhale.",
        "Repeat without bouncing or using a load that causes pain.",
    ],
    "tricep-dumbbell-kickback": [
        "Hold a dumbbell in each hand, bend your knees slightly, and hinge at your hips with a neutral back until your torso leans forward.",
        "Keep your upper arms beside your torso and your forearms bent to about 90 degrees.",
        "Extend your elbows back until your arms straighten without moving your upper arms or swinging your torso.",
        "Pause briefly, then bend your elbows slowly to return to the starting position.",
    ],
    "triceps-pushdown---rope-attachment": [
        "Attach the rope to a high pulley and grip both ends with your palms facing each other.",
        "Stand steadily with your elbows beside your torso and your forearms angled toward the pulley.",
        "Press the rope down by extending your elbows, separating the rope ends near your thighs while keeping your upper arms still.",
        "Pause briefly without forcefully locking your elbows, then return the rope slowly with an inhale.",
        "Repeat with a steady torso and a load you can control.",
    ],
    "freehand-jump-squat": [
        "Cross your arms in front of your chest.",
        "Stand with your feet shoulder-width apart, head up, and back straight.",
        "Inhale and squat until your thighs are parallel to the floor or lower, keeping your chest lifted.",
        "Push through the balls of your feet to jump vertically as high as you can control, exhaling during takeoff.",
        "On landing, bend your hips and knees to absorb impact and return to the squat.",
        "Repeat with your knees tracking over your toes and a quiet landing; stop if you lose control.",
    ],
}


def load_catalog():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def load_runtime():
    raw = RUNTIME_PATH.read_text(encoding="utf-8")
    prefix = "window.THF_EXERCISES = "
    if not raw.startswith(prefix) or not raw.rstrip().endswith(";"):
        raise AssertionError("Runtime exercise payload wrapper is invalid")
    return json.loads(raw[len(prefix):raw.rfind(";")].strip())


class EnglishInstructionSpecificityBatch7Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.runtime = load_runtime()
        cls.by_id = {item["id"]: item for item in cls.catalog}

    def test_catalog_and_runtime_payload_are_identical_and_unique(self):
        self.assertEqual(self.catalog, self.runtime)
        self.assertEqual(112, len(self.catalog))
        self.assertEqual(112, len(self.by_id))

    def test_all_exercises_keep_nonblank_bilingual_step_parity(self):
        for item in self.catalog:
            with self.subTest(exercise_id=item["id"]):
                en = item["steps"]["en"]
                ar = item["steps"]["ar"]
                self.assertTrue(en and ar)
                self.assertEqual(len(en), len(ar))
                self.assertTrue(all(isinstance(step, str) and step.strip() for step in en))
                self.assertTrue(all(isinstance(step, str) and step.strip() for step in ar))

    def test_eighteen_reviewed_english_sequences_match_curated_copy(self):
        self.assertEqual(18, len(EXPECTED_ENGLISH_STEPS))
        for exercise_id, expected_steps in EXPECTED_ENGLISH_STEPS.items():
            with self.subTest(exercise_id=exercise_id):
                self.assertIn(exercise_id, self.by_id)
                item = self.by_id[exercise_id]
                self.assertEqual(expected_steps, item["steps"]["en"])
                self.assertEqual(len(item["steps"]["ar"]), len(expected_steps))

    def test_generic_english_repetition_fillers_are_absent_from_catalog(self):
        offenders = [
            (item["id"], step)
            for item in self.catalog
            for step in item["steps"]["en"]
            if step in GENERIC_ENGLISH_FILLER
        ]
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
