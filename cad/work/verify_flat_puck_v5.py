import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pydeps"))
import generate_flat_puck_v5 as g
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_State

results = []
def check(name, ok, detail):
    results.append((ok, name, detail))

def dist(a, b):
    d = BRepExtrema_DistShapeShape(a.val().wrapped, b.val().wrapped)
    d.Perform()
    return d.Value()

top, bottom, comps = g.top, g.bottom, g.components
H, R, BT = g.H, g.R, g.BOTTOM_T

# ---- boolean: exact min clearance component vs shells ----
# (component, shell, expected min, expected max, why)
CLEAR = [
    ("kb2040_pcb",       top,    0.10, 99, "board edge to wall/guides in top shell"),
    ("kb2040_usb",       top,    0.10, 99, "USB shell to wall opening edges"),
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
    d = dist(comps[cname], top if shell is top else bottom)
    sname = "top" if shell is top else "bottom"
    check(f"{cname} vs {sname}", lo <= d <= hi, f"{d:.3f} mm ({why}; want {lo}..{hi})")

# ---- boolean: component vs component ----
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
    d = dist(comps[a], comps[b])
    check(f"{a} vs {b}", d >= lo, f"{d:.3f} mm ({why}; want >={lo})")

# ---- analytic: sensor seat ----
check("module through opening", 40.5 - 40.0 >= 0.4, f"opening D40.5 vs module D40.0: {40.5-40.0:.2f} diametral")
seat = (39.8 - g.LEDGE_ID) / 2
check("ledge seat overlap", seat >= 0.7, f"PCB rim overlaps ledge {seat:.2f} mm per side (360deg ring)")
check("overlay flush", abs((g.LEDGE_TOP + 0.01 + 0.99) - H) < 0.02, f"overlay top at {g.LEDGE_TOP+0.01+0.99:.2f} vs case top {H}")
env_bot = H - 5.61
check("sensor envelope depth", env_bot - (BT + 4.9) >= 0.8, f"{env_bot - (BT+4.9):.2f} mm over KB2040 (conservative 5.61 envelope)")

# ---- analytic: screws ----
for x, y in g.BOSS_PTS:
    r = math.hypot(x, y)
    skin = R - (r + 1.6)
    check(f"insert skin at ({x},{y})", skin >= 1.2, f"{skin:.2f} mm plastic outside D3.2 bore")
bore_end, tip = BT - 0.1 + 7.0, 0.9 + 6.0
check("M2x6 screw depth", bore_end - tip >= 0.5, f"tip z{tip:.1f} vs bore end z{bore_end:.1f} (csk 0.9 + 6 mm)")
check("insert engagement", 4.0 <= 7.0, "4 mm insert fully inside 7 mm bore, seated at plate")
for x, y in g.BOSS_PTS:
    edge = (R - 0.2) - (math.hypot(x, y) + 2.15)
    check(f"csk edge margin ({x},{y})", edge >= 0.4, f"{edge:.2f} mm from countersink to plate edge")
for fx, fy in [(-13.8, 4), (13.8, 4), (-10, -12), (10, -12)]:
    dmin = min(math.hypot(fx - x, fy - y) for x, y in g.BOSS_PTS)
    check(f"foot ({fx},{fy}) vs screws", dmin >= 7.35, f"{dmin:.2f} mm center distance (need 5.2+2.15)")

# ---- analytic: radial packing (KB2040 shifted +0.7 toward the port flat) ----
cav = R - g.WALL
for name, pts, lo in [("KB2040", [(18.2, -10.6), (18.2, 7.2)], 0.2),
                      ("adapter", [(6.875, 19.7)], 0.3),
                      ("adapter header", [(5.08, 19.47)], 0.3)]:
    worst = max(math.hypot(x, y) for x, y in pts)
    check(f"{name} inside cavity", cav - worst >= lo, f"corner r{worst:.2f} vs cavity r{cav:.1f}")

# ---- analytic: flush USB-C port (tilted facet at distance 19.4, snug hole) ----
t = math.radians(-g.PORT_TILT)
n = (math.cos(t), -math.sin(t))          # facet outward normal
conn_front = 17.5 + g.KB_DX + 0.5
recesses = [19.4 - (conn_front * n[0] + yy * n[1]) for yy in (-6.17, -1.7, 2.77)]
check("USB flush recess", max(recesses) <= 1.1,
      f"connector front sits {min(recesses):.2f}..{max(recesses):.2f} mm behind the tilted facet")
check("USB latch depth", 6.5 - max(recesses) >= 5.3, f"{6.5-max(recesses):.1f} mm of plug shell reaches the receptacle")
tangential = 19.4 * math.sin(t) - 1.7 * math.cos(t)
check("port centered on facet", abs(tangential) <= 0.2, f"port offset {tangential:+.3f} mm from facet centerline")
check("USB hole y fit", (9.8 - 8.94) / 2 >= 0.25, f"hole 9.8 vs shell 8.94: {(9.8-8.94)/2:.2f}/side")
check("USB hole z fit", 5.0 - 4.1 / 2 <= 3.4 and 6.6 <= 5.0 + 4.1 / 2, "hole z2.95-7.05 wraps connector z3.4-6.6")
check("board end vs flat wall", 18.35 - 18.2 >= 0.1, f"{18.35-18.2:.2f} mm board-end gap to local wall face")
check("flat rolls under ledge", 7.0 + (R - 19.4) <= 10.98, f"45deg slope exits cylinder at z{7.0+(R-19.4):.1f}, ledge starts z10.98")

# ---- wall integrity: mid-wall probe line behind the port flat must be solid ----
# z8.5 is above the plug hole and below the slope; x18.9 sits between the flat
# face (19.4) and the filler's inner face (18.35), continuing into cylinder wall.
leaks = []
for yy in [y / 2 for y in range(-24, 25)]:
    px = 18.9 * math.cos(t) + yy * math.sin(t)
    py = -18.9 * math.sin(t) + yy * math.cos(t)
    cls = BRepClass3d_SolidClassifier(top.val().wrapped, gp_Pnt(px, py, 8.5), 1e-6)
    if cls.State() != TopAbs_State.TopAbs_IN:
        leaks.append(yy)
check("wall sealed behind flat", not leaks, f"void at facet-y={leaks}" if leaks else "49 probe points solid along the rotated facet")

# ---- print plate ----
bb = g.plate.val().BoundingBox()
check("plate on bed", abs(bb.zmin) < 0.02, f"lowest point z={bb.zmin:.3f}")
check("plate footprint", bb.xlen <= 120 and bb.ylen <= 120, f"{bb.xlen:.1f} x {bb.ylen:.1f} mm")
halves = g.plate.solids().vals()
dd = BRepExtrema_DistShapeShape(halves[0].wrapped, halves[1].wrapped); dd.Perform()
check("parts separated on plate", dd.Value() >= 3.0, f"{dd.Value():.2f} mm gap between parts")

# ---- assembly seam ----
check("shell rim on plate", (R - 0.2) - (R - g.WALL) >= 1.4, f"{(R-0.2)-(R-g.WALL):.2f} mm contact ring width")
d_ts = dist(top, bottom)
check("top/bottom no overlap", d_ts < 0.05, f"seam distance {d_ts:.3f} (parts meet at z{BT})")

# ---- report ----
fails = [r for r in results if not r[0]]
print(f"\n===== {len(results)} checks, {len(fails)} FAIL =====")
for ok, name, detail in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
if fails:
    sys.exit(1)
