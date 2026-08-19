import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pydeps"))
import cadquery as cq
from cadquery import exporters

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs", "flat_puck_v5"))
os.makedirs(OUT, exist_ok=True)

# V5: single electronics layer using the measured 11.5 x 13.75 mm I2C adapter.
# Borderless top: the sensor drops in from above through a D40.5 opening and
# rests flush on a continuous ring ledge (no clamp posts, no bezel lip).
OD = 46.0
R = OD / 2
BOTTOM_T = 1.8
H = 13.5
WALL = 1.7
OPEN_D = 40.5       # through-opening; D40.0 module passes with 0.25 ring gap
LEDGE_ID = 38.0     # ring ledge the bare PCB rim rests on
LEDGE_TOP = H - 0.99 - 0.01   # PCB underside height for a flush overlay

# KB2040 band y -10.6..7.2 (35 x 17.8), adapter band y 8.2..19.7 (13.75 x 11.5).
# Bosses at r 20.1: half-buried in the wall for stiffness, 1.3 mm of material
# left between the insert bore and the outside surface.
BOSS_PTS = [(-14.3, 14.2), (14.3, 14.2), (0, -20.1)]

# --- top shell ---
outer = cq.Workplane("XY").workplane(offset=BOTTOM_T).circle(R).extrude(H - BOTTOM_T)
outer = outer.edges(">Z").fillet(1.2)
top = outer.cut(cq.Workplane("XY").workplane(offset=BOTTOM_T - 0.01).circle(R - WALL).extrude(LEDGE_TOP - 1.51 - BOTTOM_T))
top = top.cut(cq.Workplane("XY").workplane(offset=LEDGE_TOP - 1.52).circle(LEDGE_ID / 2).extrude(1.52))
top = top.cut(cq.Workplane("XY").workplane(offset=LEDGE_TOP).circle(OPEN_D / 2).extrude(H - LEDGE_TOP + 0.1))

# USB-C port with a local flat: the KB2040 shifts +0.7 in x so its connector
# front lands at x18.7; a flat face at x19.4 (rolling back to the cylinder at
# 45deg below the ledge) puts the connector 0.7 behind the surface — flush,
# fully latching, overmold stays outside. Snug plug-sized stadium hole.
KB_DX = 0.7
# The facet is rotated about z so its normal passes through the port center
# (y -1.7): the port lands dead-center on the flat instead of lopsided.
PORT_TILT = -math.degrees(math.atan2(1.7, 19.4))

# the filler must span the full chord where the flat plane cuts inside the
# cavity circle (|y| < 8.8), with margin — otherwise the flat opens a slot
flat_block = (cq.Workplane("XY").workplane(offset=BOTTOM_T)
              .center(20.9, 0).box(5.1, 23.0, LEDGE_TOP - 1.52 - BOTTOM_T, centered=(True, True, False))
              .intersect(cq.Workplane("XY").circle(R).extrude(H))
              .rotate((0, 0, 0), (0, 0, 1), PORT_TILT))
top = top.union(flat_block)
slope_cut = (cq.Workplane("XZ").polyline([(19.4, -0.5), (19.4, 7.0), (23.6, 11.2), (23.6, -0.5)])
             .close().extrude(13.5, both=True)
             .rotate((0, 0, 0), (0, 0, 1), PORT_TILT))
top = top.cut(slope_cut)

# 9.8 x 4.1 rounded-rect plug hole (r1.2 corners clear the shell's square
# corners), cut along the connector axis at y-1.7
top = top.cut(cq.Workplane("YZ").workplane(offset=17.5).center(-1.7, 5.0).sketch()
              .rect(9.8, 4.1).vertices().fillet(1.2).finalize().extrude(7.0))
# lead-in drawn on the facet centerline pre-rotation, then rotated with the
# facet so it lands centered on the hole with an even rim depth
lead_in = (cq.Workplane("YZ").workplane(offset=18.85).center(-0.05, 5.0).sketch()
           .rect(5.8, 5.4).push([(-2.9, 0), (2.9, 0)]).circle(2.7).finalize()
           .extrude(6.0).rotate((0, 0, 0), (0, 0, 1), PORT_TILT))
top = top.cut(lead_in)

# Three insert bosses half-buried in the wall, running full height into the
# ledge ring so the flipped print needs no supports; stock is clipped to the
# outer cylinder so nothing bulges past the case surface. Bore is deep enough
# for an M2x6 screw (tip at z6.9) over the 4 mm insert.
envelope = cq.Workplane("XY").circle(R).extrude(H)
for x, y in BOSS_PTS:
    boss = (cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x, y).circle(3.1)
            .extrude(LEDGE_TOP - 1.52 - BOTTOM_T).intersect(envelope))
    bore = cq.Workplane("XY").workplane(offset=BOTTOM_T - 0.1).center(x, y).circle(1.6).extrude(7.0)
    top = top.union(boss).cut(bore)

# --- bottom plate ---
bottom = cq.Workplane("XY").circle(R - 0.2).extrude(BOTTOM_T)
for x, y in BOSS_PTS:
    bottom = bottom.cut(cq.Workplane("XY").center(x, y).circle(1.2).extrude(BOTTOM_T + 0.2))
    bottom = bottom.cut(cq.Workplane("XY").workplane(offset=-0.01).center(x, y).circle(2.15).extrude(0.9))

# Plate edge flattened to match the shell's port flat (0.2 reveal).
bottom = bottom.cut(cq.Workplane("XY").workplane(offset=-0.1).center(21.7, 0)
                    .box(5.0, 27.0, BOTTOM_T + 0.2, centered=(True, True, False))
                    .rotate((0, 0, 0), (0, 0, 1), PORT_TILT))

# KB2040 guides: one -y side rail and one -x end stop; USB end stays open.
bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(0.7, -11.5)
                      .box(24.0, 1.4, 2.4, centered=(True, True, False)))
bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(-17.65, -1.7)
                      .box(1.4, 10.0, 2.4, centered=(True, True, False)))

# Adapter corner posts around the 11.5 x 13.75 board, 0.28 mm clearance per
# side for FDM; FFC arrives from above.
for x, y in [(-7.75, 9.5), (7.75, 9.5), (-7.75, 18.5), (7.75, 18.5)]:
    bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x, y)
                          .box(1.2, 1.2, 2.0, centered=(True, True, False)))

# Solder-relief groove under the wiring span and four foot flats clear of the screws.
bottom = bottom.cut(cq.Workplane("XY").workplane(offset=BOTTOM_T - 0.71).center(0, 2)
                    .box(8.0, 30.0, 0.72, centered=(True, True, False)))
for x, y in [(-13.8, 4), (13.8, 4), (-10, -12), (10, -12)]:
    bottom = bottom.cut(cq.Workplane("XY").workplane(offset=-0.01).center(x, y).circle(5.2).extrude(0.36))

# --- component mockups at real purchased dimensions ---
def box(x, y, z0, w, d, h):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).box(w, d, h, centered=(True, True, False))

PCB_BOT = H - 0.99   # sensor PCB underside, overlay flush with the top face
components = {
    # Cirque: PCB+overlay slab, central underside component field, edge FFC connector
    "cirque_pcb":       cq.Workplane("XY").workplane(offset=PCB_BOT).circle(39.8 / 2).extrude(0.99),
    "cirque_underside": cq.Workplane("XY").workplane(offset=H - 5.61).circle(15.0).extrude(5.61 - 0.99),
    "cirque_ffc_conn":  box(0, 15.0, PCB_BOT - 3.0, 10.0, 5.5, 3.0),
    "ffc_ribbon":       box(0, 15.3, 6.4, 8.0, 0.3, (PCB_BOT - 3.0) - 6.4),
    # adapter: measured 11.5 x 13.75 x 1.6 board, FFC connector, header body (pins clipped)
    "adapter_pcb":      box(0, 13.95, BOTTOM_T, 13.75, 11.5, 1.6),
    "adapter_ffc_conn": box(0, 12.8, BOTTOM_T + 1.6, 11.0, 6.5, 3.0),
    "adapter_header":   box(0, 18.2, BOTTOM_T + 1.6, 10.16, 2.54, 2.5),
    "adapter_r1":       box(-4.0, 16.5, BOTTOM_T + 1.6, 2.0, 1.25, 0.6),
    "adapter_r2":       box(4.0, 16.5, BOTTOM_T + 1.6, 2.0, 1.25, 0.6),
    # KB2040 (shifted +0.7 toward the port flat): 35 x 17.8 board, USB-C shell
    # with 0.5 mm overhang landing at x18.7, RP2040 chip
    "kb2040_pcb":       box(0.7, -1.7, BOTTOM_T, 35.0, 17.8, 1.6),
    "kb2040_usb":       box(15.05, -1.7, BOTTOM_T + 1.6, 7.3, 8.94, 3.2),
    "kb2040_chip":      box(-4.3, -1.7, BOTTOM_T + 1.6, 7.0, 7.0, 0.9),
}
for i, (x, y) in enumerate(BOSS_PTS):
    components[f"insert_{i}"] = cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x, y).circle(1.6).extrude(4.0)
for i, (x, y) in enumerate([(-13.8, 4), (13.8, 4), (-10, -12), (10, -12)]):
    components[f"foot_{i}"] = (cq.Workplane("XY").workplane(offset=0.36).center(x, y)
                               .circle(5.0).workplane(offset=-4.5).circle(4.75).loft())

# --- interference checks ---
print("interference volumes (mm^3, ~0 expected):")
clashes = 0
for shell_name, shell in (("top", top), ("bottom", bottom)):
    for cname, comp in components.items():
        if cname.startswith(("insert", "foot")):
            continue
        v = shell.val().intersect(comp.val()).Volume()
        if v > 0.05:
            clashes += 1
            print(f"  CLASH {shell_name} vs {cname}: {round(v, 2)}")
print(f"checks done, {clashes} clashes")

# --- exports ---
prefix = "cirque_flat_puck_v5"
exporters.export(top, os.path.join(OUT, prefix + "_top.stl"), tolerance=0.06, angularTolerance=0.10)
exporters.export(bottom, os.path.join(OUT, prefix + "_bottom.stl"), tolerance=0.06, angularTolerance=0.10)
exporters.export(top, os.path.join(OUT, prefix + "_top.step"))
exporters.export(bottom, os.path.join(OUT, prefix + "_bottom.step"))

# print plate: top flipped face-down, bottom beside it, both on the bed
top_flipped = top.rotate((0, 0, 0), (1, 0, 0), 180).translate((-25, 0, H + 0.01))
plate = top_flipped.union(bottom.translate((25, 0, 0)))
exporters.export(plate, os.path.join(OUT, prefix + "_print_plate.stl"), tolerance=0.06, angularTolerance=0.10)

# half-section: keep x >= 0 (shows the USB port side)
keep = cq.Workplane("XY").workplane(offset=-10).center(R + 5, 0).box(2 * R + 10, 2 * R + 10, H + 20, centered=(True, True, False))
half_shell = top.union(bottom).intersect(keep)
comp_union = None
for comp in components.values():
    comp_union = comp if comp_union is None else comp_union.union(comp)
half_comps = comp_union.intersect(keep)
exporters.export(half_shell, os.path.join(OUT, prefix + "_cutaway_shell.stl"), tolerance=0.06, angularTolerance=0.10)
exporters.export(half_comps, os.path.join(OUT, prefix + "_cutaway_components.stl"), tolerance=0.06, angularTolerance=0.10)

assy = cq.Assembly(name="Cirque_flat_puck_v5")
assy.add(top, name="top_shell", color=cq.Color(0.25, 0.45, 0.75))
assy.add(bottom, name="bottom_plate", color=cq.Color(0.18, 0.18, 0.20))
for cname, comp in components.items():
    assy.add(comp, name=cname, color=cq.Color(0.75, 0.30, 0.25))
assy.save(os.path.join(OUT, prefix + "_assembly_with_components.step"))

for name, obj in (("top", top), ("bottom", bottom), ("plate", plate), ("half_shell", half_shell), ("half_comps", half_comps)):
    bb = obj.val().BoundingBox()
    print(name, "solids", obj.solids().size(), "valid", obj.val().isValid(),
          "bbox", tuple(round(v, 2) for v in (bb.xlen, bb.ylen, bb.zlen)))
