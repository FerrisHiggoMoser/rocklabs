"""Neoprene travel case for the two Corne Choc Pro halves. Units: mm.

One piece of neoprene sewn into a tube, with a single seam across the middle
that makes two pockets and acts as the hinge, so the case folds shut like a
book. One elastic strap holds it closed. Sizes everything from
../corne_case.json and exports the website render, a cutting diagram and a
dimension report. Keyboard only: no puck or attachment. The keyboard model is
for the render and the fit checks, not a Keebart drawing.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "cad/references/foostan_corne_3x6_right.step"
PREFIX = "corne_case"
PITCH = 19.05

# Right-half switch centres (x, y, rotation, units) from foostan's Corne v4.1 choc PCB,
# pcbs/corne-chocolate/hotswap/corne-chocolate.kicad_pcb. KiCad's y points down; the four
# mounting holes it shares with REFERENCE put PCB point (x, y) at (x + 14.2875, -y - 57.15).
SWITCHES = [
    (19.256, 51.883, 113.88, 1.5), (41.098, 49.802, -168.06, 1), (61.913, 47.625, 180, 1),
    (33.337, -9.525, 180, 1), (33.337, 9.525, 180, 1), (33.337, 28.575, 180, 1),
    (52.388, -11.906, 180, 1), (52.388, 7.144, 180, 1), (52.388, 26.194, 180, 1),
    (71.438, -14.287, 180, 1), (71.438, 4.763, 180, 1), (71.438, 23.812, 180, 1),
    (90.487, -11.906, 180, 1), (90.487, 7.144, 180, 1), (90.487, 26.194, 180, 1),
    (109.537, -7.144, 180, 1), (109.537, 11.906, 180, 1), (109.537, 30.956, 180, 1),
    (128.588, -7.144, 180, 1), (128.588, 11.906, 180, 1), (128.588, 30.956, 180, 1),
    (14.287, 19.05, 180, 1),
]
ENCODER = (14.287, 0.0)  # upper extra position; the lower one keeps a key
FEET = [(25.0, -46.0), (146.0, -46.0), (146.0, -92.0), (34.0, -118.0)]  # illustrative, in STEP coordinates
CLEARANCE = 1.0
CORNER_RADIUS = 9.0
EDGE_RADIUS = 3.0


def shape(obj):
    return obj.val() if isinstance(obj, cq.Workplane) else obj


def compound(parts):
    return cq.Compound.makeCompound([shape(p) for p in parts])


def step_xy(x, y):
    return x + 14.2875, -y - 57.15


# Different corner and edge radii avoid the spherical corner patches that OCC meshes with gaps.
def rounded_box(w, d, h, corner, edge, z=0.0):
    body = cq.Workplane("XY").box(w, d, h, centered=(True, True, False)).edges("|Z").fillet(corner)
    return body.edges(">Z or <Z").fillet(edge).translate((0, 0, z))


def keep_behind(obj, y):
    return shape(obj).intersect(cq.Solid.makeBox(1000, 1000, 1000, cq.Vector(-500, y, -500)))


def overlap(a, b):
    return shape(a).intersect(shape(b)).Volume()


def build_half(c, checks):
    face = cq.importers.importStep(str(REFERENCE)).faces("<Z").val()
    foot, case_h = c["keyboard_foot_height"], c["keyboard_case_height"]
    case = cq.Solid.extrudeLinear(face.outerWire(), [], cq.Vector(0, 0, case_h))
    case = case.translate((0, 0, foot - case.BoundingBox().zmin))
    plate_z = foot + case_h
    cap_top = foot + c["keyboard_keycap_height_from_underside"]
    cap_z = cap_top - c["keycap_height"]
    knob_top = cap_top + c["encoder_knob_above_keycaps"]

    def cap(units):
        width = c["keycap_width"] + (units - 1) * PITCH
        body = cq.Workplane("XY").box(width, c["keycap_depth"], c["keycap_height"], centered=(True, True, False))
        return body.edges("|Z").fillet(2.0).edges(">Z").fillet(0.6).val(), width

    prototypes = {units: cap(units) for units in {s[3] for s in SWITCHES}}
    housing = cq.Workplane("XY").box(13.8, 13.8, cap_z - 1.5 - plate_z, centered=(True, True, False)).val()
    caps, switches, outside = [], [], 0
    for x, y, angle, units in SWITCHES:
        cx, cy = step_xy(x, y)
        proto, width = prototypes[units]
        caps.append(proto.rotate((0, 0, 0), (0, 0, 1), angle).translate((cx, cy, cap_z)))
        switches.append(housing.rotate((0, 0, 0), (0, 0, 1), angle).translate((cx, cy, plate_z)))
        a = math.radians(angle)
        for u, v in [(sx * width / 2, sy * c["keycap_depth"] / 2) for sx in (-1, 1) for sy in (-1, 1)]:
            corner = cq.Vector(cx + u * math.cos(a) - v * math.sin(a), cy + u * math.sin(a) + v * math.cos(a), foot + case_h / 2)
            outside += not case.isInside(corner)
    checks.append({"name": "keycaps inside the case outline", "pass": outside == 0,
                   "detail": f"{len(SWITCHES)} keys, {outside} corner(s) outside; confirms the PCB-to-case transform"})

    ex, ey = step_xy(*ENCODER)
    knob_r = c["encoder_knob_diameter"] / 2
    shaft = cq.Workplane("XY").circle(3).extrude(cap_z - 1.5 - plate_z).translate((ex, ey, plate_z))
    knob = cq.Workplane("XY").circle(knob_r).extrude(knob_top - cap_z + 1.5).edges(">Z").chamfer(0.8).translate((ex, ey, cap_z - 1.5))
    knob_inside = all(case.isInside(cq.Vector(ex + knob_r * math.cos(t), ey + knob_r * math.sin(t), foot + 1)) for t in np.linspace(0, 2 * math.pi, 12))
    checks.append({"name": "encoder knob over the case", "pass": knob_inside, "detail": f"Ø{2 * knob_r:g} knob at the upper extra key position"})
    feet = [cq.Workplane("XY").circle(c["keyboard_foot_diameter"] / 2).extrude(foot).translate((x, y, 0)) for x, y in FEET]

    bounds = face.outerWire().BoundingBox()
    shift = (-(bounds.xmin + bounds.xmax) / 2, -(bounds.ymin + bounds.ymax) / 2, 0)
    parts = {"case": case, "keycaps": compound(caps), "switches": compound(switches),
             "knob": shaft.union(knob), "feet": compound(feet)}
    parts = {name: shape(part).translate(shift) for name, part in parts.items()}
    envelope = {"length": bounds.xlen, "depth": bounds.ylen, "keycap_top": cap_top, "knob_top": knob_top,
                "height": max(cap_top, knob_top)}
    return parts, envelope


def placed(parts, angle=0, offset=(0, 0, 0)):
    return {name: part.rotate((0, 0, 0), (0, 0, 1), angle).translate(offset) for name, part in parts.items()}


def tube_size(c, env, extra_height=0.0):
    t, dt = c["neoprene_thickness"], c["divider_thickness"]
    height = env["height"] + extra_height
    flat_width = env["length"] + height + c["girth_allowance"]
    # Closed, the stretch of tube between the two halves wraps the spine as a half circle.
    web = math.pi * (height + 0.5 + 2 * t + dt) / 2
    pocket = web / 2 + env["depth"] + height + c["mouth_overlap"] + c["depth_allowance"]
    return {"width": math.ceil(2 * flat_width + 2 * c["seam_allowance"]), "length": math.ceil(2 * pocket),
            "flat_width": round(flat_width, 1), "pocket_depth": round(pocket, 1), "hinge_web": round(web, 1)}


def pocket(c, env, hollow=False, open_mouth=False):
    t = c["neoprene_thickness"]
    w, d, h = env["length"] + 2 * CLEARANCE, env["depth"] + 2 * CLEARANCE, env["height"] + 0.5
    r, corner = EDGE_RADIUS + t, CORNER_RADIUS + t
    X, Y, Z = w + 2 * t, d + 2 * t, h + 2 * t
    body = rounded_box(X, Y, Z, corner, r)
    # The tube's one long seam runs down the +X side and the mouth closes to a slit.
    body = body.cut(cq.Workplane("XY").box(1.2, Y - 2 * corner - 4, 1.0).translate((X / 2, 0, Z / 2)))
    body = body.cut(cq.Workplane("XY").box(X - 2 * corner - 4, 1.2, 1.0).translate((0, Y / 2, Z / 2)))
    if hollow:
        extra = 12 if open_mouth else 0
        body = body.cut(rounded_box(w, d + extra, h, CORNER_RADIUS, EDGE_RADIUS, z=t).translate((0, extra / 2, 0)))
    return shape(body), (X, Y, Z, r)


# Both hinge shapes reach 2.5 mm into the pockets' end walls so everything fuses into one shell.
def hinge_open(c, X, Y, Z, web):
    t = c["neoprene_thickness"]
    y = -Y / 2 - web / 2
    flat = cq.Workplane("XY").box(X, web + 5, 2 * t).translate((0, y, Z / 2))
    for z in (Z / 2 - t, Z / 2 + t):
        flat = flat.cut(cq.Workplane("XY").box(X - 10, 1.2, 1.2).translate((0, y, z)))
    return shape(flat)


def hinge_closed(c, X, Y, Z):
    t, dt = c["neoprene_thickness"], c["divider_thickness"]
    radius, zc = (Z + dt) / 2, Z + dt / 2
    ring = cq.Workplane("YZ", origin=(-X / 2, 0, 0)).center(-Y / 2, zc).circle(radius + t).circle(radius - t).extrude(X)
    half = ring.val().intersect(cq.Solid.makeBox(X + 2, radius + t + 3.5, 2 * Z + dt + 20, cq.Vector(-X / 2 - 1, -Y / 2 - radius - t - 1, -10)))
    return half.cut(cq.Solid.makeBox(X - 10, 1.2, 1.2, cq.Vector(-X / 2 + 5, -Y / 2 - radius - t - 0.6, zc - 0.6)))


def cable_pocket(c):
    w, d, t = c["cable_pocket_width"], c["cable_pocket_height"], c["neoprene_thickness"]
    seam, rise = c["cable_pocket_seam"], t + c["cable_pocket_room"]
    outer = cq.Workplane("XY").box(w, d, rise, centered=(True, True, False)).edges("|Z").fillet(8).edges(">Z").fillet(2.5)
    # Open along the +Y edge; the other three edges are where it is sewn on.
    room = cq.Workplane("XY").box(w - 2 * seam, d - seam + 1, rise - t, centered=(True, True, False)).translate((0, (seam + 1) / 2, 0))
    return shape(outer.cut(room)), rise


def cable_pocket_position(c, size, Y, Z, r):
    # Along the fabric from the middle seam, round the pocket's end, to the middle of its back.
    to_back = size["hinge_web"] / 2 + (Z / 2 - r) + math.pi * r / 2 + (Y / 2 - r)
    fold = size["width"] / 2
    x_centre = (fold + size["width"] - c["seam_allowance"]) / 2
    return {"from_fold": round(x_centre - c["cable_pocket_width"] / 2 - fold),
            "from_end": round(size["length"] / 2 - to_back - c["cable_pocket_height"] / 2)}


def convex_hull(points):
    pts = sorted(set(points))

    def turn(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) > 1 and turn(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) > 1 and turn(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def rounded_rect_points(y0, y1, z0, z1, r, n=24):
    points = []
    for cy, cz, start in [(y1 - r, z1 - r, 0), (y0 + r, z1 - r, 90), (y0 + r, z0 + r, 180), (y1 - r, z0 + r, 270)]:
        points += [(cy + r * math.cos(math.radians(start + 90 * i / n)), cz + r * math.sin(math.radians(start + 90 * i / n))) for i in range(n + 1)]
    return points


def strap(c, outline):
    # A stretched loop follows the convex hull of the closed case's cross-section.
    bt, bw = c["elastic_thickness"], c["elastic_width"]
    hull = convex_hull([(round(y, 4), round(z, 4)) for y, z in outline])

    def loop(offset):
        return cq.Workplane("YZ", origin=(-bw / 2, 0, 0)).polyline(hull).close().offset2D(offset).extrude(bw)

    solid = loop(bt + 0.05).cut(loop(0.05))
    centreline = sum(math.dist(hull[i - 1], hull[i]) for i in range(len(hull))) + math.pi * (bt + 0.1)
    return shape(solid), centreline


def elastic_cut(c, centreline):
    return math.ceil(centreline * c["elastic_stretch"] + c["elastic_join_overlap"])


def size_of(parts):
    bb = compound(parts).BoundingBox()
    return [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]


def diagram_svg(size, seam, patch):
    width, length, middle = size["width"], size["length"], size["length"] / 2
    m = 34
    x0, y0, x1, y1 = m, m, m + width, m + length
    xm, ym = x0 + width / 2, y0 + middle
    pw, ph = patch["size"]
    px, py = xm + patch["from_fold"], y0 + patch["from_end"]
    page_w, page_h = width + 2 * m, length + 2 * m
    font = 'font-family="Helvetica, Arial, sans-serif" text-anchor="middle" font-size="13"'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {page_w} {page_h}" width="{2 * page_w}" height="{2 * page_h}">
  <rect width="{page_w}" height="{page_h}" fill="#fff"/>
  <rect x="{x0}" y="{y0}" width="{width}" height="{length}" fill="none" stroke="#111" stroke-width="1.4"/>
  <g stroke="#555" stroke-width="1" stroke-dasharray="6 4">
    <line x1="{x0 + seam}" y1="{y0}" x2="{x0 + seam}" y2="{y1}"/>
    <line x1="{x1 - seam}" y1="{y0}" x2="{x1 - seam}" y2="{y1}"/>
  </g>
  <line x1="{xm}" y1="{y0}" x2="{xm}" y2="{y1}" stroke="#111" stroke-width="1" stroke-dasharray="16 4 3 4"/>
  <line x1="{x0}" y1="{ym}" x2="{x1}" y2="{ym}" stroke="#b3261e" stroke-width="2.4"/>
  <polyline points="{px},{py} {px},{py + ph} {px + pw},{py + ph} {px + pw},{py}" fill="none" stroke="#2f6b3f" stroke-width="1.6"/>
  <line x1="{px}" y1="{py}" x2="{px + pw}" y2="{py}" stroke="#2f6b3f" stroke-width="1.6" stroke-dasharray="5 4"/>
  <g {font} fill="#222">
    <text x="{xm}" y="{y0 - 12}">{width} mm</text>
    <text transform="translate({x1 + 20} {y0 + length / 4}) rotate(90)">{length} mm</text>
    <text x="{(x0 + xm) / 2}" y="{y0 + 24}">OPENING</text>
    <text x="{(x0 + xm) / 2}" y="{y1 - 14}">OPENING</text>
    <text transform="translate({xm - 7} {y0 + length / 4}) rotate(-90)">FOLD</text>
    <text transform="translate({x0 + seam + 16} {y0 + length * 0.75}) rotate(-90)">SEAM {seam:g} MM IN</text>
    <text transform="translate({x1 - seam - 9} {y0 + length * 0.75}) rotate(-90)">SEAM {seam:g} MM IN</text>
  </g>
  <g font-family="Helvetica, Arial, sans-serif" text-anchor="middle" font-size="11" fill="#2f6b3f">
    <text x="{px + pw / 2}" y="{py + ph / 2 - 8}" font-size="12">CABLE POCKET</text>
    <text x="{px + pw / 2}" y="{py + ph / 2 + 8}">{pw:g} × {ph:g} mm patch</text>
    <text x="{px + pw / 2}" y="{py + ph / 2 + 22}">open edge at the top</text>
  </g>
  <g {font} fill="#b3261e">
    <text x="{(xm + x1) / 2}" y="{ym - 9}">MIDDLE SEAM</text>
    <text x="{(xm + x1) / 2}" y="{ym + 21}">{middle:g} mm from each end</text>
  </g>
</svg>
"""


def export_stl(obj, path, fine=True):
    exporters.export(obj, str(path), tolerance=0.05 if fine else 0.12, angularTolerance=0.15 if fine else 0.35)
    mesh = trimesh.load_mesh(path, process=True)
    return bool(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0), mesh.volume


def build(c):
    checks = []
    right, env = build_half(c, checks)
    t, dt = c["neoprene_thickness"], c["divider_thickness"]
    size = tube_size(c, env)
    knob_10mm = tube_size(c, env, extra_height=env["keycap_top"] + 10 - env["height"])

    solid, (X, Y, Z, r) = pocket(c, env)
    hollow, _ = pocket(c, env, hollow=True)
    open_mouth, _ = pocket(c, env, hollow=True, open_mouth=True)
    top, web = 2 * Z + dt, size["hinge_web"]

    # Open, the second pocket lies past the hinge, mirrored front to back. Closed, it sits
    # upside down on the first, so the left half meets the right one key over key.
    patch, rise = cable_pocket(c)

    def case(lower, upper, is_open):
        if is_open:
            far = (0, -Y - web, 0)
            return (lower.fuse(hinge_open(c, X, Y, Z, web)).fuse(upper.mirror("XZ").translate(far))
                    .fuse(patch.mirror("XY").mirror("XZ").translate(far)))
        return (lower.fuse(hinge_closed(c, X, Y, Z)).fuse(upper.mirror("XY").translate((0, 0, top)))
                .fuse(patch.translate((0, 0, top))))

    case_closed, case_open = case(solid, solid, False), case(solid, solid, True)
    divider = shape(cq.Workplane("XY").box(X - 8, Y - 8, dt, centered=(True, True, False)).edges("|Z").fillet(4).translate((0, 0, Z)))
    radius = (Z + dt) / 2
    outline = (rounded_rect_points(-Y / 2, Y / 2, 0, Z, r) + rounded_rect_points(-Y / 2, Y / 2, Z + dt, top, r)
               + rounded_rect_points(-c["cable_pocket_height"] / 2, c["cable_pocket_height"] / 2, top, top + rise, 2.5)
               + [(-Y / 2 + (radius + t) * math.cos(a), Z + dt / 2 + (radius + t) * math.sin(a)) for a in np.linspace(math.pi / 2, 3 * math.pi / 2, 49)])
    band, band_line = strap(c, outline)

    in_lower = placed(right, 0, (0, 0, t))
    in_upper = {k: v.mirror("XY").translate((0, 0, top - t)) for k, v in right.items()}
    case_hollow = case(hollow, hollow, False)
    clash = overlap(compound([*in_lower.values(), *in_upper.values()]), case_hollow)
    checks.append({"name": "both halves fit inside their pockets", "pass": clash < 0.5,
                   "detail": f"{clash:.2f} mm3 overlap with the 3 mm fabric; {CLEARANCE:g} mm play each side"})
    clash = overlap(band, compound([case_closed, divider]))
    checks.append({"name": "strap sits on the closed case", "pass": clash < 0.5, "detail": f"{clash:.2f} mm3 overlap"})

    # Open view: the left half slides into the far pocket, whose mouth faces the default camera.
    slide = 0.55 * env["depth"]
    sliding_half = {k: v.mirror("XZ").translate((0, -Y - web - slide, t)) for k, v in right.items()}
    case_loading = case(solid, open_mouth, True)
    clash = overlap(compound(sliding_half.values()), case_loading)
    checks.append({"name": "half slides through the open mouth", "pass": clash < 0.5, "detail": f"{clash:.2f} mm3 overlap"})

    loops = {"closed": [elastic_cut(c, band_line)]}
    checks.append({"name": "elastic within the 1 m from the guide", "pass": sum(loops["closed"]) <= 1000,
                   "detail": f"one loop of {loops['closed'][0]} mm"})

    modes = {
        "closed": {"sleeves": [case_closed], "strap": [band], "divider": [divider]},
        "open": {"sleeves": [case_loading], **{k: [v] for k, v in sliding_half.items()}},
    }
    # Cut through both encoder knobs, the tallest part of each half, which meet face to face.
    cut_y = in_lower["knob"].Center().y
    cutaway = {"sleeves": [case_hollow], "strap": [band], "divider": [divider], **{k: [in_lower[k], in_upper[k]] for k in right}}
    modes["cutaway"] = {k: [o for o in (keep_behind(o, cut_y) for o in v) if o.Volume() > 0.01] for k, v in cutaway.items()}
    derived = {
        "keyboard_half": {"length": round(env["length"], 1), "depth": round(env["depth"], 1), "keycap_top_above_desk": env["keycap_top"],
                          "knob_top_above_desk": env["knob_top"], "packed_height": env["height"]},
        "piece": {**size, "pieces": 1, "middle_seam_from_end": size["length"] / 2},
        "piece_if_knob_10mm": [knob_10mm["width"], knob_10mm["length"]],
        "cable_pocket": {"size": [c["cable_pocket_width"], c["cable_pocket_height"]], "seam": c["cable_pocket_seam"],
                         **cable_pocket_position(c, size, Y, Z, r)},
        "pocket_outside": [round(X, 1), round(Y, 1), round(Z, 1)],
        "packed": {"closed": size_of([case_closed, band, divider]), "open": size_of([case_open])},
        "elastic_loops": loops,
        "divider": [round(X - 8, 1), round(Y - 8, 1)],
    }
    return modes, derived, checks, diagram_svg(size, c["seam_allowance"], derived["cable_pocket"])


def export(c, out, public=None):
    modes, derived, checks, svg = build(c)
    out.mkdir(parents=True, exist_ok=True)
    targets = [out] + ([public] if public is not None else [])
    for mode, parts in modes.items():
        for part, objs in parts.items():
            path = out / f"{PREFIX}_{mode}_{part}.stl"
            ok, volume = export_stl(compound(objs), path, fine=part not in ("keycaps", "switches"))
            checks.append({"name": f"{mode} {part} STL closed", "pass": ok, "detail": f"volume {volume:.0f} mm3"})
            if public is not None:
                (public / path.name).write_bytes(path.read_bytes())
    report = {"status": "Render and cutting diagram; keyboard inputs as listed, encoder knob height assumed",
              "units": "mm", "config": c, "derived": derived, "checks": checks}
    for folder in targets:
        (folder / f"{PREFIX}_diagram.svg").write_text(svg)
        (folder / f"{PREFIX}_dimensions.json").write_text(json.dumps(report, indent=2) + "\n")
    failed = [check for check in checks if not check["pass"]]
    print(json.dumps({"output": str(out), "derived": derived, "checks_passed": len(checks) - len(failed), "failed": failed}, indent=2))
    if failed:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "cad/corne_case.json")
    parser.add_argument("--out", type=Path, default=ROOT / "cad/outputs/corne_case")
    parser.add_argument("--publish-models", action="store_true", help="Copy the render models into the LOCAL website models/ folder; does not deploy")
    args = parser.parse_args()
    export(json.loads(args.config.read_text()), args.out, ROOT / "models" if args.publish_models else None)


if __name__ == "__main__":
    main()
