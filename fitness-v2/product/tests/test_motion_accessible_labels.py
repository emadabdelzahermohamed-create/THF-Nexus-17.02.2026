import json
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP_PATH = PULSE / "app.js"
HTML_PATH = PULSE / "index.html"
EXERCISES_PATH = PULSE / "data" / "exercises.js"
MOTION_PATH = PULSE / "data" / "motion-manifest.json"
CSS_PATH = PULSE / "styles.css"


def load_exercises():
    source = EXERCISES_PATH.read_text(encoding="utf-8")
    prefix = "window.THF_EXERCISES = "
    if not source.startswith(prefix):
        raise AssertionError("exercise runtime data must keep its known assignment wrapper")
    return json.loads(source[len(prefix):].strip().rstrip(";"))


class MotionAccessibleLabelsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP_PATH.read_text(encoding="utf-8")
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.exercises = {item["id"]: item for item in load_exercises()}
        cls.motion = json.loads(MOTION_PATH.read_text(encoding="utf-8"))
        cls.css = CSS_PATH.read_text(encoding="utf-8")

    def test_motion_labels_are_localized_by_actual_media_kind(self):
        self.assertIn("function motionAccessibleLabel(item, entry = motionAsset(item))", self.app)
        for phrase in (
            "فيديو تمرين ${name} يعمل دون اتصال",
            "مقطع حركة موثّق لتمرين ${name}",
            "Offline exercise video: ${name}",
            "Verified motion clip: ${name}",
        ):
            self.assertIn(phrase, self.app)

    def test_card_detail_and_active_workout_use_motion_aware_labels(self):
        player_start = self.app.index("function motionPlayer(item, context = 'detail')")
        credit_start = self.app.index("function motionCredit(item)", player_start)
        player = self.app[player_start:credit_start]
        active_start = self.app.index("function renderActiveMotion(item)")
        workout_start = self.app.index("function renderActiveWorkout()", active_start)
        active = self.app[active_start:workout_start]

        self.assertIn("motionAccessibleLabel(item, entry)", player)
        self.assertIn("motionAccessibleLabel(item, motion)", active)
        self.assertNotIn("local(item.demo?.alt) || local(item.name)", player)
        self.assertNotIn("item.demo.alt[state.lang]", active)

    def test_all_manifest_entries_map_to_existing_exercises_and_avoid_stale_alt_for_video(self):
        self.assertEqual(7, len(self.motion))
        kinds = {}
        for exercise_id, entry in self.motion.items():
            kinds[entry["kind"]] = kinds.get(entry["kind"], 0) + 1
            item = self.exercises.get(exercise_id)
            self.assertIsNotNone(item, f"manifest exercise missing from catalog: {exercise_id}")
            self.assertIn("name", item)
            self.assertIn("en", item["name"])
            self.assertIn("ar", item["name"])
            if entry["kind"] == "offline_video":
                self.assertTrue(entry["asset"].endswith((".mp4", ".webm")))
                self.assertIn("licenseUrl", entry)
                self.assertIn("Start and finish positions", item["demo"]["alt"]["en"])
            elif entry["kind"] == "verified_frame_sequence":
                self.assertTrue(entry["asset"].endswith(".webm"))
                self.assertIn("Start and finish positions", item["demo"]["alt"]["en"])
            else:
                self.fail(f"unexpected motion kind: {entry['kind']}")
        self.assertEqual({"offline_video": 5, "verified_frame_sequence": 2}, kinds)


    def test_offline_banner_reports_actual_motion_demo_coverage(self):
        self.assertIn("const offlineReferenceFrameCount = EXERCISES.filter(item => !motionManifest[item.id] && hasSafeReferenceFrames(item)).length;", self.app)
        self.assertIn("offlineBanner:offlineMotionCoverage.ar", self.app)
        self.assertIn("offlineBanner:offlineMotionCoverage.en", self.app)
        self.assertIn("7 manifest-backed motion demos plus", self.app)
        self.assertIn("عروض حركة بملفات مخصصة", self.app)
        self.assertNotIn("motion demos are available offline for ${Object.keys(motionManifest).length} selected exercises", self.app)
        self.assertIn('data-i18n="offlineBanner">مكتبة التمارين تعمل دون اتصال، مع عروض حركة موثقة وصور مرجعية تتحرك تلقائيًا.</span>', self.html)

        self.assertEqual(112, len(self.exercises))
        self.assertEqual(7, len(self.motion))
        reference_only = []
        for item in self.exercises.values():
            assets = item.get("demo", {}).get("assets", [])
            safe_pair = (
                item["id"] not in self.motion
                and isinstance(assets, list)
                and len(assets) == 2
                and all(isinstance(asset, str) and re.fullmatch(r"media/free-exercise-db/[A-Za-z0-9_/-]+\\.jpg", asset, re.IGNORECASE) for asset in assets)
            )
            if safe_pair:
                reference_only.append(item["id"])
        self.assertEqual(105, len(reference_only))
        self.assertEqual(112, len(self.motion) + len(reference_only))


    def test_active_workout_demo_respects_reduced_motion_and_os_changes(self):
        show_start = self.app.index("function showScreen")
        show_end = self.app.index("function applyLanguage", show_start)
        show_screen = self.app[show_start:show_end]
        self.assertIn("syncActiveDemoPlayback();", show_screen)
        self.assertIn("preferredReducedMotion() ? 'auto' : 'smooth'", show_screen)
        self.assertNotIn("demoVideo.play()", show_screen)

        active_start = self.app.index("function renderActiveMotion(item)")
        active_end = self.app.index("function renderActiveWorkout()", active_start)
        active_motion = self.app[active_start:active_end]
        self.assertIn("syncActiveDemoPlayback();", active_motion)
        self.assertNotIn("if (!document.hidden) video.play()", active_motion)

        preference_start = self.app.index("function preferredReducedMotion()")
        bind_start = self.app.index("function bind()")
        preference_code = self.app[preference_start:bind_start]
        self.assertIn("function syncActiveDemoPlayback()", preference_code)
        self.assertIn("if(reduced && !activeDemoManualPlay){video.pause();return;}", preference_code)
        self.assertIn("if(document.hidden || !workoutVisible){", preference_code)
        self.assertIn("if(activeDemoManualPlay){activeDemoManualPlay=false;video.loop=true;}", preference_code)
        self.assertIn("Motion paused by reduced-motion preference", preference_code)
        self.assertIn("function bindReducedMotionPreference()", preference_code)
        self.assertIn("media.addEventListener('change',onChange)", preference_code)
        self.assertIn("media.addListener(onChange)", preference_code)
        self.assertIn("store.getItem('pulse.v2.reduceMotion')!==null", preference_code)
        self.assertIn("syncActiveDemoPlayback();", preference_code)

        visibility_start = self.app.index("document.addEventListener('visibilitychange',()=>{syncActiveDemoPlayback();")
        visibility = self.app[visibility_start:visibility_start + 260]
        self.assertIn("syncActiveDemoPlayback();", visibility)
        active_video = next(line for line in self.html.splitlines() if 'id="activeDemoVideo"' in line)
        self.assertNotIn("autoplay", active_video)


    def test_active_reference_animation_uses_exact_exercise_id_before_rendering(self):
        workout_start = self.app.index("function renderActiveWorkout()")
        workout_end = self.app.index("\n  function ", workout_start + 1)
        self.assertGreater(workout_end, workout_start)
        workout = self.app[workout_start:workout_end]
        identity_assignment = "$('activeWorkoutScreen').dataset.exerciseId = item.id;"
        self.assertIn(identity_assignment, workout)
        self.assertLess(workout.index(identity_assignment), workout.index("renderActiveMotion(item);"))

        motion_runtime = (PULSE / "data" / "motion-manifest.js").read_text(encoding="utf-8")
        self.assertIn("const explicitId = byId('activeWorkoutScreen')?.dataset?.exerciseId;", motion_runtime)
        self.assertIn("if (exact) return exact;", motion_runtime)
        self.assertIn("attributeFilter: ['class', 'data-exercise-id']", motion_runtime)

    def test_active_workout_uses_offline_reference_frames_without_tap_and_respects_motion_preference(self):
        active_start = self.app.index("function renderActiveMotion(item)")
        active_end = self.app.index("function renderActiveWorkout()", active_start)
        active_motion = self.app[active_start:active_end]
        self.assertIn("const reference = $('activeDemoReference');", active_motion)
        self.assertIn("reference.innerHTML = referenceMotionPlayer(item, 'detail');", active_motion)
        self.assertIn("syncActiveReferenceMotionLabel(item);", active_motion)
        self.assertIn("function hasSafeReferenceFrames(item)", self.app)
        self.assertIn("return assets.length === 2 && assets.every(", self.app)
        self.assertIn("function syncActiveReferenceMotionLabel(item = activeExercise())", active_motion)
        self.assertIn("referenceMotionAuto:'عرض مرجعي تلقائي'", self.app)
        self.assertIn("referenceMotionStatic:'صور مرجعية ثابتة — تقليل الحركة'", self.app)
        self.assertIn("referenceMotionUnavailable:'لا تتوفر إطارات مرجعية للحركة في هذا التمرين'", self.app)
        self.assertIn("referenceMotionAuto:'Automatic reference-frame demo'", self.app)
        self.assertIn("referenceMotionStatic:'Reference frames paused — reduced motion'", self.app)
        self.assertIn("referenceMotionUnavailable:'Motion frames are unavailable for this exercise'", self.app)
        self.assertIn("animation:thf-reference-start 3.6s steps(1,end) infinite", self.css)
        self.assertIn("animation:thf-reference-finish 3.6s steps(1,end) infinite", self.css)
        self.assertIn(".motion-reduced .exercise-reference-motion img:first-of-type", self.css)
        self.assertIn(":root:not(.motion-allow-animations) .exercise-reference-motion img:first-of-type", self.css)
        self.assertIn("classList.toggle('motion-allow-animations',!enabled && hasExplicitChoice)", self.app)
        self.assertIn('id="activeDemoReference"', self.html)
        phase = next(line for line in self.html.splitlines() if 'id="activeDemoPhase"' in line)
        self.assertIn('aria-live="polite"', phase)
        self.assertIn('aria-atomic="true"', phase)
        self.assertNotIn('id="activeDemoImage"', self.html)
        self.assertNotIn("activeDemoImage", self.app)

    def test_reduced_motion_offers_accessible_one_shot_demo_playback(self):
        button = next(line for line in self.html.splitlines() if 'id="activeDemoPlayOnce"' in line)
        self.assertIn('type="button"', button)
        self.assertIn('class="button secondary active-demo-play-once hidden"', button)
        self.assertIn('data-i18n="playDemoOnce"', button)
        self.assertIn('aria-controls="activeDemoVideo"', button)
        self.assertIn('aria-describedby="activeDemoPhase"', button)
        self.assertIn("playDemoOnce:'شغّل العرض مرة واحدة'", self.app)
        self.assertIn("playDemoOnce:'Play demo once'", self.app)
        self.assertIn("motionDemoPlayingOnce:'يتم تشغيل العرض مرة واحدة'", self.app)
        self.assertIn("motionDemoPlayingOnce:'Playing demo once'", self.app)
        self.assertIn("function playActiveDemoOnce()", self.app)
        self.assertIn("video.loop=false;", self.app)
        self.assertIn("video.currentTime=0;", self.app)
        self.assertIn("playback.catch", self.app)
        self.assertIn("$('activeDemoVideo').addEventListener('ended'", self.app)
        self.assertIn("const canOfferManual=reduced && workoutVisible && !document.hidden && !manualPlayback;", self.app)
        self.assertIn("if (activeDemoExerciseId !== item.id)", self.app)
        self.assertIn("try{video.currentTime=0;}catch{}", self.app)
        self.assertIn(".active-demo-play-once{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);", self.css)
        self.assertIn(".active-demo-play-once:active{transform:translate(-50%,-49%)}", self.css)


    def test_reference_frame_phase_labels_match_visible_frame_and_localize(self):
        player_start = self.app.index("function referenceMotionPlayer(item, context = 'detail')")
        player_end = self.app.index("function motionPlayer(item, context = 'detail')", player_start)
        player = self.app[player_start:player_end]
        self.assertIn("state.lang === 'ar' ? 'البداية' : 'Start'", player)
        self.assertIn("state.lang === 'ar' ? 'النهاية' : 'Finish'", player)
        self.assertIn("const phaseLabels = context === 'card' ? '' :", player)
        self.assertIn('class="reference-frame-label reference-frame-label-start" aria-hidden="true"', player)
        self.assertIn('class="reference-frame-label reference-frame-label-finish" aria-hidden="true"', player)
        self.assertIn("${phaseLabels}</div>`;", player)
        self.assertIn("animation:thf-reference-start-label 3.6s steps(1,end) infinite", self.css)
        self.assertIn("animation:thf-reference-finish-label 3.6s steps(1,end) infinite", self.css)
        self.assertIn("@keyframes thf-reference-start-label{0%,49.99%{opacity:1}50%,100%{opacity:0}}", self.css)
        self.assertIn("@keyframes thf-reference-finish-label{0%,49.99%{opacity:0}50%,100%{opacity:1}}", self.css)
        self.assertIn(".motion-reduced .exercise-reference-motion .reference-frame-label-start{opacity:1;animation:none!important}", self.css)
        self.assertIn(".motion-reduced .exercise-reference-motion .reference-frame-label-finish{opacity:0;animation:none!important}", self.css)
        self.assertIn(":root:not(.motion-allow-animations) .exercise-reference-motion .reference-frame-label-start{opacity:1!important;animation:none!important}", self.css)
        self.assertIn(":root:not(.motion-allow-animations) .exercise-reference-motion .reference-frame-label-finish{opacity:0!important;animation:none!important}", self.css)



if __name__ == "__main__":
    unittest.main()
