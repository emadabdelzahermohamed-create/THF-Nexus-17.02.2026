#!/usr/bin/env python3
import hashlib
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGER = ROOT / "ReleaseOps" / "scripts" / "package_authoritative_android_source_v2.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CanonicalSourcePackagerV2Tests(unittest.TestCase):
    def make_project(self, base: Path) -> Path:
        project = base / "project"
        main = project / "app" / "src" / "main"
        java = main / "java" / "com" / "topherofit" / "thf" / "test"
        java.mkdir(parents=True)
        (main / "AndroidManifest.xml").write_text(
            '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application android:usesCleartextTraffic="false"/></manifest>\n',
            encoding="utf-8",
        )
        (java / "MainActivity.java").write_text(
            "package com.topherofit.thf.test; final class MainActivity {}\n",
            encoding="utf-8",
        )
        (project / "settings.gradle").write_text("pluginManagement {}\n", encoding="utf-8")
        (project / "app" / "build.gradle").write_text("android { namespace 'com.topherofit.thf.test' }\n", encoding="utf-8")
        return project

    def run_packager(self, project: Path, out: Path, expect_ok: bool = True):
        cp = subprocess.run(
            ["python3", str(PACKAGER), str(project), str(out)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if expect_ok:
            self.assertEqual(cp.returncode, 0, cp.stdout)
            self.assertIn("canonical_source_clean=PASS", cp.stdout)
        else:
            self.assertNotEqual(cp.returncode, 0, cp.stdout)
        return cp

    def test_is_byte_deterministic_for_same_source(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            project = self.make_project(base)
            one, two = base / "one.zip", base / "two.zip"
            self.run_packager(project, one)
            # Source mtimes must not influence the canonical bytes.
            os.utime(project / "settings.gradle", None)
            self.run_packager(project, two)
            self.assertEqual(sha256(one), sha256(two))
            self.assertEqual(one.read_bytes(), two.read_bytes())

    def test_excludes_build_local_and_signing_material(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            project = self.make_project(base)
            (project / "build").mkdir()
            (project / "build" / "leak.apk").write_bytes(b"apk")
            (project / "local.properties").write_text("sdk.dir=/secret\n", encoding="utf-8")
            (project / "release.jks").write_bytes(b"secret")
            out = base / "source.zip"
            self.run_packager(project, out)
            with zipfile.ZipFile(out) as zf:
                names = zf.namelist()
            self.assertNotIn("local.properties", names)
            self.assertNotIn("release.jks", names)
            self.assertFalse(any(n.startswith("build/") for n in names))
            self.assertFalse(any(n.endswith((".apk", ".aab")) for n in names))

    def test_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            project = self.make_project(base)
            target = project / "settings.gradle"
            (project / "linked.gradle").symlink_to(target)
            self.run_packager(project, base / "source.zip", expect_ok=False)

    def test_requires_manifest_and_native_activity(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            project = self.make_project(base)
            (project / "app" / "src" / "main" / "AndroidManifest.xml").unlink()
            self.run_packager(project, base / "no-manifest.zip", expect_ok=False)

        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            project = self.make_project(base)
            next(project.rglob("MainActivity.java")).unlink()
            self.run_packager(project, base / "no-activity.zip", expect_ok=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
