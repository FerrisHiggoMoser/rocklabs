# Cirque TM040040 minimum-size enclosure

Body size: **47 × 50 × 13.7 mm**, excluding the rubber feet. This is close to the practical limit for a 40.5 mm sensor pocket with printable walls and the purchased KB2040.

Compared with the original 62 × 70 × 14.8 mm enclosure, the footprint is **46% smaller** and the body is **1.1 mm thinner**. Compared with the previous compact version, it is 19% smaller in footprint.

## How it was reduced

- KB2040 runs fore–aft directly beneath the Cirque, with USB-C at the rear.
- Adapter occupies the front underside zone.
- FFC and all four AWG30 wires share one straight **8 mm-wide center channel**.
- Two rear M2 screws replace four corner screws.
- A printed front tongue retains the opposite edge without extra hardware.
- Walls are **1.8 mm** and the bottom plate is **1.8 mm**.
- Cirque uses a three-point printed retainer, leaving its cable side open.

## Print and assembly

Use PETG if possible: 0.20 mm layers, four perimeters, 25–35% infill. Print both supplied orientations with the broad exterior face on the bed. Test the front tongue before forcing it; lightly file it if your printer runs tight.

Insert the bottom tongue into the front slot first, swing the rear closed, then install the two M2 screws. M2×6 is the nominal screw length for the M2×4 inserts, but confirm against your actual screw-head geometry.

Keep the FFC and AWG30 conductors flat in the center channel. Solder short wires only after test-positioning both boards. Check that no solder joint or connector is pressed against the Cirque underside.

The delivered Keycapsss adapter must fit the approximately **28.5 × 19 mm** tray. Because its assembled connector height is not consistently published, test-fit the real board before a long final print.

Further meaningful reduction would require dropping the heat-set inserts entirely, permanently gluing the case, changing to a smaller controller, or making the enclosure less robust. None of those matches the purchased-parts/removable-bottom requirement as well as this design.
