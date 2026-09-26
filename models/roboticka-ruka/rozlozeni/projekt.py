#!/usr/bin/env python3
"""Wrap exact geometry plates in isolated Anycubic Slicer Next projects and slice.

No printer connection; transient G-code and slicer logs remain in repo .cache.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CACHE = REPO / ".cache" / "roboticka-ruka-prvni-prototyp"
SLICER = Path("/usr/bin/AnycubicSlicerNext")
SYSTEM = Path("/usr/share/AnycubicSlicerNext/resources/profiles/Anycubic")
MACHINE = SYSTEM / "machine/Anycubic Kobra X 0.4 nozzle.json"
PROCESS = SYSTEM / "process/0.16mm Standard @Anycubic Kobra X 0.4 nozzle.json"
FILAMENT = SYSTEM / "filament/Anycubic PLA @Anycubic Kobra X 0.4 nozzle.json"
FILAMENT_NAME = "PROTOTYP Alzament PLA Basic Kobra X 0.4 - podlozka 50C - nekalibrovano"


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args: list[str], log: Path, timeout=900):
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w") as output:
        result = subprocess.run(args, stdout=output, stderr=subprocess.STDOUT,
                                env=dict(os.environ, DISPLAY=""), timeout=timeout)
    assert result.returncode == 0, f"Next skončil s kódem {result.returncode}; podrobnosti: {log}"


def process_config(path: Path):
    data = json.loads(PROCESS.read_text())
    data.update({
        "name": "Roboticka ruka - prvni prototyp - Kobra X PLA 0.16",
        "print_settings_id": "Roboticka ruka - prvni prototyp - Kobra X PLA 0.16",
        "layer_height": "0.16", "initial_layer_print_height": "0.20",
        "wall_loops": "4", "sparse_infill_density": "20%", "sparse_infill_pattern": "grid",
        "outer_wall_speed": "60", "inner_wall_speed": "90",
        "sparse_infill_speed": "90", "internal_solid_infill_speed": "80",
        "top_surface_speed": "50", "gap_infill_speed": "60",
        "small_perimeter_speed": "30", "initial_layer_speed": "20",
        "initial_layer_infill_speed": "25", "bridge_speed": "25",
        "brim_type": "outer_only", "brim_width": "5", "brim_object_gap": "0.1",
        "enable_prime_tower": "0", "enable_support": "0",
        "support_type": "normal(auto)", "support_style": "snug",
        "support_on_build_plate_only": "0", "support_remove_small_overhang": "0",
        "support_threshold_angle": "45", "support_interface_top_layers": "3",
        "support_top_z_distance": "0.16", "support_bottom_z_distance": "0.16",
        "support_object_xy_distance": "0.35", "print_sequence": "by layer",
        "gcode_label_objects": "1",
    })
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return data


def filament_config(path: Path):
    """Local derivative of the installed Kobra X PLA profile; no user preset changed."""
    data = json.loads(FILAMENT.read_text())
    data.update({
        "from": "user", "is_custom_defined": "1",
        "name": FILAMENT_NAME, "setting_id": FILAMENT_NAME,
        "filament_settings_id": [FILAMENT_NAME],
        "filament_id": "PROTOTYP-Alzament-PLA-Basic-Kobra-X-50C",
        "filament_vendor": ["Alzament"],
        "hot_plate_temp": ["50"], "hot_plate_temp_initial_layer": ["50"],
        "textured_plate_temp": ["50"], "textured_plate_temp_initial_layer": ["50"],
        "filament_notes": ["Nekalibrovany pocatecni pokus: pouze podlozka 50 C; ostatni hodnoty jsou z Anycubic PLA pro Kobra X 0.4."],
    })
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return data


def main():
    manifest = json.loads((HERE / "rozlozeni.json").read_text())
    assert manifest["status"] == "geometry_only_ready" and manifest["scale"] == 1
    assert SLICER.is_file() and all(p.is_file() for p in (MACHINE, PROCESS, FILAMENT))
    CACHE.mkdir(parents=True, exist_ok=True)
    cfg = CACHE / "process.json"
    process_config(cfg)
    filament_path = CACHE / "filament-pla-basic-50c.json"
    filament = filament_config(filament_path)
    records = []
    for plate in manifest["plates"]:
        source = HERE / plate["geometry_3mf"]
        assert sha(source) == plate["geometry_sha256"]
        stem = source.stem.replace("-geometrie", "")
        job = CACHE / stem
        job.mkdir(parents=True, exist_ok=True)
        exported = job / "export.3mf"
        project = HERE / f"{stem}-nastaveny-projekt.3mf"
        settings = str(MACHINE) + ";" + str(cfg)
        export_cmd = [str(SLICER), "--datadir", str(job / "export-profile"),
                      "--arrange", "0", "--orient", "0", "--debug", "3",
                      "--load-settings", settings, "--load-filaments", str(filament_path),
                      "--export-3mf", "export.3mf", "--outputdir", str(job), str(source)]
        run(export_cmd, job / "export.log")
        assert exported.is_file()
        with ZipFile(exported) as z:
            files = {name: z.read(name) for name in z.namelist()}
        assert "Metadata/model_settings.config" in files
        root = ET.fromstring(files["Metadata/model_settings.config"])
        overrides = {}
        expected = {p["name"]: p for p in plate["items"]}
        for obj in root.findall("object"):
            name_node = obj.find('metadata[@key="name"]')
            assert name_node is not None
            name = name_node.get("value")
            assert name in expected and name not in overrides, name
            support = "1" if expected[name]["support"] else "0"
            values = {"enable_support": support}
            if name.startswith("cep_kloubu_"):
                values.update({"wall_loops": "4", "sparse_infill_density": "100%"})
            for key, value in values.items():
                ET.SubElement(obj, "metadata", key=key, value=value)
            overrides[name] = values
        assert overrides.keys() == expected.keys(), (list(overrides), list(expected))
        files["Metadata/model_settings.config"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        assert not any(n.lower().endswith(".gcode") for n in files)
        with ZipFile(project, "w", ZIP_DEFLATED) as z:
            for name, data in files.items():
                z.writestr(name, data)
        slicedir = job / "slice"
        slicedir.mkdir(exist_ok=True)
        slice_cmd = [str(SLICER), "--datadir", str(job / "slice-profile"),
                     "--arrange", "0", "--orient", "0", "--debug", "3",
                     "--slice", "0", "--export-3mf", "sliced.3mf",
                     "--outputdir", str(slicedir), str(project)]
        run(slice_cmd, job / "slice.log")
        assert (slicedir / "sliced.3mf").is_file()
        gcode = list(slicedir.glob("*.gcode"))
        assert len(gcode) == 1 and gcode[0].stat().st_size > 0, gcode
        records.append({"plate": stem, "project": project.name, "sha256": sha(project),
                        "source_geometry_sha256": sha(source), "objects": len(overrides),
                        "object_support": {n: bool(int(v["enable_support"])) for n,v in overrides.items()},
                        "slicer_exit_codes": [0, 0], "cache_slice_3mf": str(slicedir / "sliced.3mf"),
                        "cache_gcode": str(gcode[0]), "gcode_size_bytes": gcode[0].stat().st_size,
                        "warnings_log": str(job / "slice.log")})
    report = {"status": "sliced", "machine": json.loads(MACHINE.read_text())["name"],
              "process_base": json.loads(PROCESS.read_text())["name"],
              "filament_base": json.loads(FILAMENT.read_text())["name"],
              "filament_base_sha256": sha(FILAMENT),
              "filament_project": filament["name"],
              "filament_project_overrides": {k:filament[k] for k in (
                  "hot_plate_temp", "hot_plate_temp_initial_layer", "textured_plate_temp", "textured_plate_temp_initial_layer")},
              "filament_status": "Pokusný odvozený profil: podložka explicitně 50 °C v první i dalších vrstvách, ostatní hodnoty vycházejí ze systémového Anycubic PLA pro Kobra X. Fyzická cívka a kalibrace nebyly ověřeny.",
              "process_overrides": {k:v for k,v in json.loads(cfg.read_text()).items() if k in (
                  "layer_height", "initial_layer_print_height", "wall_loops", "sparse_infill_density",
                  "outer_wall_speed", "inner_wall_speed", "brim_type", "brim_width", "enable_support")},
              "plates": records}
    (HERE / "overeni-procesu.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "plates": [(r["project"], r["objects"], r["gcode_size_bytes"]) for r in records]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
