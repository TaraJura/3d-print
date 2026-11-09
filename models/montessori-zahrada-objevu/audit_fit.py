#!/usr/bin/env python3
"""Independent sampled-profile fit audit; never a physical or toy-safety test.

Run with the FreeCAD shelf Python (SciPy and Shapely are bundled there)::

  /home/novakj/.cache/freecad-shelf-1.1.3/runtime/AppRun python audit_fit.py

Input: planar-profiles.json, {"parts": [{"id": "...",
        "profile": [[x,y],...], "seat": [[x,y],...]}]} in mm.
The aliases "profiles" for "parts" and "piece" for "profile" are accepted.
The outlines must represent the widest section engaged by the socket, with
piece and seat in their intended matching orientation. Coordinates may be in
different frames: each outline is independently centred on its area centroid.
Closed duplicate end points are accepted. No design files are modified.

For each convex sampled polygon pair and angle, a linear programme finds the
best arbitrary XY translation, minimizing the greatest signed violation of a
seat edge half-plane. An angular grid and a Lipschitz bound give a conservative
lower bound for this violation between sampled angles: rotating a point at
radius R by dtheta moves it no farther than R*dtheta. The bound applies to the
input polygonal approximation, not exact CAD surfaces, deformation or prints.
DE additionally searches the outside area; a numerical search is not a proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import differential_evolution, linprog, minimize
import shapely
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def polygon(points, label):
    values = np.asarray(points, dtype=float)[:, :2]
    # OCC discretization can repeat a closing endpoint at 1e-13 mm rather
    # than exactly. Remove only such duplicates; never repair true crossings.
    keep = np.r_[True, np.linalg.norm(np.diff(values, axis=0), axis=1) > 1e-8]
    values = values[keep]
    if len(values) > 3 and np.linalg.norm(values[0] - values[-1]) < 1e-8:
        values = values[:-1]
    p = Polygon(values)
    if not p.is_valid or p.is_empty or p.area <= 0:
        raise ValueError(f"Invalid outline: {label}")
    if p.convex_hull.area - p.area > max(1e-5, p.area * 1e-8):
        raise ValueError(f"Outline is not convex: {label}; LP bound cannot be used")
    center = [p.centroid.x, p.centroid.y]
    coords = np.asarray(p.exterior.coords)[:-1] - center
    p = orient(Polygon(coords), sign=1.0)
    return p, center


def rotation(angle):
    a = math.radians(float(angle))
    return np.array([[math.cos(a), -math.sin(a)],
                     [math.sin(a), math.cos(a)]])


def points_of(p):
    return np.asarray(p.exterior.coords, dtype=float)[:-1]


def seat_planes(p):
    points = points_of(orient(p, sign=1.0))
    edges = np.roll(points, -1, axis=0) - points
    lengths = np.linalg.norm(edges, axis=1)
    keep = lengths > 1e-9
    normals = np.column_stack((edges[:, 1], -edges[:, 0]))[keep]
    normals /= lengths[keep, None]
    b = (normals * points[keep]).sum(axis=1)
    return normals, b


def lp_at_angle(piece_points, normals, b, angle):
    rotated = piece_points @ rotation(angle).T
    support = np.max(rotated @ normals.T, axis=0)
    # n.(x,y) - d <= b - support: minimize the maximum signed violation d.
    a = np.column_stack((normals, -np.ones(len(normals))))
    result = linprog([0., 0., 1.], A_ub=a, b_ub=b-support,
                     bounds=[(None, None)] * 3, method="highs")
    if not result.success:
        raise RuntimeError(f"LP failed at {angle}: {result.message}")
    return float(result.x[2]), [float(result.x[0]), float(result.x[1])]


def placed(piece_points, pose):
    return Polygon(piece_points @ rotation(pose[0]).T + pose[1:3])


def search_pair(piece, seat, grid_step, seed, de_iterations):
    pv = points_of(piece)
    normals, bounds = seat_planes(seat)
    grid_count = int(math.ceil(360. / grid_step))
    actual_step = 360. / grid_count
    best = (float("inf"), None, None)
    for angle in np.arange(grid_count) * actual_step:
        value, xy = lp_at_angle(pv, normals, bounds, float(angle))
        if value < best[0]:
            best = (value, float(angle), xy)
    radius = float(np.linalg.norm(pv, axis=1).max())
    angular_bound = radius * math.radians(actual_step / 2.)
    # Reserve more than default LP feasibility tolerance for numerical error.
    solver_allowance = 0.0001
    lower_bound = best[0] - angular_bound - solver_allowance

    def violation_angle(x):
        return lp_at_angle(pv, normals, bounds, float(x[0]) % 360.)[0]

    refined = minimize(violation_angle, [best[1]], method="Nelder-Mead",
                       options={"xatol": 1e-7, "fatol": 1e-8, "maxiter": 100})
    refined_angle = float(refined.x[0]) % 360.
    refined_margin, refined_xy = lp_at_angle(pv, normals, bounds, refined_angle)
    if refined_margin > best[0]:
        refined_margin, refined_angle, refined_xy = best
    lp_pose = [refined_angle, *refined_xy]

    def outside(pose):
        return placed(pv, pose).difference(seat).area

    minx, miny, maxx, maxy = seat.bounds
    # Any completely contained convex body's area centroid lies inside seat.
    search_bounds = [(0., 360.), (minx, maxx), (miny, maxy)]
    de = differential_evolution(outside, search_bounds, seed=seed,
                                maxiter=de_iterations, popsize=10,
                                tol=1e-8, atol=1e-8, polish=True,
                                x0=np.clip(lp_pose,
                                           [x[0] for x in search_bounds],
                                           [x[1] for x in search_bounds]))
    candidates = [(outside(lp_pose), lp_pose),
                  (float(de.fun), [float(x) for x in de.x])]
    area, pose = min(candidates, key=lambda v: v[0])
    candidate = placed(pv, pose)
    return {
        "minimum_outside_area_found_mm2": round(float(area), 7),
        "outside_area_fraction": round(float(area / piece.area), 9),
        "outside_area_best_pose": {"angle_deg": round(float(pose[0]), 7),
                                   "translation_mm": [round(float(x), 7) for x in pose[1:3]]},
        "minimum_signed_edge_violation_found_mm": round(float(refined_margin), 7),
        "edge_violation_best_pose": {"angle_deg": round(float(refined_angle), 7),
                                     "translation_mm": [round(float(x), 7) for x in refined_xy]},
        "grid_min_signed_edge_violation_mm": round(float(best[0]), 7),
        "conservative_continuous_angle_lower_bound_mm": round(float(lower_bound), 7),
        "angular_grid_deg": actual_step,
        "angular_lipschitz_allowance_mm": round(float(angular_bound), 7),
        "solver_allowance_mm": solver_allowance,
        "wrong_fit_excluded_for_sampled_convex_polygons": bool(lower_bound > 0),
        "outside_search_nfev": int(de.nfev),
        "outside_search_converged": bool(de.success),
        "outside_search_message": str(de.message),
        "best_candidate_is_fully_covered": bool(seat.covers(candidate)),
    }


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=here / "planar-profiles.json")
    parser.add_argument("--output", type=Path, default=here / "nezavisla-kontrola-fitu.json")
    parser.add_argument("--grid-step", type=float, default=1.)
    parser.add_argument("--de-iterations", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20261014)
    args = parser.parse_args()
    if not 0.01 <= args.grid_step <= 10:
        parser.error("--grid-step must be in [0.01,10] degrees")
    raw = json.loads(args.input.read_text())
    entries = raw.get("parts", raw.get("profiles")) if isinstance(raw, dict) else raw
    data = []
    for entry in entries:
        name = str(entry["id"])
        piece, pc = polygon(entry.get("profile", entry.get("piece")), name + ":piece")
        seat, sc = polygon(entry["seat"], name + ":seat")
        data.append((name, piece, seat, pc, sc))
    if len(data) < 2 or len({x[0] for x in data}) != len(data):
        raise ValueError("Need at least two profiles with unique identifiers")
    output = {
        "audit": "Independent numerical 2D fit check of sampled convex profiles",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_file": args.input.name,
        "input_sha256": sha256(args.input),
        "audit_script_sha256": sha256(Path(__file__).resolve()),
        "versions": {"numpy": np.__version__, "scipy": scipy.__version__, "shapely": shapely.__version__},
        "units": "mm",
        "limitations": [
            "Duplicate consecutive/closing sample points within 1e-8 mm are removed before validation.",
            "Input boundary sampling is an approximation of the CAD outline.",
            "The LP angular bound certifies only these sampled convex polygons and planar insertion.",
            "DE minimum outside area is a best-found numerical result, not a global optimum proof.",
            "Tilting, material deformation, printing tolerances, edge wear and physical safety are not tested.",
            "Correct fit checks assume the supplied matching orientation and centroid alignment.",
        ],
        "profiles": [], "correct_fits": [], "wrong_fits": [],
    }
    for name, piece, seat, pc, sc in data:
        output["profiles"].append({"id": name, "piece_area_mm2": piece.area,
                                    "seat_area_mm2": seat.area,
                                    "piece_boundary_points": len(points_of(piece)),
                                    "seat_boundary_points": len(points_of(seat)),
                                    "piece_source_centroid": pc, "seat_source_centroid": sc})
        output["correct_fits"].append({
            "piece": name, "seat": name,
            "outside_area_mm2": piece.difference(seat).area,
            "fully_covered": bool(seat.covers(piece)),
            "minimum_boundary_clearance_mm": piece.boundary.distance(seat.boundary),
        })
    for i, (name, piece, _, _, _) in enumerate(data):
        for j, (seat_name, _, seat, _, _) in enumerate(data):
            if i == j:
                continue
            pair = {"piece": name, "seat": seat_name,
                    **search_pair(piece, seat, args.grid_step,
                                  args.seed + i*len(data)+j, args.de_iterations)}
            output["wrong_fits"].append(pair)
            print(f"{name} -> {seat_name}: area {pair['minimum_outside_area_found_mm2']:.5f} mm2; "
                  f"margin bound {pair['conservative_continuous_angle_lower_bound_mm']:.5f} mm", flush=True)
    output["summary"] = {
        "correct_fit_count": len(output["correct_fits"]),
        "correct_fits_fully_covered": sum(x["fully_covered"] for x in output["correct_fits"]),
        "wrong_fit_count": len(output["wrong_fits"]),
        "wrong_fits_excluded_for_sampled_polygons": sum(x["wrong_fit_excluded_for_sampled_convex_polygons"]
                                                         for x in output["wrong_fits"]),
        "smallest_wrong_fit_bound_mm": min(x["conservative_continuous_angle_lower_bound_mm"]
                                              for x in output["wrong_fits"]),
        "smallest_outside_area_found_mm2": min(x["minimum_outside_area_found_mm2"]
                                                  for x in output["wrong_fits"]),
        "physical_fit_tested": False,
        "toy_safety_certified": False,
    }
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(output["summary"], ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
