#!/usr/bin/env python3
"""Render skutečné sestavné STL geometrie ORBIT 25, bez domýšlení tvaru.

Vstup: vizualni-geometrie/scene.json, parts[{file,name,color:[r,g,b]}].
Všechny STL musí být už v sestavné poloze, souřadnice jsou mm. Skript mění
jen náhledové PNG vedle sebe. Geometrii neupravuje. Přepínač --details přidá
pohled shora a rozloženou sestavu (pouze známé translace dílů podél Z).
Vyžaduje numpy a Pillow. Použitelný existující runtime:
/home/novakj/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
Barvy a osvětlení jsou ilustrativní, tvar je skutečná exportovaná síť.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import struct
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')


def unit(x):
    x = np.asarray(x, dtype=np.float64)
    return x / np.maximum(np.linalg.norm(x, axis=-1, keepdims=True), 1e-12)


def basis(eye):
    w = unit(eye)
    u = unit(np.cross([0, 0, 1], w))
    v = np.cross(w, u)
    return np.array([u, v, w])


def read_stl(path):
    data = path.read_bytes()
    count = struct.unpack('<I', data[80:84])[0] if len(data) >= 84 else 0
    if len(data) == 84 + count * 50:
        dt = np.dtype([('normal', '<f4', (3,)), ('vertex', '<f4', (3, 3)), ('attr', '<u2')])
        vertices = np.frombuffer(data, dtype=dt, offset=84)['vertex'].astype(np.float64)
    else:
        s = data.decode('ascii')
        vertices = np.array([[float(n) for n in x] for x in re.findall(
            r'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)', s)]).reshape(-1, 3, 3)
    assert np.isfinite(vertices).all() and len(vertices), str(path)
    return vertices


def corner_normals(vertices):
    """Vyhladí pouze normály sousedních plošek do 35°, nikdy pozice vertexů."""
    cross = np.cross(vertices[:, 1] - vertices[:, 0], vertices[:, 2] - vertices[:, 0])
    area = np.linalg.norm(cross, axis=1)
    normals = unit(cross)
    _, inv = np.unique(np.round(vertices.reshape(-1, 3), 5), axis=0, return_inverse=True)
    order = np.argsort(inv, kind='stable')
    borders = np.r_[0, np.flatnonzero(np.diff(inv[order])) + 1, len(order)]
    all_n = np.repeat(normals, 3, axis=0)
    all_a = np.repeat(area, 3)
    result = np.empty_like(all_n)
    for lo, hi in zip(borders[:-1], borders[1:]):
        idx = order[lo:hi]
        n = all_n[idx]
        same = n @ n.T > math.cos(math.radians(35))
        result[idx] = unit(same @ (n * all_a[idx, None]))
    return normals, result.reshape(-1, 3, 3)


def load_scene(path):
    scene = json.loads(path.read_text())
    parts = []
    for part in scene['parts']:
        file = path.parent / part['file']
        vertices = read_stl(file)
        color = np.asarray(part['color'], dtype=float)
        if color.max() > 1:
            color /= 255
        normals, smooth = corner_normals(vertices)
        parts.append(dict(file=file.stem, name=part.get('name', file.stem), v=vertices, n=normals,
                          smooth=smooth, color=color, sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
        print(f"{file.name}: {len(vertices):,} trojúhelníků", flush=True)
    assert parts, 'Prázdná scéna'
    return scene, parts


def raster_pixels(p):
    """Barycentrické souřadnice jen uvnitř jednoho promítnutého trojúhelníku."""
    x0, y0 = np.floor(p[:, :2].min(axis=0)).astype(int)
    x1, y1 = np.ceil(p[:, :2].max(axis=0)).astype(int)
    if x1 < 0 or y1 < 0 or x0 >= RASTER_W or y0 >= RASTER_H:
        return None
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, RASTER_W - 1), min(y1, RASTER_H - 1)
    den = (p[1, 1] - p[2, 1]) * (p[0, 0] - p[2, 0]) + (p[2, 0] - p[1, 0]) * (p[0, 1] - p[2, 1])
    if abs(den) < 1e-9:
        return None
    xx, yy = np.meshgrid(np.arange(x0, x1 + 1) + .5, np.arange(y0, y1 + 1) + .5)
    a = ((p[1, 1] - p[2, 1]) * (xx - p[2, 0]) + (p[2, 0] - p[1, 0]) * (yy - p[2, 1])) / den
    b = ((p[2, 1] - p[0, 1]) * (xx - p[2, 0]) + (p[0, 0] - p[2, 0]) * (yy - p[2, 1])) / den
    c = 1 - a - b
    inside = (a >= -1e-7) & (b >= -1e-7) & (c >= -1e-7)
    iy, ix = np.nonzero(inside)
    if len(ix) == 0:
        return None
    return iy + y0, ix + x0, np.array([a[inside], b[inside], c[inside]]).T


def render(parts, width=1850, height=1320, eye=(1.1, -5.5, 7.0), edge_lines=False):
    global RASTER_W, RASTER_H
    RASTER_W, RASTER_H = width, height
    points = np.concatenate([p['v'].reshape(-1, 3) for p in parts])
    center = (points.min(axis=0) + points.max(axis=0)) / 2
    base_z = points[:, 2].min()
    cam = basis(eye)
    all_screen = (points - center) @ cam.T
    span = np.ptp(all_screen[:, :2], axis=0)
    scale = min(width * .88 / span[0], height * .78 / span[1])
    shift = np.array([width / 2, height * .49, 0.])

    def project(v):
        q = (v - center) @ cam.T
        q[..., 0] *= scale
        q[..., 1] *= -scale
        return q + shift

    # Pravdivý projekční stín stejné sítě na rovinu pod modelem.
    shadow = Image.new('L', (width, height), 0)
    sd = ImageDraw.Draw(shadow)
    key = unit([-3.0, -4.0, 7.0])
    for p in parts:
        ground = p['v'].copy()
        zz = ground[:, :, 2] - base_z
        ground[:, :, 0] -= zz * key[0] / key[2]
        ground[:, :, 1] -= zz * key[1] / key[2]
        ground[:, :, 2] = base_z - .1
        g = project(ground)
        for tri in g:
            sd.polygon([tuple(x[:2]) for x in tri], fill=180)
    shadow = shadow.filter(ImageFilter.GaussianBlur(width / 90))
    bg = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shadow_rgba = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shadow_rgba.putalpha(shadow)
    bg.alpha_composite(shadow_rgba)

    zbuffer = np.full((height, width), -np.inf)
    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    view = unit(eye)
    fill = unit([4, 1, 5])
    rim = unit([-1, 6, 3.5])
    eye_position = center + view * 280
    key_position = center + np.array([-150, -170, 280])
    fill_position = center + np.array([190, 80, 190])
    rim_position = center + np.array([-50, 185, 155])

    for part in parts:
        projected = project(part['v'])
        front = np.flatnonzero(part['n'] @ view > -1e-7)
        color = part['color']
        gold = color[0] > color[2] * 1.3
        base = np.power(color, 2.2)
        for ti in front:
            tri = projected[ti]
            pix = raster_pixels(tri)
            if pix is None:
                continue
            yy, xx, bary = pix
            depth = bary @ tri[:, 2]
            visible = depth > zbuffer[yy, xx] + 1e-6
            if not visible.any():
                continue
            yy, xx, bary, depth = yy[visible], xx[visible], bary[visible], depth[visible]
            n = unit(bary @ part['smooth'][ti])
            world = bary @ part['v'][ti]
            local_view = unit(eye_position - world)
            local_key = unit(key_position - world)
            local_fill = unit(fill_position - world)
            local_rim = unit(rim_position - world)
            half_key = unit(local_key + local_view)
            half_fill = unit(local_fill + local_view)
            half_rim = unit(local_rim + local_view)
            kd = np.maximum(np.sum(n * local_key, axis=1), 0)
            fd = np.maximum(np.sum(n * local_fill, axis=1), 0)
            rd = np.maximum(np.sum(n * local_rim, axis=1), 0)
            ambient = .21 + .13 * (n[:, 2] + 1)
            diffuse = ambient + kd * .85 + fd * .38 + rd * .18
            spec = (np.maximum(np.sum(n * half_key, axis=1), 0) ** 45 * .60
                    + np.maximum(np.sum(n * half_fill, axis=1), 0) ** 20 * .25
                    + np.maximum(np.sum(n * half_rim, axis=1), 0) ** 35 * .40)
            # Rozptýlený odlesk zachovává čitelnost tmavého PLA a zlata.
            broad = np.maximum(np.sum(n * half_key, axis=1), 0) ** 7 * .06
            spec_tint = np.array([1., .88, .62]) if gold else np.array([.66, .75, .77])
            lit = base[None, :] * diffuse[:, None] + (spec + broad)[:, None] * spec_tint[None, :] * (.75 if gold else .24)
            lit += rd[:, None] ** 5 * np.array([.035, .045, .05])[None, :]
            # Gamma; stlačení pouze přesvětlených hodnot, žádné změny tvaru.
            rgb = np.clip(lit * .86, 0, 1) ** (1 / 2.2)
            rgba[yy, xx, :3] = (rgb * 255).astype(np.uint8)
            rgba[yy, xx, 3] = 255
            zbuffer[yy, xx] = depth
        print(f"Vykresleno: {part['name']}", flush=True)
    if edge_lines:
        # Technické obrysy skutečných výškových hran z hloubkové mapy.
        # Horní a zahloubené vodorovné plochy mají stejnou normálu;
        # kolmý pohled proto potřebuje obrysy pro čitelnost gravírování.
        finite = np.isfinite(zbuffer)
        z = np.where(finite, zbuffer, 0)
        edges = np.zeros((height, width), dtype=bool)
        edges[:, 1:] |= (np.abs(z[:, 1:] - z[:, :-1]) > .18) & finite[:, 1:] & finite[:, :-1]
        edges[1:, :] |= (np.abs(z[1:, :] - z[:-1, :]) > .18) & finite[1:, :] & finite[:-1, :]
        rgba[edges, :3] = (rgba[edges, :3].astype(float) * .32).astype(np.uint8)
    bg.alpha_composite(Image.fromarray(rgba, 'RGBA'))
    return bg, points.max(axis=0) - points.min(axis=0)


def font(size, bold=False, mono=False):
    suffix = 'SansMono' if mono else 'Sans'
    if bold:
        suffix += '-Bold'
    return ImageFont.truetype(str(FONT_DIR / ('DejaVu' + suffix + '.ttf')), size)


def spaced(draw, xy, text, fill, size=22, spacing=6):
    x, y = xy
    f = font(size)
    for c in text:
        draw.text((x, y), c, font=f, fill=fill)
        x += draw.textlength(c, font=f) + spacing


def compose(geometry, dimensions):
    width, height = 2400, 1650
    yy, xx = np.mgrid[:height, :width]
    glow = np.exp(-(((xx - 820) / 1100) ** 2 + ((yy - 850) / 900) ** 2))
    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    for c, value in enumerate((17, 22, 23)):
        rgb[:, :, c] = value + (glow * (15 if c == 0 else 17)).astype(np.uint8)
    canvas = Image.fromarray(rgb, 'RGB').convert('RGBA')
    d = ImageDraw.Draw(canvas)
    ivory, muted, gold = '#f0eee8', '#a5adab', '#d9b777'
    spaced(d, (110, 80), 'POMODORO / MECHANICKÝ RITUÁL', gold, size=21, spacing=4)
    d.text((104, 130), 'ORBIT 25', fill=ivory, font=font(116, True))
    d.text((112, 284), 'Malý objekt. Velké soustředění.', fill=muted, font=font(31))
    d.line((110, 362, 2290, 362), fill='#49514e', width=2)
    # Bez ořezu ani deformace modelu; pouze shodné zvětšení obou os.
    geometry.thumbnail((1740, 1190), Image.Resampling.LANCZOS)
    canvas.alpha_composite(geometry, (0, 320))
    d = ImageDraw.Draw(canvas)
    x = 1780
    entries = [
        ('01', 'Otočný věnec', ['Jemné vroubkování.', 'Vlastní rituál 25 / 5 / 15.']),
        ('02', 'Čtyři satelity', ['Oboustranné žetony', 'pro hotové bloky.']),
        ('03', 'Medailon 25 / 5', ['Otočením změníš režim', 'ze soustředění na pauzu.']),
    ]
    for i, (number, heading, lines) in enumerate(entries):
        y = 520 + i * 260
        d.text((x, y), number, fill=gold, font=font(24, mono=True))
        d.text((x, y + 53), heading, fill=ivory, font=font(36, True))
        for j, line in enumerate(lines):
            d.text((x, y + 116 + j * 43), line, fill=muted, font=font(25))
    d.line((110, 1450, 2290, 1450), fill='#49514e', width=2)
    d.text((110, 1485), 'ČERNÁ × ZLATÁ', fill=gold, font=font(25, True))
    dims = f'Ø {dimensions[0]:.0f} mm  ·  výška {dimensions[2] + 1e-4:.1f} mm'.replace('.', ',')
    d.text((110, 1530), dims, fill=muted, font=font(23))
    d.text((1030, 1488), 'Náhled skutečné CAD geometrie; barvy a světlo jsou ilustrativní.', fill=muted, font=font(22))
    d.text((1030, 1531), 'Ruční pomodoro rituál. Čas odměřuje externí časovač.', fill=muted, font=font(22))
    return canvas.convert('RGB')


def details(parts):
    """Doplňkové skutečné pohledy. Žádné řezání, domodelování ani změna měřítka dílů."""
    top, _ = render(parts, 1700, 1700, eye=(0, -.001, 1), edge_lines=True)
    canvas = Image.new('RGBA', (1800, 1970), '#202727')
    canvas.alpha_composite(top, (50, 170))
    d = ImageDraw.Draw(canvas)
    d.text((90, 60), 'ORBIT 25 / POHLED SHORA', fill='#f0eee8', font=font(48, True))
    d.text((90, 1880), 'Skutečná CAD geometrie s obrysy výškových hran. Ilustrativní barvy.', fill='#a5adab', font=font(26))
    canvas.convert('RGB').save(ROOT / 'nahled-shora-design.png', optimize=True)

    offsets = {'Base': 0, 'Rotor': 16, 'Crown': 35, 'Screw': 90,
               'Token1': 52, 'Token2': 52, 'Token3': 52, 'Token4': 52, 'ModeMedallion': 120}
    exploded = []
    for original in parts:
        part = original.copy()
        assert part['file'] in offsets, f"Chybí určení posunu dílu {part['file']}"
        part['v'] = part['v'] + np.array([0., 0., offsets[part['file']]])
        exploded.append(part)
    assembly, _ = render(exploded, 1600, 1830, eye=(1.1, -5.5, 3.4))
    canvas = Image.new('RGBA', (1800, 2100), '#202727')
    canvas.alpha_composite(assembly, (60, 140))
    d = ImageDraw.Draw(canvas)
    d.text((90, 60), 'ORBIT 25 / DEVĚT DÍLŮ', fill='#f0eee8', font=font(48, True))
    d.text((90, 1980), 'Rozložená CAD sestava. Díly posunuty pouze svisle pro přehled.', fill='#a5adab', font=font(26))
    d.text((90, 2026), 'Základna · věnec · koruna · šroub · čtyři žetony · medailon', fill='#d9b777', font=font(26))
    canvas.convert('RGB').save(ROOT / 'nahled-rozlozeno.png', optimize=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', type=Path, default=ROOT / 'vizualni-geometrie' / 'scene.json')
    parser.add_argument('--eye', type=float, nargs=3, default=(1.1, -5.5, 7.0))
    parser.add_argument('--width', type=int, default=2100)
    parser.add_argument('--height', type=int, default=1420)
    parser.add_argument('--details', action='store_true', help='Přidat pohled shora a rozloženou sestavu.')
    args = parser.parse_args()
    started = time.time()
    _, parts = load_scene(args.scene)
    geometry, dimensions = render(parts, args.width, args.height, args.eye)
    geometry.save(ROOT / 'nahled-geometrie.png', optimize=True)
    compose(geometry.copy(), dimensions).save(ROOT / 'nahled-orbit.png', optimize=True)
    if args.details:
        details(parts)
    print(json.dumps({'output': str(ROOT / 'nahled-orbit.png'), 'dimensions_mm': dimensions.tolist(),
                      'triangles': sum(len(p['v']) for p in parts), 'elapsed_seconds': round(time.time() - started, 1)}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
