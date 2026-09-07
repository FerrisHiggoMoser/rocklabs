"""External magnetic dock for the latest round V6 puck; all units are mm.

The Corne interface uses a local straight edge, not an invented Keebart outline.
Run from any directory. See ../corne_dock.json for measured and assumed inputs.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "cad/outputs/round_puck_v6"
DEFAULT_CONFIG = ROOT / "cad/corne_dock.json"
PREFIX = "corne_puck_dock"


def box(x, y, z, w, d, h):
    return cq.Workplane("XY").box(w, d, h, centered=(True, True, False)).translate((x, y, z))


def cylinder(x, y, z, r, h):
    return cq.Workplane("XY").circle(r).extrude(h).translate((x, y, z))


def compound(parts):
    return cq.Compound.makeCompound([p.val() if isinstance(p, cq.Workplane) else p for p in parts])


@dataclass
class Design:
    config: dict
    derived: dict
    dock: cq.Workplane
    coupon: cq.Workplane
    puck: cq.Shape
    sensor: cq.Workplane
    feet: cq.Shape
    magnets: cq.Shape
    targets: cq.Shape
    keyboard_contact: cq.Workplane
    risers: list
    port_keepout: cq.Workplane
    screw_keepouts: cq.Shape


def build(c):
    numeric = [k for k, v in c.items() if isinstance(v, (int, float))]
    for key in numeric:
        if not math.isfinite(c[key]) or c[key] <= 0:
            raise ValueError(f"{key} must be a finite positive number")
    if c["alignment"] not in ("keycaps", "case"):
        raise ValueError("alignment must be 'keycaps' or 'case'")
    if c["keyboard_keycap_height_from_underside"] <= c["keyboard_case_height"]:
        raise ValueError("Keycap tops must be above the keyboard case/plate")
    # The shipped puck STEP is fixed: changing these values would give a false fit.
    if (c["puck_diameter"], c["puck_height"]) != (46.0, 13.5):
        raise ValueError("The source V6 puck is fixed at diameter 46 and height 13.5")
    if c["radial_clearance"] < 0.15 or c["wall"] < 1.2:
        raise ValueError("Use at least 0.15 radial clearance and 1.2 wall thickness")
    if c["underlap"] < 48 or c["arm_width"] < 28:
        raise ValueError("The four magnet locations require underlap >=48 and arm_width >=28")
    datum = c["keyboard_case_height"] if c["alignment"] == "case" else c["keyboard_keycap_height_from_underside"]
    if datum < c["keyboard_case_height"]:
        raise ValueError("Keycap top cannot be below the case/plate")
    target_stack = c["steel_target_thickness"] + c["target_adhesive_thickness"]
    pocket_depth = c["magnet_thickness"] + c["magnet_glue_allowance"]
    min_arm = pocket_depth + c["magnet_floor"]
    lift = max(0.0, c["puck_height"] + max(2.4, c["puck_foot_height"]) - c["keyboard_foot_height"] - datum,
               min_arm + target_stack - c["keyboard_foot_height"])
    keyboard_z = c["keyboard_foot_height"] + lift
    touch_z = keyboard_z + datum
    puck_z = touch_z - c["puck_height"]
    arm_top = keyboard_z - target_stack
    inner_r = c["puck_diameter"] / 2 + c["radial_clearance"]
    outer_r = inner_r + c["wall"]
    cx = -outer_r - c["case_gap"]
    foot_open_r = math.hypot(10, 5.5) + c["puck_foot_diameter"] / 2 + 1.0
    foot_open_r = max(18.0, foot_open_r)
    if inner_r - foot_open_r < 3.0:
        raise ValueError("Puck feet leave less than 3 mm of supporting shelf")
    if puck_z < 2.4 or touch_z > 35:
        raise ValueError("This cradle needs a shelf height >=2.4 and total height <=35")

    # A full-height, straight mating face blends into the circular cradle.
    outer = cylinder(cx, 0, 0, outer_r, touch_z)
    fair_left, fair_right = cx + inner_r * 0.50, -c["case_gap"]
    fairing = box((fair_left + fair_right) / 2, 0, 0, fair_right - fair_left, 36, touch_z)
    fairing = fairing.edges("|Z").fillet(2.0)
    dock = outer.union(fairing)
    arm_start = cx + inner_r * 0.5
    arm = box((arm_start + c["underlap"]) / 2, 0, 0,
              c["underlap"] - arm_start, c["arm_width"], arm_top).edges("|Z").fillet(3)
    dock = dock.union(arm)
    # Retain both devices intact: the puck rests on an annular shelf and its
    # existing rubber feet pass through one large opening all the way to the desk.
    dock = dock.cut(cylinder(cx, 0, -0.1, foot_open_r, puck_z + 0.2))
    dock = dock.cut(cylinder(cx, 0, puck_z, inner_r, touch_z + 1))
    # 0.4 mm lead-in eases insertion; the final straight radial fit remains 0.25.
    lead = (cq.Workplane("XY").workplane(offset=touch_z - 0.4).center(cx, 0).circle(inner_r)
            .workplane(offset=0.4).circle(inner_r + 0.4).loft())
    dock = dock.cut(lead)

    # Rotate the original +X USB exit toward +Y, away from the keyboard.
    # This U-notch is open at the top: no extra USB tunnel and no printed bridge.
    port = box(cx + 1.7, (outer_r + 20 + 17) / 2, puck_z + 2.4,
               16.0, outer_r - 17 + 20, touch_z + 2)
    dock = dock.cut(port)
    bosses = [(-12.5, -14.9), (12.5, -14.9), (-12.5, 14.9), (12.5, 14.9)]
    screw_tools = [cylinder(cx - y, x, -0.1, 2.65, puck_z + 1.2) for x, y in bosses]
    for tool in screw_tools:
        dock = dock.cut(tool)

    magnet_xy = [(18.0, -9.0), (18.0, 9.0), (43.0, -9.0), (43.0, 9.0)]
    pocket_r = (c["magnet_diameter"] + c["magnet_clearance"]) / 2
    magnet_parts, target_parts = [], []
    for x, y in magnet_xy:
        if abs(y) + pocket_r + 1.0 > c["arm_width"] / 2:
            raise ValueError("Magnet pocket is too close to the arm edge")
        dock = dock.cut(cylinder(x, y, arm_top - pocket_depth, pocket_r, pocket_depth + 0.1))
        magnet_parts.append(cylinder(x, y, arm_top - c["magnet_thickness"], c["magnet_diameter"] / 2, c["magnet_thickness"]))
        target_parts.append(cylinder(x, y, arm_top, c["magnet_diameter"] / 2, c["steel_target_thickness"]))
    # Optional measured keyboard foot centers in LOCAL mount coordinates. Holes
    # pass through the tongue; the generator rejects any clash with a magnet.
    for x, y in c["keyboard_feet_in_mount"]:
        radius = c["keyboard_foot_diameter"] / 2 + 0.6
        if any(math.hypot(x - mx, y - my) < radius + pocket_r + 1.2 for mx, my in magnet_xy):
            raise ValueError("A keyboard-foot relief would cut a magnet pocket: move the dock along the case edge")
        dock = dock.cut(cylinder(x, y, -0.1, radius, arm_top + 0.2))

    def place_puck(p):
        return p.rotate((0, 0, 0), (0, 0, 1), 90).translate((cx, 0, puck_z))

    puck_parts = [place_puck(cq.importers.importStep(str(SOURCE / f"cirque_round_puck_v6_{part}.step")))
                  for part in ("top", "bottom")]
    sensor = cylinder(cx, 0, touch_z - 0.99, 20, 0.99)
    feet = [cylinder(cx - y, x, puck_z - c["puck_foot_height"], c["puck_foot_diameter"] / 2, c["puck_foot_height"])
            for x, y in [(-10, -5.5), (10, -5.5), (-10, 5.5), (10, 5.5)]]
    # A local rectangular contact envelope, NOT a Keebart whole-case mockup.
    contact = box(30, 0, keyboard_z, 60, 40, c["keyboard_case_height"])
    risers = []
    if lift > 1e-5:
        for i in range(4):
            r = cylinder(i * 16, 0, 0, c["keyboard_foot_diameter"] / 2 + 2, lift)
            risers.append(r)
    # Same fitting surfaces and target coordinates, sliced down to save filament.
    coupon = dock.intersect(box(0, 0, -0.01, 220, 100, max(puck_z + 1.2, arm_top + 0.4) + 0.01))
    d = {"puck_center_x": cx, "puck_bottom_z": puck_z, "touch_plane_z": touch_z,
         "keyboard_underside_z": keyboard_z, "keyboard_lift": lift, "arm_top_z": arm_top,
         "cradle_inner_diameter": 2 * inner_r, "cradle_outer_diameter": 2 * outer_r,
         "foot_opening_diameter": 2 * foot_open_r, "magnet_centers": magnet_xy,
         "magnet_pocket_diameter": pocket_r * 2, "magnet_pocket_depth": pocket_depth,
         "magnet_floor_thickness": arm_top - pocket_depth,
         "case_gap": c["case_gap"], "alignment_datum": datum}
    return Design(c, d, dock, coupon, compound(puck_parts), sensor, compound(feet),
                  compound(magnet_parts), compound(target_parts), contact, risers, port, compound(screw_tools))


def verify(design):
    checks = []

    def check(name, ok, detail):
        checks.append({"name": name, "pass": bool(ok), "detail": detail})

    def overlap(a, b):
        a = a.val() if isinstance(a, cq.Workplane) else a
        b = b.val() if isinstance(b, cq.Workplane) else b
        return a.intersect(b).Volume()

    c, d = design.config, design.derived
    for name, part in [("dock", design.dock), ("fit coupon", design.coupon)]:
        check(f"{name} single valid solid", part.val().isValid() and part.solids().size() == 1, f"{part.solids().size()} solid(s)")
        check(f"{name} on print bed", abs(part.val().BoundingBox().zmin) < 1e-6, "Z minimum = 0 mm")
    for name, obstacle in [("original V6 enclosure", design.puck), ("puck feet", design.feet),
                            ("USB plug corridor", design.port_keepout), ("screwdriver access", design.screw_keepouts),
                            ("keyboard contact envelope", design.keyboard_contact),
                            ("magnets", design.magnets), ("steel targets", design.targets)]:
        v = overlap(design.dock, obstacle)
        check(f"no dock collision: {name}", v < 0.001, f"intersection = {v:.6f} mm3")
    check("touch and selected keyboard datum flush", abs(d["touch_plane_z"] - d["keyboard_underside_z"] - d["alignment_datum"]) < 1e-6, f"both at {d['touch_plane_z']:.3f} mm, based on configured dimensions")
    check("original puck feet remain above desk", d["puck_bottom_z"] >= c["puck_foot_height"] - 1e-6, f"feet Z = {d['puck_bottom_z'] - c['puck_foot_height']:.3f} mm")
    check("magnet pocket floor", d["magnet_floor_thickness"] >= c["magnet_floor"] - 1e-6, f"floor {d['magnet_floor_thickness']:.3f} mm")
    check("steel plus adhesive reaches keyboard", abs(d["arm_top_z"] + c["steel_target_thickness"] + c["target_adhesive_thickness"] - d["keyboard_underside_z"]) < 1e-6, "magnets meet added steel targets")
    check("four separated magnets", len(design.magnets.Solids()) == 4, f"{len(design.magnets.Solids())} magnets")
    check("clearance fit", c["radial_clearance"] >= 0.15, f"{c['radial_clearance']} mm per side")
    check("frame supports puck underside", 18 <= d["foot_opening_diameter"] / 2 < 20, "annular bearing ledge outside the feet")
    for x, y in c["keyboard_feet_in_mount"]:
        foot = cylinder(x, y, 0, c["keyboard_foot_diameter"] / 2, d["keyboard_underside_z"])
        check(f"measured keyboard foot ({x}, {y}) clear", overlap(design.dock, foot) < 0.001, "through relief")
    if not all(row["pass"] for row in checks):
        raise ValueError(json.dumps([r for r in checks if not r["pass"]], indent=2))
    return checks


def export(design, out, public=None):
    out.mkdir(parents=True, exist_ok=True)
    checks = verify(design)
    prints = {"print": design.dock, "fit_coupon": design.coupon}
    if design.risers:
        prints["keyboard_risers"] = compound(design.risers)
    previews = {"preview_puck": design.puck, "preview_sensor": design.sensor,
                "preview_feet": design.feet, "preview_hardware": design.magnets.fuse(design.targets)}
    # Upstream Corne silhouette for orientation only. It is NOT Keebart CAD and
    # never controls the manufactured cradle, tongue, or clearance checks.
    reference = cq.importers.importStep(str(ROOT / "cad/references/foostan_corne_3x6_right.step"))
    face = reference.faces("<Z").val()
    silhouette = cq.Solid.extrudeLinear(face.outerWire(), [], cq.Vector(0, 0, design.config["keyboard_case_height"]))
    bounds = silhouette.BoundingBox()
    silhouette = silhouette.translate((-bounds.xmin, 78, design.derived["keyboard_underside_z"] - bounds.zmin))
    previews["preview_keyboard_reference"] = silhouette
    # Illustrative keycaps show which height datum is selected. Their positions
    # and profile are not measured Keebart manufacturing dimensions.
    cap_z = design.derived["keyboard_underside_z"] + design.config["keyboard_keycap_height_from_underside"]
    cap_h = min(3.3, design.config["keyboard_keycap_height_from_underside"] - design.config["keyboard_case_height"])
    if cap_h > 0:
        caps = []
        positions = [(x, y - row * 19.05, 0) for x, y in
                     [(30, 26), (49.05, 29), (68.1, 31.5), (87.15, 29), (106.2, 24), (125.25, 24)]
                     for row in range(3)]
        positions += [(9.525, 17, 0), (9.525, -2.05, 0), (15, -33, 30), (35, -30, 15), (55, -28, 0)]
        for x, y, angle in positions:
            cap = box(0, 0, 0, 17.5, 16.5, cap_h).edges("|Z").fillet(2)
            cap = cap.edges(">Z").fillet(min(0.6, cap_h / 3))
            caps.append(cap.rotate((0, 0, 0), (0, 0, 1), angle).translate((x, y, cap_z - cap_h)))
        previews["preview_keycaps_reference"] = compound(caps)
    for name, obj in {**prints, **previews}.items():
        path = out / f"{PREFIX}_{name}.stl"
        # Rounded illustrative keys otherwise dominate the page download at
        # manufacturing tessellation density. Print files keep the fine mesh.
        illustrative_keys = name == "preview_keycaps_reference"
        exporters.export(obj, str(path), tolerance=0.12 if illustrative_keys else 0.035,
                         angularTolerance=0.35 if illustrative_keys else 0.08)
        mesh = trimesh.load_mesh(path, process=True)
        expected = 1 if name in ("print", "fit_coupon") else None
        # Count adjacency components without trimesh's implicit hole repair.
        count = len(trimesh.graph.connected_components(mesh.face_adjacency, nodes=np.arange(len(mesh.faces)), engine="scipy"))
        ok = mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0 and (expected is None or count == expected)
        checks.append({"name": f"{name} STL manifold", "pass": bool(ok), "detail": f"{count} closed mesh component(s); volume {mesh.volume:.2f} mm3"})
        if not ok:
            raise ValueError(f"Invalid STL export: {path}")
        if name in prints:
            exporters.export(obj, str(out / f"{PREFIX}_{name}.step"))
        if public is not None:
            public.mkdir(parents=True, exist_ok=True)
            (public / path.name).write_bytes(path.read_bytes())
    assembly = cq.Assembly(name="Corne_external_puck_dock")
    for name, obj, color in [("dock", design.dock, (0.72, 0.79, 0.58)), ("existing_puck", design.puck, (0.20, 0.23, 0.24)),
                             ("touch_surface", design.sensor, (0.08, 0.09, 0.10)), ("existing_rubber_feet", design.feet, (0.1, 0.1, 0.1)),
                             ("magnets", design.magnets, (0.6, 0.6, 0.6)), ("add_steel_targets", design.targets, (0.8, 0.8, 0.8))]:
        assembly.add(obj, name=name, color=cq.Color(*color))
    assembly.export(str(out / f"{PREFIX}_assembly.step"))
    print_mesh = trimesh.load_mesh(out / f"{PREFIX}_print.stl")
    report = {"status": "CAD verified; physical keyboard fit not yet measured", "units": "mm",
              "config": design.config, "derived": design.derived,
              "print_size": [round(float(v), 3) for v in print_mesh.extents],
              "sources": [{"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in [SOURCE / f"cirque_round_puck_v6_{part}.step" for part in ("top", "bottom")]],
              "checks": checks}
    (out / "dimensions.json").write_text(json.dumps(report, indent=2) + "\n")
    if public is not None:
        (public / f"{PREFIX}_dimensions.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(out), "print_size_mm": report["print_size"], "checks_passed": len(checks),
                      "touch_plane_mm": design.derived["touch_plane_z"], "keyboard_lift_mm": design.derived["keyboard_lift"]}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--out", type=Path, default=ROOT / "cad/outputs/corne_dock")
    parser.add_argument("--publish-models", action="store_true", help="Copy model assets into the LOCAL website models/ folder; does not deploy")
    args = parser.parse_args()
    export(build(json.loads(args.config.read_text())), args.out, ROOT / "models" if args.publish_models else None)


if __name__ == "__main__":
    main()
