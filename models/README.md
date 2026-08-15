# Flat Cirque puck V5

Single-layer follow-up to the stacked puck, using the measured 11.5 × 13.75 × 1.6 mm I²C adapter instead of the old 28.5 × 19 mm proxy envelope.

- Body: **Ø46 × 14.0 mm** without rubber feet — 5.2 mm thinner than the stacked puck
- KB2040 and adapter sit side by side on the bottom plate; no stacked shelf
- Sensor clamps between three bottom-plate posts and the top lip when the case closes
- Closure: three M2 screws with M2×4 heat-set inserts
- USB-C opening 13 × 7 mm in the side wall; the connector sits ~5.4 mm recessed, so the opening is sized for the cable overmold
- Maximum assembled adapter height (PCB + FFC connector + header): **5.8 mm** — clip the header pins or solder wires directly; test-fit before a final print

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
