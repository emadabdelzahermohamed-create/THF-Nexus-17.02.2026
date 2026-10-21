#!/usr/bin/env bash
set -Eeuo pipefail
BASE=/tmp/build_ruinsciv_android_candidate_v6.sh
[[ -f "$BASE" ]] || { echo 'missing v6 base'; exit 80; }
python3 - "$BASE" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text()
s=s.replace('version/code=42069','version/code=42070').replace('4.6.8-rc35','4.6.8-rc36')
s=s.replace('product_change=explicit_mobile_movement_camera_controls','product_change=mobile_controls_plus_offline_objective_loop')
needle='    root.add_child(hint)\n\nfunc _button'
insert='''    root.add_child(hint)\n    var mission := PanelContainer.new()\n    mission.set_anchors_preset(Control.PRESET_TOP_WIDE)\n    mission.offset_left = 18\n    mission.offset_top = 18\n    mission.offset_right = -18\n    mission.offset_bottom = 118\n    mission.mouse_filter = Control.MOUSE_FILTER_IGNORE\n    var mission_text := Label.new()\n    mission_text.text = "OFFLINE EXPEDITION  •  Objective: Explore the ruins and secure 3 supply sites\\nProgress  0 / 3   •   Solo world   •   Local-host ready"\n    mission_text.add_theme_font_size_override("font_size", 18)\n    mission_text.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER\n    mission_text.vertical_alignment = VERTICAL_ALIGNMENT_CENTER\n    mission.add_child(mission_text)\n    root.add_child(mission)\n    var action := Button.new()\n    action.text = "INTERACT / SECURE"\n    action.custom_minimum_size = Vector2(220, 72)\n    action.add_theme_font_size_override("font_size", 18)\n    action.set_anchor_and_offset(SIDE_RIGHT, 1.0, -24)\n    action.set_anchor_and_offset(SIDE_LEFT, 1.0, -244)\n    action.set_anchor_and_offset(SIDE_BOTTOM, 1.0, -246)\n    action.set_anchor_and_offset(SIDE_TOP, 1.0, -318)\n    action.button_down.connect(_press.bind("interact"))\n    action.button_up.connect(_release.bind("interact"))\n    root.add_child(action)\n\nfunc _button'''
if needle not in s: raise SystemExit('RC36 injection anchor missing')
s=s.replace(needle,insert,1)
s=s.replace('        "camera_right": return ["camera_right", "look_right", "turn_right"]','        "camera_right": return ["camera_right", "look_right", "turn_right"]\n        "interact": return ["interact", "use", "action", "ui_accept"]')
p.write_text(s)
PY
chmod +x "$BASE"
exec bash "$BASE"
