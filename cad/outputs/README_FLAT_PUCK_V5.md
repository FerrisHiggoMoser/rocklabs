# Cirque flat puck V5

Body size: **Ø46 × 13.5 mm** excluding the rubber feet — same diameter as the stacked puck but 5.7 mm thinner (~30% less volume).

## What changed and why

The stacked puck reserved a 28.5 × 19 mm tray for the I²C adapter because its assembled size was unknown. The adapter is actually **11.5 × 13.75 × 1.6 mm**, which is small enough to sit *beside* the KB2040 in a single electronics layer:

- KB2040 lies across the middle of the plate (35 × 17.8 footprint), USB-C toward the +x wall.
- Adapter sits in the crescent on the cable side, inside four low corner posts.
- The 50 mm FFC drops straight from the Cirque connector to the adapter connector directly below it.
- Three M2 bosses (two beside the adapter, one opposite) with M2×4 heat-set inserts, per the V4 three-screw layout.

## Sensor mounting: borderless top-load

The Ø40 module cannot pass a Ø38.8 bezel opening, and clamp-from-below schemes leave the tapping force on skinny posts. V5 does it the simple way:

- The top opening is **Ø40.5, straight through** — the sensor drops in from above with a 0.25 mm ring gap.
- It rests flush on a **continuous ring ledge** (ID Ø38, 1.5 mm thick) that runs 360° around, inset far enough that the Cirque's underside FFC connector clears it.
- Overlay face sits flush with the case top. Retention is a thin ring of double-sided tape on the ledge (VHB or similar); with 0.2 mm tape the face sits 0.2 mm proud.

## Numbers that matter

- Bottom plate 1.8, walls 1.7, ledge ring 1.5 thick with its top 0.99 below the case top.
- Vertical clearance over the KB2040: 1.2 mm below the conservative 5.61 mm Cirque envelope.
- Maximum assembled adapter height: **6.0 mm**. A full-length 2.54 mm header still doesn't fit — clip the pins or solder AWG30 straight into the holes.
- USB-C opening 13 × 7: the connector is recessed ~5.4 mm behind the wall, so the opening admits the cable overmold. Very fat overmolds may not reach.
- Feet at (±14.5, 4) and (±10, −12), clear of the screw countersinks.

## Verification

`generate_flat_puck_v5.py` models every purchased part at real size (Cirque PCB + underside envelope + FFC connector, ribbon, adapter with FFC connector/header/pull-ups, KB2040 with USB-C and RP2040, inserts, feet) and runs boolean interference checks against both shell parts: **zero overlaps**. The `_cutaway_*` STLs are a half-section (x ≥ 0, through the USB port) for visual inspection.

## Print

`_print_plate.stl` has both parts print-ready on one bed: top shell face-down, bottom plate right-side-up. PETG, 0.20 mm layers, four perimeters, 25–35% infill. Nothing needs supports; the USB opening arch bridges 13 mm, which PETG handles fine.
