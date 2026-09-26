#!/usr/bin/env python3
"""Complete, reproducible geometry plates for the first robot arm prototype.

Reads only ../stl/*.stl and rozlozeni/dily.json. Writes only this directory.
The 3MF files contain geometry and placement, never a printer or filament preset.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import trimesh
from shapely.geometry import MultiPoint, box

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
BED = 260.0
EDGE = 12.0
GAP = 16.0
NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("", NS)


def tag(name: str) -> str:
    return f"{{{NS}}}{name}"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_copies():
    spec = json.loads((HERE / "dily.json").read_text())
    assert spec["units"] == "mm" and spec["scale"] == 1
    assert {p["group"] for p in spec["parts"]} <= {"merka", "sestava"}
    copies = []
    for part in spec["parts"]:
        path = MODEL / "stl" / part["stl"]
        assert path.is_file(), path
        mesh = trimesh.load_mesh(path, process=True)
        assert isinstance(mesh, trimesh.Trimesh) and mesh.is_watertight, path
        assert mesh.is_volume and mesh.volume > 0, path
        rotation = np.array(part["rotation_matrix"], dtype=float)
        assert rotation.shape == (3, 3)
        assert np.allclose(rotation.T @ rotation, np.eye(3)) and np.isclose(np.linalg.det(rotation), 1)
        local = np.asarray(mesh.vertices) @ rotation.T
        local -= local.min(axis=0)
        size = local.max(axis=0)
        assert size[2] <= BED - 2 * EDGE, (part["stl"], size)
        for n in range(1, part["count"] + 1):
            copies.append({"name": f"{path.stem}_{n:02d}", "group": part["group"],
                           "stl": part["stl"], "stl_sha256": sha(path),
                           "rotation_matrix": rotation.tolist(), "local": local.copy(),
                           "faces": np.asarray(mesh.faces).copy(), "size": size.tolist(),
                           "source_volume_mm3": float(mesh.volume),
                           "support": part["support"], "purpose": part["purpose"]})
    return copies


def pack(copies, group):
    selected = [p for p in copies if p["group"] == group]
    assert selected
    # A simple shelf plan is deliberately conservative: rectangular envelopes
    # keep every brim and every real footprint apart, even for concave parts.
    selected.sort(key=lambda p: (-p["size"][0] * p["size"][1], -max(p["size"]), p["name"]))
    plates = [[]]
    x = y = EDGE
    row_h = 0.0
    for p in selected:
        w, h = p["size"][:2]
        if x + w > BED - EDGE + 1e-8:
            x = EDGE
            y += row_h + GAP
            row_h = 0.0
        if y + h > BED - EDGE + 1e-8:
            plates.append([])
            x = y = EDGE
            row_h = 0.0
        assert x + w <= BED - EDGE + 1e-8 and y + h <= BED - EDGE + 1e-8, p["name"]
        p["plate"] = len(plates) - 1
        p["translation_mm"] = [float(x), float(y), 0.0]
        p["world"] = p["local"] + p["translation_mm"]
        p["hull"] = MultiPoint(p["world"][:, :2]).convex_hull
        assert p["hull"].area > 0
        plates[-1].append(p)
        x += w + GAP
        row_h = max(row_h, h)
    for plate in plates:
        for i, p in enumerate(plate):
            assert box(EDGE, EDGE, BED - EDGE, BED - EDGE).covers(p["hull"])
            for q in plate[i + 1:]:
                assert p["hull"].distance(q["hull"]) >= GAP - 1e-6, (p["name"], q["name"])
    return plates


def write_3mf(path: Path, parts):
    model = ET.Element(tag("model"), {"unit": "millimeter", "{http://www.w3.org/XML/1998/namespace}lang": "cs-CZ"})
    ET.SubElement(model, tag("metadata"), {"name": "Title"}).text = path.stem
    ET.SubElement(model, tag("metadata"), {"name": "Description"}).text = "Pouze geometrie a rozmisteni v mm; bez profilu, materialu a podpor."
    resources = ET.SubElement(model, tag("resources"))
    build = ET.SubElement(model, tag("build"))
    for i, p in enumerate(parts, 1):
        obj = ET.SubElement(resources, tag("object"), {"id": str(i), "name": p["name"], "type": "model"})
        mesh = ET.SubElement(obj, tag("mesh"))
        vertices = ET.SubElement(mesh, tag("vertices"))
        triangles = ET.SubElement(mesh, tag("triangles"))
        for xyz in p["world"]:
            ET.SubElement(vertices, tag("vertex"), dict(zip(("x", "y", "z"), (f"{v:.8f}" for v in xyz))))
        for a, b, c in p["faces"]:
            ET.SubElement(triangles, tag("triangle"), {"v1": str(a), "v2": str(b), "v3": str(c)})
        ET.SubElement(build, tag("item"), {"objectid": str(i)})
    content_types = b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    relations = b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    with ZipFile(path, "w", ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", relations)
        z.writestr("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True))


def render(path: Path, parts, title: str):
    fig = plt.figure(figsize=(14, 9), facecolor="white")
    ax = fig.add_axes((0.055, 0.075, 0.59, 0.82))
    ax.set_aspect("equal")
    ax.set(xlim=(0, BED), ylim=(0, BED), xlabel="X [mm]", ylabel="Y [mm]")
    ax.grid(alpha=0.15)
    cmap = plt.get_cmap("tab20")
    for i, p in enumerate(parts, 1):
        coords = np.asarray(p["hull"].exterior.coords)
        ax.add_patch(Polygon(coords, closed=True, color=cmap((i - 1) % 20), alpha=0.65))
        center = p["hull"].centroid
        ax.annotate(str(i), (center.x, center.y), ha="center", va="center",
                    bbox={"facecolor": "white", "edgecolor": "none"}, weight="bold")
    ax.add_patch(Polygon([(EDGE, EDGE), (BED-EDGE, EDGE), (BED-EDGE, BED-EDGE), (EDGE, BED-EDGE)],
                         closed=True, fill=False, linestyle=":", edgecolor="black"))
    fig.text(0.05, 0.955, title + f" · {len(parts)} kusů · Kobra X 260×260 mm · 100 %",
             fontsize=19, weight="bold")
    fig.text(0.68, 0.895, "Číslo / fyzická kopie", fontsize=11, weight="bold")
    for i, p in enumerate(parts, 1):
        fig.text(0.68, 0.865 - (i - 1) * 0.052, f"{i:02d}  {p['name']}", fontsize=10)
    fig.text(0.68, 0.10, "Obrysy ze skutečné STL geometrie;\nčísla značí všechny fyzické kopie.", fontsize=10)
    fig.savefig(path, dpi=155)
    plt.close(fig)


def main():
    all_copies = load_copies()
    outputs = []
    for group in ("merka", "sestava"):
        plates = pack(all_copies, group)
        for number, parts in enumerate(plates, 1):
            stem = f"podlozka-{group}-{number:02d}"
            out = HERE / f"{stem}-geometrie.3mf"
            write_3mf(out, parts)
            render(HERE / f"{stem}.png", parts, "Měrka motoru" if group == "merka" else "Robotická ruka")
            gap = min((p["hull"].distance(q["hull"]) for i,p in enumerate(parts) for q in parts[i+1:]), default=None)
            edge = min(min(p["hull"].bounds[0], p["hull"].bounds[1], BED-p["hull"].bounds[2], BED-p["hull"].bounds[3]) for p in parts)
            outputs.append({"group": group, "plate": number, "geometry_3mf": out.name,
                            "geometry_sha256": sha(out), "preview_png": f"{stem}.png",
                            "count": len(parts), "min_model_gap_mm": gap, "min_model_edge_mm": edge,
                            "items": [{k: p[k] for k in ("name", "stl", "stl_sha256", "purpose", "support", "rotation_matrix", "translation_mm", "size", "source_volume_mm3")} for p in parts]})
    assert sum(o["count"] for o in outputs if o["group"] == "merka") == 1
    assert sum(o["count"] for o in outputs if o["group"] == "sestava") == 12
    result = {"status": "geometry_only_ready", "bed_mm": [BED, BED], "scale": 1,
              "note": "Každou podložku otevřít samostatně jednou. Měrka není montážní díl.", "plates": outputs}
    (HERE / "rozlozeni.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"plates": [(o["geometry_3mf"], o["count"], o["min_model_gap_mm"], o["min_model_edge_mm"]) for o in outputs]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
