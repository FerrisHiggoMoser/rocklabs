"""Separate mechanically retained, angled Corne/V6 accessory. All units are mm.

The existing puck and magnetic dock are read-only inputs. Nothing here deploys.
Keyboard underside = Z0, keyboard interior = +X, cable exit = +Y.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
from pathlib import Path
import zipfile

import cadquery as cq
from cadquery import exporters
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "cad/outputs/round_puck_v6"
PREFIX = "corne_puck_suspended"


def shape(obj):
    return obj.val() if isinstance(obj, cq.Workplane) else obj


def box(x, y, z, w, d, h):
    return cq.Workplane("XY").box(w, d, h, centered=(True, True, False)).translate((x, y, z))


def cylinder(x, y, z, r, h):
    return cq.Workplane("XY").circle(r).extrude(h).translate((x, y, z))


def hexagon(x, y, z, across_flats, h):
    return cq.Workplane("XY").polygon(6, across_flats / math.cos(math.pi / 6)).extrude(h).translate((x, y, z))


def compound(parts):
    return cq.Compound.makeCompound([shape(p) for p in parts])


def overlap(a, b):
    return shape(a).intersect(shape(b)).Volume()


def on_bed(obj):
    obj = shape(obj)
    bounds = obj.BoundingBox()
    return obj.translate((-bounds.xmin, -bounds.ymin, -bounds.zmin))


def arrange(parts, gap=8):
    laid_out, x = [], 0
    for part in parts:
        part = on_bed(part)
        laid_out.append(part.translate((x, 0, 0)))
        x += part.BoundingBox().xlen + gap
    return compound(laid_out)


def fastener(x, y, seat_z, length):
    # ISO 4762 M3 socket head; no helical thread geometry in the preview.
    bolt = cylinder(x, y, seat_z - length, 1.5, length).union(cylinder(x, y, seat_z, 2.75, 3))
    washer = cylinder(x, y, seat_z - 0.5, 3.5, 0.5).cut(cylinder(x, y, seat_z - 0.6, 1.6, 0.7))
    return bolt, washer


def nut(x, y, z):
    return hexagon(x, y, z, 5.5, 2.4).cut(cylinder(x, y, z - 0.1, 1.5, 2.6))


@dataclass
class Design:
    config: dict
    derived: dict
    parts: dict
    prints: dict
    previews: dict
    coupon_parts: list
    obstacles: dict
    local_carrier: cq.Shape
    local_retainer: cq.Shape
    local_puck: cq.Shape


def build(c):
    for key, value in c.items():
        if key != "notes" and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0):
            raise ValueError(f"{key} must be a finite positive number")
    ranges = {"tilt_degrees": (10, 25), "keyboard_case_height": (6, 11),
              "keyboard_upper_lip": (3, 6), "keyboard_underlap": (10, 18),
              "clamp_span": (56, 64), "pad_thickness": (0.5, 1.2),
              "puck_center_offset": (45, 50), "touch_center_height": (17, 21),
              "radial_clearance": (0.15, 0.45), "puck_foot_height": (2, 6)}
    for key, (lo, hi) in ranges.items():
        if not lo <= c[key] <= hi:
            raise ValueError(f"{key} must be between {lo} and {hi}")
    if c["keyboard_keycap_height_from_underside"] <= c["keyboard_case_height"] + c["pad_thickness"] + 4:
        raise ValueError("Keycap height must leave room above the 4 mm upper jaw; also check full key travel physically")

    angle = c["tilt_degrees"]
    cx = -c["puck_center_offset"]
    floor, puck_h, top_gap, ring_t = 2.8, 13.5, 0.25, 2.4
    rim = floor + puck_h + top_gap
    origin_z = c["touch_center_height"] - (floor + puck_h) * math.cos(math.radians(angle))
    bore, outside = 23 + c["radial_clearance"], 26.0
    lower_z = -c["pad_thickness"] - 5
    upper_z = c["keyboard_case_height"] + c["pad_thickness"]
    span, lip, underlap = c["clamp_span"], c["keyboard_upper_lip"], c["keyboard_underlap"]
    bolt_xy = [(-7, y) for y in (-span / 2 + 6, span / 2 - 6)]
    ear_xy = [(28 * math.cos(math.radians(a)), 28 * math.sin(math.radians(a))) for a in (55, 180, 305)]
    # Pick the shortest standard bolt with one full pitch beyond the nut.
    clamp_seat = upper_z + 4 + 0.5
    clamp_length = next(length for length in (16, 20, 25, 30) if clamp_seat - lower_z + 0.5 <= length)

    def place(obj):
        return shape(obj).rotate((0, 0, 0), (0, 1, 0), angle).translate((cx, 0, origin_z))

    def unplace(obj):
        return shape(obj).translate((-cx, 0, -origin_z)).rotate((0, 0, 0), (0, 1, 0), -angle)

    # Lower case jaw plus a padded edge stop. Upper jaw is a separate part.
    lower = box((underlap - 14) / 2, 0, lower_z, underlap + 14, span, 5).edges("|Z").fillet(2)
    stop = box(-2.4, 0, lower_z, 3.2, span - 8, c["keyboard_case_height"] - lower_z)
    lower = lower.union(stop)
    upper = box((lip - 14) / 2, 0, upper_z, lip + 14, span, 4).edges("|Z").fillet(1)
    hardware, clamp_tools, nut_tools = [], [], []
    for x, y in bolt_xy:
        through = cylinder(x, y, lower_z - 8, 1.7, clamp_seat - lower_z + 12)
        pocket = hexagon(x, y, lower_z - 15, 5.8, 17.65)
        lower, upper = lower.cut(through).cut(pocket), upper.cut(through)
        clamp_tools += [through]
        nut_tools += [pocket]
        hardware += [*fastener(x, y, clamp_seat, clamp_length), nut(x, y, lower_z)]

    # Cylinder and three bolt ears; remove bores after joining the gussets so
    # feet, the plug, and bottom screwdriver paths also clear the structure.
    cup = cylinder(0, 0, 0, outside, rim)
    ring = cylinder(0, 0, rim, outside, ring_t).cut(cylinder(0, 0, rim - 0.1, 21, ring_t + 0.2))
    for x, y in ear_xy:
        cup = cup.union(cylinder(x, y, 0, 4.8, rim))
        ring = ring.union(cylinder(x, y, rim, 4.8, ring_t))
    carrier = cq.Workplane(obj=place(cup)).union(lower)
    for y in (-17, 17):
        # Two deep webs transfer touch load into the lower jaw.
        web = (cq.Workplane("XZ").polyline([(cx + 10, 4), (-14, -c["pad_thickness"]),
                (underlap - 2, -c["pad_thickness"]), (underlap - 2, lower_z),
                (cx + 20, lower_z - 4), (cx + 8, -7)]).close().extrude(3, both=True).translate((0, y, 0)))
        carrier = carrier.union(web)

    bore_tool = cylinder(0, 0, floor, bore, 60)
    foot_tool = cylinder(0, 0, -35, 18, 35 + floor)
    port_tool = box(1.7, 38.5, floor + 2.4, 16, 43, 40)
    local_tools = [bore_tool, foot_tool, port_tool]
    screw_paths = []
    for x, y in [(-12.5, -14.9), (12.5, -14.9), (-12.5, 14.9), (12.5, 14.9)]:
        tool = cylinder(-y, x, -35, 2.65, 35 + floor)
        local_tools.append(tool)
        screw_paths.append(tool)
    for x, y in ear_xy:
        hole = cylinder(x, y, -15, 1.7, 60)
        # Bottom-open hex sockets, with room to insert the nuts from below.
        pocket = hexagon(x, y, -15, 5.8, 17.65)
        local_tools += [hole, pocket]
        ring = ring.cut(hole)
        hardware += [place(p) for p in (*fastener(x, y, rim + ring_t + 0.5, 20), nut(x, y, 0))]
    for tool in local_tools:
        carrier = carrier.cut(place(tool))
    for tool in clamp_tools + nut_tools:
        carrier = carrier.cut(tool)

    # The ring is fitted AFTER dropping in the intact puck. It covers only
    # the enclosure's outer rim, with a 42 mm opening around the 40 mm sensor.
    ring_local = shape(ring)
    parts = {"carrier": shape(carrier), "upper_jaw": shape(upper), "retainer": place(ring)}
    puck_parts = [shape(cq.importers.importStep(str(SOURCE / f"cirque_round_puck_v6_{part}.step")))
                  .rotate((0, 0, 0), (0, 0, 1), 90).translate((0, 0, floor)) for part in ("top", "bottom")]
    puck_local = compound(puck_parts)
    sensor = cylinder(0, 0, floor + puck_h - 0.99, 20, 0.99)
    feet = compound([cylinder(-y, x, floor - c["puck_foot_height"], 5, c["puck_foot_height"])
                     for x, y in [(-10, -5.5), (10, -5.5), (-10, 5.5), (10, 5.5)]])
    pads = compound([box(underlap / 2, 0, -c["pad_thickness"], underlap - 1, span - 6, c["pad_thickness"]),
                     box(lip / 2, 0, c["keyboard_case_height"], lip - 1, span - 6, c["pad_thickness"]),
                     box(-0.4, 0, 0, 0.8, span - 10, c["keyboard_case_height"])])
    contact = box(45, 0, 0, 90, span + 10, c["keyboard_case_height"])
    # A conservative above-case keepout beyond the required bare edge ledge.
    key_keepout = box(40 + lip, 0, c["keyboard_case_height"], 80, span + 10, 35)
    # Actual plug envelope; the carrier's U-notch extends farther upward.
    plug = box(1.7, 38.5, floor + 2.4, 16, 43, 6.4)
    previews = {"puck": place(puck_local), "sensor": place(sensor), "feet": place(feet),
                "hardware": compound(hardware), "pads": pads}

    # Carrier prints on its side: rotate the gusset plane into the bed plane.
    # Local support may be needed beneath the curved cradle and holes.
    prints = {"carrier": on_bed(parts["carrier"].rotate((0, 0, 0), (1, 0, 0), 90)),
              "upper_jaw": on_bed(upper), "retainer": on_bed(ring)}
    fit_ring = cylinder(0, 0, 0, outside, 2).cut(cylinder(0, 0, -0.1, bore, 2.2))
    # Exact clamp interface, as a cheap independent coupon. Print the lower
    # coupon on its side, matching the full carrier layer direction.
    coupon_parts = [on_bed(shape(lower).rotate((0, 0, 0), (1, 0, 0), 90)), on_bed(upper), on_bed(fit_ring)]
    derived = {"tilt_degrees_relative_to_keyboard": angle, "cradle_inner_diameter": bore * 2,
               "retainer_opening_diameter": 42, "sensor_diameter": 40, "puck_floor": floor,
               "puck_top_local": floor + puck_h, "retainer_underside_local": rim,
               "puck_axial_clearance": top_gap, "touch_center_z": c["touch_center_height"],
               "puck_center_x": cx, "carrier_origin_z": origin_z,
               "required_straight_edge": span, "required_bare_top_ledge": lip,
               "required_clear_underside_strip": underlap, "clamp_bolt_centers": bolt_xy,
               "ring_bolt_centers_local": ear_xy, "clamp_bolt_length": clamp_length,
               "retainer_bolt_length": 20, "clamp_bolt_projection_below_nut": clamp_length - (clamp_seat - lower_z),
               "retainer_bolt_projection_below_nut": 20 - (rim + ring_t + 0.5),
               "pad_cut_sizes": [[underlap - 1, span - 6], [lip - 1, span - 6], [span - 10, c["keyboard_case_height"]]],
               "print_orientation": "Carrier on its side; upper jaw and retainer flat. Inspect local cradle supports in slicer.",
               "hardware": [f"2 x M3 x {clamp_length} socket-head bolts (keyboard clamp)",
                            "3 x M3 x 20 socket-head bolts (puck ring)", "5 x M3 DIN 934 nuts, 5.5 AF x 2.4 high",
                            "5 x M3 washers, OD 7 / ID 3.2 / thickness 0.5", "Firm rubber jaw and edge pads"]}
    return Design(c, derived, parts, prints, previews, coupon_parts,
                  {"existing puck": place(puck_local), "sensor": place(sensor), "feet": place(feet),
                   "keyboard case envelope": contact, "key travel beyond bare ledge": key_keepout,
                   "USB plug corridor": place(plug), "case screwdriver paths": place(compound(screw_paths)),
                   "hardware": previews["hardware"], "pads": pads},
                  unplace(carrier), ring_local, puck_local)


def verify(design):
    checks = []

    def check(name, ok, detail):
        checks.append({"name": name, "pass": bool(ok), "detail": detail})

    for name, part in design.parts.items():
        check(f"{name}: one valid solid", part.isValid() and len(part.Solids()) == 1, f"{len(part.Solids())} solid(s)")
        for label, obstacle in design.obstacles.items():
            v = overlap(part, obstacle)
            check(f"{name}: clear of {label}", v < 0.001, f"intersection {v:.6f} mm3")
    for (a, one), (b, two) in itertools.combinations(design.parts.items(), 2):
        v = overlap(one, two)
        check(f"{a} / {b}: assembled separation", v < 0.001, f"intersection {v:.6f} mm3")
    for name, part in design.prints.items():
        check(f"{name}: print bed datum", abs(part.BoundingBox().zmin) < 1e-6, "Z minimum = 0")
    for i, part in enumerate(design.coupon_parts):
        check(f"coupon {i + 1}: valid connected solid on bed", part.isValid() and len(part.Solids()) == 1 and abs(part.BoundingBox().zmin) < 1e-6, "Exact jaw surfaces or bore gauge")

    # Check retention using the actual source STEP, rather than just a circle:
    # a small motion in every local axis must meet a physical stop.
    enclosure = compound([design.local_carrier, design.local_retainer])
    for label, delta in [("left", (-1, 0, 0)), ("right", (1, 0, 0)), ("front", (0, -1, 0)),
                         ("rear", (0, 1, 0)), ("up into retainer", (0, 0, 1)), ("down into shelf", (0, 0, -1))]:
        v = overlap(enclosure, design.local_puck.translate(delta))
        check(f"puck movement blocked: {label}", v > 0.1, f"1 mm translation meets stop ({v:.3f} mm3); geometric retention, not a load test")
    # With the retainer removed, the assembled puck can be inserted vertically.
    for height in (1, 8, 20):
        v = overlap(design.local_carrier, design.local_puck.translate((0, 0, height)))
        check(f"puck insertion clear at +{height} mm", v < 0.001, f"intersection {v:.6f} mm3")
    for label in ("clamp", "retainer"):
        extension = design.derived[f"{label}_bolt_projection_below_nut"]
        check(f"{label}: full nut engagement", extension >= 0.5, f"{extension:.3f} mm bolt projection beyond 2.4 mm nut")
    check("touch surface fully uncovered", design.derived["retainer_opening_diameter"] >= 42, "42 mm opening around 40 mm active surface")
    failures = [r for r in checks if not r["pass"]]
    if failures:
        raise ValueError(json.dumps(failures, indent=2))
    return checks


def add_keyboard_reference(design):
    # Reuse the attributed, explicitly illustrative assets from the old dock,
    # translating their former Z2 keyboard underside to this model's Z0 datum.
    # They never control the manufactured geometry or the collision tests.
    meshes = {}
    for name in ("keyboard_reference", "keycaps_reference"):
        path = ROOT / "models" / f"corne_puck_dock_preview_{name}.stl"
        mesh = trimesh.load_mesh(path)
        if name == "keyboard_reference":
            mesh.vertices[:, 2] = (mesh.vertices[:, 2] - 2) * design.config["keyboard_case_height"] / 8.2
        else:
            mesh.vertices[:, 2] += design.config["keyboard_keycap_height_from_underside"] - 18
        meshes[name] = mesh
    return meshes


def export(design, out, public=None):
    checks = verify(design)
    out.mkdir(parents=True, exist_ok=True)
    prints = {**design.prints, "print_plate": arrange(design.prints.values()),
              "fit_coupon": arrange(design.coupon_parts)}
    objects = {**prints, **{f"preview_{k}": v for k, v in {**design.parts, **design.previews}.items()}}
    print_sizes = {}
    for name, obj in objects.items():
        path = out / f"{PREFIX}_{name}.stl"
        exporters.export(obj, str(path), tolerance=0.04, angularTolerance=0.1)
        mesh = trimesh.load_mesh(path, process=True)
        count = len(trimesh.graph.connected_components(mesh.face_adjacency, nodes=np.arange(len(mesh.faces)), engine="scipy"))
        expected = 3 if name in ("print_plate", "fit_coupon") else (1 if name in design.prints else None)
        ok = mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0 and (expected is None or count == expected)
        if name in prints:
            ok = ok and abs(mesh.bounds[0, 2]) < 1e-5
            print_sizes[name] = [round(float(v), 3) for v in mesh.extents]
            exporters.export(obj, str(out / f"{PREFIX}_{name}.step"))
        checks.append({"name": f"{name}: closed STL", "pass": bool(ok), "detail": f"{count} component(s); {mesh.volume:.2f} mm3"})
        if not ok:
            raise ValueError(f"Invalid mesh export: {name}")
        if public:
            public.mkdir(parents=True, exist_ok=True)
            (public / path.name).write_bytes(path.read_bytes())

    references = add_keyboard_reference(design)
    for name, mesh in references.items():
        path = out / f"{PREFIX}_preview_{name}.stl"
        mesh.export(path)
        if public:
            (public / path.name).write_bytes(path.read_bytes())
    # An illustrative 35-degree keyboard tent shows the entire assembly moving
    # together, with no desk under the accessory. It is not the user's mount CAD.
    tent_transform = trimesh.transformations.rotation_matrix(math.radians(35), [0, 1, 0], [90, 0, 0])
    tent_transform[2, 3] += 35
    for name in [k for k in objects if k.startswith("preview_")] + [f"preview_{k}" for k in references]:
        mesh = trimesh.load_mesh(out / f"{PREFIX}_{name}.stl")
        mesh.apply_transform(tent_transform)
        path = out / f"{PREFIX}_{name.replace('preview_', 'suspended_', 1)}.stl"
        mesh.export(path)
        if public:
            (public / path.name).write_bytes(path.read_bytes())

    assembly = cq.Assembly(name="Corne_suspended_angled_accessory")
    for name, obj in {**design.parts, **design.previews}.items():
        color = (0.70, 0.78, 0.56) if name in design.parts else (0.25, 0.28, 0.27)
        assembly.add(obj, name=name, color=cq.Color(*color))
    assembly.export(str(out / f"{PREFIX}_assembly.step"))
    sources = [SOURCE / f"cirque_round_puck_v6_{part}.step" for part in ("top", "bottom")]
    report = {"status": "CAD checked; physical fit and suspended load not yet tested", "units": "mm", "config": design.config,
              "derived": design.derived, "print_sizes": print_sizes, "checks": checks,
              "sources": [{"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]}
    report_text = json.dumps(report, indent=2) + "\n"
    (out / "dimensions.json").write_text(report_text)
    if public:
        (public / f"{PREFIX}_dimensions.json").write_text(report_text)
    # One download contains only manufacturing files plus their instructions.
    guide = ROOT / "cad/outputs/corne_suspended/README.md"
    if guide.exists():
        bundle = out / f"{PREFIX}_print_kit.zip"
        with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
            for name in prints:
                for suffix in ("stl", "step"):
                    path = out / f"{PREFIX}_{name}.{suffix}"
                    archive.write(path, path.name)
            archive.write(guide, "README.md")
            archive.write(out / "dimensions.json", "dimensions.json")
        if public:
            (public / bundle.name).write_bytes(bundle.read_bytes())
    print(json.dumps({"output": str(out), "checks_passed": len(checks), "print_sizes": print_sizes,
                      "hardware": design.derived["hardware"]}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "cad/corne_suspended.json")
    parser.add_argument("--out", type=Path, default=ROOT / "cad/outputs/corne_suspended")
    parser.add_argument("--publish-models", action="store_true", help="Copy only this new design's assets into local models/; no deployment")
    args = parser.parse_args()
    export(build(json.loads(args.config.read_text())), args.out, ROOT / "models" if args.publish_models else None)


if __name__ == "__main__":
    main()
