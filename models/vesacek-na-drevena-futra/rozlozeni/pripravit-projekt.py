#!/usr/bin/env python3
"""Nastavená a nařezaná podložka Kobra X pro jediný věšáček.

Čte podlozka-01-geometrie.3mf, zápis je omezen na tuto složku.
Jen místní Anycubic Slicer Next CLI; nikdy neodesílá data do tiskárny.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
CLI = Path("/usr/bin/AnycubicSlicerNext")
PROFILES = Path("/usr/share/AnycubicSlicerNext/resources/profiles/Anycubic")
MACHINE = PROFILES / "machine/Anycubic Kobra X 0.4 nozzle.json"
PROCESS = PROFILES / "process/0.20mm Standard @Anycubic Kobra X 0.4 nozzle.json"
FILAMENT = PROFILES / "filament/Anycubic PLA @Anycubic Kobra X 0.4 nozzle.json"
CUSTOM_PROCESS = HERE / "proces-kobra-x-pla-navrh.json"
CUSTOM_FILAMENT = HERE / "filament-kobra-x-pla-navrh.json"
GEOMETRY = HERE / "podlozka-01-geometrie.3mf"
DELIVERED = HERE / "podlozka-01-kobra-x-pla-projekt.3mf"
REPORT = HERE / "kontrola-rezani.json"


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, logfile):
    logfile.parent.mkdir(parents=True, exist_ok=True)
    with logfile.open("w", encoding="utf-8") as output:
        result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT,
                                env={**os.environ, "DISPLAY": ""}, timeout=1800)
    check(result.returncode == 0, "Slicer exit %s; see %s" % (result.returncode, logfile))


def inspect_project(path, require_gcode):
    with ZipFile(path) as archive:
        check(archive.testzip() is None, "Corrupt 3MF ZIP")
        names = set(archive.namelist())
        check("Metadata/project_settings.config" in names, "No process metadata")
        settings = json.loads(archive.read("Metadata/project_settings.config"))
        expected = {
            "printer_model": "Anycubic Kobra X", "nozzle_diameter": ["0.4"],
            "layer_height": "0.2", "wall_loops": "5", "sparse_infill_density": "100%",
            "enable_support": "0", "brim_type": "outer_only", "brim_width": "5",
        }
        for key, value in expected.items():
            check(settings.get(key) == value,
                  "Unexpected %s = %r (expected %r)" % (key, settings.get(key), value))
        root = ET.fromstring(archive.read("3D/3dmodel.model"))
        ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
        check(root.get("unit") == "millimeter", "Wrong 3MF units")
        check(len(root.findall("m:build/m:item", ns)) == 1, "Wrong physical copy count")
        has_gcode = "Metadata/plate_1.gcode" in names
        check(has_gcode == require_gcode, "Wrong G-code presence")
        info = {
            "sha256": digest(path), "physical_pieces": 1, "has_gcode": has_gcode,
            "settings": {key: settings.get(key) for key in (
                "printer_model", "printer_settings_id", "print_settings_id",
                "filament_settings_id", "filament_type", "nozzle_diameter",
                "layer_height", "wall_loops", "sparse_infill_density",
                "sparse_infill_pattern", "enable_support", "brim_type", "brim_width",
                "nozzle_temperature", "nozzle_temperature_initial_layer",
                "textured_plate_temp", "textured_plate_temp_initial_layer")}}
        if has_gcode:
            gcode = archive.read("Metadata/plate_1.gcode")
            check(len(gcode) > 10_000, "Implausibly short G-code")
            info["gcode_sha256"] = hashlib.sha256(gcode).hexdigest()
            info["gcode_bytes"] = len(gcode)
            decoded_gcode = gcode.decode("utf-8", errors="replace")
            info["layers_and_roles"] = inspect_gcode(decoded_gcode)
            info["interlayer_contact"] = inspect_interlayer_contact(decoded_gcode)
            if "Metadata/slice_info.config" in names:
                tree = ET.fromstring(archive.read("Metadata/slice_info.config"))
                info["slice_metadata"] = {
                    node.get("key"): node.get("value") for node in tree.iter("metadata")
                    if node.get("key") in ("prediction", "weight", "outside", "support_used")}
                info["warnings"] = [node.attrib for node in tree.iter("warning")]
                check(info["slice_metadata"].get("outside") in ("false", None),
                      "Part outside print area")
                check(info["slice_metadata"].get("support_used") in ("false", None),
                      "Unexpected generated support")
        return info


def inspect_gcode(gcode):
    lines = gcode.splitlines()
    layer = 0
    layers_with_extrusion = set()
    roles = set()
    active_role = ""
    e = 0.0
    relative_e = False
    x = y = 0.0
    xy_min = [float("inf"), float("inf")]
    xy_max = [float("-inf"), float("-inf")]
    first_layer_roles = set()
    for line in lines:
        if line.startswith(";LAYER_CHANGE"):
            layer += 1
        elif line.startswith(";TYPE:"):
            active_role = line[6:].strip()
            roles.add(active_role)
            if layer == 1:
                first_layer_roles.add(active_role)
        code = line.split(";", 1)[0].strip()
        if code == "M83":
            relative_e = True
        elif code == "M82":
            relative_e = False
        elif code.startswith("G92"):
            match = re.search(r"(?:^|\s)E([+-]?\d*\.?\d+)", code)
            if match:
                e = float(match.group(1))
        if not code.startswith(("G0 ", "G1 ")):
            continue
        args = {key: float(value) for key, value in re.findall(
            r"\b([XYE])([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)", code)}
        next_x, next_y = args.get("X", x), args.get("Y", y)
        next_e = args.get("E", e)
        extruded = "E" in args and (next_e > 0 if relative_e else next_e > e)
        if layer > 0 and extruded and (next_x != x or next_y != y):
            layers_with_extrusion.add(layer)
            for axis, pair in enumerate(((x, next_x), (y, next_y))):
                xy_min[axis] = min(xy_min[axis], *pair)
                xy_max[axis] = max(xy_max[axis], *pair)
        x, y = next_x, next_y
        if "E" in args:
            e = e + next_e if relative_e else next_e
    check(layer > 10 and len(layers_with_extrusion) == layer,
          "Missing extrusion on one or more layers: %s/%s" % (len(layers_with_extrusion), layer))
    check(all(0 <= xy_min[i] < xy_max[i] <= 260 for i in range(2)),
          "Extrusion outside Kobra X XY area: %s %s" % (xy_min, xy_max))
    check(not any("support" in role.lower() for role in roles),
          "Unexpected support extrusion: %s" % roles)
    return {"layer_count": layer, "all_layers_have_extrusion": True,
            "extrusion_xy_min_mm": xy_min, "extrusion_xy_max_mm": xy_max,
            "gcode_roles": sorted(roles), "first_layer_roles": sorted(first_layer_roles),
            "supports_generated": False}


def inspect_interlayer_contact(gcode):
    """Sample printed paths and flag new material without nearby prior-layer paths.

    This is a local support/island screen, not a mechanical or printing guarantee.
    """
    previous, current = set(), set()
    layer = 0
    x = y = e = 0.0
    relative_xyz = relative_e = False
    role = ""
    checked_sites = 0
    cap_sites = []
    unsupported_sites = []
    close_neighbours = [(dx, dy) for dx in range(-2, 3) for dy in range(-2, 3)
                        if dx * dx + dy * dy <= 4]
    wide_neighbours = [(dx, dy) for dx in range(-4, 5) for dy in range(-4, 5)
                       if dx * dx + dy * dy <= 16]

    def finish_layer():
        nonlocal checked_sites
        if layer <= 1:
            return
        checked_sites += len(current)
        for px, py in current:
            if not any((px + dx, py + dy) in previous for dx, dy in close_neighbours):
                site = (layer, px / 4, py / 4)
                cap_sites.append(site)
                if not any((px + dx, py + dy) in previous for dx, dy in wide_neighbours):
                    unsupported_sites.append(site)

    for line in gcode.splitlines():
        if line.startswith(";LAYER_CHANGE"):
            finish_layer()
            previous, current = current, set()
            layer += 1
        elif line.startswith(";TYPE:"):
            role = line[6:].strip()
        code = line.split(";", 1)[0].strip()
        if code == "G90": relative_xyz = False
        elif code == "G91": relative_xyz = True
        elif code == "M82": relative_e = False
        elif code == "M83": relative_e = True
        if code.startswith("G92"):
            for key, value in re.findall(r"\b([XYE])([+-]?\d*\.?\d+)", code):
                if key == "X": x = float(value)
                elif key == "Y": y = float(value)
                elif key == "E": e = float(value)
        if not code.startswith(("G0 ", "G1 ")):
            continue
        args = {key: float(value) for key, value in re.findall(
            r"\b([XYE])([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)", code)}
        next_x = x + args.get("X", 0) if relative_xyz else args.get("X", x)
        next_y = y + args.get("Y", 0) if relative_xyz else args.get("Y", y)
        next_e = args.get("E", e)
        extruded = "E" in args and (next_e > 0 if relative_e else next_e > e)
        if layer and extruded and (next_x != x or next_y != y) and role != "Custom":
            steps = max(1, math.ceil(math.hypot(next_x - x, next_y - y) / 0.2))
            for i in range(steps + 1):
                t = i / steps
                current.add((round((x + (next_x - x) * t) * 4),
                             round((y + (next_y - y) * t) * 4)))
        x, y = next_x, next_y
        if "E" in args:
            e = e + next_e if relative_e else next_e
    finish_layer()
    check(not unsupported_sites, "Paths >1 mm from prior-layer paths: %s" % unsupported_sites[:8])
    return {"method": "0.2 mm path samples on a 0.25 mm grid; prior-layer search radii 0.5 and 1 mm",
            "checked_sites": checked_sites, "sites_over_0_5_mm": len(cap_sites),
            "over_0_5_mm_examples": cap_sites[:8], "sites_over_1_mm": 0,
            "physical_print_verified": False}


def main():
    check(all(path.is_file() for path in (CLI, MACHINE, PROCESS, FILAMENT, GEOMETRY)),
          "Missing slicer, Kobra X profile or geometry")
    layout = json.loads((HERE / "kontrola-rozlozeni.json").read_text())
    check(layout["physical_pieces"] == 1 and
          layout["plate_sha256"] == digest(GEOMETRY) and
          layout["source_stl_sha256"] == digest(HERE.parent / "stl/vesacek.stl"),
          "Geometry or STL changed after plate generation")
    machine = json.loads(MACHINE.read_text())
    check(machine.get("printer_model") == "Anycubic Kobra X" and
          machine.get("nozzle_diameter") == ["0.4"], "Wrong printer profile")
    process = json.loads(PROCESS.read_text())
    process.update({
        "name": "Vesacek 0.20 mm PLA navrh Kobra X",
        "print_settings_id": "Vesacek 0.20 mm PLA navrh Kobra X",
        "layer_height": "0.2", "wall_loops": "5", "sparse_infill_density": "100%",
        "sparse_infill_pattern": "rectilinear", "top_shell_layers": "5",
        "bottom_shell_layers": "5", "brim_type": "outer_only", "brim_width": "5",
        "brim_object_gap": "0.1", "enable_support": "0",
        "initial_layer_speed": "25", "initial_layer_infill_speed": "40",
        "outer_wall_speed": "45", "inner_wall_speed": "70",
        "top_surface_speed": "45", "sparse_infill_speed": "70",
        "internal_solid_infill_speed": "70", "gap_infill_speed": "45",
        "default_acceleration": "1000", "outer_wall_acceleration": "500",
        "inner_wall_acceleration": "800", "top_surface_acceleration": "500",
    })
    CUSTOM_PROCESS.write_text(json.dumps(process, ensure_ascii=False, indent=2) + "\n")
    filament = json.loads(FILAMENT.read_text())
    filament.update({
        "name": "PLA navrh @Anycubic Kobra X 0.4 nozzle",
        "filament_settings_id": ["PLA navrh @Anycubic Kobra X 0.4 nozzle"],
        "nozzle_temperature": ["205"], "nozzle_temperature_initial_layer": ["215"],
        "nozzle_temperature_BRASS": ["205"], "nozzle_temperature_HS": ["205"],
        "nozzle_temperature_initial_layer_BRASS": ["215"],
        "nozzle_temperature_initial_layer_HS": ["215"],
        "hot_plate_temp": ["50"], "hot_plate_temp_initial_layer": ["50"],
        "textured_plate_temp": ["50"], "textured_plate_temp_initial_layer": ["50"],
    })
    CUSTOM_FILAMENT.write_text(json.dumps(filament, ensure_ascii=False, indent=2) + "\n")
    CACHE.mkdir(exist_ok=True)
    configured = CACHE / "configured.3mf"
    run([str(CLI), "--datadir", str(CACHE / "export-profile"),
         "--load-settings", str(MACHINE) + ";" + str(CUSTOM_PROCESS),
         "--load-filaments", str(CUSTOM_FILAMENT), "--arrange", "0", "--orient", "0",
         "--export-3mf", configured.name, "--outputdir", str(CACHE), str(GEOMETRY)],
        CACHE / "export.log")
    check(configured.is_file(), "Configured 3MF missing")
    configured_info = inspect_project(configured, False)
    slice_dir = CACHE / "slice"
    slice_dir.mkdir(exist_ok=True)
    run([str(CLI), "--datadir", str(CACHE / "slice-profile"),
         "--arrange", "0", "--orient", "0", "--slice", "0",
         "--export-3mf", DELIVERED.name, "--outputdir", str(slice_dir), str(configured)],
        CACHE / "slice.log")
    check((slice_dir / DELIVERED.name).is_file(), "Sliced 3MF missing")
    shutil.copyfile(slice_dir / DELIVERED.name, DELIVERED)
    delivered_info = inspect_project(DELIVERED, True)
    report = {
        "status": "locally sliced; physical print, fit, stability and load unverified",
        "source_stl_sha256": layout["source_stl_sha256"],
        "geometry_plate_sha256": layout["plate_sha256"],
        "machine_profile_sha256": digest(MACHINE),
        "process_profile_sha256": digest(CUSTOM_PROCESS),
        "filament_profile_sha256": digest(CUSTOM_FILAMENT),
        "support_decision": "back plate lies on bed; all three hook roots overlap the plate and lofts grow gradually; no automatic supports",
        "material_condition": "PLA temperature/profile is a starting assumption, not measured spool calibration or verified load capacity",
        "configured": configured_info, "delivered": delivered_info,
        "export_log_tail": (CACHE / "export.log").read_text(errors="replace")[-1800:],
        "slice_log_tail": (CACHE / "slice.log").read_text(errors="replace")[-2500:],
        "printer_contact": False,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("VESACEK_SLICED_OK", delivered_info["layers_and_roles"]["layer_count"], flush=True)


if __name__ == "__main__":
    main()
