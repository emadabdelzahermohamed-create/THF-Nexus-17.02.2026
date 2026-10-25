import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
CATALOG_PATH = PULSE / "data" / "exercises.json"
MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "CATALOG_MANIFEST.json"
PROGRAMS_PATH = PULSE / "data" / "programs.json"
PROGRAMS_MANIFEST_PATH = ROOT / "fitness-v2" / "product" / "PROGRAMS_MANIFEST.json"
CATALOG_BUILDER_PATH = ROOT / "fitness-v2" / "product" / "tools" / "build_catalog.py"

CATALOG_BUILDER_SPEC = importlib.util.spec_from_file_location(
    "thf_build_catalog",
    CATALOG_BUILDER_PATH,
)
CATALOG_BUILDER = importlib.util.module_from_spec(CATALOG_BUILDER_SPEC)
CATALOG_BUILDER_SPEC.loader.exec_module(CATALOG_BUILDER)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ProductCatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG_PATH.read_text())
        cls.manifest = json.loads(MANIFEST_PATH.read_text())
        cls.programs = json.loads(PROGRAMS_PATH.read_text())
        cls.programs_manifest = json.loads(PROGRAMS_MANIFEST_PATH.read_text())

    def guidance_diversity_validator(self):
        self.assertTrue(
            hasattr(CATALOG_BUILDER, "validate_guidance_diversity"),
            "catalog builder must expose validate_guidance_diversity",
        )
        return CATALOG_BUILDER.validate_guidance_diversity

    def test_catalog_is_large_and_every_required_section_is_real(self):
        self.assertEqual(112, len(self.catalog))
        expected = {
            "gym", "home", "running", "cycling", "football", "swimming", "yoga",
            "calisthenics", "boxing", "hiit", "mobility", "recovery", "team_sports",
        }
        counts = self.manifest["sectionCounts"]
        self.assertEqual(expected, set(counts))
        self.assertTrue(all(counts[section] >= 6 for section in expected))
        self.assertGreaterEqual(counts["gym"], 36)

    def test_every_exercise_has_bilingual_contract_and_tracking_metadata(self):
        bilingual = (
            "name", "setup", "breathing", "commonMistakes", "regression", "progression", "safety",
        )
        identifiers = set()
        source_identifiers = set()
        for item in self.catalog:
            self.assertNotIn(item["id"], identifiers)
            identifiers.add(item["id"])
            self.assertNotIn(item["sourceItemId"], source_identifiers)
            source_identifiers.add(item["sourceItemId"])
            for field in bilingual:
                self.assertTrue(item[field]["ar"], f"{item['id']} missing {field}.ar")
                self.assertTrue(item[field]["en"], f"{item['id']} missing {field}.en")
            self.assertGreaterEqual(len(item["steps"]["ar"]), 3)
            self.assertGreaterEqual(len(item["steps"]["en"]), 1)
            self.assertTrue(item["muscles"]["primary"]["ar"])
            self.assertTrue(item["muscles"]["primary"]["en"])
            self.assertTrue(item["equipment"]["id"])
            self.assertTrue(item["level"]["id"])
            self.assertTrue(item["movement"]["id"])
            self.assertTrue(item["goal"]["id"])
            self.assertIn("sets", item["prescription"])
            self.assertIn("restSeconds", item["prescription"])
            self.assertEqual({"load", "rpe", "rir", "volume"}, set(item["tracking"]))
            self.assertEqual(
                f"exercises/{item['sourceItemId']}.json",
                item["provenance"]["sourcePath"],
            )

    def test_every_movement_family_has_distinct_bilingual_guidance(self):
        expected_families = {
            "squat", "hinge", "horizontal_push", "vertical_push",
            "horizontal_pull", "vertical_pull", "isolation", "core",
            "locomotion", "jump", "mobility", "recovery",
        }
        exception_ids = {
            "Barbell_Step_Ups", "Dumbbell_Step_Ups", "Step-up_with_Knee_Raise",
            "Bodyweight_Walking_Lunge", "Leg_Extensions", "Platform_Hamstring_Slides",
            "Incline_Dumbbell_Press", "Side_Bridge", "Flutter_Kicks",
            "Downward_Facing_Balance", "Superman", "Mountain_Climbers",
            "Linear_Acceleration_Wall_Drill", "Straight-Arm_Dumbbell_Pullover",
            "One-Arm_Medicine_Ball_Slam", "Overhead_Slam",
            "Medicine_Ball_Chest_Pass", "Medicine_Ball_Scoop_Throw",
            "Catch_and_Overhead_Throw",
        }
        guidance_by_family = {}
        for item in self.catalog:
            if item["sourceItemId"] in exception_ids:
                continue
            family = item["movement"]["id"]
            guidance = {
                language: tuple(
                    item[field][language]
                    for field in ("safety", "regression", "progression")
                )
                for language in ("ar", "en")
            }
            if family in guidance_by_family:
                self.assertEqual(guidance_by_family[family], guidance)
            else:
                guidance_by_family[family] = guidance

        self.assertEqual(expected_families, set(guidance_by_family))
        for language in ("ar", "en"):
            self.assertEqual(
                12,
                len({guidance[language] for guidance in guidance_by_family.values()}),
                f"{language} guidance must remain distinct across movement families",
            )

    def test_guidance_diversity_validator_accepts_current_arabic_and_english(self):
        self.guidance_diversity_validator()(CATALOG_BUILDER.GUIDANCE)

    def test_guidance_diversity_validator_rejects_arabic_only_collapse(self):
        guidance = copy.deepcopy(CATALOG_BUILDER.GUIDANCE)
        for field in ("regression", "progression", "safety"):
            guidance["hinge"][f"{field}_ar"] = guidance["squat"][f"{field}_ar"]

        with self.assertRaisesRegex(ValueError, "Arabic guidance must contain 12 distinct families"):
            self.guidance_diversity_validator()(guidance)

    def test_guidance_diversity_validator_rejects_english_only_collapse(self):
        guidance = copy.deepcopy(CATALOG_BUILDER.GUIDANCE)
        for field in ("regression", "progression", "safety"):
            guidance["hinge"][f"{field}_en"] = guidance["squat"][f"{field}_en"]

        with self.assertRaisesRegex(ValueError, "English guidance must contain 12 distinct families"):
            self.guidance_diversity_validator()(guidance)

    def test_guidance_diversity_validator_rejects_missing_language_copy(self):
        guidance = copy.deepcopy(CATALOG_BUILDER.GUIDANCE)
        del guidance["squat"]["safety_ar"]

        with self.assertRaisesRegex(ValueError, "missing safety_ar for squat"):
            self.guidance_diversity_validator()(guidance)

    def test_guidance_diversity_validator_rejects_missing_family(self):
        guidance = copy.deepcopy(CATALOG_BUILDER.GUIDANCE)
        del guidance["squat"]

        with self.assertRaisesRegex(ValueError, "exactly the 12 movement families"):
            self.guidance_diversity_validator()(guidance)

    def test_named_family_outliers_receive_non_contradictory_guidance(self):
        items = {item["sourceItemId"]: item for item in self.catalog}
        fields = ("safety", "regression", "progression")
        languages = ("ar", "en")
        guidance = lambda item: tuple(
            item[field][language] for field in fields for language in languages
        )

        for source_id in ("Leg_Extensions",):
            self.assertEqual(guidance(items["Dumbbell_Bicep_Curl"]), guidance(items[source_id]))
        for source_id in ("Incline_Dumbbell_Press",):
            self.assertEqual(guidance(items["Pushups"]), guidance(items[source_id]))
        for source_id in (
            "Side_Bridge", "Flutter_Kicks", "Downward_Facing_Balance",
            "Superman", "Mountain_Climbers",
        ):
            self.assertEqual(guidance(items["Plank"]), guidance(items[source_id]))
        for source_id in ("Linear_Acceleration_Wall_Drill",):
            self.assertEqual(guidance(items["Trail_Running_Walking"]), guidance(items[source_id]))
        for source_id in ("Straight-Arm_Dumbbell_Pullover",):
            self.assertEqual(guidance(items["Bent_Over_Barbell_Row"]), guidance(items[source_id]))

        step_ids = (
            "Barbell_Step_Ups", "Dumbbell_Step_Ups", "Step-up_with_Knee_Raise",
            "Bodyweight_Walking_Lunge",
        )
        self.assertEqual(1, len({guidance(items[source_id]) for source_id in step_ids}))
        self.assertIn("working foot", items[step_ids[0]]["safety"]["en"])

        throw_ids = (
            "One-Arm_Medicine_Ball_Slam", "Overhead_Slam",
            "Medicine_Ball_Chest_Pass", "Medicine_Ball_Scoop_Throw",
            "Catch_and_Overhead_Throw",
        )
        self.assertEqual(1, len({guidance(items[source_id]) for source_id in throw_ids}))
        self.assertIn("throwing area", items[throw_ids[0]]["safety"]["en"])
        self.assertNotIn("landing", items[throw_ids[0]]["safety"]["en"].lower())

        self.assertIn("sliding surface", items["Platform_Hamstring_Slides"]["safety"]["en"])

    def test_high_risk_families_receive_behavior_specific_guidance(self):
        examples = {
            item["movement"]["id"]: item
            for item in self.catalog
            if item["movement"]["id"] in {"jump", "locomotion", "recovery"}
        }
        self.assertEqual(
            "Land quietly on a clear, stable surface; stop when landing alignment or balance deteriorates.",
            examples["jump"]["safety"]["en"],
        )
        self.assertEqual(
            "اخفض السرعة أو الزمن أو الميل، واختر مسارًا مستويًا أو جهازًا ثابتًا يمكن التحكم فيه.",
            examples["locomotion"]["regression"]["ar"],
        )
        self.assertEqual(
            "Progress with slightly more time or controlled pressure, never by rolling directly over a joint or nerve.",
            examples["recovery"]["progression"]["en"],
        )

    def test_every_demo_is_two_frame_offline_and_hash_verified(self):
        asset_count = 0
        for item in self.catalog:
            self.assertTrue(item["demo"]["offline"])
            self.assertEqual("two_frame_image_sequence", item["demo"]["type"])
            self.assertEqual(2, len(item["demo"]["assets"]))
            hashes = {entry["path"]: entry["sha256"] for entry in item["provenance"]["assetHashes"]}
            for relative in item["demo"]["assets"]:
                asset = PULSE / relative
                self.assertTrue(asset.is_file(), relative)
                self.assertEqual(hashes[relative], sha256(asset))
                asset_count += 1
        self.assertEqual(224, asset_count)
        self.assertEqual(asset_count, self.manifest["offlineDemoAssets"])

    def test_provenance_is_pinned_to_public_domain_source(self):
        source = self.manifest["source"]
        self.assertEqual("f00c92c7dcf1216a928a52c3706c7ce8e2f71ed5", source["commit"])
        self.assertEqual("Unlicense", source["license"])
        self.assertEqual("6b0382b16279f26ff69014300541967a356a666eb0b91b422f6862f6b7dad17e", source["licenseSha256"])
        self.assertEqual("5bb747e3fc658f095a60dcbf6d53c96627acdcc6ffb6fffde86f7e26995d40bf", source["datasetSha256"])
        license_path = ROOT / "fitness-v2" / "product" / "sources" / "free-exercise-db" / "LICENSE.md"
        self.assertEqual(source["licenseSha256"], sha256(license_path))
        self.assertTrue(all(item["provenance"]["commit"] == source["commit"] for item in self.catalog))

    def test_navigation_train_and_workout_surfaces_are_reachable_and_stage16a_free(self):
        html = (PULSE / "index.html").read_text()
        script = (PULSE / "app.js").read_text()
        nav_order = re.findall(r'data-screen="([^"]+)"', re.search(r'<nav id="primaryNav".*?</nav>', html, re.S).group())
        self.assertEqual(["todayScreen", "trainScreen", "progressScreen", "healthScreen", "profileScreen"], nav_order)
        for marker in (
            'id="exerciseSearch"', 'id="sectionRail"', 'id="filterPanel"', 'id="exerciseDetail"',
            'id="activeWorkoutScreen"', 'id="setRows"', 'id="healthScreen"', 'id="profileForm"',
        ):
            self.assertIn(marker, html)
        for handler in (
            "openDetail", "startExercise", "completeSet", "finishWorkout", "saveProfile", "renderProgress",
        ):
            self.assertIn(f"function {handler}", script)
        self.assertIn("${EXERCISES.length} documented exercises", script)
        self.assertIn("112 تمرينًا موثقًا", html)
        combined = html + script + (PULSE / "styles.css").read_text()
        self.assertNotRegex(combined, r"(?i)stage16a")
        self.assertNotRegex(combined, r"https?://")

    def test_catalog_marketing_copy_has_no_stale_fixed_exercise_count(self):
        script = (PULSE / "app.js").read_text()
        self.assertNotIn("80 تمرينًا موثقًا", script)
        self.assertNotIn("80 documented exercises", script)
        self.assertIn("${EXERCISES.length} تمرينًا موثقًا", script)
        self.assertIn("${EXERCISES.length} documented exercises", script)

    def test_workout_inputs_persist_before_set_completion(self):
        script = (PULSE / "app.js").read_text()
        self.assertIn("input.addEventListener('input'", script)
        self.assertNotIn("input.addEventListener('change'", script)
        self.assertIn("persistActive();", script)

    def test_active_workout_uses_verified_automatic_motion_when_available(self):
        html = (PULSE / "index.html").read_text()
        script = (PULSE / "app.js").read_text()
        manifest_path = PULSE / "data" / "motion-manifest.json"
        manifest = json.loads(manifest_path.read_text())

        self.assertIn('id="activeDemoVideo"', html)
        self.assertIn("autoplay", html)
        self.assertIn("muted", html)
        self.assertIn("loop", html)
        self.assertIn("playsinline", html)
        self.assertNotIn('id="toggleDemoFrame"', html)
        self.assertIn("visibilitychange", script)
        self.assertIn("motionManifest", script)
        self.assertIn("video.play()", script)

        self.assertEqual({"bodyweight-squat", "pushups"}, set(manifest))
        for exercise_id, motion in manifest.items():
            with self.subTest(exercise_id=exercise_id):
                self.assertEqual("verified_frame_sequence", motion["kind"])
                self.assertEqual(16, motion["sourceFrameCount"])
                self.assertEqual(8, motion["fps"])
                video_path = PULSE / motion["asset"]
                self.assertTrue(video_path.is_file())
                self.assertEqual(motion["sha256"], sha256(video_path))

    def test_program_library_replaces_legacy_baseline_across_every_section(self):
        expected = {
            "gym", "home", "running", "cycling", "football", "swimming", "yoga",
            "calisthenics", "boxing", "hiit", "mobility", "recovery", "team_sports",
        }
        self.assertEqual(26, len(self.programs))
        self.assertEqual(26, self.programs_manifest["programCount"])
        self.assertEqual(expected, set(self.programs_manifest["sectionCounts"]))
        self.assertTrue(all(count == 2 for count in self.programs_manifest["sectionCounts"].values()))
        self.assertEqual(self.programs_manifest["programsSha256"], sha256(PROGRAMS_PATH))

    def test_every_program_is_bilingual_offline_safe_and_references_real_exercises(self):
        exercise_ids = {item["id"] for item in self.catalog}
        program_ids = set()
        for program in self.programs:
            self.assertNotIn(program["id"], program_ids)
            program_ids.add(program["id"])
            for field in ("name", "summary", "goal", "level", "safety"):
                self.assertTrue(program[field]["ar"], f"{program['id']} missing {field}.ar")
                self.assertTrue(program[field]["en"], f"{program['id']} missing {field}.en")
            self.assertTrue(program["offline"])
            self.assertGreaterEqual(program["weeks"], 4)
            self.assertGreaterEqual(program["daysPerWeek"], 3)
            self.assertEqual(program["daysPerWeek"], len(program["sessions"]))
            self.assertGreaterEqual(len(program["progression"]["ar"]), 4)
            self.assertGreaterEqual(len(program["progression"]["en"]), 4)
            self.assertEqual("Unlicense", program["provenance"]["exerciseCatalogLicense"])
            self.assertEqual("f00c92c7dcf1216a928a52c3706c7ce8e2f71ed5", program["provenance"]["exerciseCatalogCommit"])
            for session in program["sessions"]:
                self.assertTrue(session["name"]["ar"])
                self.assertTrue(session["name"]["en"])
                self.assertGreaterEqual(len(session["exercises"]), 5)
                for reference in session["exercises"]:
                    self.assertIn(reference["exerciseId"], exercise_ids)
                    self.assertIn(reference["role"], {"warmup", "working"})
                    self.assertGreaterEqual(reference["sets"], 2)
                    self.assertGreaterEqual(reference["targetRpe"], 1)
                    self.assertGreaterEqual(reference["targetRir"], 0)

    def test_programs_are_reachable_selectable_and_update_today(self):
        html = (PULSE / "index.html").read_text()
        script = (PULSE / "app.js").read_text()
        self.assertLess(html.index("./data/programs.js"), html.index("./app.js"))
        for marker in (
            'id="trainModeTabs"', 'id="programsPane"', 'id="programSectionRail"',
            'id="programGrid"', 'id="programDetail"', 'id="useProgramBtn"',
        ):
            self.assertIn(marker, html)
        for handler in (
            "renderTrainMode", "renderProgramSections", "renderPrograms", "openProgramDetail",
            "renderProgramDetail", "useProgram", "startProgramSession",
        ):
            self.assertIn(f"function {handler}", script)
        self.assertIn("pulse.v2.program", script)
        self.assertIn("data-start-program", script)
        self.assertIn("programEntries", script)
        self.assertIn("set.exerciseId||entry.id", script)
        self.assertIn("showScreen('activeWorkoutScreen', false)", script)
        self.assertIn('aria-controls="programsPane"', html)
        self.assertIn('aria-controls="exerciseLibraryPane"', html)

    def test_first_run_onboarding_creates_the_training_profile(self):
        html = (PULSE / "index.html").read_text()
        script = (PULSE / "app.js").read_text()
        styles = (PULSE / "styles.css").read_text()
        for marker in (
            'id="onboardingDialog"', 'id="onboardingForm"', 'id="onboardingGoal"',
            'id="onboardingLevel"', 'id="onboardingDays"',
            'id="onboardingEquipmentChoices"', 'id="onboardingLanguageToggle"',
        ):
            self.assertIn(marker, html)
        for handler in (
            "renderOnboarding", "captureOnboardingDraft", "openOnboarding",
            "completeOnboarding", "toggleLanguage",
        ):
            self.assertIn(f"function {handler}", script)
        self.assertIn("!store.getItem('pulse.v2.profile') && !state.active", script)
        self.assertIn("store.setItem('pulse.v2.profile'", script)
        self.assertIn("showScreen('todayScreen')", script)
        self.assertNotIn('id="skipOnboarding"', html)
        self.assertIn(".onboarding-shell", styles)
        self.assertIn(".onboarding-benefits", styles)

    def test_mobile_set_logger_uses_labeled_one_handed_cards(self):
        script = (PULSE / "app.js").read_text()
        styles = (PULSE / "styles.css").read_text()
        self.assertEqual(4, script.count('class="set-field"'))
        self.assertIn(".set-table-head{display:none}", styles)
        self.assertIn(".set-row{grid-template-columns:1fr 1fr;min-width:0", styles)
        self.assertIn(".set-complete{grid-column:1/-1;width:100%;height:44px", styles)
        self.assertIn(".set-logger{overflow:visible}", styles)
        self.assertIn("document.body.classList.toggle('workout-active'", script)
        self.assertIn(".workout-active .workout-actions{bottom:calc(5px + env(safe-area-inset-bottom))}", styles)

    def test_accessible_names_follow_arabic_and_english_language_switches(self):
        html = (PULSE / "index.html").read_text()
        script = (PULSE / "app.js").read_text()
        expected = {
            "readinessToday", "todaySummary", "trainContentType", "programSections",
            "clearSearch", "trainingSections", "voiceGuidance", "volumeChartLabel",
            "onboardingBenefitsLabel", "close",
        }
        bound = set(re.findall(r'data-i18n-aria-label="([^"]+)"', html))
        self.assertEqual(expected, bound)
        self.assertIn("document.querySelectorAll('[data-i18n-aria-label]')", script)
        for key in expected:
            self.assertRegex(script, r"(?:^|[,{])" + re.escape(key) + r":")


if __name__ == "__main__":
    unittest.main()
