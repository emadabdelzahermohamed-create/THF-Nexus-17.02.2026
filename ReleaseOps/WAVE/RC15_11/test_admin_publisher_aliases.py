#!/usr/bin/env python3
"""Fail-closed contract for WAVE's public Admin/Publisher entry routes."""

from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parent / "overlay"


class AdminPublisherAliasTests(unittest.TestCase):
    def test_aliases_are_server_only_redirects_to_the_guarded_control_surface(self):
        for route in ("admin", "publisher"):
            with self.subTest(route=route):
                source = (ROOT / "app" / route / "page.tsx").read_text(encoding="utf-8")
                self.assertIn('from "next/navigation"', source)
                self.assertEqual(source.count('redirect("/control")'), 1)
                self.assertNotIn('"use client"', source)

    def test_aliases_do_not_duplicate_or_bypass_authentication(self):
        forbidden = (
            "ADMIN_SESSION_COOKIE",
            "hasWaveRole",
            "waveUserFromToken",
            "cookies(",
            "role =",
            "role:",
        )
        for route in ("admin", "publisher"):
            with self.subTest(route=route):
                source = (ROOT / "app" / route / "page.tsx").read_text(encoding="utf-8")
                for token in forbidden:
                    self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
