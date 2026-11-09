#!/usr/bin/env python3
"""Generate one geometry-only Core 3MF plate and its numbered plan preview.

Three complementary mesh regions form two physical pieces: a white body, its
black inlaid lettering, and a white lid. This 3MF has no process presets.
"""
import hashlib
import json
import math
from pathlib import Path
import struct
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
BED = 260.0
PARTS = [
    {"name": "telo-techtools", "stl": "telo.stl", "translation_mm": (55.0, 10.0), "physical_piece": "body"},
    {"name": "napis-techtools-uctenky", "stl": "napis.stl", "translation_mm": (55.0, 10.0), "physical_piece": "body"},
    {"name": "viko-se-sterbinou", "stl": "viko.stl", "translation_mm": (52.0, 134.0), "physical_piece": "lid"},
]
NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("", NS)

def tag(name):
    return "{%s}%s" % (NS, name)

def read_binary_stl(data):
    triangles = struct.unpack_from("<I", data, 80)[0]
    assert len(data) == 84 + triangles * 50, "Expected binary STL"
    vertices, faces, indices = [], [], {}
    for i in range(triangles):
        values = struct.unpack_from("<12fH", data, 84 + i * 50)
        face = []
        for j in (3, 6, 9):
            point = tuple(values[j:j+3])
            if point not in indices:
                indices[point] = len(vertices)
                vertices.append(point)
            face.append(indices[point])
        faces.append(face)
    return vertices, faces

def xml_bytes(model):
    return ET.tostring(model, encoding="utf-8", xml_declaration=True)

def generate():
    model = ET.Element(tag("model"), {"unit": "millimeter", "{http://www.w3.org/XML/1998/namespace}lang": "cs-CZ"})
    ET.SubElement(model, tag("metadata"), {"name": "Title"}).text = "TechTools — schránka na účtenky — podložka 01"
    ET.SubElement(model, tag("metadata"), {"name": "Description"}).text = "1 telo s vlozenym barevnym napisem + 1 viko; pouze geometrie, bez profilu"
    resources = ET.SubElement(model, tag("resources"))
    build = ET.SubElement(model, tag("build"))
    manifest = []
    for number, part in enumerate(PARTS, 1):
        path = MODEL / "stl" / part["stl"]
        source = path.read_bytes()
        vertices, faces = read_binary_stl(source)
        minimum = [min(point[i] for point in vertices) for i in range(3)]
        maximum = [max(point[i] for point in vertices) for i in range(3)]
        dx, dy = part["translation_mm"]
        if part["physical_piece"] == "lid" or part["name"] == "telo-techtools":
            assert abs(minimum[2]) < 1e-5, "Physical piece is not resting on Z=0"
        else:
            assert 0 < minimum[2] < maximum[2] < 138.0, "Lettering does not sit within body height"
        placed_min = [minimum[0] + dx, minimum[1] + dy, minimum[2]]
        placed_max = [maximum[0] + dx, maximum[1] + dy, maximum[2]]
        assert all(9 <= placed_min[i] < placed_max[i] <= BED - 9 for i in (0, 1))
        assert placed_max[2] < BED
        obj = ET.SubElement(resources, tag("object"), {"id": str(number), "type": "model", "name": part["name"]})
        mesh = ET.SubElement(obj, tag("mesh"))
        vertex_node = ET.SubElement(mesh, tag("vertices"))
        triangle_node = ET.SubElement(mesh, tag("triangles"))
        for x, y, z in vertices:
            ET.SubElement(vertex_node, tag("vertex"), {"x": "%.8f" % (x + dx), "y": "%.8f" % (y + dy), "z": "%.8f" % z})
        for face in faces:
            ET.SubElement(triangle_node, tag("triangle"), {"v1": str(face[0]), "v2": str(face[1]), "v3": str(face[2])})
        manifest.append({"name": part["name"], "count": 1, "physical_piece": part["physical_piece"], "source_stl": "../stl/" + part["stl"], "source_sha256": hashlib.sha256(source).hexdigest(), "triangle_count": len(faces), "source_bbox_mm": [maximum[i] - minimum[i] for i in range(3)], "translation_mm": [dx, dy, 0.0], "placed_min_xyz_mm": placed_min, "placed_max_xyz_mm": placed_max, "orientation": "Z as exported; body and lid bases at Z=0; lettering embedded in body wall"})
    # Lettering must occupy the body's exact XY translation. The other physical
    # piece stays separate with an actual gap on the bed.
    assert manifest[0]["translation_mm"] == manifest[1]["translation_mm"]
    assert manifest[0]["placed_min_xyz_mm"][0] <= manifest[1]["placed_min_xyz_mm"][0] < manifest[1]["placed_max_xyz_mm"][0] <= manifest[0]["placed_max_xyz_mm"][0]
    assert manifest[0]["placed_min_xyz_mm"][1] <= manifest[1]["placed_min_xyz_mm"][1] < manifest[1]["placed_max_xyz_mm"][1] <= manifest[0]["placed_max_xyz_mm"][1]
    assert manifest[0]["placed_max_xyz_mm"][1] + 10 <= manifest[2]["placed_min_xyz_mm"][1]
    # Slicer must treat the colored lettering as a second volume of the body.
    # An independent build item would be snapped to the bed or rejected as a
    # floating object. The assembly remains one physical piece on the plate.
    assembly = ET.SubElement(resources, tag("object"), {"id": "4", "type": "model", "name": "telo-techtools"})
    components = ET.SubElement(assembly, tag("components"))
    ET.SubElement(components, tag("component"), {"objectid": "1"})
    ET.SubElement(components, tag("component"), {"objectid": "2"})
    ET.SubElement(build, tag("item"), {"objectid": "4"})
    ET.SubElement(build, tag("item"), {"objectid": "3"})
    archive = HERE / "podlozka-01-geometrie.3mf"
    content_types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    relationships = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    with ZipFile(archive, "w", ZIP_DEFLATED, compresslevel=6) as output:
        output.writestr("[Content_Types].xml", content_types)
        output.writestr("_rels/.rels", relationships)
        output.writestr("3D/3dmodel.model", xml_bytes(model))
    with ZipFile(archive) as check:
        assert check.testzip() is None
        parsed = ET.fromstring(check.read("3D/3dmodel.model"))
        assert len(parsed.findall("m:build/m:item", {"m": NS})) == 2
        composite = parsed.find("m:resources/m:object[@id='4']/m:components", {"m": NS})
        assert composite is not None and [c.get("objectid") for c in composite] == ["1", "2"]
        assert not any(name.startswith("Metadata/") for name in check.namelist())
    report = {"plate": 1, "printer_bed_mm": [260, 260, 260], "physical_parts": 2, "material_regions": 3, "parts": manifest, "geometry_only_3mf": archive.name, "geometry_only_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "supports_required_by_design": False, "print_orientation": "Body upright on its floor with inlaid front lettering; lid flat exterior face on bed, locating lip upward", "no_machine_or_material_presets": True}
    (HERE / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    draw_preview(manifest)
    print(json.dumps(report, ensure_ascii=False))

def draw_preview(manifest):
    scale = 3
    pad = 72
    image = Image.new("RGB", (int(BED * scale + 2 * pad), int(BED * scale + 2 * pad)), "#f7f9fa")
    d = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    def xy(x, y):
        return (pad + x * scale, pad + (BED - y) * scale)
    d.rectangle((pad, pad, pad + BED * scale, pad + BED * scale), fill="#ffffff", outline="#667883", width=3)
    d.text((pad, 20), "01 · Kobra X 260 × 260 mm · 2 kusy", fill="#223b48", font=font)
    for part, color, subtitle in zip((manifest[0], manifest[2]), ("#567d8e", "#a7b5ba"), ("TĚLO + NÁPIS · 1×", "VÍKO · 1× · lícem dolů")):
        x0, y0 = part["placed_min_xyz_mm"][:2]
        x1, y1 = part["placed_max_xyz_mm"][:2]
        left, top = xy(x0, y1)
        right, bottom = xy(x1, y0)
        d.rounded_rectangle((left, top, right, bottom), radius=8, fill=color, outline="#243e4b", width=3)
        if part["name"].startswith("telo"):
            w, h = 3.2 * scale, 3.2 * scale
            d.rectangle((left + w, top + h, right - w, bottom - h), outline="#deebef", width=4)
        else:
            lx0, ly0 = xy((x0+x1)/2-60, (y0+y1)/2+6)
            lx1, ly1 = xy((x0+x1)/2+60, (y0+y1)/2-6)
            d.rounded_rectangle((lx0, ly0, lx1, ly1), radius=6, fill="#ffffff", outline="#62747b", width=2)
        d.text((left + 14, bottom - 33), subtitle, fill="#ffffff" if part["name"].startswith("telo") else "#243e4b", font=font_small)
    d.text((pad + 8, pad + BED * scale + 16), "Náhled půdorysu vychází z rozmístění ve 3MF; tiskový profil je v nastaveném projektu.", fill="#435861", font=font_small)
    image.save(HERE / "podlozka-01.png")

if __name__ == "__main__":
    generate()
