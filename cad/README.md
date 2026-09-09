# Cirque trackpad enclosure — CAD sources

CadQuery scripts and exported models for the Cirque TM040040 trackpad enclosure project
(Cirque TM040040 + Adafruit KB2040 + Keycapsss I²C adapter).

## Layout

- `corne_dual.json` / `work/generate_corne_dual.py` — new flat-and-suspended
  attachment, with a thin under-case lip, raised clamp nuts and permanent desk legs
- `outputs/corne_dual/` — separate models and [fit/assembly guide](outputs/corne_dual/README.md);
  the configured keyboard stays level on its original feet without risers
- `corne_suspended.json` — separate padded clamp and fixed-angle puck attachment
- `work/generate_corne_suspended.py` — mechanical case jaws and bolted retaining
  ring for an elevated keyboard; does not modify the original dock or puck
- `outputs/corne_suspended/` — three-part print plate, individual STLs/STEPs,
  fit coupon, assembly, print kit and [fit/load-test guide](outputs/corne_suspended/README.md)
- `corne_dock.json` — adjustable external dock fit and height parameters
- `work/generate_corne_dock.py` — magnetic Corne dock for the latest V6 puck;
  validates and exports the separate accessory without changing its electronics
- `outputs/corne_dock/` — fit coupon, dock STL/STEP, assembly, and dimension report
- `references/` — attributed upstream Corne silhouette for the website preview
- `work/` — CadQuery generator and verification scripts
  - `generate_flat_puck_v5.py` — flat puck V5 (Ø46×13.5, borderless top-load)
  - `generate_round_puck_v6.py` — round puck V6 (screwed top+bottom, borderless open top)
  - `generate_round_puck.py`, `generate_enclosure.py` — earlier designs
  - `verify_*.py` — boolean interference checks and export verification
- `outputs/` — exported STL/STEP files and per-design READMEs

## Running the scripts

For the new dock on Linux, from the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r cad/requirements.txt
.venv/bin/python cad/work/generate_corne_dock.py --publish-models
```

The last option updates **local** website assets. See
[the dock guide](outputs/corne_dock/README.md) before printing; exact Keebart foot
dimensions and keycap height need measuring. Open `../dock.html` through a local
HTTP server for the assembly and download page.

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
