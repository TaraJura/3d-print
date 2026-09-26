#!/usr/bin/env python3
"""Čte skutečný G-code uvnitř obou předaných 3MF a kontroluje dráhy a vrstvy."""
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
NUM = re.compile(r"([XYZE])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)")

def require(ok, message):
    if not ok:
        raise ValueError(message)

def first_layer_image(number):
    img = Image.new("RGB", (940, 990), "#f9fbfc")
    dr = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 23)
    dr.text((44, 13), f"Podložka {number:02d} · skutečné dráhy první vrstvy Z=0,2 mm", font=font, fill="#19323f")
    scale, margin = 3.2, 54
    xy = lambda x, y: (margin + scale*x, margin + scale*(260-y))
    dr.rectangle([xy(0,260),xy(260,0)],fill="#e8eef0",outline="#4e6570",width=3)
    dr.line([xy(0,0),xy(260,0)],fill="#bd5746",width=4)
    dr.text((54,910),"Tmavě: model · zeleně: 5mm lem. Podpory nejsou zapnuté.",font=font,fill="#29414a")
    return img, dr, xy

def placed_mesh_bounds(project):
    """Prověří 3MF transformace sliceru proti původním souřadnicím STL."""
    ns = {"m":"http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
    pns = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
    with ZipFile(project) as z:
        root = ET.fromstring(z.read("3D/3dmodel.model"))
        objects = {o.get("id"):o for o in root.findall("m:resources/m:object",ns)}
        result = []
        for item in root.findall("m:build/m:item",ns):
            wrapper = objects[item.get("objectid")]
            components = wrapper.findall("m:components/m:component",ns)
            require(len(components)==1,"Slicer changed mesh component count")
            component = components[0]
            path = component.get("{"+pns+"}path").lstrip("/")
            transform = list(map(float,item.get("transform").split()))
            local_transform = list(map(float,component.get("transform").split()))
            identity = [1,0,0,0,1,0,0,0,1]
            require(transform[:9]==identity and local_transform[:9]==identity and
                    all(abs(t)<1e-8 for t in local_transform[9:]),
                    "Slicer rotated or scaled a part")
            child = ET.fromstring(z.read(path))
            points = [[float(v.get(axis)) for axis in "xyz"]
                      for v in child.findall("m:resources/m:object/m:mesh/m:vertices/m:vertex",ns)]
            require(points,"No mesh vertices in 3MF child")
            lo=[min(v[k] for v in points)+transform[9+k] for k in range(3)]
            hi=[max(v[k] for v in points)+transform[9+k] for k in range(3)]
            result.append((lo,hi))
    return result

def parse(number, expected, gcode):
    img, dr, xy = first_layer_image(number)
    role = "Custom"
    width = 0.5
    owner = None
    absolute = True
    e_relative = False
    pos = dict(X=0.0,Y=0.0,Z=0.0,E=0.0)
    stats = defaultdict(lambda: {"roles": Counter(), "min_xy": [float("inf"),float("inf")],
                                 "max_xy": [-float("inf"),-float("inf")],
                                 "model_max_z": 0.0, "brim_segments": 0,
                                 "bridge_segments": 0, "max_bridge_segment_mm": 0.0,
                                 "internal_bridge_segments": 0, "max_internal_bridge_segment_mm": 0.0,
                                 "first_layer_segments": 0, "max_width_mm": 0.0})
    for line in gcode.decode(errors="replace").splitlines():
        if line.startswith(";TYPE:"):
            role = line.split(":",1)[1].strip()
        elif line.startswith(";WIDTH:"):
            width = float(line.split(":",1)[1])
        elif line.startswith("EXCLUDE_OBJECT_START NAME="):
            owner = line.split("NAME=",1)[1].split("_id_",1)[0]
        elif line.startswith("EXCLUDE_OBJECT_END"):
            owner = None
        command = line.split(";",1)[0].strip()
        if not command:
            continue
        kind = command.split()[0]
        values = {key: float(value) for key,value in NUM.findall(command)}
        if kind == "G90":
            absolute = True
        elif kind == "G91":
            absolute = False
        elif kind == "M83":
            e_relative = True
        elif kind == "M82":
            e_relative = False
        elif kind == "G92":
            pos.update(values)
        elif kind in ("G0","G1"):
            old = pos.copy()
            for axis in "XYZ":
                if axis in values:
                    pos[axis] = values[axis] if absolute else pos[axis]+values[axis]
            delta_e = values.get("E",0) if e_relative else values.get("E",pos["E"])-pos["E"]
            if "E" in values:
                pos["E"] = pos["E"]+values["E"] if e_relative else values["E"]
            if delta_e <= 0 or (pos["X"] == old["X"] and pos["Y"] == old["Y"]) or role == "Custom":
                continue
            require(owner is not None, f"Extrusion without object on plate {number}: {line[:90]}")
            entry = stats[owner]
            entry["roles"][role] += 1
            entry["max_width_mm"] = max(entry["max_width_mm"],width)
            for point in (old,pos):
                entry["min_xy"][0] = min(entry["min_xy"][0],point["X"]-width/2)
                entry["min_xy"][1] = min(entry["min_xy"][1],point["Y"]-width/2)
                entry["max_xy"][0] = max(entry["max_xy"][0],point["X"]+width/2)
                entry["max_xy"][1] = max(entry["max_xy"][1],point["Y"]+width/2)
            if role == "Brim":
                entry["brim_segments"] += 1
            elif not role.startswith("Support"):
                entry["model_max_z"] = max(entry["model_max_z"],pos["Z"])
            if role in ("Bridge","Internal Bridge"):
                length = math.hypot(pos["X"]-old["X"],pos["Y"]-old["Y"])
                if role == "Bridge":
                    entry["bridge_segments"] += 1
                    entry["max_bridge_segment_mm"] = max(entry["max_bridge_segment_mm"],length)
                else:
                    entry["internal_bridge_segments"] += 1
                    entry["max_internal_bridge_segment_mm"] = max(entry["max_internal_bridge_segment_mm"],length)
            if abs(pos["Z"]-0.2) < 0.015:
                entry["first_layer_segments"] += 1
                color = "#289053" if role == "Brim" else "#2f5a70"
                dr.line([xy(old["X"],old["Y"]),xy(pos["X"],pos["Y"])],fill=color,width=2)
        elif kind in ("G2","G3"):
            raise ValueError(f"Arc extrusion audit not implemented: {kind}")
    expected_numbers = {item["global_index"] for item in expected["items"]}
    actual_numbers = {int(n[:2]) for n in stats}
    require(actual_numbers == expected_numbers and len(stats) == expected["copies"],
            f"Wrong sliced object count: {stats.keys()}")
    records = {}
    for name, item in stats.items():
        n = int(name[:2])
        source = next(x for x in expected["items"] if x["global_index"] == n)
        require(item["brim_segments"] > 0 and item["first_layer_segments"] > 0,
                f"Missing brim/first layer: {name}")
        require(not any(role.startswith("Support") for role in item["roles"]),
                f"Unexpected support path: {name}")
        target_height = source["placed_max_mm"][2]
        require(abs(item["model_max_z"]-target_height) <= 0.22,
                f"Model incomplete in Z: {name}: {item['model_max_z']} vs {target_height}")
        require(min(item["min_xy"]) > 2 and max(item["max_xy"]) < 258,
                f"Toolpath outside safe bed area: {name}")
        records[name] = {**item, "roles": dict(item["roles"]),
                         "nominal_height_mm": target_height}
    names = list(records)
    gaps = []
    for i, a in enumerate(names):
        for b in names[i+1:]:
            A,B = records[a],records[b]
            dx = max(0,A["min_xy"][0]-B["max_xy"][0],B["min_xy"][0]-A["max_xy"][0])
            dy = max(0,A["min_xy"][1]-B["max_xy"][1],B["min_xy"][1]-A["max_xy"][1])
            gap = math.hypot(dx,dy)
            require(gap > 1, f"Toolpath envelopes touch: {a} {b}: {gap}")
            gaps.append({"a":a,"b":b,"gap_mm":gap})
    img_path = HERE / f"drahy-prvni-vrstvy-{number:02d}.png"
    img.save(img_path)
    return {"plate":number,"objects":records,"gaps":gaps,
            "nearest_path_envelope_gap_mm":min(x["gap_mm"] for x in gaps),
            "minimum_path_edge_mm":min(min(v["min_xy"][0],v["min_xy"][1],
                                           260-v["max_xy"][0],260-v["max_xy"][1]) for v in records.values()),
            "first_layer_preview":img_path.name}

def main():
    layout = json.loads((HERE / "kontrola-rozlozeni.json").read_text())
    profiles = json.loads((HERE / "overeni-rezu.json").read_text())
    results = []
    for number in (1,2):
        plate = layout["plates"][number-1]
        delivered = profiles["plates"][number-1]["delivered"]
        path = HERE / f"drzak-podlozka-{number:02d}-nastaveny-projekt.3mf"
        require(hashlib.sha256(path.read_bytes()).hexdigest() == delivered["sha256"],
                "Project changed since slicing")
        require(delivered["slice_metadata"]["outside"] == "false" and
                delivered["slice_metadata"]["support_used"] == "false",
                "Slicer reports outside/support")
        with ZipFile(path) as z:
            gcode = z.read("Metadata/plate_1.gcode")
        require(hashlib.sha256(gcode).hexdigest() == delivered["gcode_sha256"],
                "G-code changed")
        actual_bounds=placed_mesh_bounds(path)
        require(len(actual_bounds)==plate["copies"],"Sliced mesh copy count changed")
        worst=0.0
        for (lo,hi),item in zip(actual_bounds,plate["items"]):
            for got,want in zip(lo+hi,item["placed_min_mm"]+item["placed_max_mm"]):
                worst=max(worst,abs(got-want))
        require(worst<0.02,f"Slicer moved or resized a mesh: {worst} mm")
        parsed=parse(number,plate,gcode)
        parsed["maximum_mesh_bounds_delta_mm"]=worst
        results.append(parsed)
    result = {"state":"actual toolpaths checked; no physical print or fit evidence",
              "total_copies":sum(len(x["objects"]) for x in results),"plates":results,
              "limitations":"Axis cap friction, roll change clearance, mounting wall and PLA durability require physical fit test."}
    require(result["total_copies"] == 6,"Missing sliced piece")
    (HERE / "kontrola-drah.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"copies":result["total_copies"],
                      "nearest_gaps_mm":[round(p["nearest_path_envelope_gap_mm"],2) for p in results],
                      "minimum_edges_mm":[round(p["minimum_path_edge_mm"],2) for p in results]},ensure_ascii=False))

if __name__ == "__main__":
    main()
