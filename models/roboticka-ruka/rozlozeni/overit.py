#!/usr/bin/env python3
"""Audit actual local slicing, imported geometry, support and path clearance."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
from shapely.geometry import MultiPoint

HERE = Path(__file__).resolve().parent
MODEL = HERE.parent
REPO = HERE.parents[2]
CACHE = REPO / ".cache" / "roboticka-ruka-prvni-prototyp"
NUM = re.compile(r"([XYZE])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)")
NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
PRODUCTION = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_from_3mf(text):
    matrix = np.eye(4)
    if text:
        matrix[:3, :] = np.asarray(list(map(float, text.split()))).reshape(4, 3).T
    return matrix


def meshes(path):
    with ZipFile(path) as z:
        roots = {name: ET.fromstring(z.read(name)) for name in z.namelist() if name.endswith(".model")}
        assert all(root.get("unit", "millimeter") == "millimeter" for root in roots.values())
        objects = {(name, obj.get("id")): obj for name,root in roots.items()
                   for obj in root.findall("m:resources/m:object", NS)}
        names = {}
        if "Metadata/model_settings.config" in z.namelist():
            cfg = ET.fromstring(z.read("Metadata/model_settings.config"))
            for obj in cfg.findall("object"):
                node = obj.find('metadata[@key="name"]')
                if node is not None:
                    names[obj.get("id")] = node.get("value")

        def shape(key, transform):
            obj = objects[key]
            mesh = obj.find("m:mesh", NS)
            if mesh is not None:
                vertices = np.asarray([[float(v.get(k)) for k in ("x", "y", "z")] + [1.0]
                                       for v in mesh.findall("m:vertices/m:vertex", NS)])
                faces = np.asarray([[int(f.get(k)) for k in ("v1", "v2", "v3")]
                                    for f in mesh.findall("m:triangles/m:triangle", NS)])
                return (vertices @ transform.T)[:, :3], faces
            vertices, faces, count = [], [], 0
            for component in obj.findall("m:components/m:component", NS):
                file = component.get(PRODUCTION + "path", key[0]).lstrip("/")
                v, f = shape((file, component.get("objectid")),
                             transform @ matrix_from_3mf(component.get("transform")))
                vertices.append(v)
                faces.append(f + count)
                count += len(v)
            return np.concatenate(vertices), np.concatenate(faces)

        result = {}
        for item in roots["3D/3dmodel.model"].findall("m:build/m:item", NS):
            key = ("3D/3dmodel.model", item.get("objectid"))
            name = objects[key].get("name", names.get(key[1], key[1]))
            assert name not in result
            result[name] = shape(key, matrix_from_3mf(item.get("transform")))
        return result


def parse_gcode(gcode: str):
    absolute = True
    e_relative = False
    pos = dict(X=0., Y=0., Z=0., E=0.)
    role = "Custom"
    owner = None
    width = 0.5
    paths = defaultdict(lambda: defaultdict(list))
    max_width = defaultdict(float)
    for line in gcode.splitlines():
        if line.startswith(";TYPE:"):
            role = line.split(":", 1)[1].strip()
        elif line.startswith(";WIDTH:"):
            width = float(line.split(":", 1)[1])
        elif line.startswith("EXCLUDE_OBJECT_START NAME="):
            owner = line.split("NAME=", 1)[1].split("_id_", 1)[0]
        elif line.startswith("EXCLUDE_OBJECT_END"):
            owner = None
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        fields = {k: float(v) for k,v in NUM.findall(code)}
        if command == "G90":
            absolute = True
        elif command == "G91":
            absolute = False
        elif command == "M83":
            e_relative = True
        elif command == "M82":
            e_relative = False
        elif command == "G92":
            pos.update(fields)
        elif command in ("G0", "G1"):
            old = dict(pos)
            for axis in "XYZ":
                if axis in fields:
                    pos[axis] = fields[axis] if absolute else pos[axis] + fields[axis]
            delta_e = fields.get("E", 0) if e_relative else fields.get("E", pos["E"]) - pos["E"]
            if "E" in fields:
                pos["E"] = pos["E"] + fields["E"] if e_relative else fields["E"]
            if delta_e > 0 and (old["X"] != pos["X"] or old["Y"] != pos["Y"]) and role != "Custom":
                assert owner is not None, (line, role)
                paths[owner][role].append([[old[a] for a in "XYZ"], [pos[a] for a in "XYZ"]])
                max_width[owner] = max(max_width[owner], width)
        elif command in ("G2", "G3") and role != "Custom":
            raise AssertionError("Arc interpolation not audited")
    return {name: {role: np.asarray(v) for role,v in roles.items()} for name,roles in paths.items()}, max_width


def object_settings(z):
    root = ET.fromstring(z.read("Metadata/model_settings.config"))
    result = {}
    for obj in root.findall("object"):
        settings = {m.get("key"): m.get("value") for m in obj.findall("metadata")}
        name = settings["name"]
        assert name not in result
        result[name] = settings
    return result


def main():
    manifest = json.loads((HERE / "rozlozeni.json").read_text())
    processes = json.loads((HERE / "overeni-procesu.json").read_text())
    records = []
    total_items = []
    global_mesh_delta = 0.0
    for entry, process in zip(manifest["plates"], processes["plates"]):
        stem = entry["geometry_3mf"].replace("-geometrie.3mf", "")
        assert process["plate"] == stem
        geometry = HERE / entry["geometry_3mf"]
        project = HERE / process["project"]
        sliced = CACHE / stem / "slice/sliced.3mf"
        assert sha(geometry) == entry["geometry_sha256"]
        assert sha(project) == process["sha256"]
        source_meshes = meshes(geometry)
        expected = {p["name"] for p in entry["items"]}
        assert set(source_meshes) == expected and len(expected) == entry["count"]
        for item in entry["items"]:
            source_stl = MODEL / "stl" / item["stl"]
            assert source_stl.is_file() and sha(source_stl) == item["stl_sha256"], (item["name"], source_stl)
        for file in (project, sliced):
            actual = meshes(file)
            assert actual.keys() == source_meshes.keys()
            for name, (vertices, faces) in source_meshes.items():
                v, f = actual[name]
                assert np.array_equal(faces, f), name
                delta = float(np.max(np.abs(vertices - v)))
                assert delta < 2e-5, (name, delta)
                global_mesh_delta = max(global_mesh_delta, delta)
                assert abs(v[:, 2].min()) < 1e-5
        with ZipFile(project) as z:
            assert not any(n.lower().endswith(".gcode") for n in z.namelist())
            project_settings = json.loads(z.read("Metadata/project_settings.config"))
            before = object_settings(z)
        with ZipFile(sliced) as z:
            after = object_settings(z)
            cfg = json.loads(z.read("Metadata/project_settings.config"))
            info_xml = ET.fromstring(z.read("Metadata/slice_info.config"))
            info = {m.get("key"): m.get("value") for m in info_xml.iter("metadata") if m.get("key") in ("prediction", "weight", "outside", "support_used")}
            warnings = [w.attrib for w in info_xml.iter("warning")]
            gcode = z.read("Metadata/plate_1.gcode").decode()
        assert before == after and set(before) == expected
        assert cfg["printer_model"] == "Anycubic Kobra X" and cfg["nozzle_diameter"] == ["0.4"]
        assert cfg["layer_height"] == "0.16" and cfg["brim_width"] == "5"
        assert cfg["filament_settings_id"] == [processes["filament_project"]]
        assert cfg["curr_bed_type"] == "Textured PEI Plate"
        assert all(cfg[key] == ["50"] for key in (
            "hot_plate_temp", "hot_plate_temp_initial_layer",
            "textured_plate_temp", "textured_plate_temp_initial_layer"))
        assert float(cfg["temperature_vitrification"][0]) >= 50
        assert re.search(r"(?m)^M140 S50(?:\s|$)", gcode), stem
        assert not any(w.get("msg") == "bed_temperature_too_high_than_filament" for w in warnings), warnings
        assert info["outside"] == "false"
        setting_changes = {key: [project_settings.get(key), cfg.get(key)] for key in project_settings.keys() | cfg.keys() if project_settings.get(key) != cfg.get(key)}
        assert set(setting_changes) <= {"machine_max_junction_deviation"}, setting_changes
        groups, widths = parse_gcode(gcode)
        assert set(groups) == expected, (stem, set(groups) ^ expected)
        footprints = {}
        role_report = {}
        for part in entry["items"]:
            name = part["name"]
            roles = groups[name]
            assert len(roles.get("Brim", [])) > 0, name
            model_roles = [value for role,value in roles.items() if role != "Brim" and not role.startswith("Support")]
            assert model_roles, name
            model_pts = np.concatenate(model_roles).reshape(-1, 3)
            actual_max_z = float(model_pts[:, 2].max())
            expected_max_z = float(source_meshes[name][0][:, 2].max())
            assert abs(actual_max_z - expected_max_z) < 0.18, (name, actual_max_z, expected_max_z)
            support = [value for role,value in roles.items() if role.startswith("Support")]
            assert bool(support) == (before[name]["enable_support"] == "1"), (name, list(roles), before[name]["enable_support"])
            assert bool(support) == part["support"]
            points = np.concatenate(list(roles.values())).reshape(-1, 3)
            footprint = MultiPoint(points[:, :2]).convex_hull.buffer(widths[name] / 2)
            footprints[name] = footprint
            edge = min(footprint.bounds[0], footprint.bounds[1], 260 - footprint.bounds[2], 260 - footprint.bounds[3])
            assert edge > 1, (name, edge)
            role_report[name] = {"roles": {role: len(value) for role,value in roles.items()},
                                 "model_max_z_mm": actual_max_z, "mesh_max_z_mm": expected_max_z,
                                 "support_bounds_mm": [np.concatenate(support).reshape(-1,3).min(axis=0).tolist(),
                                                       np.concatenate(support).reshape(-1,3).max(axis=0).tolist()] if support else None,
                                 "path_envelope_edge_mm": edge}
            total_items.append(name)
        gaps = [(a, b, footprints[a].distance(footprints[b])) for i,a in enumerate(footprints) for b in list(footprints)[i+1:]]
        nearest = min(gaps, key=lambda row: row[2]) if gaps else None
        if nearest:
            assert nearest[2] > 1.0, nearest
        min_edge = min(min(h.bounds[0], h.bounds[1], 260-h.bounds[2], 260-h.bounds[3]) for h in footprints.values())
        # Actual toolpath projection, including model, brim and generated support.
        fig, axes = plt.subplots(1, 2, figsize=(15, 7), facecolor="white")
        item_number = {item["name"]: i for i, item in enumerate(entry["items"], 1)}
        for name, roles in groups.items():
            h = footprints[name]
            xy = np.asarray(h.exterior.coords)
            axes[0].fill(xy[:, 0], xy[:, 1], alpha=0.35, color=plt.get_cmap("tab20")((item_number[name] - 1) % 20))
            ctr = h.centroid
            axes[0].text(ctr.x, ctr.y, str(item_number[name]), ha="center", va="center", fontsize=8)
            for role, segments in roles.items():
                color = "#e07a1f" if role.startswith("Support") else "#23945d" if role == "Brim" else "#49778c"
                axes[1].add_collection(LineCollection(segments[:, :, :2], colors=color, linewidths=0.3,
                                                      alpha=0.65 if role.startswith("Support") or role == "Brim" else 0.16,
                                                      rasterized=True))
        for ax in axes:
            ax.set(xlim=(0, 260), ylim=(0, 260), xlabel="X [mm]", ylabel="Y [mm]")
            ax.set_aspect("equal")
            ax.grid(alpha=0.14)
        axes[0].set_title("Obálky všech skutečných extruzních drah")
        axes[1].set_title("Model modře · brim zeleně · podpory oranžově")
        fig.suptitle(f"{stem}: řez na Kobra X, 0,4 mm · {len(expected)} kusů")
        fig.tight_layout()
        preview = HERE / f"{stem}-drahy.png"
        fig.savefig(preview, dpi=140)
        plt.close(fig)
        critical_preview = None
        if stem == "podlozka-sestava-01":
            rotor = groups["otocna_zakladna_01"]
            critical = [(0.36, 0.68, "Pod kotoučem a uvnitř kluzného prstence"),
                        (29.96, 30.28, "Pod horní hranou čelistí")]
            fig, axes = plt.subplots(1, 2, figsize=(12, 6), facecolor="white")
            for ax, (support_z, model_z, label) in zip(axes, critical):
                for role, segments in rotor.items():
                    if role == "Brim":
                        continue
                    is_support = role.startswith("Support")
                    z = support_z if is_support else model_z
                    chosen = segments[np.abs(segments[:, 1, 2] - z) < 0.003]
                    if len(chosen):
                        ax.add_collection(LineCollection(chosen[:, :, :2],
                                            colors="#e07a1f" if is_support else "#49778c",
                                            linewidths=0.7))
                ax.set(xlim=(8, 66), ylim=(94, 152), xlabel="X [mm]", ylabel="Y [mm]")
                ax.set_aspect("equal")
                ax.grid(alpha=0.14)
                ax.set_title(f"{label}\nPodpora Z={support_z:.2f} · model Z={model_z:.2f} mm")
            fig.suptitle("Otočná základna: skutečné vrstvy z místního řezu")
            fig.tight_layout()
            critical_preview = "podlozka-sestava-01-kriticke-vrstvy.png"
            fig.savefig(HERE / critical_preview, dpi=155)
            plt.close(fig)
        records.append({"plate": stem, "count": len(expected), "support_used": info["support_used"],
                        "predicted_seconds": int(info["prediction"]), "predicted_weight_g": float(info["weight"]),
                        "effective_textured_bed_temp_c": 50,
                        "gcode_contains_M140_S50": True,
                        "warnings": warnings, "sliced_3mf_sha256": sha(sliced),
                        "gcode_sha256": hashlib.sha256(gcode.encode()).hexdigest(),
                        "max_import_vertex_delta_mm": global_mesh_delta,
                        "minimum_actual_path_gap_mm": float(nearest[2]) if nearest else None,
                        "nearest_objects": list(nearest[:2]) if nearest else None,
                        "minimum_actual_path_edge_mm": min_edge,
                        "object_roles": role_report, "setting_changes_after_slice": setting_changes,
                        "toolpath_preview": preview.name,
                        "critical_layers_preview": critical_preview})
    assert len(total_items) == len(set(total_items)) == 13
    assert sum(r["count"] for r in records) == 13
    assert {r["plate"]: r["count"] for r in records} == {"podlozka-merka-01": 1, "podlozka-sestava-01": 12}
    report = {"status": "pass_with_recorded_profile_warnings", "copies": {"assembly": 12, "motor_gauge": 1},
              "max_import_vertex_delta_mm": global_mesh_delta,
              "limits": "Lokální řez a geometrie nedokazují fyzickou přilnavost, rozměrový fit, odstranitelnost podpor ani zatížitelnost. Startovací/custom G-code není v kontrole obálek.",
              "plates": records}
    (HERE / "overeni.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "plates": [(r["plate"], r["count"], r["support_used"], r["minimum_actual_path_gap_mm"], r["minimum_actual_path_edge_mm"], r["predicted_weight_g"]) for r in records]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
