import os, sys, math
# Local build cache lives outside the site checkout; a normal CadQuery install
# is used automatically when that cache is absent.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "pydeps")))
import cadquery as cq
from cadquery import exporters

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs", "round_puck_v6"))
os.makedirs(OUT, exist_ok=True)

# V6 rev5: the exact compact round puck currently served by rocklabs.rocks,
# revised only where needed for four screws and reliable print orientation:
#   - Four wall-buried M2 insert bosses and four bottom screw holes.
#   - Top prints seam/open-side down, with the cosmetic/touch face upward.
#   - The old unsupported horizontal sensor shelf is replaced by two 45-degree
#     cones. Four tiny 45-degree friction ribs retain the sensor without tape.
#   - Hull: pure D46 cylinder — no port flat, no slope cutoff.
#   - USB-C: the first design's port verbatim — 10.2 x 4.6 at z5.2 straight
#     through the curved wall, plug face ~4.2 mm behind the curved surface.
#   - Underside: completely flat, no foot recesses.
#   - The final public print is one STL containing both parts side by side.
OD = 46.0
R = OD / 2
BOTTOM_T = 1.8
H = 13.5
WALL = 1.7
OPEN_D = 40.5       # through-opening; D40.0 module passes with 0.25 ring gap
LEDGE_ID = 38.0     # ring ledge the bare PCB rim rests on
CAV_R = R - WALL
OPEN_R = OPEN_D / 2
LEDGE_R = LEDGE_ID / 2
PCB_BOT = H - 0.99

# Support-free hourglass. The upper 45-degree cone reaches r20.0 exactly at the
# nominal sensor underside height, keeping the D40 module flush with the case.
CONE_MID = PCB_BOT - (20.0 - LEDGE_R)
CONE_TOP = CONE_MID + (OPEN_R - LEDGE_R)
CONE_START = CONE_MID - (CAV_R - LEDGE_R)

BOSS_PTS = [(-12.5, -14.9), (12.5, -14.9), (-12.5, 14.9), (12.5, 14.9)]
FOOT_PTS = [(-10.0, -5.5), (10.0, -5.5), (-10.0, 5.5), (10.0, 5.5)]
FOOT_MARK_INNER_R = 5.10
FOOT_MARK_OUTER_R = 5.35
FOOT_MARK_DEPTH = 0.18
KB_DX = 0.7
CONN_FRONT = 17.5 + KB_DX + 0.5        # 18.7
PORT_Y, PORT_Z = -1.7, 5.2             # first design's port height, on the connector axis

# Small printable retention ribs. Their lower and upper lead-ins are 45 degrees.
RIB_INNER_R = 19.92
RIB_TOP_INNER_R = 20.10
RIB_OUTER_R = 20.43
RIB_LOWER_RISE = OPEN_R - RIB_INNER_R
RIB_HOLD = 0.06
RIB_UPPER_RISE = RIB_TOP_INNER_R - RIB_INNER_R
RIB_H = RIB_LOWER_RISE + RIB_HOLD + RIB_UPPER_RISE

def friction_rib(z0):
    return (cq.Workplane("XZ")
            .polyline([
                (OPEN_R, z0),
                (RIB_OUTER_R, z0),
                (RIB_OUTER_R, z0 + RIB_H),
                (RIB_TOP_INNER_R, z0 + RIB_H),
                (RIB_INNER_R, z0 + RIB_LOWER_RISE + RIB_HOLD),
                (RIB_INNER_R, z0 + RIB_LOWER_RISE),
            ]).close().extrude(1.5, both=True))

# --- top shell ---
outer = cq.Workplane("XY").workplane(offset=BOTTOM_T).circle(R).extrude(H - BOTTOM_T)
outer = outer.edges(">Z").fillet(1.2)
lower_void = (cq.Workplane("XY").workplane(offset=BOTTOM_T - 0.01).circle(CAV_R)
              .extrude(CONE_START - (BOTTOM_T - 0.01) + 0.01))
lower_cone_void = (cq.Workplane("XY").workplane(offset=CONE_START).circle(CAV_R)
                   .workplane(offset=CONE_MID - CONE_START).circle(LEDGE_R).loft(combine=True))
upper_cone_void = (cq.Workplane("XY").workplane(offset=CONE_MID).circle(LEDGE_R)
                   .workplane(offset=CONE_TOP - CONE_MID).circle(OPEN_R).loft(combine=True))
opening_void = (cq.Workplane("XY").workplane(offset=CONE_TOP).circle(OPEN_R)
                .extrude(H - CONE_TOP + 0.1))
top = outer.cut(lower_void).cut(lower_cone_void).cut(upper_cone_void).cut(opening_void)

# USB-C: the first design's opening — 10.2 x 4.6 through the curved wall.
usb = (cq.Workplane("YZ").workplane(offset=R - 0.8).center(PORT_Y, PORT_Z)
       .rect(10.2, 4.6).extrude(3.0, both=True))
top = top.cut(usb)

# Four insert bosses half-buried in the wall.
envelope = cq.Workplane("XY").circle(R).extrude(H)
for x, y in BOSS_PTS:
    boss = (cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x, y).circle(3.1)
            .extrude(CONE_MID - BOTTOM_T).intersect(envelope))
    bore = cq.Workplane("XY").workplane(offset=BOTTOM_T - 0.1).center(x, y).circle(1.6).extrude(7.0)
    top = top.union(boss).cut(bore)

for angle in (45, 135, 225, 315):
    top = top.union(friction_rib(CONE_TOP).rotate((0, 0, 0), (0, 0, 1), angle))

# --- bottom plate: full circle, screw holes and countersinks back, flat underside ---
bottom = cq.Workplane("XY").circle(R - 0.2).extrude(BOTTOM_T)
for x, y in BOSS_PTS:
    bottom = bottom.cut(cq.Workplane("XY").center(x, y).circle(1.2).extrude(BOTTOM_T + 0.2))
    bottom = bottom.cut(cq.Workplane("XY").workplane(offset=-0.01).center(x, y).circle(2.15).extrude(0.9))

# Flat D10 adhesive-foot locations: shallow outlines only, not recessed pockets.
for x, y in FOOT_PTS:
    foot_mark = (cq.Workplane("XY").workplane(offset=-0.01).center(x, y)
                 .circle(FOOT_MARK_OUTER_R).circle(FOOT_MARK_INNER_R)
                 .extrude(FOOT_MARK_DEPTH + 0.01))
    bottom = bottom.cut(foot_mark)

# Compact KB2040 locating stops avoid the two new lower screw bosses.
for x in (-8.0, 9.0):
    bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x, -11.4)
                          .box(2.5, 1.2, 2.0, centered=(True, True, False)))
for y in (-5.0, 2.0):
    bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(-17.55, y)
                          .box(1.2, 2.5, 2.0, centered=(True, True, False)))
# Adapter corner posts and the single shared FFC/AWG30 route.
for x, y in [(-7.75, 9.5), (7.75, 9.5), (-7.75, 18.5), (7.75, 18.5)]:
    bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x, y)
                          .box(1.2, 1.2, 1.8, centered=(True, True, False)))
bottom = bottom.cut(cq.Workplane("XY").workplane(offset=BOTTOM_T - 0.71).center(0, 2)
                    .box(8.0, 30.0, 0.72, centered=(True, True, False)))

# --- component mockups at real purchased dimensions (V5 set) ---
def box(x, y, z0, w, d, h):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).box(w, d, h, centered=(True, True, False))

components = {
    "cirque_pcb":       cq.Workplane("XY").workplane(offset=PCB_BOT).circle(20.0).extrude(0.99),
    "cirque_underside": cq.Workplane("XY").workplane(offset=H - 5.61).circle(15.0).extrude(5.61 - 0.99),
    "cirque_ffc_conn":  box(0, 15.0, PCB_BOT - 4.10, 10.0, 5.5, 4.10),
    "ffc_ribbon":       box(0, 15.3, 6.4, 8.0, 0.35, (PCB_BOT - 4.10) - 6.4),
    "adapter_pcb":      box(0, 13.95, BOTTOM_T, 13.75, 11.5, 1.6),
    "adapter_ffc_conn": box(0, 12.8, BOTTOM_T + 1.6, 11.0, 6.5, 3.0),
    # AWG30 is soldered directly here; the supplied upright header is omitted.
    "adapter_wire_pad": box(0, 18.2, BOTTOM_T + 1.6, 10.16, 2.54, 1.5),
    "adapter_r1":       box(-4.0, 16.5, BOTTOM_T + 1.6, 2.0, 1.25, 0.6),
    "adapter_r2":       box(4.0, 16.5, BOTTOM_T + 1.6, 2.0, 1.25, 0.6),
    "kb2040_pcb":       box(0.7, -1.7, BOTTOM_T, 35.0, 17.8, 1.6),
    "kb2040_usb":       box(15.05, -1.7, BOTTOM_T + 1.6, 7.3, 8.94, 3.2),
    "kb2040_chip":      box(-4.3, -1.7, BOTTOM_T + 1.6, 7.0, 7.0, 0.9),
    "wire_bundle":      box(0, 2.0, BOTTOM_T - 0.66, 3.0, 29.0, 0.55),
}
for i, (x, y) in enumerate(BOSS_PTS):
    components[f"insert_{i}"] = cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x, y).circle(1.6).extrude(4.0)
    components[f"screw_{i}"] = (
        cq.Workplane("XY").workplane(offset=-1.1).center(x, y).circle(2.0).extrude(2.0)
        .union(cq.Workplane("XY").workplane(offset=0.9).center(x, y).circle(1.0).extrude(6.0))
    )
for i, (x, y) in enumerate(FOOT_PTS):
    components[f"foot_{i}"] = (cq.Workplane("XY").workplane(offset=-4.5)
                                .center(x, y).circle(5.0).extrude(4.5))

# ================= dimension checks =================
results = []
def check(name, ok, detail):
    results.append((ok, name, detail))

from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_State

def dist(a, b):
    d = BRepExtrema_DistShapeShape(a.val().wrapped, b.val().wrapped)
    d.Perform()
    return d.Value()

# boolean interference: every component vs each shell, ~0 expected
clashes = 0
for shell_name, shell in (("top", top), ("bottom", bottom)):
    for cname, comp in components.items():
        if cname.startswith(("insert", "screw", "foot")):
            continue
        if shell_name == "top" and cname == "cirque_pcb":
            continue  # the four local ribs intentionally grip the PCB edge
        v = shell.val().intersect(comp.val()).Volume()
        if v > 0.05:
            clashes += 1
            print(f"  CLASH {shell_name} vs {cname}: {round(v, 2)}")
check("no shell/component interference", clashes == 0, f"{clashes} clashes")

CLEAR = [
    ("kb2040_pcb",       top,    0.10, 99, "board edge to wall in top shell"),
    ("kb2040_usb",       top,    0.10, 99, "USB shell to port opening edges"),
    ("kb2040_chip",      top,    0.10, 99, "RP2040 to shell"),
    ("adapter_pcb",      top,    0.10, 99, "adapter board to wall/bosses"),
    ("adapter_ffc_conn", top,    0.10, 99, "adapter FFC connector to shell"),
    ("adapter_wire_pad", top,    0.10, 99, "direct-solder wire pad to shell"),
    ("cirque_pcb",       top,    0.0,  0.30, "sensor seats in the upper cone and friction ribs"),
    ("cirque_underside", top,    0.10, 99, "sensor component field to shell"),
    ("cirque_ffc_conn",  top,    0.30, 99, "sensor FFC connector to conical seat"),
    ("ffc_ribbon",       top,    0.10, 99, "ribbon to shell"),
    ("wire_bundle",      bottom, 0.05, 99, "four AWG30 wires inside the shared groove"),
    ("kb2040_pcb",       bottom, 0.0,  0.30, "board sits on plate between guides"),
    ("adapter_pcb",      bottom, 0.0,  0.30, "adapter sits on plate inside fence"),
    ("cirque_underside", bottom, 1.0,  99, "sensor components above plate floor"),
]
for cname, shell, lo, hi, why in CLEAR:
    sname = "top" if shell is top else "bottom"
    d = dist(components[cname], shell)
    check(f"{cname} vs {sname}", lo <= d <= hi, f"{d:.3f} mm ({why}; want {lo}..{hi})")

# component vs component (V5 set)
PAIRS = [
    ("cirque_underside", "kb2040_usb",       0.8, "sensor envelope over USB connector"),
    ("cirque_underside", "kb2040_pcb",       0.8, "sensor envelope over KB2040 board"),
    ("cirque_underside", "adapter_ffc_conn", 0.8, "sensor envelope over adapter connector"),
    ("cirque_underside", "adapter_wire_pad", 0.8, "sensor envelope over direct-solder pads"),
    ("cirque_ffc_conn",  "adapter_ffc_conn", 0.5, "the two FFC connectors"),
    ("kb2040_pcb",       "adapter_pcb",      0.5, "KB2040 to adapter board"),
    ("kb2040_usb",       "adapter_pcb",      0.5, "USB shell to adapter"),
]
for a, b, lo, why in PAIRS:
    d = dist(components[a], components[b])
    check(f"{a} vs {b}", d >= lo, f"{d:.3f} mm ({why}; want >={lo})")

# analytic: sensor seat
check("module through opening", OPEN_D - 40.0 >= 0.4, f"opening D{OPEN_D} vs module D40.0")
seat_r = LEDGE_R + (PCB_BOT - CONE_MID)
check("conical sensor seat", abs(seat_r - 20.0) < 0.02,
      f"upper 45deg cone radius at PCB underside = {seat_r:.2f} mm")
check("overlay flush", abs((PCB_BOT + 0.99) - H) < 0.02,
      f"overlay top at {PCB_BOT + 0.99:.2f} vs case top {H}")
check("lower cone is 45 degrees", abs((CAV_R - LEDGE_R) - (CONE_MID - CONE_START)) < 0.01,
      f"run/rise {CAV_R - LEDGE_R:.2f}/{CONE_MID - CONE_START:.2f} mm")
check("upper cone is 45 degrees", abs((OPEN_R - LEDGE_R) - (CONE_TOP - CONE_MID)) < 0.01,
      f"run/rise {OPEN_R - LEDGE_R:.2f}/{CONE_TOP - CONE_MID:.2f} mm")
env_bot = H - 5.61
check("sensor envelope depth", env_bot - (BOTTOM_T + 4.9) >= 0.8,
      f"{env_bot - (BOTTOM_T + 4.9):.2f} mm over KB2040 (conservative 5.61 envelope)")

# analytic: four screws and feet
check("four screw positions", len(BOSS_PTS) == 4, f"{len(BOSS_PTS)} bosses/holes")
for x, y in BOSS_PTS:
    skin = R - (math.hypot(x, y) + 1.6)
    check(f"insert skin at ({x},{y})", skin >= 1.2, f"{skin:.2f} mm plastic outside D3.2 bore")
bore_end, tip = BOTTOM_T - 0.1 + 7.0, 0.9 + 6.0
check("M2x6 screw depth", bore_end - tip >= 0.5, f"tip z{tip:.1f} vs bore end z{bore_end:.1f} (csk 0.9 + 6 mm)")
check("insert engagement", 4.0 <= 7.0, "4 mm insert fully inside 7 mm bore, seated at plate")
for x, y in BOSS_PTS:
    edge = (R - 0.2) - (math.hypot(x, y) + 2.15)
    check(f"csk edge margin ({x},{y})", edge >= 1.0, f"{edge:.2f} mm from countersink to plate edge")
for i, (x, y) in enumerate(FOOT_PTS):
    edge = (R - 0.2) - (math.hypot(x, y) + FOOT_MARK_OUTER_R)
    screw_gap = min(math.hypot(x-bx, y-by) - (FOOT_MARK_OUTER_R + 2.15)
                    for bx, by in BOSS_PTS)
    check(f"foot {i} flat location", edge >= 3.5 and screw_gap >= 2.0,
          f"edge {edge:.2f} mm; nearest screw {screw_gap:.2f} mm")

# analytic: radial packing (unchanged V5 layout)
cav = R - WALL
for name, pts, lo in [("KB2040", [(18.2, -10.6), (18.2, 7.2)], 0.2),
                      ("adapter", [(6.875, 19.7)], 0.3),
                      ("adapter wire pads", [(5.08, 19.47)], 0.3)]:
    worst = max(math.hypot(x, y) for x, y in pts)
    check(f"{name} inside cavity", cav - worst >= lo, f"corner r{worst:.2f} vs cavity r{cav:.1f}")

# analytic: USB-C port, first-design style (10.2 x 4.6 straight through the wall)
check("USB hole y fit", (10.2 - 8.94) / 2 >= 0.25, f"hole 10.2 vs shell 8.94: {(10.2-8.94)/2:.2f}/side")
check("USB hole z fit", PORT_Z - 4.6 / 2 <= 3.4 and 6.6 <= PORT_Z + 4.6 / 2,
      f"hole z{PORT_Z-2.3:.1f}-{PORT_Z+2.3:.1f} wraps connector z3.4-6.6")
recess = math.sqrt(R * R - PORT_Y * PORT_Y) - CONN_FRONT
check("USB recess (first-design gap, accepted)", recess <= 4.5,
      f"plug face sits {recess:.2f} mm behind the curved surface, same as the round stacked puck")
check("wall below the port", PORT_Z - 4.6 / 2 - BOTTOM_T >= 0.5,
      f"{PORT_Z - 2.3 - BOTTOM_T:.1f} mm of wall between the opening and the seam")

# the hull really is a puck: no flat anywhere
bb = top.val().BoundingBox()
check("hull is round (no cutoff)", abs(bb.xlen - OD) < 0.05 and abs(bb.ylen - OD) < 0.05,
      f"top bbox {bb.xlen:.2f} x {bb.ylen:.2f} (a flat would shrink one axis)")

# wall integrity: probe ring above the port (z10) and opposite the port (z5)
leaks = []
for shell_z, span in ((10.0, range(0, 360, 5)), (5.0, range(90, 271, 5))):
    for ang in span:
        a = math.radians(ang)
        px, py = 22.15 * math.cos(a), 22.15 * math.sin(a)
        cls = BRepClass3d_SolidClassifier(top.val().wrapped, gp_Pnt(px, py, shell_z), 1e-6)
        if cls.State() != TopAbs_State.TopAbs_IN:
            leaks.append((round(shell_z, 1), ang))
check("wall solid ring", not leaks, f"voids at {leaks[:6]}" if leaks else "109 mid-wall probes solid")

# --- exports ---
prefix = "cirque_round_puck_v6"
for part, name in ((top, "_top"), (bottom, "_bottom")):
    exporters.export(part, os.path.join(OUT, prefix + name + ".stl"), tolerance=0.06, angularTolerance=0.10)
    exporters.export(part, os.path.join(OUT, prefix + name + ".step"))

# One print file, two separated objects: top seam/open-side down (no rotation),
# bottom exterior down beside it. Both are already at Z=0 for slicing.
top_print = top.translate((-25, 0, -BOTTOM_T))
plate = top_print.union(bottom.translate((25, 0, 0)))
exporters.export(plate, os.path.join(OUT, prefix + "_print_plate.stl"), tolerance=0.06, angularTolerance=0.10)

pb = plate.val().BoundingBox()
check("plate on bed", abs(pb.zmin) < 0.02, f"lowest point z={pb.zmin:.3f}")
check("plate footprint", pb.xlen <= 120 and pb.ylen <= 120, f"{pb.xlen:.1f} x {pb.ylen:.1f} mm")
halves = plate.solids().vals()
check("two objects on the plate", len(halves) == 2, f"{len(halves)} solids")
dd = BRepExtrema_DistShapeShape(halves[0].wrapped, halves[1].wrapped); dd.Perform()
check("parts separated on plate", dd.Value() >= 3.0, f"{dd.Value():.2f} mm gap between the 2 parts")
d_ts = dist(top, bottom)
check("top/bottom seam", d_ts < 0.05, f"seam distance {d_ts:.3f} (parts meet at z{BOTTOM_T})")

# half-section cutaway with every component (x >= 0 keeps the USB side)
keep = cq.Workplane("XY").workplane(offset=-10).center(R + 5, 0).box(2 * R + 10, 2 * R + 10, H + 20, centered=(True, True, False))
half_shell = top.union(bottom).intersect(keep)
comp_union = None
for comp in components.values():
    comp_union = comp if comp_union is None else comp_union.union(comp)
half_comps = comp_union.intersect(keep)
exporters.export(half_shell, os.path.join(OUT, prefix + "_cutaway_shell.stl"), tolerance=0.06, angularTolerance=0.10)
exporters.export(half_comps, os.path.join(OUT, prefix + "_cutaway_components.stl"), tolerance=0.06, angularTolerance=0.10)

# fully assembled view: both shells together, trackpad resting in the conical seat
assembled = top.union(bottom).union(components["cirque_pcb"])
exporters.export(assembled, os.path.join(OUT, prefix + "_assembled.stl"), tolerance=0.06, angularTolerance=0.10)

assy = cq.Assembly(name="Cirque_round_puck_v6")
assy.add(top, name="top_shell", color=cq.Color(0.25, 0.45, 0.75))
assy.add(bottom, name="bottom_plate", color=cq.Color(0.18, 0.18, 0.20))
for cname, comp in components.items():
    assy.add(comp, name=cname, color=cq.Color(0.75, 0.30, 0.25))
assy.save(os.path.join(OUT, prefix + "_assembly_with_components.step"))

for name, obj in (("top", top), ("bottom", bottom), ("plate", plate)):
    b = obj.val().BoundingBox()
    print(name, "solids", obj.solids().size(), "valid", obj.val().isValid(),
          "bbox", tuple(round(v, 2) for v in (b.xlen, b.ylen, b.zlen)))

fails = [r for r in results if not r[0]]
print(f"\n===== {len(results)} checks, {len(fails)} FAIL =====")
for ok, name, detail in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
if fails:
    sys.exit(1)
