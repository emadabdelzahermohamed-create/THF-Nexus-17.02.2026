#!/usr/bin/env python3
from __future__ import annotations
import hashlib, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

EXPECTED_INPUT_SHA = "8b0b892d1f32bdc7d5daa9867a442a349f6306969f29e9771dab2af3a9178784"
ROOT_NAME = "THF_NEXUS_6_FINAL"
DRAFT_MARKER = "THF POLICY DRAFT - NOT APPROVED FOR PRODUCTION"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, got {n}")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: builder.py INPUT.zip OUTPUT.zip")
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    if not src.is_file():
        raise SystemExit("input candidate missing")
    got = sha256(src)
    print(f"INPUT_SHA256={got}")
    if got != EXPECTED_INPUT_SHA:
        raise SystemExit("input SHA mismatch")
    if out.exists():
        raise SystemExit("refusing to overwrite existing output")

    with tempfile.TemporaryDirectory(prefix="thf-policy-resources-v1-") as td:
        t = Path(td)
        with zipfile.ZipFile(src) as z:
            z.extractall(t)
        root = t / ROOT_NAME
        if not root.is_dir():
            raise SystemExit("candidate root missing")
        if any("wave-mawja" in str(p).lower() or "wave_mawja" in str(p).lower() for p in root.rglob("*")):
            raise SystemExit("THF/WAVE isolation failure")

        web = root / "clients" / "web"
        apppy = root / "src" / "thf" / "app.py"
        py = apppy.read_text(encoding="utf-8")
        old = "web=(self.runtime.root/'clients'/'web').resolve();target=(web/'account-deletion.html') if path=='/account-deletion' else (web/'index.html' if path in {'','/'} else (web/path.lstrip('/')).resolve())"
        new = "web=(self.runtime.root/'clients'/'web').resolve();special={'/account-deletion':'account-deletion.html','/privacy':'privacy.html','/terms':'terms.html','/.well-known/security.txt':'security.txt'};target=(web/special[path]) if path in special else (web/'index.html' if path in {'','/'} else (web/path.lstrip('/')).resolve())"
        py = replace_once(py, old, new, "policy static routing")

        privacy = f'''<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>THF Nexus Privacy Policy — Draft</title></head><body><main><h1>Privacy Policy — Draft Technical Resource</h1><p>{DRAFT_MARKER}</p><p>This page exists only to validate independent HTTPS/static routing before reviewed policy text is approved. It MUST be replaced by owner/legal-approved privacy text before any production release or Play submission.</p><p>Technical data-flow evidence is maintained separately in ReleaseOps and is not a substitute for the final legal policy.</p></main></body></html>\n'''
        terms = f'''<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>THF Nexus Terms — Draft</title></head><body><main><h1>Terms — Draft Technical Resource</h1><p>{DRAFT_MARKER}</p><p>This page exists only to validate independent routing. Final Terms require owner/legal approval and MUST replace this draft before production release where Terms are required.</p></main></body></html>\n'''
        security = f'''# {DRAFT_MARKER}\n# Routing validation resource only. Do not publish as the final security.txt.\n# Final Contact, Expires, Canonical and policy fields require an approved operational security-contact decision.\n'''

        apppy.write_text(py, encoding="utf-8")
        (web / "privacy.html").write_text(privacy, encoding="utf-8")
        (web / "terms.html").write_text(terms, encoding="utf-8")
        (web / "security.txt").write_text(security, encoding="utf-8")

        subprocess.run([sys.executable, "-m", "py_compile", str(apppy)], check=True)
        for p in (web / "privacy.html", web / "terms.html", web / "security.txt"):
            if DRAFT_MARKER not in p.read_text(encoding="utf-8"):
                raise SystemExit(f"draft marker missing: {p.name}")

        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "x", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(root.rglob("*")):
                if p.is_file():
                    z.write(p, Path(ROOT_NAME) / p.relative_to(root))

    print(f"OUTPUT={out}")
    print(f"OUTPUT_SHA256={sha256(out)}")
    print("POLICY_ROUTING_CANDIDATE_BUILT=PASS")
    print("LEGAL_CONTENT_APPROVED=FALSE")
    print("THF_WAVE_ISOLATION=PASS")
    print("CANONICAL_SOURCE_MUTATED=FALSE")


if __name__ == "__main__":
    main()
