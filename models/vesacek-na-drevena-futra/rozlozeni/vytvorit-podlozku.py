#!/usr/bin/env python3
"""Jeden věšáček na podložce Kobra X, zatím pouze geometrie.

Čte ../stl/vesacek.stl. Přepíše jen soubory této složky; neovládá tiskárnu.
Souřadnice CAD: X napříč futry, Y od futer, Z nahoru. Pro tisk leží
zadní dosedací plocha Y=0 na podložce: tiskové Z = CAD Y.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
STL = HERE.parent / "stl/vesacek.stl"
PLATE = HERE / "podlozka-01-geometrie.3mf"
PREVIEW = HERE / "podlozka-01.png"
REPORT = HERE / "kontrola-rozlozeni.json"
NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
BED = 260


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_stl():
    raw = STL.read_bytes()
    count = struct.unpack_from("<I", raw, 80)[0]
    check(len(raw) == 84 + 50 * count and count > 100, "Expected binary STL")
    vertices, index, triangles = [], {}, []
    source_low, source_high = [float("inf")] * 3, [float("-inf")] * 3
    for i in range(count):
        values = struct.unpack_from("<12fH", raw, 84 + i * 50)
        triangle = []
        for start in (3, 6, 9):
            x, y, z = (float(values[start + axis]) for axis in range(3))
            for axis, value in enumerate((x, y, z)):
                source_low[axis] = min(source_low[axis], value)
                source_high[axis] = max(source_high[axis], value)
            # A true +90-degree rotation about CAD X, followed by centering.
            point = (130 + x, 173 - z, 0.0 if abs(y) < 1e-6 else y)
            key = tuple(round(v, 6) for v in point)
            if key not in index:
                index[key] = len(vertices)
                vertices.append(point)
            triangle.append(index[key])
        check(len(set(triangle)) == 3, "Degenerate facet")
        triangles.append(tuple(triangle))
    expected_low, expected_high = (-22, 0, 0), (22, 58, 86)
    check(all(abs(source_low[i] - expected_low[i]) < 0.02 and
              abs(source_high[i] - expected_high[i]) < 0.02 for i in range(3)),
          "Source STL bounds changed: %s %s" % (source_low, source_high))
    edges = Counter(tuple(sorted((triangle[k], triangle[(k + 1) % 3])))
                    for triangle in triangles for k in range(3))
    check(all(count == 2 for count in edges.values()), "STL is not watertight/manifold")
    lower = [min(v[axis] for v in vertices) for axis in range(3)]
    upper = [max(v[axis] for v in vertices) for axis in range(3)]
    check(all(0 <= lower[i] < upper[i] <= BED for i in range(3)) and
          lower[2] == 0, "Part outside Kobra X bed or above Z=0")
    return vertices, triangles, lower, upper, source_low, source_high


def write_plate(vertices, triangles):
    ET.register_namespace("", NS)
    model = ET.Element("{%s}model" % NS, {
        "unit": "millimeter", "{http://www.w3.org/XML/1998/namespace}lang": "cs-CZ"})
    ET.SubElement(model, "metadata", {"name": "Title"}).text = (
        "Věšáček na dřevěná futra – podložka 01, pouze geometrie")
    ET.SubElement(model, "metadata", {"name": "Description"}).text = (
        "1 kus 1:1, bez tiskového procesu a filamentu. Návrhový koncept; fyzický fit a nosnost neověřeny.")
    resources = ET.SubElement(model, "resources")
    obj = ET.SubElement(resources, "object", {
        "id": "1", "type": "model", "name": "01 Věšáček – zadní plochou na podložce"})
    mesh = ET.SubElement(obj, "mesh")
    verts = ET.SubElement(mesh, "vertices")
    tris = ET.SubElement(mesh, "triangles")
    for point in vertices:
        ET.SubElement(verts, "vertex", {
            axis: format(value, ".9g") for axis, value in zip("xyz", point)})
    for tri in triangles:
        ET.SubElement(tris, "triangle", {
            "v%d" % (i + 1): str(value) for i, value in enumerate(tri)})
    build = ET.SubElement(model, "build")
    ET.SubElement(build, "item", {"objectid": "1"})
    types = ET.Element("Types", {
        "xmlns": "http://schemas.openxmlformats.org/package/2006/content-types"})
    ET.SubElement(types, "Default", {"Extension": "rels", "ContentType":
        "application/vnd.openxmlformats-package.relationships+xml"})
    ET.SubElement(types, "Default", {"Extension": "model", "ContentType":
        "application/vnd.ms-package.3dmanufacturing-3dmodel+xml"})
    rels = ET.Element("Relationships", {
        "xmlns": "http://schemas.openxmlformats.org/package/2006/relationships"})
    ET.SubElement(rels, "Relationship", {"Target": "/3D/3dmodel.model", "Id": "rel0",
        "Type": "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"})
    serialize = lambda element: ET.tostring(element, encoding="utf-8", xml_declaration=True)
    with ZipFile(PLATE, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", serialize(types))
        archive.writestr("_rels/.rels", serialize(rels))
        archive.writestr("3D/3dmodel.model", serialize(model))
    with ZipFile(PLATE) as archive:
        check(archive.testzip() is None, "Corrupt 3MF")
        root = ET.fromstring(archive.read("3D/3dmodel.model"))
        check(len(root.findall("{%s}build/{%s}item" % (NS, NS))) == 1,
              "Incorrect physical copy count")


def write_preview(vertices, triangles):
    img = Image.new("RGB", (1020, 1100), "#f7f9fb")
    draw = ImageDraw.Draw(img)
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    title = ImageFont.truetype(font, 29)
    label = ImageFont.truetype(font, 18)
    draw.text((58, 25), "PODLOŽKA 01  ·  KOBRA X  ·  260 × 260 mm",
              fill="#173642", font=title)
    scale, left, top = 3.4, 68, 98
    to_px = lambda point: (left + point[0] * scale,
                           top + (BED - point[1]) * scale)
    draw.rectangle((left, top, left + BED * scale, top + BED * scale),
                   fill="#e9eff2", outline="#506a77", width=3)
    # Horní pohled je rasterizace skutečných trojúhelníků otočeného 3MF.
    for tri in sorted(triangles, key=lambda t: sum(vertices[i][2] for i in t) / 3):
        height = sum(vertices[i][2] for i in tri) / 3
        t = height / 58
        fill = (int(80 + 45 * t), int(131 + 20 * t), int(146 + 16 * t))
        draw.polygon([to_px(vertices[i]) for i in tri], fill=fill)
    draw.line(((left, top + BED * scale), (left + BED * scale, top + BED * scale)),
              fill="#be6552", width=5)
    draw.text((68, 1015), "1× věšáček · zadní dosedací plochou na podložce · bez podpor",
              fill="#2b4652", font=label)
    draw.text((68, 1043), "Červená hrana = přední strana podložky. Barva = výška modelu.",
              fill="#536d78", font=label)
    img.save(PREVIEW)


def main():
    vertices, triangles, lower, upper, source_low, source_high = read_stl()
    write_plate(vertices, triangles)
    write_preview(vertices, triangles)
    report = {
        "status": "geometry-only, no process or G-code",
        "source_stl": "../stl/vesacek.stl", "source_stl_sha256": digest(STL),
        "plate": PLATE.name, "plate_sha256": digest(PLATE), "preview": PREVIEW.name,
        "printer": "Anycubic Kobra X 0.4 nozzle", "bed_mm": [260, 260, 260],
        "physical_pieces": 1, "triangle_count": len(triangles),
        "source_bounds_mm": {"min": source_low, "max": source_high},
        "placed_bounds_mm": {"min": lower, "max": upper},
        "orientation": "back Y=0 to bed Z=0; +90 deg about CAD X",
        "xy_min_margin_mm": min(lower[0], lower[1], BED-upper[0], BED-upper[1]),
        "support_setting": "to be checked in configured project",
        "physical_fit_or_strength_verified": False,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("VESACEK_PLATE_OK", report["placed_bounds_mm"], flush=True)


if __name__ == "__main__":
    main()
