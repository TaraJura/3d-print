#!/usr/bin/env python3
"""Místní procesní 3MF pro jeden kryt; bez odeslání do tiskárny.

Čte *-geometrie.3mf. Přepíše zdejší dva návrhové profily JSON,
*-nastaveny-projekt.3mf a overeni-rezu.json. Alzament PLA Basic je pouze
dostupný návrhový materiál; vhodnost poblíž potrubí musí být změřena.
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
CUSTOM_PROCESS = HERE / "proces-kobra-x-pla-navrh.json"
CUSTOM_FILAMENT = HERE / "filament-kobra-x-alzament-pla-basic-navrh.json"
GEOMETRY = HERE / "kryt-podlozka-01-geometrie.3mf"
DELIVERED = HERE / "kryt-podlozka-01-nastaveny-projekt.3mf"

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(command, log):
    with log.open("w") as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                env={**os.environ, "DISPLAY": ""}, timeout=1200)
    require(result.returncode == 0, f"Slicer returned {result.returncode}; see {log}")

def project_info(path, require_gcode):
    with ZipFile(path) as archive:
        require(archive.testzip() is None, "Corrupt project ZIP")
        names = set(archive.namelist())
        require("Metadata/project_settings.config" in names, "No process settings")
        cfg = json.loads(archive.read("Metadata/project_settings.config"))
        require(cfg.get("printer_model") == "Anycubic Kobra X", "Wrong printer")
        require(cfg.get("nozzle_diameter") == ["0.4"], "Wrong nozzle")
        require(cfg.get("enable_support") == "0", "Unexpected supports")
        require(cfg.get("brim_type") == "outer_only" and float(cfg.get("brim_width")) == 5,
                "Missing 5 mm brim")
        model = ET.fromstring(archive.read("3D/3dmodel.model"))
        ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
        copies = len(model.findall("m:build/m:item", ns))
        require(copies == 1, f"Wrong number of objects: {copies}")
        has_gcode = "Metadata/plate_1.gcode" in names
        require(has_gcode == require_gcode, "Wrong G-code presence")
        info = {"path": str(path), "sha256": sha(path), "copies": copies,
                "has_gcode": has_gcode,
                "profile": {key: cfg.get(key) for key in (
                    "printer_model", "printer_settings_id", "print_settings_id",
                    "filament_settings_id", "filament_type", "nozzle_diameter",
                    "layer_height", "brim_type", "brim_width", "enable_support",
                    "wall_loops", "sparse_infill_density", "outer_wall_speed",
                    "inner_wall_speed", "initial_layer_speed", "nozzle_temperature",
                    "nozzle_temperature_initial_layer", "hot_plate_temp")}}
        if has_gcode:
            gcode = archive.read("Metadata/plate_1.gcode")
            require(len(gcode) > 10000, "Implausibly short G-code")
            info["gcode_bytes"] = len(gcode)
            info["gcode_lines"] = gcode.count(b"\n")
            info["gcode_sha256"] = hashlib.sha256(gcode).hexdigest()
            if "Metadata/slice_info.config" in names:
                root = ET.fromstring(archive.read("Metadata/slice_info.config"))
                info["slice_metadata"] = {
                    item.get("key"): item.get("value") for item in root.iter("metadata")
                    if item.get("key") in ("prediction", "weight", "outside", "support_used")}
                info["warnings"] = [item.attrib for item in root.iter("warning")]
        return info

def relabel_delivery(source, destination):
    old_title = "Kryt trubky digestoře – podložka 01, pouze geometrie"
    new_title = "Kryt trubky digestoře – podložka 01, nastavený a nařezaný koncept"
    old_description = "1 kus 1:1, bez tiskového procesu, filamentu a G-code. K tisku použijte nastavený projekt."
    new_description = "1 kus 1:1, Kobra X 0,4 mm, návrhový profil PLA. Fit, teplota a fyzický tisk neověřené."
    with ZipFile(source) as incoming, ZipFile(destination, "w") as outgoing:
        for info in incoming.infolist():
            data = incoming.read(info.filename)
            if info.filename == "3D/3dmodel.model":
                model = data.decode("utf-8")
                require(old_title in model and old_description in model,
                        "Unexpected original 3MF metadata")
                data = model.replace(old_title, new_title).replace(old_description, new_description).encode("utf-8")
            outgoing.writestr(info, data)

def main():
    require(all(path.is_file() for path in (CLI, MACHINE, PROCESS, FILAMENT, GEOMETRY)),
            "Slicer, Kobra X profiles or geometry 3MF missing")
    layout = json.loads((HERE / "kontrola-rozlozeni.json").read_text())
    require(layout["physical_pieces"] == 1 and
            layout["plate"]["sha256"] == sha(GEOMETRY), "Geometry manifest drift")
    system_machine = json.loads(MACHINE.read_text())
    require(system_machine.get("printer_model") == "Anycubic Kobra X" and
            system_machine.get("nozzle_diameter") == ["0.4"], "Wrong system profile")

    process = json.loads(PROCESS.read_text())
    process.update({
        "name": "Kryt digestoře 0.20 mm PLA koncept Kobra X",
        "print_settings_id": "Kryt digestoře 0.20 mm PLA koncept Kobra X",
        "layer_height": "0.2", "wall_loops": "4", "sparse_infill_density": "25%",
        "sparse_infill_pattern": "gyroid", "brim_type": "outer_only",
        "brim_width": "5", "brim_object_gap": "0.1", "enable_support": "0",
        "initial_layer_speed": "25", "initial_layer_infill_speed": "40",
        "outer_wall_speed": "50", "inner_wall_speed": "75",
        "top_surface_speed": "50", "sparse_infill_speed": "75",
        "internal_solid_infill_speed": "75", "gap_infill_speed": "50",
        "default_acceleration": "1000", "outer_wall_acceleration": "500",
        "inner_wall_acceleration": "800", "top_surface_acceleration": "500",
    })
    CUSTOM_PROCESS.write_text(json.dumps(process, ensure_ascii=False, indent=2) + "\n")
    filament = json.loads(FILAMENT.read_text())
    filament.update({
        "name": "Alzament PLA Basic návrh @Anycubic Kobra X 0.4 nozzle",
        "filament_settings_id": ["Alzament PLA Basic návrh @Anycubic Kobra X 0.4 nozzle"],
        "nozzle_temperature": ["205"], "nozzle_temperature_initial_layer": ["215"],
        "nozzle_temperature_BRASS": ["205"], "nozzle_temperature_HS": ["205"],
        "nozzle_temperature_initial_layer_BRASS": ["215"],
        "nozzle_temperature_initial_layer_HS": ["215"],
        "hot_plate_temp": ["50"], "hot_plate_temp_initial_layer": ["50"],
        "textured_plate_temp": ["50"], "textured_plate_temp_initial_layer": ["50"],
    })
    CUSTOM_FILAMENT.write_text(json.dumps(filament, ensure_ascii=False, indent=2) + "\n")

    with tempfile.TemporaryDirectory(prefix="kryt-digestore-next-") as temporary:
        work = Path(temporary)
        configured = work / "configured.3mf"
        command1 = [str(CLI), "--datadir", str(work / "datadir-export"),
                    "--load-settings", str(MACHINE)+";"+str(CUSTOM_PROCESS),
                    "--load-filaments", str(CUSTOM_FILAMENT),
                    "--arrange", "0", "--orient", "0",
                    "--export-3mf", configured.name, "--outputdir", str(work), str(GEOMETRY)]
        run(command1, work / "export.log")
        require(configured.is_file(), "Configured project not created")
        configured_info = project_info(configured, False)

        command2 = [str(CLI), "--datadir", str(work / "datadir-slice"),
                    "--arrange", "0", "--orient", "0", "--slice", "0",
                    "--export-3mf", DELIVERED.name, "--outputdir", str(work), str(configured)]
        run(command2, work / "slice.log")
        temporary_delivery = work / DELIVERED.name
        require(temporary_delivery.is_file(), "Sliced project not created")
        temporary_info = project_info(temporary_delivery, True)
        relabel_delivery(temporary_delivery, DELIVERED)
        delivered_info = project_info(DELIVERED, True)
        require(temporary_info["gcode_sha256"] == delivered_info["gcode_sha256"],
                "Copy changed sliced output")
        result = {"status": "locally sliced; print, fit and material suitability unverified",
                  "material_condition": "PLA only a draft profile; measure temperature near operating duct first",
                  "machine_profile_sha256": sha(MACHINE),
                  "process_profile_sha256": sha(CUSTOM_PROCESS),
                  "filament_profile_sha256": sha(CUSTOM_FILAMENT),
                  "configured": configured_info, "delivered": delivered_info,
                  "slice_log_tail": (work / "slice.log").read_text(errors="replace")[-2500:]}
    (HERE / "overeni-rezu.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("DUCT_COVER_SLICED_OK", delivered_info["gcode_bytes"], flush=True)

if __name__ == "__main__":
    main()
