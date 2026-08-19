# Cirque trackpad enclosure — CAD sources

CadQuery scripts and exported models for the Cirque TM040040 trackpad enclosure project
(Cirque TM040040 + Adafruit KB2040 + Keycapsss I²C adapter).

## Layout

- `work/` — CadQuery generator and verification scripts
  - `generate_flat_puck_v5.py` — flat puck V5 (Ø46×13.5, borderless top-load)
  - `generate_round_puck_v6.py` — round puck V6 (screwed top+bottom, borderless open top)
  - `generate_round_puck.py`, `generate_enclosure.py` — earlier designs
  - `verify_*.py` — boolean interference checks and export verification
- `outputs/` — exported STL/STEP files and per-design READMEs

## Running the scripts

The scripts need CadQuery on Python 3.12 (3.14 does not work with the prebuilt wheels):

```
py -3.12 -m pip install cadquery
py -3.12 work/generate_flat_puck_v5.py
```

The original working copy used a vendored `pydeps/` folder of cp312 Windows binaries
(~1.1 GB, not committed here); a plain `pip install cadquery` replaces it. If a script
inserts `pydeps` into `sys.path`, that line can be removed or left as-is once cadquery
is installed normally.

The print-ready STLs used by the site viewer live in `../models/`.
