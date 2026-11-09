#!/usr/bin/env python3
"""Build and slice the actual Kobra X / PLA Next project without printer I/O.

The configured 3MF is delivered here. Slice outputs, G-code and CLI logs stay
in the repository's ignored .cache directory. Rerunning overwrites only this
model's configured 3MF, slice report and selected-layer preview.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
ET.register_namespace("", "http://schemas.microsoft.com/3dmanufacturing/core/2015/02")
ET.register_namespace("p", "http://schemas.microsoft.com/3dmanufacturing/production/2015/06")
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CACHE = REPO / ".cache" / "schranka-na-uctenky-techtools"
PROFILES = Path("/usr/share/AnycubicSlicerNext/resources/profiles/Anycubic")
MACHINE = PROFILES / "machine/Anycubic Kobra X 0.4 nozzle.json"
PROCESS = PROFILES / "process/0.20mm Standard @Anycubic Kobra X 0.4 nozzle.json"
SOURCE_FILAMENT = PROFILES / "filament/Anycubic PLA @Anycubic Kobra X 0.4 nozzle.json"
SLICER = "/usr/bin/AnycubicSlicerNext"
GEOMETRY = HERE / "podlozka-01-geometrie.3mf"
PROJECT = HERE / "podlozka-01-kobra-x-pla-projekt.3mf"

OVERRIDES = {
    "name": "Schranka TechTools 0.20mm PLA bila cerna 3 steny 15%",
    "print_settings_id": "Schranka TechTools 0.20mm PLA bila cerna 3 steny 15%",
    "wall_loops": "3",
    "sparse_infill_density": "15%",
    "outer_wall_speed": "70",
    "inner_wall_speed": "100",
    "sparse_infill_speed": "100",
    "internal_solid_infill_speed": "90",
    "gap_infill_speed": "70",
    "top_surface_speed": "60",
    "initial_layer_speed": "35",
    "initial_layer_infill_speed": "60",
    "enable_support": "0",
    "brim_type": "auto_brim",
    "brim_width": "5",
    "print_sequence": "by layer",
    "enable_prime_tower": "1",
    "wipe_tower_x": ["12"],
    "wipe_tower_y": ["165"],
}

EXTRUDERS = {
    "telo-techtools": "1",
    "napis-techtools-uctenky": "2",
    "viko-se-sterbinou": "1",
}

def run(command, log):
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as output:
        result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT,
                                env=dict(os.environ, DISPLAY=""), timeout=1800)
    if result.returncode:
        raise RuntimeError("Slicer return code %d; see %s" % (result.returncode, log))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def zip_info(path):
    with ZipFile(path) as z:
        assert z.testzip() is None
        names = z.namelist()
        settings = json.loads(z.read("Metadata/project_settings.config"))
        model_settings = ET.fromstring(z.read("Metadata/model_settings.config"))
        objects = model_settings.findall("object")
        source_paths = [name for name in names if name.startswith("3D/") and name.endswith(".model")]
        assert len(objects) == 2, (path, len(objects))
        repairs = [stat.attrib for stat in model_settings.findall(".//mesh_stat")]
        assert len(repairs) == 3 and all(all(int(value) == 0 for value in entry.values()) for entry in repairs)
        assert len(source_paths) >= 1
        secret_keys = [key for key in settings if re.search(r"password|(?:access|refresh)_token|api_?key", key, re.I)]
        assert all(settings[key] in ("", [], {}, None) for key in secret_keys)
        assert not any(b"/home/novakj/" in z.read(name) for name in names if not name.endswith(".png"))
        assignments = {}
        object_names = []
        for obj in objects:
            name = obj.find('metadata[@key="name"]').get("value")
            object_names.append(name)
            for part in obj.findall("part"):
                part_name = part.find('metadata[@key="name"]').get("value")
                part_extruder = part.find('metadata[@key="extruder"]')
                assignments[part_name] = part_extruder.get("value") if part_extruder is not None else obj.find('metadata[@key="extruder"]').get("value")
        assert assignments == EXTRUDERS, assignments
        assert set(object_names) == {"telo-techtools", "viko-se-sterbinou"}
        return {"settings": settings, "objects": object_names, "extruders": assignments,
                "names": names, "mesh_repairs": repairs}

def project_mesh_checks(path, manifest):
    ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
    production_path = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}path"
    def translation(value):
        matrix = [float(number) for number in value.split()] if value else [1,0,0,0,1,0,0,0,1,0,0,0]
        assert matrix[:9] == [1,0,0,0,1,0,0,0,1], "Slicer changed object orientation or scale"
        return matrix[9:]
    records = []
    with ZipFile(path) as z:
        root = ET.fromstring(z.read("3D/3dmodel.model"))
        assert root.get("unit") == "millimeter"
        items = root.findall("m:build/m:item", ns)
        assert len(items) == manifest["physical_parts"] == 2
        model_settings = ET.fromstring(z.read("Metadata/model_settings.config"))
        expected_parts = {part["name"]: part for part in manifest["parts"]}
        for item in items:
            obj = root.find("m:resources/m:object[@id='%s']" % item.get("objectid"), ns)
            object_config = model_settings.find("object[@id='%s']" % item.get("objectid"))
            assert obj is not None and object_config is not None
            components = obj.findall("m:components/m:component", ns)
            parts = object_config.findall("part")
            assert len(components) == len(parts)
            for component, part_settings in zip(components, parts):
                name = part_settings.find('metadata[@key="name"]').get("value")
                expected = expected_parts[name]
                assert component.get("objectid") == part_settings.get("id")
                component_path = component.get(production_path).lstrip("/")
                nested = ET.fromstring(z.read(component_path))
                mesh = nested.find("m:resources/m:object[@id='%s']/m:mesh" % component.get("objectid"), ns)
                assert mesh is not None
                offset = [a+b for a,b in zip(translation(item.get("transform")), translation(component.get("transform")))]
                vertices = [tuple(float(node.get(axis)) + offset[i] for i, axis in enumerate("xyz")) for node in mesh.findall("m:vertices/m:vertex", ns)]
                triangles = [tuple(int(node.get("v%d" % i)) for i in (1,2,3)) for node in mesh.findall("m:triangles/m:triangle", ns)]
                mins = [min(v[i] for v in vertices) for i in range(3)]
                maxs = [max(v[i] for v in vertices) for i in range(3)]
                assert len(triangles) == expected["triangle_count"]
                assert all(abs(mins[i] - expected["placed_min_xyz_mm"][i]) < 0.001 and abs(maxs[i] - expected["placed_max_xyz_mm"][i]) < 0.001 for i in range(3))
                source = (HERE / expected["source_stl"]).read_bytes()
                assert hashlib.sha256(source).hexdigest() == expected["source_sha256"]
                triangle_count = struct.unpack_from("<I", source, 80)[0]
                assert triangle_count == len(triangles)
                source_vertices, source_indices, source_faces = [], {}, []
                for i in range(triangle_count):
                    values = struct.unpack_from("<12fH", source, 84 + i*50)
                    face = []
                    for j in (3,6,9):
                        point = tuple(values[j:j+3])
                        if point not in source_indices:
                            source_indices[point] = len(source_vertices)
                            source_vertices.append(point)
                        face.append(source_indices[point])
                    source_faces.append(tuple(face))
                assert source_faces == triangles, "Slicer changed triangle connectivity"
                assert len(source_vertices) == len(vertices)
                maximum_vertex_delta = max(abs(source_vertices[i][axis] + expected["translation_mm"][axis] - vertices[i][axis]) for i in range(len(vertices)) for axis in range(3))
                assert maximum_vertex_delta < 0.0001, maximum_vertex_delta
                records.append({"name": expected["name"], "triangle_count": len(triangles), "min_xyz_mm": mins, "max_xyz_mm": maxs, "source_triangles_and_placement_preserved": True, "maximum_vertex_delta_mm": maximum_vertex_delta})
    assert {record["name"] for record in records} == set(expected_parts)
    return records

def create_layer_preview(gcode, manifest):
    # Actual extrusion XY paths, with the active tool and object at each path.
    selected = {1: "první vrstva", 56: "víko nahoře", 320: "černé účtenky",
                430: "černé TechTools", 690: "horní okraj těla"}
    paths = {index: [] for index in selected}
    layer, role = 0, "Unknown"
    x = y = z = e = 0.0
    absolute_e = True
    absolute_xyz = True
    tool, owner = 0, None
    tool_changes, owner_tools = [], {name: {} for name in ("telo-techtools", "viko-se-sterbinou")}
    black_min = [float("inf")] * 3
    black_max = [float("-inf")] * 3
    tower_min = [float("inf")] * 2
    tower_max = [float("-inf")] * 2
    tower_segments = 0
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    number = r"[+-]?\d*\.?\d+(?:[eE][+-]?\d+)?"
    for line in gcode.splitlines():
        if line == ";LAYER_CHANGE":
            layer += 1
        elif line.startswith(";TYPE:"):
            role = line[6:].strip()
        elif line.startswith("EXCLUDE_OBJECT_START NAME="):
            owner = line.split("NAME=", 1)[1].split("_id_", 1)[0]
            assert owner in owner_tools, owner
        elif line.startswith("EXCLUDE_OBJECT_END"):
            owner = None
        code = line.split(";", 1)[0].strip()
        if re.fullmatch(r"T\d+", code):
            tool = int(code[1:])
            tool_changes.append(tool)
            continue
        if code == "G90":
            absolute_xyz = True
        elif code == "G91":
            absolute_xyz = False
        if line.startswith("M83"):
            absolute_e = False
        elif line.startswith("M82"):
            absolute_e = True
        if code.startswith("G92"):
            for key, value in re.findall(r"\b([XYZE])(" + number + r")", code):
                if key == "X": x = float(value)
                elif key == "Y": y = float(value)
                elif key == "Z": z = float(value)
                elif key == "E": e = float(value)
        if not code.startswith(("G0 ", "G1 ")):
            continue
        arguments = {key: float(value) for key, value in re.findall(r"\b([XYZE])(" + number + r")", code)}
        new_x = arguments.get("X", x) if absolute_xyz else x + arguments.get("X", 0)
        new_y = arguments.get("Y", y) if absolute_xyz else y + arguments.get("Y", 0)
        new_z = arguments.get("Z", z) if absolute_xyz else z + arguments.get("Z", 0)
        new_e = arguments.get("E", e)
        gain = new_e if not absolute_e and "E" in arguments else new_e - e
        if gain > 0 and (new_x != x or new_y != y) and role != "Custom":
            min_x, min_y = min(min_x, x, new_x), min(min_y, y, new_y)
            max_x, max_y = max(max_x, x, new_x), max(max_y, y, new_y)
            if owner is not None:
                owner_tools[owner][tool] = owner_tools[owner].get(tool, 0) + 1
            if owner == "telo-techtools" and tool == 1:
                for i, pair in enumerate(((x, new_x), (y, new_y), (z, new_z))):
                    black_min[i] = min(black_min[i], *pair)
                    black_max[i] = max(black_max[i], *pair)
            if "tower" in role.lower():
                tower_segments += 1
                for i, pair in enumerate(((x, new_x), (y, new_y))):
                    tower_min[i] = min(tower_min[i], *pair)
                    tower_max[i] = max(tower_max[i], *pair)
            if layer in paths:
                paths[layer].append((x, y, new_x, new_y, role, tool, owner))
        x, y, z = new_x, new_y, new_z
        if "E" in arguments:
            e = e + new_e if not absolute_e else new_e
    assert all(paths.values()), {i: len(v) for i, v in paths.items()}
    assert 0 <= min_x <= max_x <= 260
    assert 0 <= min_y <= max_y <= 260
    assert set(tool_changes) == {0, 1}, tool_changes
    assert set(owner_tools["telo-techtools"]) == {0, 1}, owner_tools
    assert set(owner_tools["viko-se-sterbinou"]) == {0}, owner_tools
    assert all(count > 0 for values in owner_tools.values() for count in values.values()), owner_tools
    label = next(part for part in manifest["parts"] if part["name"] == "napis-techtools-uctenky")
    assert all(label["placed_min_xyz_mm"][i] - 0.5 <= black_min[i] <= black_max[i] <= label["placed_max_xyz_mm"][i] + 0.5 for i in range(3)), (black_min, black_max)
    assert tower_segments > 0, "Prime tower has no actual extrusion paths"
    assert tower_max[0] + 1 < min(part["placed_min_xyz_mm"][0] for part in manifest["parts"] if part["physical_piece"] in ("body", "lid")), (tower_min, tower_max)
    assert any(p[6] == "telo-techtools" and p[5] == 1 for p in paths[320])
    assert any(p[6] == "telo-techtools" and p[5] == 1 for p in paths[430])
    assert any(p[6] == "viko-se-sterbinou" and p[5] == 0 for p in paths[56])
    assert any(p[6] == "telo-techtools" and p[5] == 0 for p in paths[690])
    first = paths[1]
    assert {p[6] for p in first if p[6] is not None} == {"telo-techtools", "viko-se-sterbinou"}
    assert any(55 <= (segment[0]+segment[2])/2 <= 205 and 10 <= (segment[1]+segment[3])/2 <= 121 for segment in first)
    assert any(52 <= (segment[0]+segment[2])/2 <= 208 and 134 <= (segment[1]+segment[3])/2 <= 250 for segment in first)
    slot_clear = not any(90 < (segment[0]+segment[2])/2 < 170 and 188 < (segment[1]+segment[3])/2 < 196 for segment in first)
    assert slot_clear, "First-layer extrusion fills the receipt slot"
    tile, margin, scale = 660, 34, 2.2
    image = Image.new("RGB", (tile * 2, tile * 3), "#f7f9fa")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 23)
    for index, (layer_number, title) in enumerate(selected.items()):
        ox, oy = (index % 2) * tile, (index // 2) * tile
        draw.rectangle((ox + margin, oy + margin + 38, ox + margin + 260 * scale, oy + margin + 38 + 260 * scale), fill="white", outline="#7b8b93", width=2)
        draw.text((ox + margin, oy + 6), "%s · vrstva %d" % (title, layer_number), fill="#203f4c", font=font)
        for x0, y0, x1, y1, role, active_tool, part in paths[layer_number]:
            color = "#272a2c" if active_tool == 1 else "#c8d7df"
            if "tower" in role.lower():
                color = "#bd7d55"
            draw.line((ox+margin+x0*scale, oy+margin+38+(260-y0)*scale,
                       ox+margin+x1*scale, oy+margin+38+(260-y1)*scale), fill=color, width=1)
    image.save(HERE / "podlozka-01-vrstvy.png")
    return {"selected_layer_extrusion_segments": {str(i): len(paths[i]) for i in paths},
            "extrusion_xy_bounds_mm": [[min_x, min_y], [max_x, max_y]],
            "tool_changes": len(tool_changes), "used_tools_zero_based": sorted(set(tool_changes)),
            "per_object_extrusion_segments_by_tool": owner_tools,
            "black_lettering_extrusion_bounds_xyz_mm": [black_min, black_max],
            "prime_tower_xy_bounds_mm": [tower_min, tower_max],
            "prime_tower_extrusion_segments": tower_segments,
            "both_parts_present_on_first_layer": True,
            "receipt_slot_clear_on_first_layer": slot_clear}

def main():
    assert GEOMETRY.exists()
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["physical_parts"] == 2 and manifest["material_regions"] == 3
    assert [part["name"] for part in manifest["parts"]] == list(EXTRUDERS)
    assert digest(GEOMETRY) == manifest["geometry_only_sha256"]
    with ZipFile(GEOMETRY) as source:
        assert source.testzip() is None
        assert not any(name.startswith("Metadata/") for name in source.namelist())
        ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
        model = ET.fromstring(source.read("3D/3dmodel.model"))
        assert model.get("unit") == "millimeter"
        build = model.findall("m:build/m:item", ns)
        assert len(build) == 2
        body = model.find("m:resources/m:object[@id='%s']" % build[0].get("objectid"), ns)
        assert [component.get("objectid") for component in body.findall("m:components/m:component", ns)] == ["1", "2"]
    CACHE.mkdir(parents=True, exist_ok=True)
    process = json.loads(PROCESS.read_text(encoding="utf-8"))
    process.update(OVERRIDES)
    local_process = CACHE / "process.json"
    local_process.write_text(json.dumps(process, indent=2) + "\n", encoding="utf-8")
    # Provisional PLA Basic start settings, within the supplier's documented
    # 190–220 °C nozzle / 45–60 °C bed range. Not a measured calibration.
    local_filaments = []
    for colour, code in (("bila", "#F7F7F2"), ("cerna", "#17191B")):
        filament = json.loads(SOURCE_FILAMENT.read_text(encoding="utf-8"))
        name = "NAVRH Alzament PLA Basic %s @Kobra X 0.4" % colour
        filament.update({"name": name, "setting_id": name, "filament_id": "NAVRH-Alzament-PLA-Basic-" + colour,
                         "filament_settings_id": [name], "filament_vendor": ["Alzament"],
                         "filament_colour": [code], "default_filament_colour": [code],
                         "from": "user", "is_custom_defined": "1",
                         "filament_notes": ["Navrh pro 2 barvy, bez fyzicke kalibrace; overit skutecnou civku a ACE slot."]})
        for key, value in {
            "textured_plate_temp": "50", "textured_plate_temp_initial_layer": "50",
            "hot_plate_temp": "50", "hot_plate_temp_initial_layer": "50",
            "nozzle_temperature": "205", "nozzle_temperature_BRASS": "205",
            "nozzle_temperature_HS": "205", "nozzle_temperature_initial_layer": "215",
            "nozzle_temperature_initial_layer_BRASS": "215",
            "nozzle_temperature_initial_layer_HS": "215",
        }.items():
            filament[key] = [value]
        path = CACHE / ("filament-" + colour + ".json")
        path.write_text(json.dumps(filament, indent=2) + "\n", encoding="utf-8")
        local_filaments.append(path)
    export = [SLICER, "--datadir", str(CACHE / "export-profile"), "--arrange", "0", "--orient", "0", "--load-settings", str(MACHINE) + ";" + str(local_process), "--load-filaments", ";".join(map(str, local_filaments)), "--export-3mf", "export.3mf", "--outputdir", str(CACHE), str(GEOMETRY)]
    run(export, CACHE / "export.log")
    exported = CACHE / "export.3mf"
    assert exported.is_file()
    with ZipFile(exported) as source:
        files = {name: source.read(name) for name in source.namelist()}
    object_settings = ET.fromstring(files["Metadata/model_settings.config"])
    assigned = {}
    for obj in object_settings.findall("object"):
        name = obj.find('metadata[@key="name"]').get("value")
        assert name in ("telo-techtools", "viko-se-sterbinou"), name
        obj.find('metadata[@key="extruder"]').set("value", "1")
        parts = obj.findall("part")
        assert len(parts) == (2 if name == "telo-techtools" else 1)
        for part in parts:
            volume_id = part.find('metadata[@key="source_volume_id"]').get("value")
            part_name = "napis-techtools-uctenky" if name == "telo-techtools" and volume_id == "1" else name
            assert part_name not in assigned, part_name
            part.find('metadata[@key="name"]').set("value", part_name)
            extruder = part.find('metadata[@key="extruder"]')
            if extruder is None:
                extruder = ET.SubElement(part, "metadata", key="extruder")
            extruder.set("value", EXTRUDERS[part_name])
            assigned[part_name] = EXTRUDERS[part_name]
    assert assigned == EXTRUDERS, assigned
    files["Metadata/model_settings.config"] = ET.tostring(object_settings, encoding="utf-8", xml_declaration=True)
    assert not any(name.endswith(".gcode") for name in files)
    with ZipFile(PROJECT, "w", ZIP_DEFLATED) as output:
        for name, data in files.items():
            output.writestr(name, data)
    check = zip_info(PROJECT)
    mesh_checks = project_mesh_checks(PROJECT, manifest)
    settings = check["settings"]
    assert settings["printer_settings_id"] == "Anycubic Kobra X 0.4 nozzle"
    assert settings["layer_height"] == "0.2"
    assert settings["wall_loops"] == "3"
    assert settings["enable_support"] == "0"
    assert settings["brim_type"] == "auto_brim"
    assert settings["enable_prime_tower"] == "1"
    assert settings["filament_settings_id"] == ["NAVRH Alzament PLA Basic bila @Kobra X 0.4",
                                                "NAVRH Alzament PLA Basic cerna @Kobra X 0.4"]
    assert settings["filament_colour"] == ["#F7F7F2", "#17191B"]
    assert settings["nozzle_temperature"] == ["205", "205"]
    assert settings["nozzle_temperature_initial_layer"] == ["215", "215"]
    assert settings["textured_plate_temp"] == ["50", "50"]
    assert len(check["objects"]) == 2
    assert not any(name.endswith(".gcode") for name in check["names"])
    slice_dir = CACHE / "slice"
    slice_dir.mkdir(exist_ok=True)
    slice_command = [SLICER, "--datadir", str(CACHE / "slice-profile"), "--arrange", "0", "--orient", "0", "--slice", "0", "--export-3mf", "sliced.3mf", "--outputdir", str(slice_dir), str(PROJECT)]
    run(slice_command, CACHE / "slice.log")
    sliced = slice_dir / "sliced.3mf"
    assert sliced.is_file()
    sliced_check = zip_info(sliced)
    assert sliced_check["extruders"] == check["extruders"]
    sliced_mesh_checks = project_mesh_checks(sliced, manifest)
    with ZipFile(sliced) as z:
        assert z.testzip() is None
        gcode = z.read("Metadata/plate_1.gcode").decode("utf-8", errors="replace")
        slice_info = ET.fromstring(z.read("Metadata/slice_info.config"))
        warnings = [node.attrib for node in slice_info.findall(".//warning")]
        sliced_settings = json.loads(z.read("Metadata/project_settings.config"))
    assert sliced_settings["printer_settings_id"] == settings["printer_settings_id"]
    assert sliced_settings["wall_loops"] == "3" and sliced_settings["enable_support"] == "0"
    assert sliced_settings["enable_prime_tower"] == "1"
    assert sliced_settings["filament_settings_id"] == settings["filament_settings_id"]
    assert sliced_settings["filament_colour"] == settings["filament_colour"]
    assert not warnings, warnings
    layer_count = gcode.count(";LAYER_CHANGE")
    roles = sorted(set(re.findall(r"^;TYPE:(.+)$", gcode, re.M)))
    assert layer_count == 690, layer_count  # 138 mm at 0.20 mm per layer
    assert not any("Support" in role for role in roles), roles
    assert any("Outer wall" in role for role in roles)
    assert all(name in gcode for name in check["objects"]), check["objects"]
    assert "G9111 bedTemp=50 extruderTemp=215" in gcode
    deposition = create_layer_preview(gcode, manifest)
    mass_match = re.search(r"^; total filament used \[g\] = ([0-9.]+)$", gcode, re.M)
    colour_mass_match = re.search(r"^; filament used \[g\] = ([0-9.]+), ([0-9.]+)$", gcode, re.M)
    time_match = re.search(r"^; estimated printing time \(normal mode\) = (.+)$", gcode, re.M)
    assert mass_match and colour_mass_match and time_match
    colour_mass = [float(colour_mass_match.group(1)), float(colour_mass_match.group(2))]
    assert abs(sum(colour_mass) - float(mass_match.group(1))) < 0.02
    summary = {"project": PROJECT.name, "project_sha256": digest(PROJECT), "geometry_only_3mf": GEOMETRY.name, "geometry_only_sha256": digest(GEOMETRY), "object_names": check["objects"], "physical_parts": 2, "material_regions": 3, "object_extruders_one_based": check["extruders"], "machine": settings["printer_settings_id"], "process": settings["print_settings_id"], "filament": settings["filament_settings_id"], "filament_colours": settings["filament_colour"], "filament_status": "Provisional Alzament PLA Basic start values, not physically calibrated; physical ACE slots unverified", "effective_settings": {k: settings[k] for k in ("layer_height", "wall_loops", "sparse_infill_density", "enable_support", "enable_prime_tower", "brim_type", "brim_width", "outer_wall_speed", "inner_wall_speed", "top_surface_speed", "textured_plate_temp", "textured_plate_temp_initial_layer", "nozzle_temperature", "nozzle_temperature_initial_layer")}, "slicer_exit_codes": [0, 0], "slice_warning_details": warnings, "layers": layer_count, "gcode_roles": roles, "supports_generated": any("Support" in role for role in roles), "brim_generated": any("Brim" in role for role in roles), "project_meshes": mesh_checks, "sliced_meshes": sliced_mesh_checks, "project_mesh_repairs": check["mesh_repairs"], "sliced_mesh_repairs": sliced_check["mesh_repairs"], **deposition, "layer_preview": "podlozka-01-vrstvy.png", "estimated_filament_g": float(mass_match.group(1)), "estimated_filament_by_tool_g": {"white_T0": colour_mass[0], "black_T1": colour_mass[1]}, "estimated_normal_time": time_match.group(1), "first_layer_gcode_temperatures_c": {"bed": 50, "nozzle": 215}, "gcode_stored_in_project": False, "gcode_kept_only_in_ignored_cache": True, "physical_print_verified": False, "physical_fit_verified": False}
    (HERE / "kontrola-rezani.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == "__main__":
    main()
