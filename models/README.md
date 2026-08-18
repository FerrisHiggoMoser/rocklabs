# Round Cirque puck V6

The V5 internals inside the round-puck hull: a pure Ø46 cylinder — no port flat, no 45° slope cutoff.

- Body: **Ø46 × 14.3 mm** without rubber feet (0.8 taller than V5 for the trim ring)
- Same verified single-layer V5 layout inside: KB2040 and the measured 11.5 × 13.75 × 1.6 mm adapter side by side, three M2 heat-set inserts, identical internal heights
- Top: the sensor still drops in from above onto the 360° ledge, but the V5 borderless opening (with its visible 0.25 mm ring gap) is replaced by a **0.8 mm flush trim ring** glued into a rebate — clean Ø38.8 opening, no gap, and the ring retains the sensor (no tape)
- USB-C: one 13.4 × 7.2 rounded opening straight through the curved wall, sized so the plug **overmold** enters and the plug latches fully against the connector in its V5 position — the curved surface stays uninterrupted otherwise
- `print_plate` is all three parts bed-ready: top face-down, bottom plate, trim ring
- 57 automated dimension checks pass: shell/component interference, seat and ring overlaps, screw and insert margins, radial packing, plug latch and pocket clearances, wall-integrity probes

# Flat Cirque puck V5

Single-layer follow-up to the stacked puck, using the measured 11.5 × 13.75 × 1.6 mm I²C adapter instead of the old 28.5 × 19 mm proxy envelope.

- Body: **Ø46 × 13.5 mm** without rubber feet — 5.7 mm thinner than the stacked puck
- KB2040 and adapter sit side by side on the bottom plate; no stacked shelf
- Borderless top: the sensor drops in **from above** through a Ø40.5 opening and rests flush on a continuous 360° ring ledge; a thin ring of double-sided tape on the ledge keeps it seated
- Closure: three M2 screws with M2×4 heat-set inserts
- USB-C port: flush — a local flat on the case side brings the wall to 0.7 mm from the connector face; snug 9.8 × 4.1 plug hole, full latch, overmold stays outside
- Maximum assembled adapter height (PCB + FFC connector + header): **6.0 mm** — clip the header pins or solder wires directly; test-fit before a final print
- `print_plate` is both parts print-ready on one bed: top shell face-down, bottom plate beside it

The `cutaway` files are a half-section with every purchased component modeled at real size (Cirque incl. underside envelope, KB2040 with USB-C, adapter with FFC connector and header, inserts, feet). Boolean interference checks between shell and components pass with zero overlap.

# Round stacked Cirque puck

This version follows the circular sensor instead of wrapping it in a rectangular body.

- Body: **Ø46 × 19.2 mm** without rubber feet
- Cirque: centered, flush, Ø38.8 mm visible opening
- Controller: KB2040 directly beneath the Cirque
- Adapter: stacked above the KB2040 on eight small support posts
- Closure: four M2 screws and four M2×4 heat-set inserts
- Wiring: one central vertical path and one 8 mm bottom groove
- USB-C: side opening aligned with the horizontally mounted KB2040

The footprint is approximately **29% smaller** than the 47 × 50 mm rounded-rectangle version, but the enclosure is **5.5 mm taller** because the adapter and controller occupy separate vertical layers.

The small internal blocks are support posts, not cable slots. The KB2040 rests on the bottom plate; the adapter sits on the upper posts. Keep exposed solder joints clear of the posts and use short, flat AWG30 wiring.

Before a full print, measure the delivered Keycapsss adapter. This model reserves a conservative 28.5 × 19 mm plan envelope, but assembled connector height is not consistently published. Confirm the stack closes without pressure on the Cirque underside. Print in PETG with 0.20 mm layers, four perimeters, and 25–35% infill.
