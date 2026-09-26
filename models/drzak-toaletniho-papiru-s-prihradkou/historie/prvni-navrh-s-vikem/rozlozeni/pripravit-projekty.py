#!/usr/bin/env python3
"""Z geometrických 3MF připraví a rozřeže dva úplné projekty Next pro Kobra X.

Pouze místní CLI, systémové profily a vlastní dočasný datadir v /tmp.
Nepřipojuje se k tiskárně. Přepisuje jen zdejší procesní JSON, konečné
*-nastaveny-projekt.3mf a overeni-rezu.json. Spusťte po vytvor-podlozky.py.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
CLI = Path("/usr/bin/AnycubicSlicerNext")
PROFILES = Path("/usr/share/AnycubicSlicerNext/resources/profiles/Anycubic")
MACHINE = PROFILES / "machine/Anycubic Kobra X 0.4 nozzle.json"
PROCESS = PROFILES / "process/0.20mm Standard @Anycubic Kobra X 0.4 nozzle.json"
FILAMENT = PROFILES / "filament/Anycubic PLA @Anycubic Kobra X 0.4 nozzle.json"
CUSTOM = HERE / "proces-kobra-x-pla-navrh.json"
CUSTOM_FILAMENT = HERE / "filament-kobra-x-alzament-pla-basic-navrh.json"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def run(cmd, log):
    with log.open("w") as stream:
        result = subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT,
                                env={**os.environ, "DISPLAY": ""}, timeout=1200)
    require(result.returncode == 0, f"Slicer returned {result.returncode}; see {log}")

def config_from_zip(z, name):
    return json.loads(z.read("Metadata/"+name).decode())

def relabel_delivered(source, target, plate):
    """Opraví převzatý název 'pouze geometrie' ve výsledném projektu 3MF."""
    old_title = f"Držák s přihrádkou – podložka {plate:02d}, pouze geometrie"
    new_title = f"Držák s přihrádkou – podložka {plate:02d}, nastavený a nařezaný projekt"
    old_description = "1:1, bez tiskového procesu, filamentu a G-code. K tisku použijte nastavený projekt."
    new_description = "1:1, Kobra X 0,4 mm, návrhový profil PLA, místně nařezáno; fyzický tisk neověřen."
    with ZipFile(source) as incoming, ZipFile(target, "w") as outgoing:
        for info in incoming.infolist():
            data = incoming.read(info.filename)
            if info.filename == "3D/3dmodel.model":
                text = data.decode("utf-8")
                require(old_title in text and old_description in text,
                        "Unexpected original 3MF metadata")
                data = text.replace(old_title,new_title).replace(old_description,new_description).encode("utf-8")
            outgoing.writestr(info,data)

def read_project(path, expected_copies, require_gcode):
    with ZipFile(path) as z:
        require(z.testzip() is None, f"Bad ZIP: {path}")
        names = set(z.namelist())
        require("Metadata/project_settings.config" in names, "No process settings")
        cfg = config_from_zip(z, "project_settings.config")
        require(cfg.get("printer_model") == "Anycubic Kobra X", "Wrong printer model")
        require(cfg.get("nozzle_diameter") == ["0.4"], "Wrong nozzle")
        require(cfg.get("enable_support") == "0", "Unexpected global supports")
        require(cfg.get("brim_type") == "outer_only" and float(cfg.get("brim_width")) == 5,
                "Missing explicit brim")
        require(cfg.get("wall_loops") == "4" and cfg.get("sparse_infill_density") == "25%",
                "Wrong strength settings")
        model = ET.fromstring(z.read("3D/3dmodel.model"))
        ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
        copies = len(model.findall("m:build/m:item", ns))
        require(copies == expected_copies, f"Wrong copies in {path}: {copies}")
        has_gcode = "Metadata/plate_1.gcode" in names
        require(has_gcode == require_gcode, f"Wrong G-code presence: {path}")
        info = {"path": str(path), "sha256": sha(path), "copies": copies,
                "profile": {k: cfg.get(k) for k in (
                    "printer_model", "printer_settings_id", "print_settings_id",
                    "filament_settings_id", "filament_type", "nozzle_diameter",
                    "layer_height", "brim_type", "brim_width", "enable_support",
                    "wall_loops", "sparse_infill_density", "outer_wall_speed",
                    "inner_wall_speed", "initial_layer_speed", "nozzle_temperature",
                    "nozzle_temperature_initial_layer", "hot_plate_temp")},
                "has_gcode": has_gcode}
        if has_gcode:
            gcode = z.read("Metadata/plate_1.gcode")
            info["gcode_sha256"] = hashlib.sha256(gcode).hexdigest()
            info["gcode_bytes"] = len(gcode)
            info["gcode_lines"] = gcode.count(b"\n")
            require(len(gcode) > 10000, "Implausibly short sliced output")
            if "Metadata/slice_info.config" in names:
                root = ET.fromstring(z.read("Metadata/slice_info.config"))
                info["slice_metadata"] = {m.get("key"): m.get("value") for m in root.iter("metadata")
                                          if m.get("key") in ("prediction", "weight", "outside", "support_used")}
                info["warnings"] = [w.attrib for w in root.iter("warning")]
        return info

def main():
    require(CLI.is_file() and MACHINE.is_file() and PROCESS.is_file() and FILAMENT.is_file(),
            "Anycubic Slicer Next or Kobra X system profiles missing")
    machine = json.loads(MACHINE.read_text())
    require(machine.get("printer_model") == "Anycubic Kobra X" and
            machine.get("nozzle_diameter") == ["0.4"], "Wrong system machine profile")
    layout = json.loads((HERE / "kontrola-rozlozeni.json").read_text())
    require(layout["physical_pieces"] == 6, "Unexpected inventory")
    process = json.loads(PROCESS.read_text())
    process.update({
        "name": "Drzak s prihradkou 0.20 mm PLA navrh Kobra X",
        "print_settings_id": "Drzak s prihradkou 0.20 mm PLA navrh Kobra X",
        "layer_height": "0.2", "wall_loops": "4", "sparse_infill_density": "25%",
        "sparse_infill_pattern": "gyroid", "brim_type": "outer_only",
        "brim_width": "5", "brim_object_gap": "0.1", "enable_support": "0",
        "initial_layer_speed": "25", "initial_layer_infill_speed": "40",
        "outer_wall_speed": "70", "inner_wall_speed": "100",
        "top_surface_speed": "70", "sparse_infill_speed": "100",
        "internal_solid_infill_speed": "100", "gap_infill_speed": "70",
        "default_acceleration": "1000", "outer_wall_acceleration": "500",
        "inner_wall_acceleration": "800", "top_surface_acceleration": "500",
    })
    CUSTOM.write_text(json.dumps(process, ensure_ascii=False, indent=2) + "\n")
    filament = json.loads(FILAMENT.read_text())
    filament.update({
        "name": "Alzament PLA Basic navrh @Anycubic Kobra X 0.4 nozzle",
        "filament_settings_id": ["Alzament PLA Basic navrh @Anycubic Kobra X 0.4 nozzle"],
        "nozzle_temperature": ["205"], "nozzle_temperature_initial_layer": ["215"],
        "nozzle_temperature_BRASS": ["205"], "nozzle_temperature_HS": ["205"],
        "nozzle_temperature_initial_layer_BRASS": ["215"],
        "nozzle_temperature_initial_layer_HS": ["215"],
        "hot_plate_temp": ["50"], "hot_plate_temp_initial_layer": ["50"],
        "textured_plate_temp": ["50"], "textured_plate_temp_initial_layer": ["50"],
    })
    CUSTOM_FILAMENT.write_text(json.dumps(filament, ensure_ascii=False, indent=2) + "\n")
    result = {"status": "local sliced projects; physical print and fit not tested",
              "machine_profile": {"path": str(MACHINE), "sha256": sha(MACHINE)},
              "filament_profile": {"path": CUSTOM_FILAMENT.name, "sha256": sha(CUSTOM_FILAMENT),
                                   "based_on_system_profile_sha256": sha(FILAMENT),
                                   "note": "Design starting point within Alzament PLA Basic supplier ranges; not physically calibrated"},
              "custom_process": {"path": CUSTOM.name, "sha256": sha(CUSTOM)},
              "plates": []}
    with tempfile.TemporaryDirectory(prefix="drzak-next-") as temp:
        base = Path(temp)
        for plate in (1, 2):
            geometry = HERE / f"drzak-podlozka-{plate:02d}-geometrie.3mf"
            manifest = layout["plates"][plate-1]
            require(sha(geometry) == manifest["geometry_sha256"], "Layout/geometry drift")
            work = base / f"plate-{plate:02d}"
            work.mkdir()
            exported = work / "configured.3mf"
            cmd1 = [str(CLI), "--datadir", str(work / "datadir-export"),
                    "--load-settings", str(MACHINE)+";"+str(CUSTOM),
                    "--load-filaments", str(CUSTOM_FILAMENT), "--arrange", "0", "--orient", "0",
                    "--export-3mf", exported.name, "--outputdir", str(work), str(geometry)]
            run(cmd1, work / "export.log")
            require(exported.is_file(), "No configured project")
            configured_info = read_project(exported, manifest["copies"], False)
            delivered = HERE / f"drzak-podlozka-{plate:02d}-nastaveny-projekt.3mf"
            sliced_temp = work / delivered.name
            cmd2 = [str(CLI), "--datadir", str(work / "datadir-slice"),
                    "--arrange", "0", "--orient", "0", "--slice", "0",
                    "--export-3mf", delivered.name, "--outputdir", str(work), str(exported)]
            run(cmd2, work / "slice.log")
            require(sliced_temp.is_file(), "No sliced project")
            relabel_delivered(sliced_temp,delivered,plate)
            sliced_info = read_project(delivered, manifest["copies"], True)
            result["plates"].append({"number": plate, "copies": manifest["copies"],
                                     "geometry_sha256": sha(geometry),
                                     "configured": configured_info,
                                     "delivered": sliced_info,
                                     "slice_log_tail": (work / "slice.log").read_text(errors="replace")[-2500:]})
            print(f"SLICED_PLATE_{plate:02d} copies={manifest['copies']} bytes={sliced_info['gcode_bytes']}", flush=True)
    (HERE / "overeni-rezu.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("SLICED_PROJECTS_OK", flush=True)

if __name__ == "__main__":
    main()
