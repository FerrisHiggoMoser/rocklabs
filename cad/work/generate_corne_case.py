"""Neoprene travel case for the two Corne Choc Pro halves. Units: mm.

Sizes two sewn sleeves and their elastic bands from ../corne_case.json and
exports the website render, a 1:1 A4 cut pattern and a dimension report.
Keyboard only: no puck or attachment. The keyboard model is for the render
and the fit checks, not a Keebart drawing.
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


def mirrored(parts):
    return {name: part.mirror("YZ") for name, part in parts.items()}


def placed(parts, angle=0, offset=(0, 0, 0)):
    return {name: part.rotate((0, 0, 0), (0, 0, 1), angle).translate(offset) for name, part in parts.items()}


def sleeve(c, env, hollow=False, open_mouth=False):
    t = c["neoprene_thickness"]
    w, d, h = env["length"] + 2 * CLEARANCE, env["depth"] + 2 * CLEARANCE, env["height"] + 0.5
    r, corner = EDGE_RADIUS + t, CORNER_RADIUS + t
    X, Y, Z = w + 2 * t, d + 2 * t, h + 2 * t
    body = rounded_box(X, Y, Z, corner, r)
    # The side seams and the mouth show as creases once the sleeve is turned right side out.
    for side in (-1, 1):
        body = body.cut(cq.Workplane("XY").box(1.2, Y - 2 * corner - 4, 1.0).translate((side * X / 2, 0, Z / 2)))
    body = body.cut(cq.Workplane("XY").box(X - 2 * corner - 4, 1.2, 1.0).translate((0, Y / 2, Z / 2)))
    if hollow:
        extra = 12 if open_mouth else 0
        body = body.cut(rounded_box(w, d + extra, h, CORNER_RADIUS, EDGE_RADIUS, z=t).translate((0, extra / 2, 0)))
    return shape(body), (X, Y, Z, r)


def band(c, x, zc, span_y, span_z, r):
    bt, bw = c["elastic_thickness"], c["elastic_width"]

    def loop(a, b, rr):
        sketch = cq.Workplane("YZ", origin=(x - bw / 2, 0, 0)).center(0, zc).sketch()
        return sketch.rect(a, b).vertices().fillet(rr).finalize().extrude(bw)

    solid = loop(span_y + 2 * bt, span_z + 2 * bt, r + bt).cut(loop(span_y, span_z, r))
    centreline = 2 * (span_y + span_z) - (8 - 2 * math.pi) * r + math.pi * bt
    return shape(solid), centreline


def elastic_cut(c, centreline):
    return math.ceil(centreline * c["elastic_stretch"] + c["elastic_join_overlap"])


def size_of(parts):
    bb = compound(parts).BoundingBox()
    return [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]


def pattern_svg(cut_w, cut_l, seam, half):
    page_w, page_h = 210, 297
    x0, y0 = (page_w - cut_w) / 2, (page_h - cut_l) / 2
    x1, y1, fold = x0 + cut_w, y0 + cut_l, y0 + cut_l / 2
    mid = page_w / 2
    text = 'font-family="Helvetica, Arial, sans-serif" fill="#222"'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{page_w}mm" height="{page_h}mm" viewBox="0 0 {page_w} {page_h}">
  <rect width="{page_w}" height="{page_h}" fill="#fff"/>
  <rect x="{x0:.2f}" y="{y0:.2f}" width="{cut_w}" height="{cut_l}" fill="none" stroke="#111" stroke-width="0.5"/>
  <g stroke="#555" stroke-width="0.3" stroke-dasharray="3 2">
    <line x1="{x0 + seam:.2f}" y1="{y0:.2f}" x2="{x0 + seam:.2f}" y2="{y1:.2f}"/>
    <line x1="{x1 - seam:.2f}" y1="{y0:.2f}" x2="{x1 - seam:.2f}" y2="{y1:.2f}"/>
  </g>
  <line x1="{x0:.2f}" y1="{fold:.2f}" x2="{x1:.2f}" y2="{fold:.2f}" stroke="#111" stroke-width="0.35" stroke-dasharray="8 2 1 2"/>
  <g {text} font-size="3.2" text-anchor="middle">
    <text x="{mid}" y="{fold - 2:.2f}">FOLD</text>
    <text x="{mid}" y="{y0 + 7:.2f}">OPENING · top of the sleeve</text>
    <text x="{mid}" y="{y1 - 4:.2f}">OPENING · underside of the sleeve</text>
    <text x="{mid}" y="{y0 - 4:.2f}">{cut_w} mm</text>
    <text transform="translate({x1 + 6:.2f} {fold:.2f}) rotate(90)">{cut_l} mm</text>
    <text transform="translate({x0 + seam - 2:.2f} {y0 + cut_l / 4:.2f}) rotate(-90)">sew {seam:g} mm in</text>
    <text transform="translate({x1 - seam + 4.5:.2f} {y0 + cut_l / 4:.2f}) rotate(-90)">sew {seam:g} mm in</text>
  </g>
  <g {text} text-anchor="middle">
    <text x="{mid}" y="{y0 + cut_l / 4 - 4:.2f}" font-size="5.5" font-weight="700">CORNE SLEEVE · CUT 2</text>
    <text x="{mid}" y="{y0 + cut_l / 4 + 3:.2f}" font-size="3.2">3 mm neoprene fabric · one piece per keyboard half</text>
    <text x="{mid}" y="{y0 + cut_l / 4 + 8:.2f}" font-size="3.2">Fits a {half}</text>
  </g>
  <line x1="{x0:.2f}" y1="{y1 + 11:.2f}" x2="{x0 + 50:.2f}" y2="{y1 + 11:.2f}" stroke="#111" stroke-width="0.8"/>
  <text x="{x0 + 53:.2f}" y="{y1 + 12.2:.2f}" font-size="3.2" {text}>This bar is 50 mm when printed at 100 %. A4, actual size.</text>
</svg>
"""


def export_stl(obj, path, fine=True):
    exporters.export(obj, str(path), tolerance=0.05 if fine else 0.12, angularTolerance=0.15 if fine else 0.35)
    mesh = trimesh.load_mesh(path, process=True)
    return bool(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0), mesh.volume


def build(c):
    checks = []
    right, env = build_half(c, checks)
    left = mirrored(right)
    t, s = c["neoprene_thickness"], c["seam_allowance"]
    L, D, H = env["length"], env["depth"], env["height"]

    seam_width = L + H + c["girth_allowance"]
    seam_depth = D + H + c["mouth_overlap"] + c["depth_allowance"]
    cut_w, cut_l = math.ceil(seam_width + 2 * s), math.ceil(2 * seam_depth)
    checks.append({"name": "pattern fits A4 at actual size", "pass": cut_w <= 190 and cut_l <= 270,
                   "detail": f"{cut_w} × {cut_l} mm inside a 190 × 270 mm printable area"})

    closed, (X, Y, Z, r) = sleeve(c, env)
    hollow, _ = sleeve(c, env, hollow=True)
    open_sleeve, _ = sleeve(c, env, hollow=True, open_mouth=True)
    turned = lambda obj: obj.rotate((0, 0, 0), (0, 0, 1), 180)

    # A hair of space between the two sleeves keeps their meshes separate.
    pitch = Y + 0.3
    side_sleeves = [closed.translate((0, pitch / 2, 0)), turned(closed).translate((0, -pitch / 2, 0))]
    side_bands, side_line = zip(*[band(c, x, Z / 2, Y + pitch, Z, r) for x in (-X / 4, X / 4)])
    dt = c["divider_thickness"]
    divider = shape(cq.Workplane("XY").box(X - 8, Y - 8, dt, centered=(True, True, False)).edges("|Z").fillet(4).translate((0, 0, Z)))
    stack_sleeves = [closed, closed.translate((0, 0, Z + dt))]
    stack_bands, stack_line = zip(*[band(c, x, (2 * Z + dt) / 2, Y, 2 * Z + dt, r) for x in (-X / 4, X / 4)])

    in_right = placed(right, 0, (0, pitch / 2, t))
    in_left = placed(left, 180, (0, -pitch / 2, t))
    hollow_sleeves = [hollow.translate((0, pitch / 2, 0)), turned(hollow).translate((0, -pitch / 2, 0))]
    # Turned so the open mouth faces the viewer's default camera.
    slide = 0.55 * D
    sliding_half = placed(right, 180, (0, -slide, t))
    open_sleeve = turned(open_sleeve)

    keyboard = compound([*in_right.values(), *in_left.values()])
    clash = overlap(keyboard, compound(hollow_sleeves))
    checks.append({"name": "both halves fit inside their sleeves", "pass": clash < 0.5,
                   "detail": f"{clash:.2f} mm3 overlap with the 3 mm fabric; {CLEARANCE:g} mm play each side"})
    clash = overlap(compound(sliding_half.values()), open_sleeve)
    checks.append({"name": "half slides through the open mouth", "pass": clash < 0.5, "detail": f"{clash:.2f} mm3 overlap"})
    for label, bands, sleeves in [("side by side", side_bands, side_sleeves), ("stacked", stack_bands, [*stack_sleeves, divider])]:
        clash = overlap(compound(bands), compound(sleeves))
        checks.append({"name": f"bands sit on the {label} sleeves", "pass": clash < 0.5, "detail": f"{clash:.2f} mm3 overlap"})

    loops = {"side_by_side": [elastic_cut(c, v) for v in side_line], "stacked": [elastic_cut(c, v) for v in stack_line]}
    for label, cuts in loops.items():
        checks.append({"name": f"elastic for {label.replace('_', ' ')} within 1 m", "pass": sum(cuts) <= 1000,
                       "detail": f"{len(cuts)} loops of {cuts[0]} mm = {sum(cuts)} mm"})

    modes = {
        "side": {"sleeves": side_sleeves, "bands": side_bands},
        "stacked": {"sleeves": stack_sleeves, "bands": stack_bands, "divider": [divider]},
        "sliding": {"sleeve": [open_sleeve], **{k: [v] for k, v in sliding_half.items()}},
    }
    # Cut through the front sleeve along the encoder knob, the tallest part of the half.
    cut_y = in_left["knob"].Center().y
    cutaway = {"sleeves": hollow_sleeves, "bands": side_bands, **{k: [in_right[k], in_left[k]] for k in right}}
    modes["cutaway"] = {k: [o for o in (keep_behind(o, cut_y) for o in v) if o.Volume() > 0.01] for k, v in cutaway.items()}
    derived = {
        "keyboard_half": {"length": round(L, 1), "depth": round(D, 1), "keycap_top_above_desk": env["keycap_top"],
                          "knob_top_above_desk": env["knob_top"], "packed_height": H},
        "sleeve": {"cut_width": cut_w, "cut_length": cut_l, "pieces": 2, "seam_line_width": round(seam_width, 1),
                   "fold_to_opening": round(seam_depth, 1), "fold_from_end": cut_l / 2, "outside": [round(X, 1), round(Y, 1), round(Z, 1)]},
        "neoprene_needed": [2 * cut_w, cut_l],
        "packed": {"side_by_side": size_of([*side_sleeves, *side_bands]), "stacked": size_of([*stack_sleeves, *stack_bands, divider])},
        "elastic_loops": loops,
        "divider": [round(X - 8, 1), round(Y - 8, 1)],
        "slide_out_shown": round(slide, 1),
    }
    return modes, derived, checks, pattern_svg(cut_w, cut_l, s, f"{L:.1f} × {D:.1f} × {H:.1f} mm half")


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
    report = {"status": "Render and sewing pattern; keyboard inputs as listed, encoder knob height assumed",
              "units": "mm", "config": c, "derived": derived, "checks": checks}
    for folder in targets:
        (folder / f"{PREFIX}_pattern.svg").write_text(svg)
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
