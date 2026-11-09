#!/usr/bin/env python3
"""Create six labelled geometry-only concept plates; NEVER a print-ready project.

Only the six named enclosure STL files are read. Reference electronics are not
exported. Existing concept 3MF, PNG and manifest files in this directory are
replaced on regeneration. No source CAD/STL or slicer presets are modified.
"""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import struct
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
BED = (260.0, 260.0, 260.0)
MIN_MARGIN = 5.0
STATUS = "KONCEPT-NEVYRABET"
PARTS = ("telo", "celo", "vrsek", "ramecek-1", "ramecek-2", "ramecek-3")
LABELS = ("TĚLO", "ČELO", "VRŠEK", "RÁMEČEK 1", "RÁMEČEK 2", "RÁMEČEK 3")
NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("", NS)


def tag(name):
    return "{%s}%s" % (NS, name)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_stl(data):
    assert len(data) >= 84, "STL is too short"
    count = struct.unpack_from("<I", data, 80)[0]
    assert count > 0 and len(data) == 84 + count * 50, "Expected binary STL"
    vertices, faces, indices = [], [], {}
    for index in range(count):
        values = struct.unpack_from("<12fH", data, 84 + index * 50)
        face = []
        for offset in (3, 6, 9):
            point = tuple(values[offset:offset + 3])
            assert all(math.isfinite(value) for value in point), "Non-finite vertex"
            if point not in indices:
                indices[point] = len(vertices)
                vertices.append(point)
            face.append(indices[point])
        faces.append(tuple(face))
    return vertices, faces


def bounds(vertices):
    return ([min(p[axis] for p in vertices) for axis in range(3)],
            [max(p[axis] for p in vertices) for axis in range(3)])


def mesh_check(vertices, faces):
    """Verify closed oriented edges, connected shells, and positive volume."""
    edges = defaultdict(list)
    signed_volume = 0.0
    for index, face in enumerate(faces):
        assert len(set(face)) == 3, "Degenerate triangle indices"
        a, b, c = (vertices[v] for v in face)
        ab = [b[i] - a[i] for i in range(3)]
        ac = [c[i] - a[i] for i in range(3)]
        normal = (ab[1] * ac[2] - ab[2] * ac[1],
                  ab[2] * ac[0] - ab[0] * ac[2],
                  ab[0] * ac[1] - ab[1] * ac[0])
        assert sum(n * n for n in normal) > 1e-16, "Zero-area triangle"
        signed_volume += sum(a[i] * normal[i] for i in range(3)) / 6.0
        for start, end in zip(face, (face[1], face[2], face[0])):
            edges[tuple(sorted((start, end)))].append((index, start, end))
    assert all(len(entries) == 2 for entries in edges.values()), "Open or non-manifold edge"
    assert all(e[0][1] == e[1][2] and e[0][2] == e[1][1]
               for e in edges.values()), "Inconsistent winding"
    adjacency = defaultdict(set)
    for entries in edges.values():
        left, right = entries[0][0], entries[1][0]
        adjacency[left].add(right)
        adjacency[right].add(left)
    unseen = set(range(len(faces)))
    components = 0
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            for adjacent in adjacency[stack.pop()]:
                if adjacent in unseen:
                    unseen.remove(adjacent)
                    stack.append(adjacent)
    assert components == 1, "Expected one connected physical part"
    assert signed_volume > 0, "Expected positive enclosed volume"
    return {"watertight_edges": True, "consistent_winding": True,
            "connected_shells": components, "signed_volume_mm3": signed_volume,
            "vertex_count": len(vertices), "triangle_count": len(faces),
            "self_intersections_tested": False}


def orient_and_place(vertices, name):
    if name == "celo":
        oriented = [(x, z, -y) for x, y, z in vertices]
        description = "Rotation X=source X, Y=source Z, Z=-source Y; thickness on print Z"
    else:
        oriented = list(vertices)
        description = "Exported XYZ orientation preserved"
    minimum, maximum = bounds(oriented)
    translation = [(BED[0] - minimum[0] - maximum[0]) / 2,
                   (BED[1] - minimum[1] - maximum[1]) / 2,
                   -minimum[2]]
    placed = [tuple(point[i] + translation[i] for i in range(3)) for point in oriented]
    low, high = bounds(placed)
    margins = [low[0], low[1], BED[0] - high[0], BED[1] - high[1]]
    assert min(margins) >= MIN_MARGIN - 1e-6, "Plate edge clearance below 5 mm"
    assert abs(low[2]) <= 1e-6 and 0 < high[2] <= BED[2], "Part exceeds height or floats"
    return placed, {"orientation": description, "translation_after_rotation_mm": translation,
                    "placed_min_xyz_mm": low, "placed_max_xyz_mm": high,
                    "placed_bbox_mm": [high[i] - low[i] for i in range(3)],
                    "edge_margins_left_front_right_back_mm": margins,
                    "minimum_edge_margin_mm": min(margins),
                    "height_clearance_mm": BED[2] - high[2]}


def write_3mf(path, vertices, faces, number, name):
    model = ET.Element(tag("model"), {"unit": "millimeter", "{http://www.w3.org/XML/1998/namespace}lang": "cs-CZ"})
    ET.SubElement(model, tag("metadata"), {"name": "Title"}).text = f"{STATUS} — {number:02d} — {name}"
    ET.SubElement(model, tag("metadata"), {"name": "Description"}).text = (
        "Rozmerove neovereny koncept. 1 fyzicky dil. Pouze geometrie; bez profilu, "
        "materialu, podpor a G-code. Pred vyrobou doplnit mereni, spoje a proverit slicer.")
    resources = ET.SubElement(model, tag("resources"))
    obj = ET.SubElement(resources, tag("object"), {"id": "1", "type": "model", "name": f"{STATUS}-{name}"})
    mesh = ET.SubElement(obj, tag("mesh"))
    vertex_nodes = ET.SubElement(mesh, tag("vertices"))
    triangle_nodes = ET.SubElement(mesh, tag("triangles"))
    for x, y, z in vertices:
        ET.SubElement(vertex_nodes, tag("vertex"), {"x": f"{x:.8f}", "y": f"{y:.8f}", "z": f"{z:.8f}"})
    for a, b, c in faces:
        ET.SubElement(triangle_nodes, tag("triangle"), {"v1": str(a), "v2": str(b), "v3": str(c)})
    build = ET.SubElement(model, tag("build"))
    ET.SubElement(build, tag("item"), {"objectid": "1"})
    content_types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    relationships = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    with ZipFile(path, "w", ZIP_DEFLATED, compresslevel=6) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", relationships)
        archive.writestr("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True))
    with ZipFile(path) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == {"[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"}
        parsed = ET.fromstring(archive.read("3D/3dmodel.model"))
        assert parsed.get("unit") == "millimeter"
        assert len(parsed.findall("m:resources/m:object", {"m": NS})) == 1
        assert len(parsed.findall("m:build/m:item", {"m": NS})) == 1
        assert len(parsed.findall(".//m:triangle", {"m": NS})) == len(faces)
        restored = [tuple(float(element.get(axis)) for axis in ("x", "y", "z"))
                    for element in parsed.findall(".//m:vertex", {"m": NS})]
        assert len(restored) == len(vertices)
        assert all(abs(a - b) < 1e-7 for p, q in zip(vertices, restored) for a, b in zip(p, q))


def preview(path, vertices, faces, number, label, dimensions):
    scale, pad, top = 3.0, 62, 110
    image = Image.new("RGB", (904, 1015), "#f2f4f6")
    draw = ImageDraw.Draw(image)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = ImageFont.truetype(font_path, 27)
    small = ImageFont.truetype(font_path, 18)
    medium = ImageFont.truetype(font_path, 22)
    draw.text((pad, 18), f"{number:02d} · {label} · 1 kus", fill="#173447", font=font)
    draw.text((pad, 58), "KONCEPT — NEVYRÁBĚT", fill="#b33327", font=medium)
    draw.rectangle((pad, top, pad + 260 * scale, top + 260 * scale), fill="#ffffff", outline="#6c7d87", width=2)
    for coordinate in range(20, 260, 20):
        draw.line((pad + coordinate * scale, top, pad + coordinate * scale, top + 260 * scale), fill="#eef1f3")
        draw.line((pad, top + coordinate * scale, pad + 260 * scale, top + coordinate * scale), fill="#eef1f3")
    draw.rectangle((pad + 5 * scale, top + 5 * scale, pad + 255 * scale, top + 255 * scale), outline="#e7aa79", width=1)
    zmax = max(p[2] for p in vertices)
    # Actual transformed triangle projection, sorted from low to high surfaces.
    # This is a geometric plan view, not a slicer toolpath or rendered CAD scene.
    for face in sorted(faces, key=lambda f: sum(vertices[v][2] for v in f)):
        points = [vertices[v] for v in face]
        projected = [(pad + p[0] * scale, top + (260 - p[1]) * scale) for p in points]
        area2 = abs(sum(projected[i][0] * projected[(i + 1) % 3][1] - projected[(i + 1) % 3][0] * projected[i][1] for i in range(3)))
        if area2 < 0.03:
            continue
        height = sum(p[2] for p in points) / (3 * max(zmax, 0.001))
        color = tuple(int(lo + (hi - lo) * height) for lo, hi in zip((128, 160, 174), (43, 91, 115)))
        draw.polygon(projected, fill=color)
    draw.text((pad, 911), "Kobra X · plocha 260 × 260 mm · měřítko geometrie 100 %", fill="#344e5b", font=small)
    draw.text((pad, 940), "Rozměr v této orientaci: " + " × ".join(f"{v:.1f}" for v in dimensions) + " mm", fill="#344e5b", font=small)
    draw.text((pad, 969), "Pouze geometrie; rozměry, spoje, podpory a řezání nedokončené.", fill="#a43c31", font=small)
    image.save(path)


def generate():
    cad_report = json.loads((MODEL / "kontrola-modelu.json").read_text(encoding="utf-8"))
    assert set(cad_report["printed_parts"]) == set(PARTS), "Unexpected physical-part inventory"
    prepared = []
    # Validate every input before replacing any plate outputs.
    for number, (name, label) in enumerate(zip(PARTS, LABELS), 1):
        source = (MODEL / "stl" / f"{name}.stl").read_bytes()
        assert sha256(source) == cad_report["printed_parts"][name]["sha256"], "STL and CAD report disagree"
        vertices, faces = read_stl(source)
        check = mesh_check(vertices, faces)
        placed, placement = orient_and_place(vertices, name)
        source_low, source_high = bounds(vertices)
        stem = f"podlozka-{number:02d}-{name}-{STATUS}"
        record = {"plate": number, "part": name, "count": 1,
                  "source_stl": f"../stl/{name}.stl", "source_sha256": sha256(source),
                  "source_bbox_mm": [source_high[i] - source_low[i] for i in range(3)],
                  "geometry_only_3mf": stem + ".3mf", "preview": stem + ".png",
                  "mesh_check": check, **placement}
        prepared.append((record, placed, faces, label))
    for record, vertices, faces, label in prepared:
        output = HERE / record["geometry_only_3mf"]
        write_3mf(output, vertices, faces, record["plate"], record["part"])
        preview(HERE / record["preview"], vertices, faces, record["plate"], label, record["placed_bbox_mm"])
        record["geometry_only_sha256"] = sha256(output.read_bytes())
    report = {"status": STATUS, "geometry_only": True, "ready_to_print": False,
              "dimensions_are_unmeasured_design_placeholders": True,
              "printer_reference": "Anycubic Kobra X; bed envelope only, NO printer preset",
              "printer_envelope_mm": BED, "minimum_required_edge_margin_mm": MIN_MARGIN,
              "plate_count": len(prepared), "total_physical_parts": sum(p[0]["count"] for p in prepared),
              "no_machine_material_or_process_presets": True,
              "reference_electronics_included": False,
              "slicing_performed": False, "supports_configured": False,
              "assembly_connectors_complete": False, "physical_fit_verified": False,
              "verification_scope": "Exact named STL inventory and hashes; one closed consistently oriented mesh per part; single build item and exact coordinates in each Core 3MF; plate bounds and numbered geometric previews. Not a self-intersection, strength, thermal, fit or slicing test.",
              "parts": [record for record, _, _, _ in prepared]}
    assert report["plate_count"] == report["total_physical_parts"] == 6
    (HERE / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": STATUS, "plates": 6, "physical_parts": 6,
                      "minimum_edge_margin_mm": min(p[0]["minimum_edge_margin_mm"] for p in prepared),
                      "maximum_height_mm": max(p[0]["placed_max_xyz_mm"][2] for p in prepared),
                      "manifest": str(HERE / "manifest.json")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    generate()
