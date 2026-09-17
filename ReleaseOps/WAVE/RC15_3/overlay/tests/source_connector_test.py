from __future__ import annotations

import copy
import ast
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "media-server" / "api"))

from source_connector import (  # noqa: E402
    LOCALES,
    SourceManifestError,
    canonical_source_origin,
    normalize_manifest_document,
)


def manifest() -> dict[str, object]:
    now = datetime.now(timezone.utc)
    return {
        "version": "wave-media-source/v1",
        "source_name": "Licensed Partner",
        "authorization": {
            "platform": "wave_موجة",
            "allow_copy_to_private_storage": True,
            "allow_transcode": True,
            "allow_publish": True,
            "rights": {
                "owner": "Licensed Partner",
                "basis": "written-license",
                "evidence_reference": "CONTRACT-42",
                "territories": ["EG", "SA"],
                "starts_at": (now - timedelta(days=1)).isoformat(),
                "expires_at": (now + timedelta(days=30)).isoformat(),
                "allow_download": True,
                "allow_ads": True,
            },
        },
        "allowed_media_hosts": ["cdn.partner.example"],
        "items": [
            {
                "external_id": "film:42", "kind": "movie", "slug": "licensed-film-42",
                "source_url": "https://cdn.partner.example/film.mp4", "title": {"ar": "الفيلم"},
                "downloads_allowed": True, "ads_allowed": True,
            },
            {
                "external_id": "show:42:s01e01", "kind": "episode", "slug": "licensed-show-42-s01e01",
                "source_url": "https://cdn.partner.example/s01e01.mp4", "title": {"en": "Episode one"},
                "series": {"slug": "licensed-show-42", "title": {"en": "Licensed Show"}},
                "season_number": 1, "episode_number": 1, "downloads_allowed": False, "ads_allowed": True,
            },
        ],
    }


class SourceConnectorTests(unittest.TestCase):
    def test_all_21_product_languages_are_normalized_and_translatable(self) -> None:
        expected = (
            "ar", "en", "zh", "hi", "ko", "ja", "tr", "es", "fr", "pt", "de",
            "it", "ru", "id", "th", "fa", "ur", "bn", "ms", "pl", "vi",
        )
        self.assertEqual(LOCALES, expected)
        result = normalize_manifest_document(manifest(), "CONTRACT-42", "partner.example")
        self.assertEqual(tuple(result["items"][0]["title"]), expected)
        worker_path = Path(__file__).resolve().parents[1] / "media-server" / "ai-worker" / "ai_worker.py"
        tree = ast.parse(worker_path.read_text(encoding="utf-8"))
        language_node = next(
            node.value for node in tree.body
            if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "LANGUAGES" for target in node.targets)
        )
        languages = ast.literal_eval(language_node)
        self.assertEqual(tuple(languages), expected)
        self.assertEqual(len(languages), 21)
        worker_source = worker_path.read_text(encoding="utf-8")
        self.assertIn('TRANSLATION_MODEL = os.getenv("TRANSLATION_MODEL", "facebook/nllb-200-distilled-600M")', worker_source)
        self.assertIn("NLLB_CODES = {", worker_source)
        self.assertIn("tokenizer.src_lang = NLLB_CODES[source_language]", worker_source)
        self.assertIn("forced_bos_token_id=int(forced_bos)", worker_source)
        self.assertNotIn("google/madlad400-3b-mt", worker_source)

    def test_normalizes_authorized_movie_and_episode(self) -> None:
        result = normalize_manifest_document(manifest(), "CONTRACT-42", "partner.example")
        self.assertEqual(result["allowed_hosts"], ["cdn.partner.example", "partner.example"])
        self.assertEqual(result["items"][0]["title"]["en"], "الفيلم")
        self.assertTrue(result["items"][0]["downloads_allowed"])
        self.assertFalse(result["items"][1]["downloads_allowed"])
        self.assertEqual(result["items"][1]["series"]["title"]["ar"], "Licensed Show")

    def test_permission_reference_must_match(self) -> None:
        with self.assertRaisesRegex(SourceManifestError, "permission reference"):
            normalize_manifest_document(manifest(), "DIFFERENT-CONTRACT", "partner.example")

    def test_publisher_attestation_supplies_missing_documentary_authorization(self) -> None:
        value = manifest(); value.pop("authorization")
        result = normalize_manifest_document(value, "", "partner.example")
        self.assertEqual(result["rights"]["basis"], "publisher-attestation")
        self.assertEqual(result["rights"]["territories"], ["GLOBAL"])

    def test_all_copy_permissions_are_required(self) -> None:
        value = copy.deepcopy(manifest()); value["authorization"]["allow_transcode"] = False
        with self.assertRaisesRegex(SourceManifestError, "copy, transcode and publish"):
            normalize_manifest_document(value, "CONTRACT-42", "partner.example")

    def test_wildcard_and_credential_urls_are_blocked(self) -> None:
        value = copy.deepcopy(manifest()); value["allowed_media_hosts"] = ["*.partner.example"]
        with self.assertRaisesRegex(SourceManifestError, "exact domain"):
            normalize_manifest_document(value, "CONTRACT-42", "partner.example")
        value = manifest(); value["items"][0]["source_url"] = "https://user:pass@cdn.partner.example/film.mp4"
        with self.assertRaisesRegex(SourceManifestError, "credential-free"):
            normalize_manifest_document(value, "CONTRACT-42", "partner.example")

    def test_source_origin_requires_https_domain(self) -> None:
        self.assertEqual(canonical_source_origin("https://Partner.Example/path?q=1"), ("https://partner.example", "partner.example"))
        for value in ("http://partner.example", "https://127.0.0.1", "https://user@partner.example"):
            with self.subTest(value=value), self.assertRaises(SourceManifestError):
                canonical_source_origin(value)

    def test_invalid_numeric_metadata_is_rejected_cleanly(self) -> None:
        value = manifest(); value["items"][0]["duration_seconds"] = "not-a-number"
        with self.assertRaisesRegex(SourceManifestError, "duration_seconds must be an integer"):
            normalize_manifest_document(value, "CONTRACT-42", "partner.example")
        value = manifest(); value["items"][1]["season_number"] = 0
        with self.assertRaisesRegex(SourceManifestError, "season_number must be between"):
            normalize_manifest_document(value, "CONTRACT-42", "partner.example")


if __name__ == "__main__":
    unittest.main()
