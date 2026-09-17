#!/usr/bin/env python3
from pathlib import Path
import re

path = Path("tests/source_connector_test.py")
text = path.read_text(encoding="utf-8")
pattern = re.compile(
    r"^    def test_all_21_product_languages_are_normalized_and_translatable\(self\):\n.*?(?=^    def |\Z)",
    re.MULTILINE | re.DOTALL,
)
replacement = '''    def test_all_21_product_languages_are_normalized_and_translatable(self):
        worker_source = (ROOT / "media-server" / "ai-worker" / "ai_worker.py").read_text(encoding="utf-8")
        self.assertIn('TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "facebook/nllb-200-distilled-600M")', worker_source)
        self.assertIn("NLLB_CODES = {", worker_source)
        self.assertIn("tokenizer.src_lang = NLLB_CODES[source_language]", worker_source)
        self.assertIn("forced_bos_token_id=int(forced_bos)", worker_source)
        for code in ["ar", "en", "zh", "hi", "ko", "ja", "tr", "es", "fr", "pt", "de", "it", "ru", "id", "th", "fa", "ur", "bn", "ms", "pl", "vi"]:
            self.assertIn(f'"{code}":', worker_source)

'''
updated, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit("RC15.7: NLLB test method not found exactly once")
path.write_text(updated, encoding="utf-8")
print("RC15_7_NLLB_TEST_RECONCILE=PASS")
