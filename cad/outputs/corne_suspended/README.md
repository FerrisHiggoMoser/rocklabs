# Corne + puck: suspended, angled attachment

A **new, separate accessory** for the existing V6 Ø46 × 13.5 mm round puck.
The original puck enclosures and magnetic desk dock remain available.

The padded, two-bolt clamp captures the keyboard case between an upper and lower
jaw. Two gussets carry the cradle. A three-bolt retaining ring captures the puck
above an annular shelf, including when the keyboard is tilted or inverted.
The touch surface slopes **15° toward the keyboard**, measured relative to the
keyboard plane. The angle is fixed in the print, with no friction hinge to slip.

**Status: CAD prototype; physical fit and suspended loads have not been tested.**
CAD checks establish solid geometry, clearance and retention stops. They do not
establish clamp friction, printed strength, pad adhesion or long-term creep.
The keyboard's existing mount must carry the keyboard and accessory. This is a
puck attachment, **not an anchor for suspending the keyboard**.

## Check your keyboard first

The default is for the inner straight edge of the right keyboard half, with the
keyboard extending toward +X and the puck's USB cable exiting toward +Y.

| Interface | Default | What to check |
| --- | --- | --- |
| Closed case thickness | 8.2 mm | Inherited from the earlier dock, not measured on your keyboard |
| Straight case edge | 56 mm | Entire clamp span must sit on a straight, structurally sound case |
| Bare upper case ledge | 4 mm inward from edge | No keys, switches or exposed PCB beneath the upper jaw |
| Clear underside strip | 14 mm inward from edge | No feet, recesses, ports, screws or suspension hardware in the jaw area |
| Installed top/bottom pad thickness | 0.8 mm each | Include adhesive; pads compress slightly when tightened |
| Keyboard underside to keycap tops | 16 mm | An assumed preview dimension; check full key travel using the coupon |
| Puck body | Ø46 × 13.5 mm | Actual source V6 STEP geometry |
| Cradle bore | Ø46.5 mm | 0.25 mm radial print clearance |
| Puck center from case edge | 45 mm outward | Check reach and cable slack in your own suspended position |
| Touch center above keyboard underside | 18 mm | Center height only: the touch plane is tilted |
| Retainer opening | Ø42 mm | Leaves the Ø40 mm touch surface exposed |
| Puck feet | Ø10 × 4.5 mm | CAD assumption; the Ø36 mm underside opening clears them |

If the bare ledge or clear underside strip is missing, **this default clamp does
not fit**. Do not tighten it against keys, switches, a bare PCB or the suspension
mount. The fit coupon is the first print. The pale keyboard in the viewer is an
upstream Corne silhouette with illustrative keys, not exact Keebart case CAD.
Its cosmetic keys are not a key-travel clearance test.

## Files

- `corne_puck_suspended_print_kit.zip`: print files, matching editable STEP files,
  this guide and the dimension/check report.
- `corne_puck_suspended_fit_coupon.stl`: three separate test pieces in one file:
  the actual lower clamp interface, upper jaw and a Ø46.5 mm bore gauge. This
  coupon has no carrier arm or puck shelf and is not a usable suspended mount.
- `corne_puck_suspended_print_plate.stl`: all **three** final parts, arranged on
  the print bed. Split into objects in the slicer to tune supports or spacing.
- `corne_puck_suspended_carrier.stl`: angled cradle, lower jaw, edge stop and webs.
- `corne_puck_suspended_upper_jaw.stl`: removable upper keyboard jaw.
- `corne_puck_suspended_retainer.stl`: three-bolt top ring.
- Matching `.step` files: editable solids in the same print orientations.
- `corne_puck_suspended_assembly.step`: the real assembled accessory, intact puck,
  pads and hardware. **Reference only; do not print.**
- `*_preview_*.stl` / `*_suspended_*.stl`: colored-viewer components and an
  illustrative 35° keyboard tent. **Reference only; do not print.**

## Hardware for the default configuration

- **5 × M3 × 20 mm socket-head bolts**: two for the keyboard clamp, three for the
  retaining ring. Length is measured under the head.
- **5 × M3 DIN 934 hex nuts**, 5.5 mm across flats and 2.4 mm high.
- **5 × M3 flat washers**, 7 mm OD, 3.2 mm ID, 0.5 mm thick.
- Firm adhesive-backed rubber: a **13 × 50 mm** lower pad, **3 × 50 mm** upper
  pad and **46 × 8.2 mm** edge pad. Installed thickness is 0.8 mm.
- A 2.5 mm hex key. Optional removable low-strength thread locker compatible
  with your hardware and printed material; keep it off the enclosure and pads.

The model uses Ø3.4 mm clearance holes and 5.8 mm AF nut pockets. Use the nut
standard specified above; nyloc nuts are taller and do not fit these pockets.
The washers spread bolt-head pressure on the printed parts. Purchased washers
must match the assumed dimensions. Custom rebuilds may require longer keyboard
clamp bolts; use `dimensions.json → derived → hardware` for the active lengths.

The screw envelope follows [Accu's ISO 4762 M3 socket-head specification](https://www.accu.co.uk/metric-cap-head-screws/1010028-NBK-SNSP-M3-20-R360)
(5.5 mm head diameter, 3 mm head height). Nut height follows
[Accu's M3 DIN 934 dimension sheet](https://www.accu.co.uk/api/product-datasheet?id=268686).
These are dimensional references, not requirements to buy those materials.

## Printing and assembly

1. Print the coupon in PETG at 0.20 mm layer height, with at least five walls.
   The lower jaw is already on its side, matching the carrier layer direction;
   the upper jaw and bore gauge sit flat. Check the bore, nut pockets, padding,
   full key travel, USB access and suspension-mount clearance on the real devices.
2. After the fit check, print the three final parts in PETG or another suitable
   engineering filament, with five or six walls and approximately 40% infill.
   The carrier is oriented on its side so the gussets develop in the layer plane.
   **Inspect supports in your slicer**: local support may be needed beneath the
   curved cradle, bolt ears and transverse holes. Use a brim if needed; keep
   supports removable from the bore and nut pockets. The two flat parts normally
   need no support. No support-free claim is made for the carrier.
3. Clean the holes and seats without enlarging the load-bearing walls. Test the
   nuts and bolts in the detached parts. Insert the two keyboard-clamp nuts and
   three ring nuts into their underside-open hex pockets before mounting.
4. Apply the rubber pads to the lower contact strip, upper lip and vertical edge
   stop. The adhesive positions the pads; bolts provide the clamping action.
5. Place the keyboard case between the lower jaw and upper jaw. Insert two
   M3 × 20 bolts through washers and the upper jaw into the lower captive nuts.
   Tighten alternately by hand until the case cannot shift. Stop if the printed
   jaw bends markedly or the case deforms. No torque rating has been established.
6. Rotate the existing puck so its offset USB opening points through the rear
   notch, lower it onto the shelf, and let its original rubber feet project
   through the open underside. The enclosure and its four original screws stay
   intact. Verify that the plug fits before fitting the retainer.
7. Fit the ring above the puck's outside rim. Install three M3 × 20 bolts with
   washers into the cradle's nuts. Tighten to seat the ring on the printed ears;
   its 0.25 mm axial gap avoids squeezing the sensor. The ring's inner opening
   stays outside the active touch surface. A little puck play is intentional.
8. With the keyboard supported close above a soft surface, check ordinary touch
   pressure, gentle side pressure, your normal suspended angle and inversion.
   Inspect for jaw slip, ring movement, print cracks and cable pull. Recheck
   after initial use and periodically for pad compression or polymer creep.
   Until physical testing succeeds, do not rely on this prototype to hold over
   a drop. Do not use the puck as a handle for moving the keyboard.

Keep cable slack near both devices and secure the cable to the keyboard's
existing support so cable weight does not pull on the USB socket. The lower jaw
and gussets extend below the keyboard's ordinary feet; this accessory is intended
for an elevated keyboard. Use the original magnetic dock for the existing flat
desk arrangement.

## Rebuild and checks

From the repository root, using the existing Python 3.12 environment:

```bash
.venv/bin/python cad/work/generate_corne_suspended.py --publish-models
.venv/bin/python cad/work/verify_corne_suspended.py
```

To change fit or the fixed angle without overwriting website downloads:

```bash
.venv/bin/python cad/work/generate_corne_suspended.py --config my-fit.json --out /tmp/my-suspended-puck
```

Start from `cad/corne_suspended.json`. Supported input ranges are checked, and
each generated shape must additionally pass all collision checks. A value being
within range does not guarantee that every combination will fit. The tilt can be
rebuilt from 10° to 25°. Changing it requires a new print, not a hinge adjustment.

Checks use the existing puck's actual top and bottom STEP files, with hashes in
the report. They cover connected valid print solids, bed orientation, manifold
STLs, part-to-part clearance, full bolt/nut engagement, the case and bare-ledge
envelopes, pads, feet, screw access and USB plug path. Tests also verify that the
assembled puck meets stops in all six translation directions and can be inserted
with the ring removed. **These are geometry checks, not FEA or a load rating.**

The web preview reuses the [attributed upstream Corne silhouette](../../references/README.md),
translated to the keyboard-underside datum. The suspended view rotates every
component together by an illustrative 35° and raises the assembly; it does not
claim to model the user's suspension hardware. Only the accessory is printable.

[New model page](../../../suspended.html) · [Original magnetic dock](../../../dock.html)
