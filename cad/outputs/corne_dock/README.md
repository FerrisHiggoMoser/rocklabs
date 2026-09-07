# Corne + round puck magnetic dock

An external, removable accessory for the **latest V6 Ø46 × 13.5 mm enclosure**.
The puck remains a separate USB device. No new electronic mounts, wiring, or
keyboard disassembly are required.

**Status: CAD checked, physical fit prototype.** Print the coupon and measure your
keyboard before the full dock. The default is the inner straight edge of the right
Corne half. Keebart's exact contour and rubber feet have not been measured.

## What to print

- `corne_puck_dock_fit_coupon.stl`: print first. Full under-keyboard tongue,
  magnet pockets, puck bearing ledge, and a short fit rim.
- `corne_puck_dock_print.stl`: the complete dock, one connected solid at Z=0.
- Matching `.step` files: editable solid CAD.
- `corne_puck_dock_assembly.step`: dock, existing puck, feet, sensor, magnets,
  and added steel targets in their assembled positions. **Not a print file.**
- `*_preview_*.stl`: viewer assets, including purchased components. **Do not print.**
- `dimensions.json`: active parameters, derived dimensions, source hashes,
  and the actual CAD/mesh check results.

The model viewer is at [dock.html](../../../dock.html). The public STL copies are
generated into `models/`; the generator does not deploy or push the website.

## Default dimensions (mm)

| Item | Dimension | Basis |
| --- | --- | --- |
| Existing puck body | Ø46 × 13.5 | Latest V6 CAD |
| Cradle straight bore | Ø46.5 | 0.25 clearance per side |
| Cradle circular exterior | Ø49.7 | 1.6 wall; straight side fairing extends this locally |
| Touch plane | 18.0 above desk | Assumed 16.0 underside-to-keycap + 2.0 keyboard feet |
| Keyboard case/plate profile | 8.2 | Keebart product annotation |
| Keyboard feet | Ø8 × 2.0 | **Assumed; measure yours** |
| Existing puck feet | Ø10 × 4.5 | V6 CAD; confirm fitted feet |
| Open underside | Ø36 | Clears all four modeled puck feet |
| Under-keyboard tongue | 56 underlap × 32 wide × 1.7 high | Derived for the default 2 mm foot gap |
| Straight mating face | 36 total span, rounded corners | Verify a straight section on your case |
| Nominal case gap | 0.3 | Assembly clearance |
| Magnets | 4 × Ø8 × 1.0 | Added hardware |
| Magnet pockets | Ø8.2 × 1.1 deep | 0.1 diameter-per-side and 0.1 glue allowance |
| Steel targets | Ø8 × 0.2 plus 0.1 adhesive | Added beneath keyboard |

Do not confuse the **case rim** with the **keycap tops**. With the default feet,
the existing puck's touch surface cannot be lowered to an 8.2 mm case rim without
raising the keyboard. Set `alignment` to `case` to generate the correct keyboard
lift and a separate set of four risers. Default case alignment raises the keyboard
7.8 mm; the original feet remain attached and rest on the risers. If you regenerate
that configuration, add its risers to your print; the default website files align
to the assumed keycap height instead.

## Fit and assembly

1. Measure the keyboard's underside-to-keycap height and uncompressed rubber-foot
   height. Also measure your puck's actual feet. Adjust `cad/corne_dock.json` and
   regenerate if different from the defaults. Every input is in millimetres.
2. Print the coupon flat, using PETG, 0.20 mm layers, four perimeters, and 25–35%
   infill. Test the cradle fit with the existing puck, without forcing it. Tune
   `radial_clearance` for your printer.
3. Slide the tongue under the inner straight case edge; the keyboard must remain
   level on its feet. The default tongue has no guessed keyboard-foot holes.
   Position it between the actual feet. If a foot overlaps, record its center in
   local coordinates in `keyboard_feet_in_mount` (pairs of X/Y), or move the dock
   along the straight edge. Reliefs that collide with magnets are rejected.
4. Check that the USB cable routes toward the back (+Y) and that the inner/thumb
   keys can fully travel beside the cradle. The pale outline in the website is
   an upstream reference, so this physical check is necessary.
5. Glue four Ø8 × 1 mm magnets into the upward-open pockets, with faces flush to
   the tongue. Put a steel target on each magnet, add adhesive to the target's
   exposed face, then position the keyboard at the checked alignment. Let the
   adhesive bond and peel the dock away to leave the targets in place. Use the
   actual target/adhesive thicknesses in the config. Plastic and aluminium need
   these targets; the dock does not rely on keyboard screws or a MagSafe ring.
6. Print the full dock flat. The rear USB notch is open at the top, so it adds no
   bridge or plug recess. Inspect/remove only supports suggested by your slicer
   after checking the model; the intended orientation does not require supports.
7. Set the puck on the annular ledge. The open center accommodates its original
   feet, and the four bores leave the screws accessible. The cradle rests on the
   desk and carries downward touch loads; the magnets locate it laterally.

Magnet holding strength, adhesive durability, and printer shrinkage are not
established by the CAD checks. Do not lift the keyboard by the mounted puck.
Do not blindly mirror this model: the real puck's USB exit has a 1.7 mm offset.

## Rebuild

From the repository root with Python 3.12:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r cad/requirements.txt
.venv/bin/python cad/work/generate_corne_dock.py --publish-models
```

For a separate custom export, without replacing website assets:

```bash
.venv/bin/python cad/work/generate_corne_dock.py --config my-measurements.json --out /tmp/my-corne-dock
```

The build checks valid connected solids, Z=0 print orientation, the existing
enclosure's real STEP geometry, foot and screw clearance, the USB corridor,
magnet-pocket floors, configured touch-plane alignment, and closed STL meshes.
Those checks do not prove a match to an unmeasured physical keyboard.

Additional fit scenarios and invalid-input checks:

```bash
.venv/bin/python cad/work/verify_corne_dock.py
```

The optional website browser check requires `playwright` and its Chromium browser.
With a local server running at `http://127.0.0.1:8765/`, run
`.venv/bin/python cad/work/verify_dock_site.py`. It checks all three views,
mobile layout, downloads, the original puck link, and missing-model handling.

See [reference sources and attribution](../../references/README.md).
