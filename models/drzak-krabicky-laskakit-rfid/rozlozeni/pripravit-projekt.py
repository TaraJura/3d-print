#!/usr/bin/env python3
"""Create and locally slice the one-part Kobra X 0.4 mm holder project.

Requires an explicit support decision after reviewing the finished CAD/STL.
Does not connect to, send a job to, or control the printer. The PLA settings
are a named uncalibrated draft, not a verified material or strength result.
"""
import argparse
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
GEOMETRY = HERE / "podlozka-01-geometrie.3mf"
LAYOUT_AUDIT = HERE / "overeni-rozlozeni.json"
DELIVERED = HERE / "podlozka-01-nastaveny-projekt.3mf"
AUDIT = HERE / "overeni-rezu.json"


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, log):
    with log.open("w") as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                env={**os.environ, "DISPLAY": ""}, timeout=3600)
    require(result.returncode == 0, f"Slicer exited {result.returncode}; see {log}")


def project_info(path, support_enabled, require_gcode):
    with ZipFile(path) as archive:
        require(archive.testzip() is None, "Corrupt project ZIP")
        names = set(archive.namelist())
        require("Metadata/project_settings.config" in names, "Missing process settings")
        cfg = json.loads(archive.read("Metadata/project_settings.config"))
        require(cfg.get("printer_model") == "Anycubic Kobra X", "Wrong printer")
        require(cfg.get("nozzle_diameter") == ["0.4"], "Wrong nozzle")
        require(cfg.get("enable_support") == ("1" if support_enabled else "0"),
                "Support switch changed during import")
        require(cfg.get("brim_type") == "outer_only" and float(cfg.get("brim_width")) == 5,
                "Missing 5 mm brim")
        model = ET.fromstring(archive.read("3D/3dmodel.model"))
        ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
        copies = len(model.findall("m:build/m:item", ns))
        require(copies == 1, f"Expected one physical object, found {copies}")
        has_gcode = "Metadata/plate_1.gcode" in names
        require(has_gcode == require_gcode, "Unexpected G-code presence")
        info = {"path": str(path), "sha256": sha(path), "physical_parts": copies,
                "has_gcode": has_gcode,
                "profile": {key: cfg.get(key) for key in (
                    "printer_model", "printer_settings_id", "print_settings_id",
                    "filament_settings_id", "filament_type", "nozzle_diameter",
                    "layer_height", "brim_type", "brim_width", "enable_support",
                    "support_type", "support_on_build_plate_only", "wall_loops",
                    "sparse_infill_density", "outer_wall_speed", "inner_wall_speed",
                    "initial_layer_speed", "nozzle_temperature",
                    "nozzle_temperature_initial_layer", "hot_plate_temp")}}
        if has_gcode:
            gcode = archive.read("Metadata/plate_1.gcode")
            require(len(gcode) > 10000, "Implausibly short G-code")
            info["gcode_bytes"] = len(gcode)
            info["gcode_sha256"] = hashlib.sha256(gcode).hexdigest()
            if "Metadata/slice_info.config" in names:
                root = ET.fromstring(archive.read("Metadata/slice_info.config"))
                info["slice_metadata"] = {
                    item.get("key"): item.get("value") for item in root.iter("metadata")
                    if item.get("key") in ("prediction", "weight", "outside", "support_used")}
                info["warnings"] = [item.attrib for item in root.iter("warning")]
                require(info["slice_metadata"].get("outside") == "false", "Slicer reports outside-bed geometry")
        return info


def relabel_delivery(source, destination):
    old_title = "Držák krabičky LaskaKit RFID – podložka 01, pouze geometrie"
    new_title = "Držák krabičky LaskaKit RFID – podložka 01, nastavený a nařezaný projekt"
    old_description = ("Jeden díl 1:1, bez tiskového procesu, filamentu a G-code. "
                       "Nekombinujte s nastavenou variantou téže podložky.")
    new_description = ("Jeden díl 1:1; Kobra X 0,4 mm; návrhový proces PLA. "
                       "Fyzický fit, nosnost, uchycení a tisk neověřeny.")
    with ZipFile(source) as incoming, ZipFile(destination, "w") as outgoing:
        for item in incoming.infolist():
            data = incoming.read(item.filename)
            if item.filename == "3D/3dmodel.model":
                content = data.decode("utf-8")
                require(old_title in content and old_description in content,
                        "Unexpected source 3MF description")
                data = content.replace(old_title, new_title).replace(
                    old_description, new_description).encode("utf-8")
            outgoing.writestr(item, data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supports", choices=("on", "off"), required=True,
                        help="Decision after checking actual overhangs and support removal")
    args = parser.parse_args()
    support_enabled = args.supports == "on"
    require(all(path.is_file() for path in (CLI, MACHINE, PROCESS, FILAMENT,
                                            GEOMETRY, LAYOUT_AUDIT)),
            "Missing slicer, Kobra X profile, geometry 3MF or layout audit")
    layout = json.loads(LAYOUT_AUDIT.read_text())
    require(layout["parts"] == 1 and layout["plate"]["sha256"] == sha(GEOMETRY),
            "Geometry changed after layout verification")
    require(sha(HERE.parent / "stl/drzak.stl") == layout["stl_sha256"],
            "STL changed after layout verification")
    machine = json.loads(MACHINE.read_text())
    require(machine.get("printer_model") == "Anycubic Kobra X" and
            machine.get("nozzle_diameter") == ["0.4"], "Wrong machine profile")

    process = json.loads(PROCESS.read_text())
    process.update({
        "name": "Drzak RFID 0.20 mm PLA navrh Kobra X",
        "print_settings_id": "Drzak RFID 0.20 mm PLA navrh Kobra X",
        "layer_height": "0.2", "wall_loops": "4", "sparse_infill_density": "25%",
        "sparse_infill_pattern": "gyroid", "brim_type": "outer_only",
        "brim_width": "5", "brim_object_gap": "0.1",
        "enable_support": "1" if support_enabled else "0",
        "support_type": "normal(auto)", "support_style": "snug",
        "support_on_build_plate_only": "0", "support_object_xy_distance": "0.35",
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

    with tempfile.TemporaryDirectory(prefix="rfid-holder-next-") as temporary:
        work = Path(temporary)
        configured = work / "configured.3mf"
        command_export = [str(CLI), "--datadir", str(work / "datadir-export"),
                          "--load-settings", str(MACHINE) + ";" + str(CUSTOM_PROCESS),
                          "--load-filaments", str(CUSTOM_FILAMENT),
                          "--arrange", "0", "--orient", "0",
                          "--export-3mf", configured.name, "--outputdir", str(work),
                          str(GEOMETRY)]
        run(command_export, work / "export.log")
        require(configured.is_file(), "Configured project not created")
        configured_info = project_info(configured, support_enabled, False)
        command_slice = [str(CLI), "--datadir", str(work / "datadir-slice"),
                         "--arrange", "0", "--orient", "0", "--slice", "0",
                         "--export-3mf", "sliced.3mf", "--outputdir", str(work),
                         str(configured)]
        run(command_slice, work / "slice.log")
        sliced = work / "sliced.3mf"
        require(sliced.is_file(), "Sliced project not created")
        sliced_info = project_info(sliced, support_enabled, True)
        relabel_delivery(sliced, DELIVERED)
        delivered_info = project_info(DELIVERED, support_enabled, True)
        require(sliced_info["gcode_sha256"] == delivered_info["gcode_sha256"],
                "Final project changed toolpaths")
        audit = {"status": "locally sliced; actual layer/toolpath audit still required",
                 "physical_fit_load_wall_anchors_print": "unverified",
                 "supports_requested": support_enabled,
                 "material": "Alzament PLA Basic draft profile, not calibrated",
                 "machine_profile_sha256": sha(MACHINE),
                 "process_profile_sha256": sha(CUSTOM_PROCESS),
                 "filament_profile_sha256": sha(CUSTOM_FILAMENT),
                 "geometry_sha256": sha(GEOMETRY), "configured": configured_info,
                 "delivered": delivered_info,
                 "export_log_tail": (work / "export.log").read_text(errors="replace")[-2500:],
                 "slice_log_tail": (work / "slice.log").read_text(errors="replace")[-2500:]}
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
    print("RFID_HOLDER_SLICED_PROJECT_OK", delivered_info["gcode_bytes"])


if __name__ == "__main__":
    main()
