#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    root = Path(args.root)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    terra = root / 'terra/native/world/WorldMain.gd'
    rift = root / 'rift/THF_Nexus_Arena_Core/native/arena/RiftAudioFeedback.gd'
    if not terra.is_file() or not rift.is_file():
        raise SystemExit('EXPECTED_SOURCE_FILES_MISSING')

    before = {'terra': sha256(terra), 'rift': sha256(rift)}
    (out / 'SHA_BEFORE.txt').write_text(
        f"{before['terra']}  {terra}\n{before['rift']}  {rift}\n",
        encoding='utf-8',
    )
    (out / 'WorldMain.before.gd').write_bytes(terra.read_bytes())
    (out / 'RiftAudioFeedback.before.gd').write_bytes(rift.read_bytes())

    t = terra.read_text(encoding='utf-8')
    replacements = [
        ('    var role_label := {', '    var role_label: String = str({'),
        ('    }.get(role, "Citizen / مواطن")\n    var intent_label := {',
         '    }.get(role, "Citizen / مواطن"))\n    var intent_label: String = str({'),
        ('    }.get(intent, "World cue / تنبيه")\n    return str(role_label)',
         '    }.get(intent, "World cue / تنبيه"))\n    return str(role_label)'),
    ]
    for old, new in replacements:
        if t.count(old) != 1:
            raise SystemExit(f'TERRA_EXPECTED_PATTERN_COUNT_{t.count(old)}: {old!r}')
        t = t.replace(old, new, 1)
    terra.write_text(t, encoding='utf-8')

    r = rift.read_text(encoding='utf-8')
    r_replacements = [
        ('        var extra := players.pop_back()',
         '        var extra: AudioStreamPlayer = players.pop_back() as AudioStreamPlayer'),
        ('    var spec := {', '    var spec: Array = {'),
        ('    }.get(kind, [280.0, 0.045, 0.25])\n    var hz := float(spec[0])',
         '    }.get(kind, [280.0, 0.045, 0.25]) as Array\n    var hz := float(spec[0])'),
    ]
    for old, new in r_replacements:
        if r.count(old) != 1:
            raise SystemExit(f'RIFT_EXPECTED_PATTERN_COUNT_{r.count(old)}: {old!r}')
        r = r.replace(old, new, 1)
    rift.write_text(r, encoding='utf-8')

    (out / 'WorldMain.after.gd').write_bytes(terra.read_bytes())
    (out / 'RiftAudioFeedback.after.gd').write_bytes(rift.read_bytes())
    after = {'terra': sha256(terra), 'rift': sha256(rift)}
    (out / 'SHA_AFTER.txt').write_text(
        f"{after['terra']}  {terra}\n{after['rift']}  {rift}\n",
        encoding='utf-8',
    )
    (out / 'PATCH_SUMMARY.txt').write_text(
        'scope=diagnostic_disposable_workspace_only\n'
        'terra=2 Variant-return Dictionary.get expressions explicitly converted to String\n'
        'rift=AudioStreamPlayer pop_back explicitly cast; audio spec Dictionary.get explicitly cast to Array\n'
        'gameplay_logic_changed=false\n'
        'canonical_archives_mutated=false\n',
        encoding='utf-8',
    )
    print('DIAGNOSTIC_TYPE_ONLY_PATCH_APPLIED=PASS')
    print(f"TERRA_BEFORE={before['terra']}")
    print(f"TERRA_AFTER={after['terra']}")
    print(f"RIFT_BEFORE={before['rift']}")
    print(f"RIFT_AFTER={after['rift']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
