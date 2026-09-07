# Reference geometry and verified sources

The dock's physical fit is based on the Rocklabs V6 CAD plus explicitly adjustable
measurements. **The upstream Corne outline is a visual placement reference only;
it is not a Keebart case model or a machining/printing template for that case.**

## Keebart

- [Corne Choc Pro product](https://www.keebart.com/products/corne): wired, USB-C
  between halves, closed case, 5- and 6-column options, Choc v1/v2 switches.
- [Official profile image](https://raw.githubusercontent.com/Keebart/picture-cdn/main/corne/lowprofile.webp):
  **8.2 mm** annotated case/plate profile. It does not establish keycap or foot height.
- [Plastic case](https://www.keebart.com/ru/parts/corne/plastic-case): includes rubber
  feet and is specifically for Keebart's USB-C version, not the standard TRRS Corne.
- [Aluminium case](https://www.keebart.com/products/corne-aluminium-case): specific
  Keebart PCB/version compatibility; includes rubber feet. The case material alone
  does not provide the dock's required magnetic mating targets.
- [Aluminium underside image](https://raw.githubusercontent.com/Keebart/picture-cdn/main/corne/aluminium-specs.webp):
  shows the MagLift-ring recess and peripheral feet. This dock uses discrete added
  steel targets and does not assume MagLift/MagSafe compatibility.

Accessed 2026-09-07. No dimensioned Keebart XY case drawing, stock foot dimensions,
or case STEP file was found in these public sources. Do not substitute the
upstream Corne dimensions as verified Keebart dimensions.

## Upstream preview attribution

`foostan_corne_3x6_right.step` is the right 3x6 Corne case from
[foostan/crkbd](https://github.com/foostan/crkbd/blob/main/cases/3x6/right.step),
retrieved 2026-09-07. Copyright belongs to foostan and the Corne contributors.
Licensed under **Creative Commons Attribution 4.0 International**; see
[FOOSTAN_LICENSE_CC.txt](FOOSTAN_LICENSE_CC.txt).

The generated `corne_puck_dock_preview_keyboard_reference.stl` extracts the
bottom face's outer wire, fills internal features, extrudes the silhouette to the
configured case height, and translates it beside the dock. Those modifications
are for visual orientation only. Its outline is approximately 138.35 × 97.62 mm,
measured from this upstream STEP, **not from a Keebart case**. No claim of
Keebart endorsement or exact compatibility is made.

The separate keycap preview is an illustrative 23-key layout with rounded boxes
at the configured keycap height. It is not a measured Keebart keycap profile or
a key-clearance test. Check full thumb-key travel with the physical fit coupon.

The reference silhouette is excluded from every printable STL and from the dock
STEP assembly. Geometry checks use a local straight case-edge envelope instead.

## Existing puck

The second model linked by `index.html` is V6 rev5, not the older unlinked V7 file.
The latest four-screw source STEP files are in `cad/outputs/round_puck_v6/`.
The older `models/cirque_round_puck_v6_top.step` and bottom STEP/STL files were
not all synchronized by the prior commit. The dock generator deliberately imports
the current CAD output directory, and records SHA-256 hashes in its report.

The V6 enclosure is Ø46 × 13.5 mm. The existing CAD represents four Ø10 × 4.5 mm
rubber feet at (±10, ±5.5) before the dock's 90° rotation. These are CAD dimensions,
not confirmation of the rubber feet actually fitted to your puck.
