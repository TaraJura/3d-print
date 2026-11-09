#!/usr/bin/env python3
"""Skutečný náhled Montessori Zahrady objevů z finálních sestavných STL.

Vstup vizualni-geometrie/scene.json: parts[{file,name,color:[r,g,b]}].
Pozice vertexů jsou zachované. Druhý pohled používá výhradně translace
existujících pěti kamenů ze sedel do výškové řady před základnou.
Materiály a světlo jsou ilustrativní; nejde o fotografii fyzického výtisku.
Výstup: nahled-zahrada.png, nahled-hry.png a nahled-shora.png.
Spuštění přes existující runtime s numpy a Pillow, bez instalace:
/home/novakj/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 vizualizace.py
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


def render(parts, width=1900, height=1230, eye=(1.0, -5.5, 7.0), edge_lines=False):
    """Ortografická projekce přesných trojúhelníků se světelnou hloubkovou mapou."""
    global RASTER_W, RASTER_H
    points = np.concatenate([p['v'].reshape(-1, 3) for p in parts])
    center = (points.min(axis=0) + points.max(axis=0)) / 2
    base_z = points[:, 2].min()
    cam = basis(eye)
    all_screen = (points - center) @ cam.T
    span = np.ptp(all_screen[:, :2], axis=0)
    scale = min(width * .88 / span[0], height * .82 / span[1])
    shift = np.array([width / 2, height * .48, 0.])

    def project(v):
        q = (v - center) @ cam.T
        q[..., 0] *= scale
        q[..., 1] *= -scale
        return q + shift

    key = unit([-3.0, -4.0, 7.0])
    light_basis = basis(key)
    lp = (points - center) @ light_basis.T
    light_span = np.ptp(lp[:, :2], axis=0)
    light_scale = 1400 / max(light_span)
    light_center = (lp[:, :2].min(axis=0) + lp[:, :2].max(axis=0)) / 2
    shadow_w = 1536
    def light_project(v):
        q = (v - center) @ light_basis.T
        q[..., :2] = (q[..., :2] - light_center) * light_scale + shadow_w / 2
        return q
    RASTER_W = RASTER_H = shadow_w
    light_buffer = np.full((shadow_w, shadow_w), -np.inf)
    for part in parts:
        lit_tris = light_project(part['v'])
        for ti in np.flatnonzero(part['n'] @ key > -1e-7):
            tri = lit_tris[ti]
            pix = raster_pixels(tri)
            if pix is None:
                continue
            yy, xx, bary = pix
            z = bary @ tri[:, 2]
            light_buffer[yy, xx] = np.maximum(light_buffer[yy, xx], z)

    RASTER_W, RASTER_H = width, height
    # Projekce stejné geometrie na společnou rovinu podložky.
    shadow = Image.new('L', (width, height), 0)
    sd = ImageDraw.Draw(shadow)
    for part in parts:
        ground = part['v'].copy()
        zz = ground[:, :, 2] - base_z
        ground[:, :, 0] -= zz * key[0] / key[2]
        ground[:, :, 1] -= zz * key[1] / key[2]
        ground[:, :, 2] = base_z - .1
        g = project(ground)
        for tri in g:
            sd.polygon([tuple(x[:2]) for x in tri], fill=55)
    shadow = shadow.filter(ImageFilter.GaussianBlur(width / 130))
    bg = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shadow_rgba = Image.new('RGBA', (width, height), (58, 44, 33, 0))
    shadow_rgba.putalpha(shadow)
    bg.alpha_composite(shadow_rgba)

    zbuffer = np.full((height, width), -np.inf)
    rgba = np.zeros((height, width, 4), dtype=np.uint8)
    view = unit(eye)
    eye_position = center + view * 400
    fill_position = center + np.array([190, 80, 290])
    rim_position = center + np.array([-50, 185, 255])
    for part in parts:
        projected = project(part['v'])
        front = np.flatnonzero(part['n'] @ view > -1e-7)
        base = np.power(part['color'], 2.2)
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
            local_fill = unit(fill_position - world)
            local_rim = unit(rim_position - world)
            half_key = unit(key + local_view)
            kd = np.maximum(n @ key, 0)
            fd = np.maximum(np.sum(n * local_fill, axis=1), 0)
            rd = np.maximum(np.sum(n * local_rim, axis=1), 0)
            lq = light_project(world)
            lx, ly = np.rint(lq[:, 0]).astype(int), np.rint(lq[:, 1]).astype(int)
            visibility = np.zeros(len(lx))
            for dx, dy in [(0, 0), (-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2)]:
                sz = light_buffer[np.clip(ly + dy, 0, shadow_w - 1), np.clip(lx + dx, 0, shadow_w - 1)]
                visibility += (sz <= lq[:, 2] + .40)
            visibility /= 7
            ambient = .34 + .12 * (n[:, 2] + 1)
            diffuse = ambient + kd * .64 * visibility + fd * .21 + rd * .13
            # Široký velmi mírný odlesk matného PLA; barva není kov.
            spec = np.maximum(np.sum(n * half_key, axis=1), 0) ** 20 * .028 * visibility
            lit = base[None, :] * diffuse[:, None] + spec[:, None] * np.array([1., .95, .85])
            rgb = np.clip(lit * .91, 0, 1) ** (1 / 2.2)
            rgba[yy, xx, :3] = (rgb * 255).astype(np.uint8)
            rgba[yy, xx, 3] = 255
            zbuffer[yy, xx] = depth
        print(f"Vykresleno: {part['name']}", flush=True)
    if edge_lines:
        finite = np.isfinite(zbuffer)
        z = np.where(finite, zbuffer, 0)
        edges = np.zeros((height, width), dtype=bool)
        edges[:, 1:] |= (np.abs(z[:, 1:] - z[:, :-1]) > .20) & finite[:, 1:] & finite[:, :-1]
        edges[1:, :] |= (np.abs(z[1:, :] - z[:-1, :]) > .20) & finite[1:, :] & finite[:-1, :]
        rgba[edges, :3] = (rgba[edges, :3].astype(float) * .65).astype(np.uint8)
    bg.alpha_composite(Image.fromarray(rgba, 'RGBA'))
    return bg, points.max(axis=0) - points.min(axis=0)


def font(size, serif=False, bold=False):
    if serif:
        name = '/usr/share/fonts/truetype/gentium-basic/GenBasR.ttf'
    else:
        name = '/usr/share/fonts/truetype/dejavu/DejaVuSans' + ('-Bold' if bold else '') + '.ttf'
    return ImageFont.truetype(name, size)


def spaced(draw, xy, text, fill, size=22, spacing=5):
    x, y = xy
    f = font(size)
    for c in text:
        draw.text((x, y), c, font=f, fill=fill)
        x += draw.textlength(c, font=f) + spacing


def background(width=2400, height=1750):
    yy, xx = np.mgrid[:height, :width]
    glow = np.exp(-(((xx - 1050) / 1300) ** 2 + ((yy - 920) / 1000) ** 2))
    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    for c, value in enumerate((232, 225, 213)):
        rgb[:, :, c] = value + (glow * 14).astype(np.uint8)
    return Image.fromarray(rgb, 'RGB').convert('RGBA')


def compose_hero(geometry, dimensions):
    canvas = background()
    d = ImageDraw.Draw(canvas)
    ink, muted, terracotta = '#343b31', '#77766a', '#9b5d47'
    spaced(d, (120, 78), 'SMYSLOVÁ GEOMETRIE / MONTESSORI INSPIRACE', terracotta, 22, 4)
    d.text((112, 128), 'Zahrada objevů', fill=ink, font=font(130, serif=True))
    d.text((126, 278), 'Pět tvarů. Pět výšek. Spousta vlastních objevů.', fill=muted, font=font(31))
    d.text((2070, 148), '1—5', fill=terracotta, font=font(86, serif=True))
    d.line((125, 350, 2275, 350), fill='#cac2b3', width=2)
    geometry.thumbnail((2200, 1200), Image.Resampling.LANCZOS)
    canvas.alpha_composite(geometry, ((2400 - geometry.width) // 2, 360))
    d = ImageDraw.Draw(canvas)
    d.line((125, 1510, 2275, 1510), fill='#cac2b3', width=2)
    entries = [('TVARY', 'Najdi každému kameni jeho místo.'),
               ('VÝŠKA', 'Seřaď je od nejnižšího k nejvyššímu.'),
               ('POČET', 'Objevuj množství dotykem i pohledem.')]
    for x, (title, subtitle) in zip((125, 870, 1615), entries):
        spaced(d, (x, 1544), title, terracotta, 23, 4)
        d.text((x, 1596), subtitle, fill=ink, font=font(23))
    d.text((125, 1685), f'Ø {dimensions[0]:.0f} mm · 6 samostatných dílů · CAD návrh', fill=muted, font=font(21))
    d.text((1475, 1685), 'Skutečná geometrie · ilustrativní barvy a světlo', fill=muted, font=font(21))
    return canvas.convert('RGB')


def row_parts(parts):
    """Přesun kamenů ze známých os sedel, zachování tvaru a orientace."""
    result = []
    for source in parts:
        part = source.copy()
        if source['file'] == 'Base':
            shift = np.array([0., 58., 0.])
        else:
            m = re.fullmatch(r'Stone([1-5])', source['file'])
            assert m, f"Neočekávaný díl {source['file']}"
            n = int(m[1])
            angle = math.radians(-90 + (n - 1) * 72)
            initial = np.array([73 * math.cos(angle), 73 * math.sin(angle), 8.])
            target = np.array([(n - 3) * 61., -102., 0.])
            shift = target - initial
        part['v'] = source['v'] + shift
        result.append(part)
    return result


def compose_play(geometry):
    canvas = background()
    d = ImageDraw.Draw(canvas)
    ink, muted, terracotta = '#343b31', '#77766a', '#9b5d47'
    spaced(d, (120, 78), 'ZAHRADA OBJEVŮ / DALŠÍ ZPŮSOB HRY', terracotta, 22, 4)
    d.text((112, 128), 'Malé kroky k velkým objevům.', fill=ink, font=font(104, serif=True))
    d.text((126, 269), 'Vyndej. Porovnej. Seřaď. Vrať na své místo.', fill=muted, font=font(31))
    d.line((125, 345, 2275, 345), fill='#cac2b3', width=2)
    geometry.thumbnail((2200, 1190), Image.Resampling.LANCZOS)
    canvas.alpha_composite(geometry, ((2400 - geometry.width) // 2, 355))
    d = ImageDraw.Draw(canvas)
    d.line((125, 1520, 2275, 1520), fill='#cac2b3', width=2)
    spaced(d, (125, 1562), 'JEDNA SADA, OTEVŘENÁ HRA', terracotta, 25, 3)
    d.text((125, 1620), 'Třídění tvarů · řazení výšek · přiřazování množství · hmatové zkoumání', fill=ink, font=font(28))
    d.text((125, 1695), 'Stejných šest CAD dílů; pět kamenů pouze přemístěno do řady. Barvy a světlo jsou ilustrativní.', fill=muted, font=font(21))
    return canvas.convert('RGB')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', type=Path, default=ROOT / 'vizualni-geometrie' / 'scene.json')
    parser.add_argument('--width', type=int, default=2200)
    parser.add_argument('--height', type=int, default=1190)
    args = parser.parse_args()
    started = time.time()
    _, parts = load_scene(args.scene)
    assert len(parts) == 6
    hero, dims = render(parts, args.width, args.height, eye=(.65, -5.5, 7.7))
    compose_hero(hero, dims).save(ROOT / 'nahled-zahrada.png', optimize=True)
    play, _ = render(row_parts(parts), args.width, args.height, eye=(.5, -5.5, 7.4))
    compose_play(play).save(ROOT / 'nahled-hry.png', optimize=True)
    top, _ = render(parts, 1700, 1700, eye=(0, -.001, 1), edge_lines=True)
    canvas = background(1900, 2050)
    canvas.alpha_composite(top, (100, 180))
    d = ImageDraw.Draw(canvas)
    d.text((100, 56), 'Zahrada objevů / pohled shora', fill='#343b31', font=font(72, serif=True))
    d.text((100, 1945), 'Skutečná CAD geometrie · ilustrativní barvy a světlo', fill='#77766a', font=font(28))
    canvas.convert('RGB').save(ROOT / 'nahled-shora.png', optimize=True)
    print(json.dumps({'output': str(ROOT / 'nahled-zahrada.png'), 'dimensions_mm': dims.tolist(),
                      'triangles': sum(len(p['v']) for p in parts), 'elapsed_seconds': round(time.time() - started, 1),
                      'source_hashes': {p['file']: p['sha256'] for p in parts}}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
