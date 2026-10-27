import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP_JS = PULSE / "app.js"
STYLES = PULSE / "styles.css"
PROGRAMS_JS = PULSE / "data" / "programs.js"


def load_programs():
    source = PROGRAMS_JS.read_text(encoding="utf-8")
    payload = source.partition("=")[2].strip()
    if payload.endswith(";"):
        payload = payload[:-1].rstrip()
    return json.loads(payload)


class ProgramEquipmentVisibilityTest(unittest.TestCase):
    def test_all_program_equipment_metadata_is_bilingual(self):
        programs = load_programs()
        self.assertEqual(26, len(programs))
        self.assertTrue(all(program.get("equipment") for program in programs))
        for program in programs:
            with self.subTest(program=program["id"]):
                for equipment in program["equipment"]:
                    self.assertTrue(equipment.get("en"))
                    self.assertTrue(equipment.get("ar"))

    def test_program_cards_and_details_render_equipment(self):
        app = APP_JS.read_text(encoding="utf-8")
        self.assertIn("function programEquipmentText(program)", app)
        self.assertIn("programEquipmentText(program)", app)
        self.assertIn("function programEquipmentTags(program)", app)
        self.assertIn("${programEquipmentTags(program)}", app)
        self.assertIn("program-equipment", app)

    def test_equipment_labels_exist_in_both_languages(self):
        app = APP_JS.read_text(encoding="utf-8")
        self.assertIn("programEquipment:'المعدات المذكورة'", app)
        self.assertIn("programEquipment:'Equipment listed'", app)
        self.assertIn("noProgramEquipment:'لم تُحدد معدات'", app)
        self.assertIn("noProgramEquipment:'No equipment listed'", app)

    def test_equipment_names_are_escaped_and_long_lists_wrap(self):
        app = APP_JS.read_text(encoding="utf-8")
        styles = STYLES.read_text(encoding="utf-8")
        self.assertIn("escapeHtml(programEquipmentText(program))", app)
        self.assertIn("escapeHtml(local(item))", app)
        self.assertIn("overflow-wrap:anywhere", styles)


if __name__ == "__main__":
    unittest.main()
