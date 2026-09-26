#!/usr/bin/env python3
"""Build and audit a geometry-only, millimetre 3MF from the three final STL files.

Overwrites only the 3MF and JSON beside this script after source validation.
No slicer, process, filament, network or printer operations are performed.
Uses the Python standard library; dimensions below are a deliberate design check.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile
sys.dont_write_bytecode = True
from schema_modelu import load_parts, MODEL_AUDIT


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "prepazka-575-snap-pracovni-geometrie.3mf"
AUDIT = HERE / "kontrola-podlozky.json"
PROFILE = Path("/home/novakj/.config/AnycubicSlicerNext/system/Anycubic/machine/Anycubic Kobra X 0.4 nozzle.json")
FALLBACK_PROFILE = Path("/usr/share/AnycubicSlicerNext/resources/profiles/Anycubic/machine/Anycubic Kobra X 0.4 nozzle.json")
MODEL_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
TOLERANCE = 0.0001
MESH_DIMENSION_TOLERANCE_MM = 0.001  # Tessellation need not sample the CAD arc apex exactly.


def require(ok, text):
    if not ok:
        raise ValueError(text)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual, expected):
    return all(abs(a - b) <= TOLERANCE for a, b in zip(actual, expected))


def read_stl(path):
    """Read binary or ASCII STL and weld identical export vertex coordinates."""
    raw = path.read_bytes()
    triangle_count = struct.unpack_from("<I", raw, 80)[0] if len(raw) >= 84 else -1
    if len(raw) == 84 + 50 * triangle_count:
        points = []
        for index in range(triangle_count):
            record = struct.unpack_from("<12fH", raw, 84 + 50 * index)
            points.extend(tuple(record[start:start + 3]) for start in (3, 6, 9))
    else:
        points = []
        for line in raw.decode("ascii").splitlines():
            fields = line.strip().split()
            if fields and fields[0].lower() == "vertex":
                require(len(fields) == 4, f"Malformed STL vertex: {path}")
                points.append(tuple(float(value) for value in fields[1:]))
        require(len(points) % 3 == 0, f"Malformed STL triangles: {path}")
    require(bool(points), f"No triangles: {path}")
    vertices, lookup, indices = [], {}, []
    for point in points:
        key = tuple(round(value, 9) for value in point)
        if key not in lookup:
            lookup[key] = len(vertices)
            vertices.append(point)
        indices.append(lookup[key])
    return vertices, [tuple(indices[index:index + 3]) for index in range(0, len(indices), 3)]


def mesh_audit(vertices, triangles):
    minimum = [min(p[axis] for p in vertices) for axis in range(3)]
    maximum = [max(p[axis] for p in vertices) for axis in range(3)]
    edges, directed_edges = Counter(), Counter()
    adjacency = defaultdict(set)
    degenerates = 0
    volume = 0.0
    planar_base_area = 0.0
    downward_facets_above_base = []
    for tri in triangles:
        a, b, c = (vertices[i] for i in tri)
        ab = [b[i] - a[i] for i in range(3)]
        ac = [c[i] - a[i] for i in range(3)]
        cross = (ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0])
        degenerates += len(set(tri)) != 3 or sum(n*n for n in cross) < 1e-20
        if all(abs(point[2]) <= TOLERANCE for point in (a, b, c)):
            planar_base_area += sum(n*n for n in cross) ** 0.5 / 2.0
        norm = sum(n*n for n in cross) ** 0.5
        if norm>1e-10 and cross[2]/norm < -0.5 and min(a[2],b[2],c[2])>TOLERANCE:
            downward_facets_above_base.append({'area_mm2':norm/2,
                'normal_z':cross[2]/norm,'minimum_z_mm':min(a[2],b[2],c[2]),
                'triangle_vertices_mm':[a,b,c]})
        volume += (a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0])) / 6.0
        for left, right in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            edges[tuple(sorted((left, right)))] += 1
            directed_edges[(left, right)] += 1
            adjacency[left].add(right)
            adjacency[right].add(left)
    remaining = set(range(len(vertices)))
    components = 0
    while remaining:
        stack = [remaining.pop()]
        components += 1
        while stack:
            for neighbour in adjacency[stack.pop()]:
                if neighbour in remaining:
                    remaining.remove(neighbour)
                    stack.append(neighbour)
    bad_edges = sum(count != 2 for count in edges.values())
    bad_winding = sum(directed_edges[(a, b)] != 1 or directed_edges[(b, a)] != 1 for a, b in edges)
    duplicate_faces = sum(count - 1 for count in Counter(tuple(sorted(tri)) for tri in triangles).values())
    return {
        "bounds_mm": [minimum, maximum],
        "dimensions_mm": [maximum[i] - minimum[i] for i in range(3)],
        "vertices": len(vertices), "triangles": len(triangles), "edges": len(edges),
        "connected_components": components,
        "nonmanifold_or_boundary_edges": bad_edges,
        "inconsistent_winding_edges": bad_winding,
        "degenerate_triangles": degenerates, "duplicate_faces": duplicate_faces,
        "euler_characteristic": len(vertices) - len(edges) + len(triangles),
        "closed_manifold": bad_edges == 0,
        "consistently_oriented": bad_winding == 0,
        "signed_volume_mm3": volume,
        "planar_base_area_at_z0_mm2": planar_base_area,
        "downward_facets_above_base": downward_facets_above_base,
        "downward_surface_area_above_base_mm2": sum(item['area_mm2'] for item in downward_facets_above_base),
    }


def validate_mesh(audit, filename, expected_dimensions):
    require(close(audit["bounds_mm"][0], (0.0, 0.0, 0.0)), f"Nonlocal STL origin: {filename}")
    require(all(abs(a-b) <= MESH_DIMENSION_TOLERANCE_MM for a, b in zip(audit["dimensions_mm"], expected_dimensions)), f"Unexpected dimensions: {filename}: {audit['dimensions_mm']}")
    require(audit["closed_manifold"] and audit["consistently_oriented"], f"Open/nonmanifold/inconsistent STL: {filename}")
    require(audit["connected_components"] == 1, f"STL is not one connected shell: {filename}")
    require(audit["degenerate_triangles"] == 0 and audit["duplicate_faces"] == 0, f"Degenerate or duplicate STL triangles: {filename}")
    require(audit["signed_volume_mm3"] > 0, f"Nonpositive mesh volume: {filename}")
    require(audit["planar_base_area_at_z0_mm2"] > 1.0, f"No substantial planar base at Z=0: {filename}")


def xml_bytes(element):
    return ET.tostring(element, encoding="utf-8", xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample', action='store_true', help='Separate two-piece joint test plate')
    args = parser.parse_args()
    model_data, records = load_parts(args.sample)
    parts = [(entry['file'], entry['dimensions'], entry['translation']) for entry in records]
    stl_dir = HERE.parent
    output = HERE / 'TEST-575-snap-pracovni-geometrie.3mf' if args.sample else OUTPUT
    audit_path = HERE / 'kontrola-podlozky-TEST.json' if args.sample else AUDIT
    profile_path = PROFILE if PROFILE.is_file() else FALLBACK_PROFILE
    profile = json.loads(profile_path.read_text())
    require(profile["printer_model"] == "Anycubic Kobra X", "Wrong printer profile")
    require(profile["nozzle_diameter"] == ["0.4"], "Wrong nozzle profile")
    plate = [[float(value) for value in pair.split("x")] for pair in profile["printable_area"]]
    require(plate == [[0, 0], [260, 0], [260, 260], [0, 260]], "Printable area changed; layout needs review")
    require(not profile.get("bed_exclude_area"), "New excluded bed region needs review")
    height = float(profile["printable_height"])

    ET.register_namespace("", MODEL_NS)
    model = ET.Element(f"{{{MODEL_NS}}}model", {"unit": "millimeter", "{http://www.w3.org/XML/1998/namespace}lang": "cs-CZ"})
    ET.SubElement(model, "metadata", {"name": "Title"}).text = f"{'TEST zacvaknutí' if args.sample else 'Přepážka575mm se zacvaknutím'} — pracovní geometrie, {len(parts)} díly"
    ET.SubElement(model, "metadata", {"name": "Description"}).text = "Pouze geometrie 1:1. Bez tiskového procesu, filamentu a G-code. Materiál a funkce nejsou ověřené."
    resources = ET.SubElement(model, "resources")
    build = ET.SubElement(model, "build")
    audits = []
    for object_id, (filename, dimensions, translation) in enumerate(parts, 1):
        path = stl_dir / filename
        if records[object_id-1]['sha256']:
            require(sha256(path)==records[object_id-1]['sha256'],f'STL differs from CAD audit hash: {filename}')
        vertices, triangles = read_stl(path)
        audit = mesh_audit(vertices, triangles)
        validate_mesh(audit, filename, dimensions)
        object_element = ET.SubElement(resources, "object", {"id": str(object_id), "type": "model", "name": path.stem})
        mesh = ET.SubElement(object_element, "mesh")
        vertex_element = ET.SubElement(mesh, "vertices")
        triangle_element = ET.SubElement(mesh, "triangles")
        for point in vertices:
            ET.SubElement(vertex_element, "vertex", {axis: format(value, ".12g") for axis, value in zip("xyz", point)})
        for triangle in triangles:
            ET.SubElement(triangle_element, "triangle", {f"v{i+1}": str(value) for i, value in enumerate(triangle)})
        transform = (1, 0, 0, 0, 1, 0, 0, 0, 1, *translation)
        ET.SubElement(build, "item", {"objectid": str(object_id), "transform": " ".join(map(str, transform))})
        placed_bounds = [[audit["bounds_mm"][j][i] + translation[i] for i in range(3)] for j in range(2)]
        require(all(placed_bounds[0][axis] >= 0 and placed_bounds[1][axis] <= limit for axis, limit in enumerate((260, 260, height))), f"Part outside plate: {filename}")
        audit.update({"stl": str(path.relative_to(HERE.parent)), "stl_sha256": sha256(path), "object_id": object_id,
                      "nominal_cad_dimensions_mm": list(dimensions),
                      "mesh_dimension_tolerance_mm": MESH_DIMENSION_TOLERANCE_MM,
                      "mesh_minus_nominal_dimensions_mm": [a-b for a, b in zip(audit["dimensions_mm"], dimensions)],
                      "retention_audit_regions": records[object_id-1]['retention_regions'],
                      "translation_mm": list(translation), "rotation_degrees": [0, 0, 0], "scale": [1, 1, 1],
                      "placed_bounds_mm": placed_bounds, "inside_printable_volume": True,
                      "flat_base_on_z0": abs(placed_bounds[0][2]) <= TOLERANCE})
        audits.append(audit)

    gaps = []
    for i in range(len(audits)):
        for j in range(i + 1, len(audits)):
            a, b = audits[i]["placed_bounds_mm"], audits[j]["placed_bounds_mm"]
            dx = max(0, a[0][0] - b[1][0], b[0][0] - a[1][0])
            dy = max(0, a[0][1] - b[1][1], b[0][1] - a[1][1])
            distance = (dx*dx + dy*dy) ** 0.5
            require(distance > 0, f"Overlapping XY bounding boxes: {i+1}, {j+1}")
            gaps.append({"objects": [i+1, j+1], "xy_bounding_box_gap_mm": distance})

    content_types = ET.Element("Types", {"xmlns": "http://schemas.openxmlformats.org/package/2006/content-types"})
    ET.SubElement(content_types, "Default", {"Extension": "rels", "ContentType": "application/vnd.openxmlformats-package.relationships+xml"})
    ET.SubElement(content_types, "Default", {"Extension": "model", "ContentType": "application/vnd.ms-package.3dmanufacturing-3dmodel+xml"})
    relationships = ET.Element("Relationships", {"xmlns": "http://schemas.openxmlformats.org/package/2006/relationships"})
    ET.SubElement(relationships, "Relationship", {"Target": "/3D/3dmodel.model", "Id": "rel0", "Type": "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"})
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", xml_bytes(content_types))
        archive.writestr("_rels/.rels", xml_bytes(relationships))
        archive.writestr("3D/3dmodel.model", xml_bytes(model))

    # Reopen the written ZIP/XML and compare every vertex, triangle and transform.
    ns = {"m": MODEL_NS}
    with zipfile.ZipFile(output) as archive:
        require(archive.testzip() is None, "Corrupt ZIP")
        require(set(archive.namelist()) == {"[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"}, "Unexpected nongeometry content")
        loaded = ET.fromstring(archive.read("3D/3dmodel.model"))
    require(loaded.get("unit") == "millimeter", "Wrong 3MF unit")
    objects = loaded.findall("m:resources/m:object", ns)
    items = loaded.findall("m:build/m:item", ns)
    require(len(objects) == len(items) == len(parts), "Wrong object or instance count")
    for object_element, item, (filename, dimensions, translation) in zip(objects, items, parts):
        vertices = [tuple(float(vertex.get(axis)) for axis in "xyz") for vertex in object_element.findall("m:mesh/m:vertices/m:vertex", ns)]
        triangles = [tuple(int(triangle.get(f"v{i}")) for i in (1, 2, 3)) for triangle in object_element.findall("m:mesh/m:triangles/m:triangle", ns)]
        original_vertices, original_triangles = read_stl(stl_dir / filename)
        require(len(vertices) == len(original_vertices) and all(close(a, b) for a, b in zip(vertices, original_vertices)), "3MF vertices differ from STL")
        require(triangles == original_triangles, "3MF triangles differ from STL")
        expected_transform = [1, 0, 0, 0, 1, 0, 0, 0, 1, *translation]
        require(close([float(value) for value in item.get("transform").split()], expected_transform), "3MF placement changed")
        require(item.get("objectid") == object_element.get("id"), "Wrong object reference")
        validate_mesh(mesh_audit(vertices, triangles), filename, dimensions)

    plate_minimum = [min(a["placed_bounds_mm"][0][axis] for a in audits) for axis in range(3)]
    plate_maximum = [max(a["placed_bounds_mm"][1][axis] for a in audits) for axis in range(3)]
    edge_margins = [plate_minimum[0], 260 - plate_maximum[0], plate_minimum[1], 260 - plate_maximum[1]]
    result = {
        "status": "geometry-only working alternative; not sliced, not print-ready, no physical validation",
        "model_revision": "revize-03-575-zacvak",
        "cad_audit_sha256": sha256(MODEL_AUDIT),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "printer_profile_evidence": {"path": str(profile_path), "sha256": sha256(profile_path), "name": profile["name"],
                                     "printable_area_mm": plate, "printable_height_mm": height, "nozzle_mm": 0.4},
        "output": output.name, "output_sha256": sha256(output), "unit": "millimeter", "plates": 1,
        "physical_parts": len(parts), "object_instances": len(parts), "separate_joint_test": args.sample,
        "contains_process_or_filament": False, "contains_gcode": False,
        "scale_1_to_1": True, "all_flat_bases_at_z0": True,
        "plate_contents_bounds_mm": [plate_minimum, plate_maximum],
        "plate_edge_margins_mm_left_right_front_back": edge_margins,
        "minimum_plate_edge_margin_mm": min(edge_margins),
        "pairwise_gaps": gaps,
        "minimum_xy_bounding_box_gap_mm": min(gap["xy_bounding_box_gap_mm"] for gap in gaps),
        "parts": audits,
        "reopened_zip_xml_meshes_and_transforms_verified": True,
        "limitations": ["Slicer import and toolpaths have not been checked for this geometry-only file.", "Alzament TPU95A is specified; physical calibration and snap fit remain unverified.",
                        "Mesh closure does not establish watertight physical printing or joint sealing.",
                        "The layout reserves no specific brim or support envelope because no print process is selected.",
                        "No physical fit, adhesion, flexibility or water test has been performed."],
    }
    audit_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"3mf": str(output), "audit": str(audit_path), "parts": len(parts),
                      "minimum_gap_mm": result["minimum_xy_bounding_box_gap_mm"], "edge_margin_mm": min(edge_margins)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
