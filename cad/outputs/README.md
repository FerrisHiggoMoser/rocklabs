# Cirque TM040040 standalone enclosure — revision 1

Compact two-part, screw-closed enclosure requiring no hardware beyond the listed build parts. The Cirque snaps behind the top lip; the KB2040 and Keycapsss adapter sit in printed locating trays; four M2 screws enter heat-set inserts in the top shell.

## Main dimensions

- Finished body: **62 × 70 × 14.8 mm** (excluding 4.5 mm rubber feet)
- Corner radius: **8 mm**
- Normal wall: **2.2 mm**; bottom: **2.4 mm**
- Visible touch opening: **Ø37.8 mm**
- Cirque underside pocket: **Ø40.5 mm**, designed around the conservative **5.61 mm assembled thickness**
- KB2040 design envelope: **35.5 × 18.3 × 5.4 mm** around the published 35.0 × 17.8 × 4.9 mm board
- USB-C shell opening: **10.2 × 4.6 mm**, centered in the rear wall
- Heat-set insert bores: **Ø3.2 mm × 5.5 mm deep**, in **Ø6.8 mm** bosses
- Bottom screw clearance: **Ø2.4 mm**, with **Ø4.3 × 1.25 mm** head recess
- Four adhesive-foot recesses: **Ø10.4 × 0.35 mm**

## Print

- Print both parts in the supplied STL orientation: large flat faces on the bed.
- 0.20 mm layers, 4 perimeters, 5 top/bottom layers, 20–30% infill; PETG is preferred for the small Cirque retaining nibs, but PLA should work if handled gently.
- No support should be needed on a well-tuned printer. Bridge the USB-C opening; enable support there only if your printer bridges poorly.
- First print only the first few millimetres of each part or use your slicer's fit-test feature to confirm screw/insert fit.

## Assembly

1. Heat four M2×4 inserts into the top bosses from the open underside. Stop flush; do not push into the roof.
2. Flex the top shell only slightly and seat the Cirque from below, touch surface against the annular top lip. Feed the included FFC through the 15 mm routing opening.
3. Seat the Keycapsss adapter in the front tray and the KB2040 in the rear tray, with its USB-C connector facing the rear opening. Solder four short AWG30 wires between them and leave a gentle service loop.
4. Connect and lock the FFC. Verify the USB plug enters freely before closing.
5. Close with four M2 screws. Use screws long enough to pass the 2.4 mm plate and engage the insert, but not so long that they bottom out; **M2×6 is the intended nominal size**.
6. Apply the four Ø10 mm adhesive feet in the marked recesses.

## Important fit checks

The primary part dimensions are verified online, but the assembled Keycapsss adapter outline/connector height and the exact position of the KB2040 USB-C metal shell can vary slightly by production revision. Before a full print, compare the delivered parts to the tray/opening dimensions above. The adapter tray accepts up to approximately **28.5 × 19 mm**. If your adapter is larger, edit the parametric source in `work/generate_enclosure.py` or trim the low locating rails; no extra hardware is required.

Deburr the touch opening and keep the printed lip/nibs away from exposed components on the Cirque underside. Do not force the sensor past a nib; lightly file the nib if your printer runs dimensionally tight.

## Files

- `cirque_trackpad_top.stl` / `.step` — top shell
- `cirque_trackpad_bottom.stl` / `.step` — removable bottom plate
- `cirque_trackpad_enclosure.step` — two-part assembly

Revision 1 is a dimensionally conservative printable prototype. Always test-fit electronics before applying power.
