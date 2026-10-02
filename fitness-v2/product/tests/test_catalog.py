import hashlib
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

    def test_catalog_is_large_and_every_required_section_is_real(self):
        self.assertEqual(80, len(self.catalog))
        expected = {
            "gym", "home", "running", "cycling", "football", "swimming", "yoga",
            "calisthenics", "boxing", "hiit", "mobility", "recovery", "team_sports",
        }
        counts = self.manifest["sectionCounts"]
        self.assertEqual(expected, set(counts))
        self.assertTrue(all(counts[section] >= 2 for section in expected))
        self.assertGreaterEqual(counts["gym"], 36)

    def test_every_exercise_has_bilingual_contract_and_tracking_metadata(self):
        bilingual = (
            "name", "setup", "breathing", "commonMistakes", "regression", "progression", "safety",
        )
        identifiers = set()
        for item in self.catalog:
            self.assertNotIn(item["id"], identifiers)
            identifiers.add(item["id"])
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
        self.assertEqual(160, asset_count)
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
        combined = html + script + (PULSE / "styles.css").read_text()
        self.assertNotRegex(combined, r"(?i)stage16a")
        self.assertNotRegex(combined, r"https?://")

    def test_workout_inputs_persist_before_set_completion(self):
        script = (PULSE / "app.js").read_text()
        self.assertIn("input.addEventListener('input'", script)
        self.assertNotIn("input.addEventListener('change'", script)
        self.assertIn("persistActive();", script)

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


if __name__ == "__main__":
    unittest.main()
