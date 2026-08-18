# Round Cirque puck V6

The V5 internals inside the round-puck hull: a pure Ø46 cylinder — no port flat, no 45° slope cutoff.

- Body: **Ø46 × 14.4 mm** without rubber feet
- Same verified single-layer V5 layout inside: KB2040 and the measured 11.5 × 13.75 × 1.6 mm adapter side by side, three M2 heat-set inserts, identical internal heights
- Top: no separate ring. The top face is a **full-width 0.9 mm cap** with the crown fillet and a clean Ø38.8 opening — the first design's bezel look, one unbroken surface. The sensor drops onto the 360° ledge, then the cap glues onto the wall's top annulus; its underside holds the sensor (no tape). The only seam is a hairline line on the side.
- USB-C: the **first design's port verbatim** — one 10.2 × 4.6 opening at the same height, straight through the curved wall. The plug face sits 4.2 mm behind the curved surface, the same gap the round stacked puck had.
- `print_plate` is all three parts bed-ready: top shell face-down, bottom plate, cap crown-up
- 55 automated dimension checks pass: shell/component interference, seat and cap overlaps, screw and insert margins, radial packing, port fit, wall-integrity probes

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
