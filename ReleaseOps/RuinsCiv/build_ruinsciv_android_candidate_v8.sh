#!/usr/bin/env bash
set -Eeuo pipefail
BASE=/tmp/build_ruinsciv_android_candidate_v7.sh
[[ -f "$BASE" ]] || { echo 'missing v7 base'; exit 80; }
python3 - "$BASE" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text()
s=s.replace('version/code=42070','version/code=42071').replace('4.6.8-rc36','4.6.8-rc37')
s=s.replace('product_change=mobile_controls_plus_offline_objective_loop','product_change=mobile_controls_objective_loop_plus_populated_supply_sites')
needle='    root.add_child(action)\n\nfunc _button'
insert='''    root.add_child(action)\n    _add_world_population()\n\nfunc _add_world_population():\n    var world := get_tree().current_scene\n    if world == null:\n        return\n    var sites := [Vector3(7, 0, -9), Vector3(-10, 0, -14), Vector3(14, 0, -20)]\n    for i in range(sites.size()):\n        var marker := MeshInstance3D.new()\n        marker.name = "SupplySite_%d" % (i + 1)\n        var mesh := CylinderMesh.new()\n        mesh.top_radius = 0.8\n        mesh.bottom_radius = 1.25\n        mesh.height = 2.4\n        marker.mesh = mesh\n        marker.position = sites[i]\n        world.add_child(marker)\n        var beacon := OmniLight3D.new()\n        beacon.name = "SupplyBeacon_%d" % (i + 1)\n        beacon.omni_range = 7.0\n        beacon.light_energy = 3.0\n        beacon.position = sites[i] + Vector3(0, 2.2, 0)\n        world.add_child(beacon)\n    var camp := MeshInstance3D.new()\n    camp.name = "ExpeditionCamp"\n    var camp_mesh := BoxMesh.new()\n    camp_mesh.size = Vector3(5.0, 1.2, 3.5)\n    camp.mesh = camp_mesh\n    camp.position = Vector3(0, 0.6, -6)\n    world.add_child(camp)\n\nfunc _button'''
if needle not in s: raise SystemExit('RC37 world-population injection anchor missing')
s=s.replace(needle,insert,1)
p.write_text(s)
PY
chmod +x "$BASE"
exec bash "$BASE"
