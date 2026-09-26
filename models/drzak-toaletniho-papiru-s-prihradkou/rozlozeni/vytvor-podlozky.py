#!/usr/bin/env python3
"""Dvě reprodukovatelné 3MF podložky pouze s geometrií; následně se doplní profil.

Čte výsledná STL vedle FreeCAD dokumentu. Přepisuje jen *-geometrie.3mf,
podlozka-*.png a kontrola-rozlozeni.json v této složce. Bez komunikace s tiskárnou.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PARTS = {
    1: [
        ("01 Schránka", "body.stl", (35, 15, 0)),
        ("02 Levé rameno", "bracket.stl", (29, 150, 0)),
        ("03 Pravé rameno", "bracket.stl", (140, 150, 0)),
    ],
    2: [
        ("04 Zásuvka", "drawer.stl", (35, 15, 0)),
        ("05 Osa", "axle.stl", (55, 165, 0)),
        ("06 Zátka", "cap.stl", (112, 211, 0)),
    ],
}
COLORS = ["#354b59", "#5b8390", "#6d9ba5", "#475963", "#b37444", "#bd8e53"]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def read_stl(path):
    raw = path.read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0] if len(raw) >= 84 else -1
    if n >= 0 and len(raw) == 84 + 50 * n:
        points = []
        for i in range(n):
            record = struct.unpack_from("<12fH", raw, 84 + 50 * i)
            points.extend([tuple(record[k:k+3]) for k in (3, 6, 9)])
    else:
        points = []
        for line in raw.decode("ascii").splitlines():
            tokens = line.strip().split()
            if tokens and tokens[0].lower() == "vertex":
                points.append(tuple(map(float, tokens[1:4])))
    require(points and len(points) % 3 == 0, f"Empty/malformed STL: {path}")
    vertices, lookup, triangles = [], {}, []
    for point in points:
        key = tuple(round(x, 6) for x in point)
        if key not in lookup:
            lookup[key] = len(vertices)
            vertices.append(point)
        triangles.append(lookup[key])
    return vertices, [tuple(triangles[i:i+3]) for i in range(0, len(triangles), 3)]

def mesh_check(vertices, triangles, name):
    require(all(len(set(t)) == 3 for t in triangles), f"Degenerate triangles: {name}")
    edges = Counter(tuple(sorted((a, b))) for t in triangles for a, b in
                    ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])))
    require(all(n == 2 for n in edges.values()), f"Nonmanifold/open STL: {name}")
    mins = [min(v[i] for v in vertices) for i in range(3)]
    maxs = [max(v[i] for v in vertices) for i in range(3)]
    # Kruhová tessellace nemusí obsahovat matematický extrém v ose X/Y.
    require(all(abs(v) < 0.01 for v in mins), f"STL does not start at origin: {name}: {mins}")
    return mins, maxs

def xml_bytes(root):
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)

def draw_preview(number, items):
    img = Image.new("RGB", (960, 1040), "#f7f8f9")
    dr = ImageDraw.Draw(img)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    title_font = ImageFont.truetype(font_path, 32)
    label_font = ImageFont.truetype(font_path, 20)
    small_font = ImageFont.truetype(font_path, 17)
    dr.text((64, 22), f"Podložka {number:02d} · Anycubic Kobra X · 260 × 260 mm", fill="#182a35", font=title_font)
    scale, margin = 3.25, 58
    xy = lambda x, y: (margin + scale*x, margin + scale*(260-y))
    dr.rectangle([xy(0, 260), xy(260, 0)], outline="#465e6c", width=3, fill="#e8edef")
    dr.line([xy(0, 0), xy(260, 0)], fill="#c95946", width=5)
    dr.text((margin, 915), "Červená hrana = přední strana tiskárny. Čísla jsou fyzické kusy.", fill="#354b59", font=small_font)
    for index, item in enumerate(items):
        points = item["vertices"]
        triangles = item["triangles"]
        tr = item["translation_mm"]
        color = COLORS[item["global_index"]-1]
        for tri in triangles:
            coords = [xy(points[i][0]+tr[0], points[i][1]+tr[1]) for i in tri]
            dr.polygon(coords, fill=color)
        x0, y0, _ = item["placed_min_mm"]
        x1, y1, _ = item["placed_max_mm"]
        label = f"{item['global_index']:02d}"
        center = xy((x0+x1)/2, (y0+y1)/2)
        bbox = dr.textbbox((0, 0), label, font=label_font)
        dr.rounded_rectangle((center[0]-23, center[1]-18, center[0]+23, center[1]+18),
                             radius=7, fill="#ffffff", outline="#233747", width=2)
        dr.text((center[0]-(bbox[2]-bbox[0])/2, center[1]-(bbox[3]-bbox[1])/2-2),
                label, fill="#172b35", font=label_font)
        dr.text((64, 949+index*27), f"{item['label']}: 1 ks", fill="#253c49", font=small_font)
    path = HERE / f"podlozka-{number:02d}.png"
    img.save(path)
    return path

def build_plate(number, specifications, nominal):
    ET.register_namespace("", NS)
    model = ET.Element(f"{{{NS}}}model", {"unit": "millimeter", "{http://www.w3.org/XML/1998/namespace}lang": "cs-CZ"})
    ET.SubElement(model, "metadata", {"name": "Title"}).text = f"Držák se zásuvkou – podložka {number:02d}, pouze geometrie"
    ET.SubElement(model, "metadata", {"name": "Description"}).text = "1:1, bez tiskového procesu, filamentu a G-code. K tisku použijte nastavený projekt."
    resources = ET.SubElement(model, "resources")
    build = ET.SubElement(model, "build")
    items = []
    for local_index, (label, filename, translation) in enumerate(specifications, 1):
        path = ROOT / "stl" / filename
        vertices, triangles = read_stl(path)
        mins, maxs = mesh_check(vertices, triangles, filename)
        require(all(abs(maxs[k]-mins[k]-nominal[filename][k]) < 0.03 for k in range(3)),
                f"Unexpected mesh dimensions: {filename}")
        placed_min = [mins[k]+translation[k] for k in range(3)]
        placed_max = [maxs[k]+translation[k] for k in range(3)]
        require(all(placed_min[k] >= 0 and placed_max[k] <= 260 for k in range(3)),
                f"Outside Kobra X printable volume: {label}")
        obj = ET.SubElement(resources, "object", {"id": str(local_index), "type": "model", "name": label})
        mesh = ET.SubElement(obj, "mesh")
        verts = ET.SubElement(mesh, "vertices")
        tris = ET.SubElement(mesh, "triangles")
        for v in vertices:
            ET.SubElement(verts, "vertex", {a: format(value, ".12g") for a, value in zip("xyz", v)})
        for t in triangles:
            ET.SubElement(tris, "triangle", {f"v{k+1}": str(i) for k, i in enumerate(t)})
        transform = (1,0,0,0,1,0,0,0,1,*translation)
        ET.SubElement(build, "item", {"objectid": str(local_index),
                                      "transform": " ".join(map(str, transform))})
        items.append({"global_index": 3*(number-1)+local_index,
                      "label": label, "stl": filename, "stl_sha256": sha(path),
                      "translation_mm": list(translation), "placed_min_mm": placed_min,
                      "placed_max_mm": placed_max, "vertices": vertices, "triangles": triangles,
                      "vertices_count": len(vertices), "triangles_count": len(triangles)})
    for i, a in enumerate(items):
        for b in items[i+1:]:
            amin, amax = a["placed_min_mm"], a["placed_max_mm"]
            bmin, bmax = b["placed_min_mm"], b["placed_max_mm"]
            gap_x = max(0, amin[0]-bmax[0], bmin[0]-amax[0])
            gap_y = max(0, amin[1]-bmax[1], bmin[1]-amax[1])
            require(gap_x > 0 or gap_y > 0, f"Overlapping part bounds: {a['label']} {b['label']}")
    types = ET.Element("Types", {"xmlns": "http://schemas.openxmlformats.org/package/2006/content-types"})
    ET.SubElement(types, "Default", {"Extension": "rels", "ContentType": "application/vnd.openxmlformats-package.relationships+xml"})
    ET.SubElement(types, "Default", {"Extension": "model", "ContentType": "application/vnd.ms-package.3dmanufacturing-3dmodel+xml"})
    rels = ET.Element("Relationships", {"xmlns": "http://schemas.openxmlformats.org/package/2006/relationships"})
    ET.SubElement(rels, "Relationship", {"Target": "/3D/3dmodel.model", "Id": "rel0",
                                        "Type": "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"})
    output = HERE / f"drzak-podlozka-{number:02d}-geometrie.3mf"
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", xml_bytes(types))
        archive.writestr("_rels/.rels", xml_bytes(rels))
        archive.writestr("3D/3dmodel.model", xml_bytes(model))
    with ZipFile(output) as archive:
        require(archive.testzip() is None, "Corrupt 3MF ZIP")
        reloaded = ET.fromstring(archive.read("3D/3dmodel.model"))
        require(len(reloaded.findall(f"{{{NS}}}build/{{{NS}}}item")) == len(items),
                "3MF copy count changed")
    preview = draw_preview(number, items)
    for item in items:
        del item["vertices"], item["triangles"]
    return {"plate": number, "geometry_3mf": output.name,
            "geometry_sha256": sha(output), "preview": preview.name,
            "copies": len(items), "items": items,
            "edge_margin_mm": min(min(a["placed_min_mm"][0], a["placed_min_mm"][1],
                                      260-a["placed_max_mm"][0], 260-a["placed_max_mm"][1]) for a in items)}

def main():
    report = json.loads((ROOT / "kontrola-modelu.json").read_text())
    nominal = {record["stl"].split("/")[-1]: record["print_dimensions_mm"]
               for record in report["parts"].values()}
    plates = [build_plate(n, spec, nominal) for n, spec in PARTS.items()]
    result = {"state": "geometrie 1:1; tiskový proces v samostatném nastaveném projektu",
              "printer": "Anycubic Kobra X 0.4 nozzle", "bed_mm": [260, 260],
              "physical_pieces": sum(p["copies"] for p in plates),
              "types": len(set(item["stl"] for p in plates for item in p["items"])),
              "plates": plates}
    require(result["physical_pieces"] == 6 and result["types"] == 5, "BOM mismatch")
    (HERE / "kontrola-rozlozeni.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"plates": len(plates), "copies": result["physical_pieces"],
                      "margins_mm": [p["edge_margin_mm"] for p in plates]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
