#!/usr/bin/env bash
set -Eeuo pipefail
BASE=/tmp/build_ruinsciv_android_candidate_v7.sh
[[ -f "$BASE" ]] || { echo 'missing v7 base'; exit 80; }
python3 - "$BASE" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text()
s=s.replace('version/code=42070','version/code=42073').replace('4.6.8-rc36','4.6.8-rc39')
s=s.replace('product_change=mobile_controls_plus_offline_objective_loop','product_change=direct_mobile_motion_camera_plus_populated_ruins_biome')
needle='    root.add_child(action)'
insert='''    root.add_child(action)\n    _add_world_population()\n\nfunc _add_world_population():\n    var world := get_tree().current_scene\n    if world == null:\n        return\n    var sites := [Vector3(7, 0, -9), Vector3(-10, 0, -14), Vector3(14, 0, -20)]\n    for i in range(sites.size()):\n        var marker := MeshInstance3D.new()\n        marker.name = "SupplySite_%d" % (i + 1)\n        var mesh := CylinderMesh.new()\n        mesh.top_radius = 0.8\n        mesh.bottom_radius = 1.25\n        mesh.height = 2.4\n        marker.mesh = mesh\n        marker.position = sites[i]\n        world.add_child(marker)\n        var beacon := OmniLight3D.new()\n        beacon.name = "SupplyBeacon_%d" % (i + 1)\n        beacon.omni_range = 7.0\n        beacon.light_energy = 3.0\n        beacon.position = sites[i] + Vector3(0, 2.2, 0)\n        world.add_child(beacon)\n    var camp := MeshInstance3D.new()\n    camp.name = "ExpeditionCamp"\n    var camp_mesh := BoxMesh.new()\n    camp_mesh.size = Vector3(5.0, 1.2, 3.5)\n    camp.mesh = camp_mesh\n    camp.position = Vector3(0, 0.6, -6)\n    world.add_child(camp)\n    var ruins := [Vector3(-6,1,-8),Vector3(5,1,-13),Vector3(-15,1,-18),Vector3(11,1,-27),Vector3(-4,1,-31),Vector3(19,1,-12),Vector3(-20,1,-7),Vector3(3,1,-23)]\n    for i in range(ruins.size()):\n        var wall := MeshInstance3D.new()\n        wall.name = "AncientRuin_%02d" % (i + 1)\n        var wall_mesh := BoxMesh.new()\n        wall_mesh.size = Vector3(3.5 + float(i % 3), 2.0 + float(i % 2), 0.65)\n        wall.mesh = wall_mesh\n        wall.position = ruins[i]\n        wall.rotation.y = float(i) * 0.61\n        world.add_child(wall)\n    var trees := [Vector3(-8,1.5,-5),Vector3(9,1.5,-6),Vector3(-13,1.5,-11),Vector3(16,1.5,-16),Vector3(-18,1.5,-24),Vector3(7,1.5,-29),Vector3(20,1.5,-25),Vector3(-2,1.5,-19),Vector3(12,1.5,-35),Vector3(-12,1.5,-34)]\n    for i in range(trees.size()):\n        var tree := MeshInstance3D.new()\n        tree.name = "DeadTree_%02d" % (i + 1)\n        var tree_mesh := CylinderMesh.new()\n        tree_mesh.top_radius = 0.12\n        tree_mesh.bottom_radius = 0.42\n        tree_mesh.height = 3.0 + float(i % 3) * 0.55\n        tree.mesh = tree_mesh\n        tree.position = trees[i]\n        tree.rotation.z = (-0.10 if i % 2 == 0 else 0.12)\n        world.add_child(tree)\n    var landmark := MeshInstance3D.new()\n    landmark.name = "RuinsObeliskLandmark"\n    var landmark_mesh := BoxMesh.new()\n    landmark_mesh.size = Vector3(1.4, 7.5, 1.4)\n    landmark.mesh = landmark_mesh\n    landmark.position = Vector3(0, 3.75, -38)\n    landmark.rotation.y = 0.35\n    world.add_child(landmark)\n    var landmark_light := OmniLight3D.new()\n    landmark_light.name = "ObeliskBeacon"\n    landmark_light.omni_range = 12.0\n    landmark_light.light_energy = 4.0\n    landmark_light.position = Vector3(0, 7.8, -38)\n    world.add_child(landmark_light)'''
if needle not in s: raise SystemExit('RC38 stable action anchor missing')
s=s.replace(needle,insert,1)
p.write_text(s)
PY
chmod +x "$BASE"
exec bash "$BASE"
