import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pydeps"))
import cadquery as cq
from cadquery import exporters

STYLE = os.environ.get("ENCLOSURE_STYLE", "borderless").lower()
if STYLE not in ("rounded", "borderless"):
    raise ValueError("ENCLOSURE_STYLE must be rounded or borderless")
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs", "centered_two_versions"))
os.makedirs(OUT, exist_ok=True)

# All dimensions mm. Coordinate system: X left/right, Y front/rear, Z bottom/top.
W, D = 47.0, 50.0
R = 5.0
BOTTOM_T = 1.8
TOP_H = 13.7
WALL = 1.8
TRACK_X, TRACK_Y = 0.0, 0.0
TRACK_POCKET_D = 40.5
TOUCH_OPEN_D = 38.8 if STYLE == "borderless" else 37.8

def rounded_box(w, d, h, r, z=0):
    return (cq.Workplane("XY").workplane(offset=z).rect(w-2*r, d).extrude(h)
            .union(cq.Workplane("XY").workplane(offset=z).rect(w, d-2*r).extrude(h))
            .union(cq.Workplane("XY").workplane(offset=z).pushPoints([
                (-w/2+r,-d/2+r),(w/2-r,-d/2+r),(-w/2+r,d/2-r),(w/2-r,d/2-r)
            ]).circle(r).extrude(h)))

# TOP SHELL: rounded outer body, hollow from below, circular touch opening and underside pocket.
outer = rounded_box(W, D, TOP_H-BOTTOM_T, R, BOTTOM_T)
# Soft continuous top perimeter rather than a sharp printed edge.
outer = outer.edges(">Z").fillet(1.8)
inner = rounded_box(W-2*WALL, D-2*WALL, TOP_H-BOTTOM_T-2.2, R-WALL, BOTTOM_T-0.01)
top = outer.cut(inner)
if STYLE == "borderless":
    # Shallow flush-seat. The remaining 0.85 mm annulus retains the sensor.
    top = top.cut(cq.Workplane("XY").workplane(offset=TOP_H-0.50)
                  .center(TRACK_X, TRACK_Y).circle(40.5/2).extrude(0.55))
top = top.cut(cq.Workplane("XY").workplane(offset=TOP_H-2.3)
              .center(TRACK_X, TRACK_Y).circle(TOUCH_OPEN_D/2).extrude(2.5))
top = top.cut(cq.Workplane("XY").workplane(offset=TOP_H-7.0)
              .center(TRACK_X, TRACK_Y).circle(TRACK_POCKET_D/2).extrude(4.9))

# FFC exit from circular pocket toward adapter region.
top = top.cut(cq.Workplane("XY").workplane(offset=TOP_H-8.0)
              .center(0, TRACK_Y+18.0).box(10.0, 14.0, 7.0, centered=(True,True,False)))

# Four small integrated retaining nibs under the Cirque perimeter.
# Three retainers; the fourth quadrant stays open for the FFC.
for x,y,sx,sy in [(-20.0,TRACK_Y,1,0),(20.0,TRACK_Y,-1,0),(0,TRACK_Y-20.0,0,1)]:
    nib = cq.Workplane("XY").workplane(offset=TOP_H-7.15).center(x,y).box(
        3.2 if sx else 6.0, 6.0 if sx else 3.2, 5.0, centered=(True,True,False))
    top = top.union(nib)

# USB-C opening in rear wall. 10.2 x 4.6 gives generous plug-shell clearance.
usb_cut = cq.Workplane("XZ").workplane(offset=D/2-1.0).center(0,7.0).rect(10.2,4.6).extrude(4.0,both=True)
top = top.cut(usb_cut)

# Four compact corner screws fit in the space outside the circular sensor pocket.
boss_pts = [(-18.5,-20.5),(18.5,-20.5),(-18.5,20.5),(18.5,20.5)]
for x,y in boss_pts:
    boss = cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x,y).circle(3.2).extrude(9.3)
    bore = cq.Workplane("XY").workplane(offset=BOTTOM_T-0.1).center(x,y).circle(1.6).extrude(5.8)
    top = top.union(boss).cut(bore)

# BOTTOM: inset plate, screw holes/counterbores, feet pads, electronics locating rails.
bottom = rounded_box(W-0.40, D-0.40, BOTTOM_T, R-0.25, 0)
for x,y in boss_pts:
    bottom = bottom.cut(cq.Workplane("XY").center(x,y).circle(1.2).extrude(BOTTOM_T+0.2))
    bottom = bottom.cut(cq.Workplane("XY").workplane(offset=-0.01).center(x,y).circle(2.15).extrude(0.9))

# KB2040 tray: board 35 x 17.8 x 4.9, placed with USB-C centered at rear opening.
# Rails locate the board with 0.5 mm XY clearance; closing shell retains it vertically.
for x in (-18.25,18.25):
    bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x,13.2)
                          .box(1.6,19.0,2.0,centered=(True,True,False)))
bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(0,3.2)
                      .box(38.1,1.6,2.0,centered=(True,True,False)))

# Conservative adapter tray (nominal max envelope 27 x 18 mm); cable can leave either side.
for x in (-14.25,14.25):
    bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(x,-13.0)
                          .box(1.5,19.0,1.8,centered=(True,True,False)))
bottom = bottom.union(cq.Workplane("XY").workplane(offset=BOTTOM_T).center(0,-22.0)
                      .box(30.0,1.5,1.8,centered=(True,True,False)))

# One straight 8 mm service channel for FFC and the four AWG30 conductors.
bottom = bottom.cut(cq.Workplane("XY").workplane(offset=BOTTOM_T-0.01).center(0,-1.0)
                    .box(8.0,36.0,0.75,centered=(True,True,False)))

# Four flat, recessed adhesive-foot locations: 10.4 mm diameter x 0.35 mm.
foot_pts = [(-15,-15),(15,-15),(-15,13),(15,13)]
for x,y in foot_pts:
    bottom = bottom.cut(cq.Workplane("XY").workplane(offset=-0.01).center(x,y).circle(5.2).extrude(0.36))

# Export separate printable pieces and a two-solid assembly STEP.
prefix = "centered_borderless" if STYLE == "borderless" else "centered_rounded_bezel"
exporters.export(top, os.path.join(OUT,f"{prefix}_top.stl"), tolerance=0.06, angularTolerance=0.10)
exporters.export(bottom, os.path.join(OUT,f"{prefix}_bottom.stl"), tolerance=0.06, angularTolerance=0.10)
exporters.export(top, os.path.join(OUT,f"{prefix}_top.step"))
exporters.export(bottom, os.path.join(OUT,f"{prefix}_bottom.step"))
assy = cq.Assembly(name="Cirque_TM040040_enclosure")
assy.add(top, name="top_shell", color=cq.Color(0.20,0.42,0.72))
assy.add(bottom, name="bottom_plate", color=cq.Color(0.18,0.18,0.20))
assy.save(os.path.join(OUT,f"{prefix}_assembly.step"))

for name, obj in [("top",top),("bottom",bottom)]:
    bb=obj.val().BoundingBox()
    print(name, "solid=",obj.val().isValid(), "volume=",round(obj.val().Volume(),1),
          "bbox=",tuple(round(v,2) for v in (bb.xlen,bb.ylen,bb.zlen)))
