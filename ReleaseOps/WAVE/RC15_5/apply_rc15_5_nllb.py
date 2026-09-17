#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path.cwd()


def patch(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"NLLB patch anchor missing: {path}: {old[:100]!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# Avoid depending on a particular Pydantic URL alias in the reconstructed base.
patch(
    "media-server/api/main.py",
    "    page_url: HttpUrl\n\n\nclass LocalizedText(BaseModel):",
    '    page_url: str = Field(min_length=9, max_length=4096)\n\n\nclass LocalizedText(BaseModel):',
)

ai_path = ROOT / "media-server/ai-worker/ai_worker.py"
ai = ai_path.read_text(encoding="utf-8")
ai = ai.replace('google/madlad400-3b-mt', 'facebook/nllb-200-distilled-600M')

codes = '''NLLB_CODES = {
    "ar": "arb_Arab", "en": "eng_Latn", "zh": "zho_Hans", "hi": "hin_Deva",
    "ko": "kor_Hang", "ja": "jpn_Jpan", "tr": "tur_Latn", "es": "spa_Latn",
    "fr": "fra_Latn", "pt": "por_Latn", "de": "deu_Latn", "it": "ita_Latn",
    "ru": "rus_Cyrl", "id": "ind_Latn", "th": "tha_Thai", "fa": "pes_Arab",
    "ur": "urd_Arab", "bn": "ben_Beng", "ms": "zsm_Latn", "pl": "pol_Latn",
    "vi": "vie_Latn",
}


'''
if "NLLB_CODES = {" not in ai:
    marker = "def load_translator():\n"
    if marker not in ai:
        raise SystemExit("load_translator anchor missing")
    ai = ai.replace(marker, codes + marker, 1)

old_translate = '''def translate_texts(texts: list[str], source_language: str, target_language: str) -> list[str]:
    if target_language == source_language:
        return texts
    tokenizer, model = load_translator()
    target_code = LANGUAGES[target_language][0]
    result: list[str] = []
    for start in range(0, len(texts), 12):
        batch = texts[start:start + 12]
        tagged_batch = [f"<2{target_code}> {text}" for text in batch]
        encoded = tokenizer(tagged_batch, return_tensors="pt", padding=True, truncation=True, max_length=384).to(AI_DEVICE)
        with torch.inference_mode():
            generated = model.generate(
                **encoded,
                max_new_tokens=384,
                num_beams=TRANSLATION_BEAMS,
                early_stopping=True,
            )
        result.extend(tokenizer.batch_decode(generated, skip_special_tokens=True))
    return result
'''
new_translate = '''def translate_texts(texts: list[str], source_language: str, target_language: str) -> list[str]:
    if target_language == source_language:
        return texts
    if source_language not in NLLB_CODES or target_language not in NLLB_CODES:
        raise ValueError(f"unsupported NLLB translation pair: {source_language}->{target_language}")
    tokenizer, model = load_translator()
    tokenizer.src_lang = NLLB_CODES[source_language]
    target_code = NLLB_CODES[target_language]
    forced_bos = tokenizer.convert_tokens_to_ids(target_code)
    if forced_bos is None or int(forced_bos) < 0:
        raise ValueError(f"NLLB target token is unavailable: {target_code}")
    result: list[str] = []
    for start in range(0, len(texts), 6):
        batch = texts[start:start + 6]
        encoded = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=384).to(AI_DEVICE)
        with torch.inference_mode():
            generated = model.generate(
                **encoded,
                forced_bos_token_id=int(forced_bos),
                max_new_tokens=384,
                num_beams=TRANSLATION_BEAMS,
                early_stopping=True,
            )
        result.extend(tokenizer.batch_decode(generated, skip_special_tokens=True))
    return result
'''
if old_translate not in ai:
    raise SystemExit("translate_texts anchor missing")
ai = ai.replace(old_translate, new_translate, 1)
ai_path.write_text(ai, encoding="utf-8")

for env_name in ["media-server/.env.example", "media-server/.env.universal.example"]:
    p = ROOT / env_name
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8")
    text = re.sub(r"^TRANSLATION_MODEL=.*$", "TRANSLATION_MODEL=facebook/nllb-200-distilled-600M", text, flags=re.M)
    p.write_text(text, encoding="utf-8")

print("RC15.5 NLLB patch applied: multilingual source -> Arabic target, CPU-sized translator")
