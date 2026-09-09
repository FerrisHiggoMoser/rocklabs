# Corne + puck: flat desk and suspended attachment

This separate revision uses **the same assembled parts in both positions**.
Set the keyboard on the desk or lift it onto its existing suspension mount
without removing or adjusting the attachment. The puck stays tilted **15°
toward the keyboard**. All earlier designs remain available.

**CAD prototype:** physical fit, clamp grip, desk stability, printed strength,
pad compression and long-term creep still need testing. CAD checks establish
clearance and retention geometry, not a load rating.

## How it works flat

The keyboard stays level on its original feet, with **no added risers**.
A **1.2 mm lower lip + 0.5 mm pad** fit in the assumed 2 mm foot gap, leaving
**0.3 mm desk clearance**. The short lip extends 8 mm beneath the case.
The thicker clamp block and side-entry nuts sit outside the case, with shorter
screws above desk level. Reinforcing webs rise beside the case.

Two permanent legs under the outer side of the puck carry desk touch loads.
Their 0.8 mm rubber sole pads meet the same desk plane as the keyboard feet.
Both legs stay attached when the keyboard is suspended.

The touch center sits 21.5 mm above the keyboard underside. At 15°, the lower
edge of the Ø40 touch surface is **16.32 mm** above that underside, close to the
assumed 16 mm keycap height. The touch plane remains angled when the keyboard
is flat. These dimensions apply to the configuration, not an unmeasured case.

## Measure before printing (mm)

| Interface | Default | Required check |
| --- | --- | --- |
| Closed case thickness | 8.2 | Inherited assumption; measure your case |
| Straight case edge | 56 | Full clamp span on a structurally sound case |
| Bare upper ledge | 4 | No keys, switches or exposed PCB beneath the jaw |
| Clear underside strip | 8 | No feet, ports or suspension hardware |
| Installed keyboard feet | 2.0 | Include actual compression |
| Lower lip | 1.2 | Do not thin below this value |
| Installed jaw pads | 0.5 each | Include adhesive; use firm rubber |
| Lip + lower pad | 1.7 | Must clear the desk by at least 0.2 |
| Desk sole pads | 2 × 8 × 8 × 0.8 | Match both contact heights to prevent rocking |
| Existing puck | Ø46 × 13.5 | Actual V6 STEP geometry |
| Cradle bore | Ø46.5 | 0.25 radial print clearance |
| Existing puck feet | Ø10 × 4.5 | CAD assumption; verify fitted feet |
| Retainer opening | Ø42 | Clears the Ø40 touch surface |

The default uses the inner straight edge of the right half, keyboard toward
+X and USB toward +Y. If the bare ledge or underside gap is missing, **this
default clamp does not fit**. Do not clamp a bare PCB, switches or suspension
hardware. Do not force the keyboard down against a jaw or screw on the desk.

The keyboard's existing suspension mount carries the whole assembly. This
accessory is not a keyboard suspension anchor. Provide cable slack.

## Files

- `corne_puck_dual_fit_coupon.stl`: actual lower and upper clamp interfaces plus
  a Ø46.5 bore gauge; three test pieces, not a complete attachment.
- `corne_puck_dual_print_plate.stl`: all **three final parts**, oriented on the
  bed: carrier with both desk legs, upper jaw and retaining ring.
- `corne_puck_dual_carrier.stl`, `corne_puck_dual_upper_jaw.stl`,
  `corne_puck_dual_retainer.stl`: individual final parts.
- Matching `.step` files: editable solids in print orientations.
- `corne_puck_dual_print_kit.zip`: five STL/STEP pairs, this guide, and the
  dimension/check report. Print the plate OR individual parts, not both.
- `corne_puck_dual_assembly.step`: assembled reference; do not print.
- `*_preview_*`, `*_flat_*`, `*_suspended_*`: viewer meshes including purchased
  components, illustrative keyboard and desk references. **Do not print.**

## Default hardware

- **2 × M3 × 12 mm socket-head bolts** for the keyboard clamp.
- **3 × M3 × 20 mm socket-head bolts** for the retaining ring.
- **5 × M3 DIN 934 nuts**, 5.5 mm across flats, 2.4 mm high.
- **5 × M3 washers**, OD 7, ID 3.2, thickness 0.5 mm.
- Firm adhesive-backed rubber: lower jaw **7 × 50 × 0.5 mm**, upper jaw
  **3 × 50 × 0.5 mm**, case edge **46 × 8.2 × 0.8 mm**, and
  **two 8 × 8 × 0.8 mm** desk soles.
- 2.5 mm hex key. A tiny dab of removable adhesive can position nuts during
  assembly; the seated nuts and bolts provide the mechanical retention.

**Do not reuse the first attachment's 20 mm clamp screws:** they protrude below
this clamp. Only the ring still uses 20 mm screws. Custom builds may need another
clamp length; consult `dimensions.json → derived → hardware`. Do not substitute
taller nyloc nuts. Clearance holes are Ø3.4 and nut pockets 5.8 mm AF.

Fastener envelopes follow the dimensional references in the
[first attachment guide](../corne_suspended/README.md).

## Print and assemble

1. Measure the case edge and installed keyboard feet. Print the coupon in PETG
   at 0.20 mm layers with five or six walls. The lower jaw is on its side,
   matching the final carrier's layer direction.
2. Fit the real jaw pads and **12 mm** screws. Slide each nut in from the nearest
   end of the lower jaw. Check all original keyboard feet still touch the desk
   and the lip stays clear. Check full key travel, ports and suspension hardware.
   Stop if tightening deforms the case or thin lip; no torque rating is established.
3. Check the puck with the bore gauge. After a successful fit test, print the
   three final parts in PETG or a suitable engineering filament, with five or
   six walls and approximately 40% infill. Use a brim as needed and **inspect
   local supports** below the curved cradle, legs, nut-slot roofs and transverse
   holes. The upper jaw and ring print flat. Clean the slots without thinning
   their walls.
4. Insert two clamp nuts from the ends and three ring nuts from below. Apply
   jaw and edge pads. Clamp the case using two M3 × 12 bolts, washers and the
   upper jaw. Tighten alternately by hand only until secure.
5. Seat the intact puck, USB toward the rear notch and feet through the center.
   Check plug clearance. Fit the ring using three M3 × 20 bolts, washers and
   nuts. Seat it on its printed ears; the 0.25 axial gap avoids squeezing the
   enclosure or sensor.
6. Add the two sole pads and set the assembly on a flat desk. **All keyboard
   feet and both puck soles must contact together.** Check with a paper strip
   and light touch pressure around the puck. If it rocks, correct sole-pad
   thickness or rebuild for the measured foot height. Do not overtighten the
   clamp to pull it flat. Confirm clearance under the lip and all screw tips,
   including after the pads settle.
7. Lift the keyboard onto its suspension mount. No parts change between modes.
   Test close above a soft surface first: normal touch force, gentle side
   pressure, your working angle and inversion. Check jaw slip, pads and cracks.
   Recheck after initial use and periodically for creep. Do not lift by the puck.

The actual foot pattern and keyboard mass distribution are unmeasured, so desk
stability under hand pressure must be tested physically.

## Rebuild and checks

From the repository root:

```bash
.venv/bin/python cad/work/generate_corne_dual.py --publish-models
.venv/bin/python cad/work/verify_corne_dual.py
```

For custom measurements without replacing website downloads:

```bash
.venv/bin/python cad/work/generate_corne_dual.py --config my-measurements.json --out /tmp/my-dual-puck
```

Start from `cad/corne_dual.json`. Inputs are range-checked, then all geometry
must pass collision and desk checks. Steeper angles can require a higher cradle
and extra side clearance. Shorter keyboard feet require checking the lip/pad
stack; the lip must remain at least 1.2 mm thick.

Checks cover actual V6 STEP geometry, valid connected solids, manifold prints,
hardware and device clearance, nut engagement, insertion, six retention
directions, every real part above the desk, fully backed sole pads, and a common
desk plane with the original keyboard feet. Suspended preview parts receive
one common transform of the same assembly. **These are not FEA or load tests.**

The pale keyboard, keys and shown keyboard-foot positions are illustrative,
not measured manufacturing geometry. Flat mode adds a separate desk reference;
suspended mode shows an illustrative 35° keyboard pose. See
[Corne attribution](../../references/README.md).

[New page](../../../dual.html) · [First suspended version](../../../suspended.html)
· [Magnetic desk dock](../../../dock.html)
