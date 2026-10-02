#!/usr/bin/env python3
"""Deterministic CPU preview for the canonical THF Stage16A GLB.

This intentionally uses only Python, NumPy and Pillow.  It evaluates the real
skinned GLB, blends the upright ``idle`` pose into the canonical
``UAL1_Crouch_Idle_Loop`` pose, and produces review frames even when WebGL is
unavailable.  It is evidence tooling, not an in-product visual fallback.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


COMPONENTS = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
WIDTHS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def quat_normalize(q: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(q))
    return q / norm if norm > 1e-9 else np.array([0.0, 0.0, 0.0, 1.0])


def quat_slerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    a, b = quat_normalize(a), quat_normalize(b)
    dot = float(np.dot(a, b))
    if dot < 0:
        b, dot = -b, -dot
    if dot > 0.9995:
        return quat_normalize(a + (b - a) * t)
    theta = math.acos(max(-1.0, min(1.0, dot)))
    sine = math.sin(theta)
    return a * (math.sin((1 - t) * theta) / sine) + b * (math.sin(t * theta) / sine)


def quat_matrix(q: np.ndarray) -> np.ndarray:
    x, y, z, w = quat_normalize(q)
    return np.array([
        [1 - 2 * (y*y + z*z), 2 * (x*y - z*w), 2 * (x*z + y*w), 0],
        [2 * (x*y + z*w), 1 - 2 * (x*x + z*z), 2 * (y*z - x*w), 0],
        [2 * (x*z - y*w), 2 * (y*z + x*w), 1 - 2 * (x*x + y*y), 0],
        [0, 0, 0, 1],
    ], dtype=np.float64)


def trs_matrix(t: np.ndarray, r: np.ndarray, s: np.ndarray) -> np.ndarray:
    out = quat_matrix(r)
    out[:3, :3] *= s[np.newaxis, :]
    out[:3, 3] = t
    return out


class Glb:
    def __init__(self, path: Path):
        raw = path.read_bytes()
        if raw[:4] != b'glTF':
            raise ValueError('not a GLB file')
        offset, doc, binary = 12, None, None
        while offset < len(raw):
            length, kind = struct.unpack_from('<II', raw, offset)
            chunk = raw[offset + 8:offset + 8 + length]
            offset += 8 + length
            if kind == 0x4E4F534A:
                doc = json.loads(chunk.rstrip(b'\x00 \t\r\n'))
            elif kind == 0x004E4942:
                binary = chunk
        if doc is None or binary is None:
            raise ValueError('GLB JSON or BIN chunk missing')
        self.path, self.doc, self.binary = path, doc, binary

    def accessor(self, index: int) -> np.ndarray:
        acc = self.doc['accessors'][index]
        view = self.doc['bufferViews'][acc['bufferView']]
        dtype = np.dtype(COMPONENTS[acc['componentType']]).newbyteorder('<')
        width = WIDTHS[acc['type']]
        offset = int(view.get('byteOffset', 0)) + int(acc.get('byteOffset', 0))
        stride = int(view.get('byteStride', dtype.itemsize * width))
        shape = (int(acc['count']), width)
        arr = np.ndarray(shape=shape, dtype=dtype, buffer=self.binary, offset=offset,
                         strides=(stride, dtype.itemsize)).copy()
        return arr[:, 0] if width == 1 else arr

    def image(self, index: int) -> Image.Image:
        spec = self.doc['images'][index]
        view = self.doc['bufferViews'][spec['bufferView']]
        start = int(view.get('byteOffset', 0))
        return Image.open(io.BytesIO(self.binary[start:start + int(view['byteLength'])])).convert('RGB')


def rest_pose(doc: dict) -> list[dict[str, np.ndarray]]:
    pose = []
    for node in doc['nodes']:
        pose.append({
            't': np.asarray(node.get('translation', [0, 0, 0]), dtype=np.float64),
            'r': np.asarray(node.get('rotation', [0, 0, 0, 1]), dtype=np.float64),
            's': np.asarray(node.get('scale', [1, 1, 1]), dtype=np.float64),
        })
    return pose


def evaluate_animation(glb: Glb, name: str, normalized_time: float = 0.35) -> list[dict[str, np.ndarray]]:
    animation = next(a for a in glb.doc['animations'] if a.get('name') == name)
    pose = rest_pose(glb.doc)
    durations = [float(np.max(glb.accessor(s['input']))) for s in animation['samplers']]
    clip_time = max(durations, default=0.0) * normalized_time
    for channel in animation['channels']:
        target = channel['target']
        path = target['path']
        if path not in {'translation', 'rotation', 'scale'}:
            continue
        sampler = animation['samplers'][channel['sampler']]
        times = np.asarray(glb.accessor(sampler['input']), dtype=np.float64)
        values = np.asarray(glb.accessor(sampler['output']), dtype=np.float64)
        if sampler.get('interpolation') == 'CUBICSPLINE':
            values = values.reshape(len(times), 3, -1)[:, 1, :]
        if clip_time <= times[0]:
            value = values[0]
        elif clip_time >= times[-1]:
            value = values[-1]
        else:
            hi = int(np.searchsorted(times, clip_time, side='right'))
            lo = hi - 1
            u = float((clip_time - times[lo]) / max(times[hi] - times[lo], 1e-9))
            if sampler.get('interpolation') == 'STEP':
                u = 0.0
            value = quat_slerp(values[lo], values[hi], u) if path == 'rotation' else values[lo] * (1-u) + values[hi] * u
        pose[target['node']][{'translation': 't', 'rotation': 'r', 'scale': 's'}[path]] = value.copy()
    return pose


def blend_pose(a: list[dict[str, np.ndarray]], b: list[dict[str, np.ndarray]], weight: float) -> list[dict[str, np.ndarray]]:
    out = []
    for left, right in zip(a, b):
        out.append({
            't': left['t'] * (1-weight) + right['t'] * weight,
            'r': quat_slerp(left['r'], right['r'], weight),
            's': left['s'] * (1-weight) + right['s'] * weight,
        })
    return out


def global_matrices(doc: dict, pose: list[dict[str, np.ndarray]]) -> list[np.ndarray]:
    parents = {child: parent for parent, node in enumerate(doc['nodes']) for child in node.get('children', [])}
    local = [trs_matrix(p['t'], p['r'], p['s']) for p in pose]
    result: list[np.ndarray | None] = [None] * len(local)

    def resolve(index: int) -> np.ndarray:
        if result[index] is not None:
            return result[index]  # type: ignore[return-value]
        result[index] = resolve(parents[index]) @ local[index] if index in parents else local[index]
        return result[index]  # type: ignore[return-value]

    return [resolve(i) for i in range(len(local))]


def skinned_meshes(glb: Glb, pose: list[dict[str, np.ndarray]]) -> list[dict]:
    doc = glb.doc
    globals_ = global_matrices(doc, pose)
    skin = doc['skins'][0]
    joints = skin['joints']
    inv_bind = glb.accessor(skin['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)
    joint_mats = np.stack([globals_[joint] @ inv_bind[i] for i, joint in enumerate(joints)])
    out = []
    for node_index, node in enumerate(doc['nodes']):
        if 'mesh' not in node:
            continue
        mesh = doc['meshes'][node['mesh']]
        for primitive in mesh['primitives']:
            attrs = primitive['attributes']
            pos = np.asarray(glb.accessor(attrs['POSITION']), dtype=np.float64)
            joints0 = np.asarray(glb.accessor(attrs['JOINTS_0']), dtype=np.int64)
            weights = np.asarray(glb.accessor(attrs['WEIGHTS_0']), dtype=np.float64)
            uv = np.asarray(glb.accessor(attrs['TEXCOORD_0']), dtype=np.float64)
            homogeneous = np.concatenate([pos, np.ones((len(pos), 1))], axis=1)
            skinned = np.zeros((len(pos), 4), dtype=np.float64)
            for slot in range(4):
                transformed = np.einsum('nij,nj->ni', joint_mats[joints0[:, slot]], homogeneous)
                skinned += transformed * weights[:, slot:slot+1]
            mesh_world = globals_[node_index]
            skinned = (mesh_world @ skinned.T).T[:, :3]
            indices = np.asarray(glb.accessor(primitive['indices']), dtype=np.int64).reshape(-1, 3)
            material = doc['materials'][primitive.get('material', 0)]
            texture_index = material.get('pbrMetallicRoughness', {}).get('baseColorTexture', {}).get('index')
            texture = None
            if texture_index is not None:
                image_index = doc['textures'][texture_index]['source']
                texture = glb.image(image_index)
            out.append({'positions': skinned, 'uv': uv, 'indices': indices, 'texture': texture})
    return out


def render(glb: Glb, pose: list[dict[str, np.ndarray]], out_path: Path, label: str, width: int = 540, height: int = 720) -> dict:
    meshes = skinned_meshes(glb, pose)
    all_pos = np.concatenate([m['positions'] for m in meshes], axis=0)
    minimum, maximum = all_pos.min(axis=0), all_pos.max(axis=0)
    center = (minimum + maximum) / 2
    stature = float(maximum[1] - minimum[1])
    scale = 2.38 / max(stature, 1e-6)
    for mesh in meshes:
        mesh['positions'] = (mesh['positions'] - np.array([center[0], minimum[1], center[2]])) * scale

    image = Image.new('RGB', (width, height), '#061722')
    draw = ImageDraw.Draw(image, 'RGBA')
    draw.rounded_rectangle((12, 12, width-12, height-12), radius=28, fill='#082330', outline='#1e726c', width=2)
    floor_y = int(height * 0.88)
    draw.ellipse((width*.18, floor_y-28, width*.82, floor_y+25), fill=(0, 0, 0, 80), outline=(69, 221, 174, 80), width=2)

    camera = np.array([0.0, 1.20, 4.35])
    target_y = 1.18
    f = (height * 0.5) / math.tan(math.radians(34) / 2)
    triangles = []
    light = np.array([0.38, 0.78, 0.50]); light /= np.linalg.norm(light)
    for mesh in meshes:
        p, uv, texture = mesh['positions'], mesh['uv'], mesh['texture']
        rel = p - camera
        z = -rel[:, 2]
        sx = width/2 + f * rel[:, 0] / np.maximum(z, .05)
        sy = height*.54 - f * (p[:, 1] - target_y) / np.maximum(z, .05)
        for tri in mesh['indices']:
            if np.any(z[tri] <= .05):
                continue
            points3 = p[tri]
            normal = np.cross(points3[1]-points3[0], points3[2]-points3[0])
            normal_norm = np.linalg.norm(normal)
            if normal_norm < 1e-8:
                continue
            normal /= normal_norm
            shade = 0.36 + 0.72 * max(0.0, float(np.dot(normal, light))) + 0.18 * max(0.0, float(-normal[2]))
            color = np.array([150, 168, 180], dtype=np.float64)
            if texture is not None:
                tuv = np.mean(uv[tri], axis=0)
                tx = int((tuv[0] % 1.0) * (texture.width-1))
                ty = int(((1.0-tuv[1]) % 1.0) * (texture.height-1))
                color = np.asarray(texture.getpixel((tx, ty)), dtype=np.float64)
            color = tuple(int(max(0, min(255, c*shade))) for c in color)
            points2 = [(float(sx[i]), float(sy[i])) for i in tri]
            triangles.append((float(np.mean(z[tri])), points2, color))
    for _, points, color in sorted(triangles, key=lambda item: item[0], reverse=True):
        draw.polygon(points, fill=(*color, 255))

    draw.rounded_rectangle((28, 28, width-28, 80), radius=18, fill=(5, 22, 32, 225), outline=(69, 221, 174, 135), width=2)
    draw.text((48, 45), label, font=ImageFont.load_default(size=15), fill=(223, 255, 247, 255))
    draw.rounded_rectangle((28, height-94, width-28, height-34), radius=18, fill=(5, 22, 32, 225), outline=(69, 221, 174, 110), width=2)
    draw.text((48, height-73), 'Stage16A • idle ↔ UAL1_Crouch_Idle_Loop • CPU evidence', font=ImageFont.load_default(size=13), fill=(160, 235, 216, 255))
    image.save(out_path)
    return {'vertices': int(sum(len(m['positions']) for m in meshes)), 'triangles': int(len(triangles)), 'stature': stature}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('glb', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    glb = Glb(args.glb)
    names = [a.get('name') for a in glb.doc['animations']]
    for required in ('idle', 'UAL1_Crouch_Idle_Loop'):
        if required not in names:
            raise SystemExit(f'missing required animation: {required}')
    upright = evaluate_animation(glb, 'idle')
    crouch = evaluate_animation(glb, 'UAL1_Crouch_Idle_Loop')
    manifest = {'source': str(args.glb), 'source_bytes': args.glb.stat().st_size, 'joint_count': len(glb.doc['skins'][0]['joints']), 'clip_count': len(names), 'frames': []}
    for phase in (0, 25, 50, 75):
        weight = 0.5 - 0.5 * math.cos((phase / 100) * math.tau)
        target = args.output / f'squat_phase_{phase:02d}.png'
        metrics = render(glb, blend_pose(upright, crouch, weight), target, f'BODYWEIGHT SQUAT • {phase}% • blend {weight:.2f}')
        manifest['frames'].append({'phase': phase, 'blend_weight': round(weight, 6), 'path': target.name, **metrics})
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
