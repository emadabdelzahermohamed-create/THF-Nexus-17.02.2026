#!/usr/bin/env python3
"""Deterministic tests for the bounded WAVE alias propagation smoke."""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import textwrap
import unittest


ROOT = pathlib.Path(__file__).resolve().parent
SMOKE = ROOT / "smoke_control_aliases.sh"


MOCK_CURL = r"""#!/usr/bin/env bash
set -Eeuo pipefail

output=/dev/null
write_format=
follow=0
url=
while (($#)); do
  case "$1" in
    --connect-timeout|--max-time) shift 2 ;;
    -o) output="$2"; shift 2 ;;
    -w) write_format="$2"; shift 2 ;;
    -L) follow=1; shift ;;
    -sS) shift ;;
    *) url="$1"; shift ;;
  esac
done

path="${url#${WAVE_LIVE_URL}}"
old=0
if [[ "$path" == "/publisher" ]]; then
  count=0
  [[ -f "$MOCK_STATE" ]] && count="$(cat "$MOCK_STATE")"
  count=$((count + 1))
  printf '%s\n' "$count" > "$MOCK_STATE"
  if [[ "${MOCK_ALWAYS_FAIL:-0}" == "1" ]] || (( count <= 3 )); then
    old=1
  fi
fi

if (( follow == 1 )); then
  if (( old == 1 )); then
    printf 'not found\n' > "$output"
    printf '404 %s%s' "$WAVE_LIVE_URL" "$path"
  else
    printf 'دخول لوحة التحكم\n' > "$output"
    printf '200 %s/admin-login?return_to=%%2Fcontrol' "$WAVE_LIVE_URL"
  fi
elif [[ "$write_format" == '%{redirect_url}' ]]; then
  (( old == 1 )) || printf '%s/control' "$WAVE_LIVE_URL"
else
  if (( old == 1 )); then printf '404'; else printf '307'; fi
fi
"""


class AliasPropagationSmokeTests(unittest.TestCase):
    def run_smoke(self, *, always_fail: bool = False) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = pathlib.Path(temp)
            mock = temp_path / "curl"
            mock.write_text(textwrap.dedent(MOCK_CURL), encoding="utf-8")
            mock.chmod(0o755)
            env = os.environ.copy()
            env.update(
                {
                    "CURL_BIN": str(mock),
                    "MOCK_STATE": str(temp_path / "state"),
                    "RUNNER_TEMP": temp,
                    "WAVE_ALIAS_ATTEMPTS": "2",
                    "WAVE_ALIAS_RETRY_SECONDS": "0",
                    "WAVE_LIVE_URL": "https://wave.example.invalid",
                    "MOCK_ALWAYS_FAIL": "1" if always_fail else "0",
                }
            )
            return subprocess.run(
                ["bash", str(SMOKE)],
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_transient_publisher_staleness_retries_then_passes(self) -> None:
        result = self.run_smoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WAVE_CONTROL_ALIAS=PASS path=/admin attempt=1", result.stdout)
        self.assertIn("WAVE_CONTROL_ALIAS=PASS path=/publisher attempt=2", result.stdout)
        self.assertIn("WAVE_CONTROL_ALIAS_RETRY path=/publisher attempt=1/2", result.stderr)

    def test_persistent_staleness_fails_closed_after_bound(self) -> None:
        result = self.run_smoke(always_fail=True)
        self.assertEqual(result.returncode, 33)
        self.assertIn("WAVE_CONTROL_ALIAS=FAIL path=/publisher attempts=2", result.stderr)


if __name__ == "__main__":
    unittest.main()
