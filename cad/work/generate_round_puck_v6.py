import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pydeps"))
import cadquery as cq
from cadquery import exporters

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs", "round_puck_v6"))
os.makedirs(OUT, exist_ok=True)

# V6 rev4: two parts, top and bottom, screwed — the V5 architecture back:
#   - Top shell with the three wall-buried M2 insert bosses and the 360deg
#     ledge; the sensor drops in from above and rests on the ledge, nothing
#     over it (borderless top, no cap, no ring).
#   - Bottom plate screwed with three M2x6 into heat-set inserts.
#   - Hull: pure D46 cylinder — no port flat, no slope cutoff.
#   - USB-C: the first design's port verbatim — 10.2 x 4.6 at z5.2 straight
#     through the curved wall, plug face ~4.2 mm behind the curved surface.
#   - Underside: completely flat, no foot recesses.
# All internal dimensions identical to the verified V5.
OD = 46.0
R = OD / 2
BOTTOM_T = 1.8
H = 13.5
WALL = 1.7
OPEN_D = 40.5       # through-opening; D40.0 module passes with 0.25 ring gap
LEDGE_ID = 38.0     # ring ledge the bare PCB rim rests on
LEDGE_TOP = H - 0.99 - 0.01   # PCB underside height for a flush overlay

BOSS_PTS = [(-14.3, 14.2), (14.3, 14.2), (0, -20.1)]
KB_DX = 0.7
CONN_FRONT = 17.5 + KB_DX + 0.5        # 18.7
PORT_Y, PORT_Z = -1.7, 5.2             # first design's port height, on the connector axis

# --- top shell ---
outer = cq.Workplane("XY").workplane(offset=BOTTOM_T).circle(R).extrude(H - BOTTOM_T)
outer = outer.edges(">Z").fillet(1.2)
top = outer.cut(cq.Workplane("XY").workplane(offset=BOTTOM_T - 0.01).circle(R - WALL).extrude(LEDGE_TOP - 1.51 - BOTTOM_T))
top = top.cut(cq.Workplane("XY").workplane(offset=LEDGE_TOP - 1.52).circle(LEDGE_ID / 2).extrude(1.52))
top = top.cut(cq.Workplane("XY").workplane(offset=LEDGE_TOP).circle(OPEN_D / 2).extrude(H - LEDGE_TOP + 0.1))

# USB-C: the first design's opening — 10.2 x 4.6 through the curved wall.
usb = (cq.Workplane("YZ").workplane(offset=R - 0.8).center(PORT_Y, PORT_Z)
       .rect(10.2, 4.6).extrude(3.0, both=True))
top = top.cut(usb)

# Three insert bosses half-buried in the wall (V5 geometry, unchanged).
envelope = cq.Workplane("XY").circle(R).extrude(H)
for x, y in BOSS_PTS:
    boss = (cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x, y).circle(3.1)
            .extrude(LEDGE_TOP - 1.52 - BOTTOM_T).intersect(envelope))
    bore = cq.Workplane("XY").workplane(offset=BOTTOM_T - 0.1).center(x, y).circle(1.6).extrude(7.0)
    top = top.union(boss).cut(bore)

# --- bottom plate: full circle, screw holes and countersinks back, flat underside ---
bottom = cq.Workplane("XY").circle(R - 0.2).extrude(BOTTOM_T)
for x, y in BOSS_PTS:
    bottom = bottom.cut(cq.Workplane("XY").center(x, y).circle(1.2).extrude(BOTTOM_T + 0.2))
    bottom = bottom.cut(cq.Workplane("XY").workplane(offset=-0.01).center(x, y).circle(2.15).extrude(0.9))

# KB2040 guides, adapter corner posts, solder groove (all V5); no foot recesses.
bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(0.7, -11.5)
                      .box(24.0, 1.4, 2.4, centered=(True, True, False)))
bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(-17.65, -1.7)
                      .box(1.4, 10.0, 2.4, centered=(True, True, False)))
for x, y in [(-7.75, 9.5), (7.75, 9.5), (-7.75, 18.5), (7.75, 18.5)]:
    bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x, y)
                          .box(1.2, 1.2, 2.0, centered=(True, True, False)))
bottom = bottom.cut(cq.Workplane("XY").workplane(offset=BOTTOM_T - 0.71).center(0, 2)
                    .box(8.0, 30.0, 0.72, centered=(True, True, False)))

# --- component mockups at real purchased dimensions (V5 set) ---
def box(x, y, z0, w, d, h):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).box(w, d, h, centered=(True, True, False))

PCB_BOT = H - 0.99   # sensor PCB underside, overlay flush with the top face
components = {
    "cirque_pcb":       cq.Workplane("XY").workplane(offset=PCB_BOT).circle(39.8 / 2).extrude(0.99),
    "cirque_underside": cq.Workplane("XY").workplane(offset=H - 5.61).circle(15.0).extrude(5.61 - 0.99),
    "cirque_ffc_conn":  box(0, 15.0, PCB_BOT - 3.0, 10.0, 5.5, 3.0),
    "ffc_ribbon":       box(0, 15.3, 6.4, 8.0, 0.3, (PCB_BOT - 3.0) - 6.4),
    "adapter_pcb":      box(0, 13.95, BOTTOM_T, 13.75, 11.5, 1.6),
    "adapter_ffc_conn": box(0, 12.8, BOTTOM_T + 1.6, 11.0, 6.5, 3.0),
    "adapter_header":   box(0, 18.2, BOTTOM_T + 1.6, 10.16, 2.54, 2.5),
    "adapter_r1":       box(-4.0, 16.5, BOTTOM_T + 1.6, 2.0, 1.25, 0.6),
    "adapter_r2":       box(4.0, 16.5, BOTTOM_T + 1.6, 2.0, 1.25, 0.6),
    "kb2040_pcb":       box(0.7, -1.7, BOTTOM_T, 35.0, 17.8, 1.6),
    "kb2040_usb":       box(15.05, -1.7, BOTTOM_T + 1.6, 7.3, 8.94, 3.2),
    "kb2040_chip":      box(-4.3, -1.7, BOTTOM_T + 1.6, 7.0, 7.0, 0.9),
}
for i, (x, y) in enumerate(BOSS_PTS):
    components[f"insert_{i}"] = cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x, y).circle(1.6).extrude(4.0)

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
        if cname.startswith("insert"):
            continue
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
    ("adapter_header",   top,    0.10, 99, "header body to shell"),
    ("cirque_pcb",       top,    0.0,  0.30, "sensor rests on ledge (near-touch)"),
    ("cirque_underside", top,    0.10, 99, "sensor component field to shell"),
    ("cirque_ffc_conn",  top,    0.30, 99, "sensor FFC connector to ledge ring"),
    ("ffc_ribbon",       top,    0.10, 99, "ribbon to shell"),
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
    ("cirque_underside", "adapter_header",   0.8, "sensor envelope over header"),
    ("cirque_ffc_conn",  "adapter_ffc_conn", 0.5, "the two FFC connectors"),
    ("kb2040_pcb",       "adapter_pcb",      0.5, "KB2040 to adapter board"),
    ("kb2040_usb",       "adapter_pcb",      0.5, "USB shell to adapter"),
]
for a, b, lo, why in PAIRS:
    d = dist(components[a], components[b])
    check(f"{a} vs {b}", d >= lo, f"{d:.3f} mm ({why}; want >={lo})")

# analytic: sensor seat
check("module through opening", OPEN_D - 40.0 >= 0.4, f"opening D{OPEN_D} vs module D40.0")
seat = (39.8 - LEDGE_ID) / 2
check("ledge seat overlap", seat >= 0.7, f"PCB rim overlaps ledge {seat:.2f} mm per side (360deg ring)")
check("overlay flush", abs((LEDGE_TOP + 0.01 + 0.99) - H) < 0.02,
      f"overlay top at {LEDGE_TOP + 0.01 + 0.99:.2f} vs case top {H} (rests on the ledge, nothing above)")
env_bot = H - 5.61
check("sensor envelope depth", env_bot - (BOTTOM_T + 4.9) >= 0.8,
      f"{env_bot - (BOTTOM_T + 4.9):.2f} mm over KB2040 (conservative 5.61 envelope)")

# analytic: screws (V5 geometry, back in)
for x, y in BOSS_PTS:
    skin = R - (math.hypot(x, y) + 1.6)
    check(f"insert skin at ({x},{y})", skin >= 1.2, f"{skin:.2f} mm plastic outside D3.2 bore")
bore_end, tip = BOTTOM_T - 0.1 + 7.0, 0.9 + 6.0
check("M2x6 screw depth", bore_end - tip >= 0.5, f"tip z{tip:.1f} vs bore end z{bore_end:.1f} (csk 0.9 + 6 mm)")
check("insert engagement", 4.0 <= 7.0, "4 mm insert fully inside 7 mm bore, seated at plate")
for x, y in BOSS_PTS:
    edge = (R - 0.2) - (math.hypot(x, y) + 2.15)
    check(f"csk edge margin ({x},{y})", edge >= 0.4, f"{edge:.2f} mm from countersink to plate edge")

# analytic: radial packing (unchanged V5 layout)
cav = R - WALL
for name, pts, lo in [("KB2040", [(18.2, -10.6), (18.2, 7.2)], 0.2),
                      ("adapter", [(6.875, 19.7)], 0.3),
                      ("adapter header", [(5.08, 19.47)], 0.3)]:
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

# print plate: two objects — top shell face-down, bottom plate beside it
top_flipped = top.rotate((0, 0, 0), (1, 0, 0), 180).translate((-25, 0, H + 0.01))
plate = top_flipped.union(bottom.translate((25, 0, 0)))
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

# fully assembled view: both shells together, trackpad resting on the ledge
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
