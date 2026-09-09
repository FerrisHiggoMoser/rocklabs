"""Additional fit scenarios and mechanical assembly checks for the new accessory."""
from copy import deepcopy
import json

from generate_corne_suspended import ROOT, build, verify, overlap, compound, cylinder, hexagon, shape


def main():
    config = json.loads((ROOT / "cad/corne_suspended.json").read_text())
    cases = [
        ("default", {}),
        ("shallower 10 degree tilt", {"tilt_degrees": 10}),
        ("25 degree tilt with more case clearance", {"tilt_degrees": 25, "puck_center_offset": 48}),
        ("thicker case uses longer clamp bolts", {"keyboard_case_height": 11,
                                                 "keyboard_keycap_height_from_underside": 20,
                                                 "puck_center_offset": 48}),
    ]
    for name, changes in cases:
        c = {**deepcopy(config), **changes}
        design = build(c)
        checks = verify(design)
        if c["keyboard_case_height"] == 11:
            assert design.derived["clamp_bolt_length"] == 25
        if name == "default":
            # The real nut insertion and Allen-key paths must remain open,
            # including the parts of the gussets below the lower jaw.
            all_parts = compound(design.parts.values())
            for x, y in design.derived["clamp_bolt_centers"]:
                access = hexagon(x, y, -30, 5.5, 30 - c["pad_thickness"] - 5)
                assert overlap(all_parts, access) < 0.001, "Clamp nut cannot be inserted from below"
                key = cylinder(x, y, c["keyboard_case_height"] + c["pad_thickness"] + 4, 1.5, 30)
                assert overlap(all_parts, key) < 0.001, "Clamp hex-key access blocked"
            local_parts = compound([design.local_carrier, design.local_retainer])
            for x, y in design.derived["ring_bolt_centers_local"]:
                access = hexagon(x, y, -30, 5.5, 30)
                assert overlap(local_parts, access) < 0.001, "Ring nut cannot be inserted from below"
                key = cylinder(x, y, design.derived["retainer_underside_local"] + 2.4, 1.5, 30)
                assert overlap(local_parts, key) < 0.001, "Ring hex-key access blocked"
            # The top jaw must have some tightening travel before meeting
            # the edge stop, and both pads must then contact the case.
            tightened = design.parts["upper_jaw"].translate((0, 0, -0.35))
            assert overlap(tightened, design.parts["carrier"]) < 0.001
            assert overlap(tightened, design.obstacles["pads"]) > 1
            assert overlap(tightened, design.obstacles["keyboard case envelope"]) < 0.001
            print("PASS nut insertion, tool access and padded clamp tightening travel", flush=True)
        print(f"PASS {name}: {len(checks)} solid geometry checks", flush=True)

    for name, changes in [
        ("zero tilt", {"tilt_degrees": 0}),
        ("nonfinite tilt", {"tilt_degrees": float("nan")}),
        ("excessive tilt", {"tilt_degrees": 40}),
        ("boolean dimension", {"radial_clearance": True}),
        ("case without a bare ledge", {"keyboard_upper_lip": 0}),
        ("too little key clearance", {"keyboard_keycap_height_from_underside": 10}),
        ("insufficient print clearance", {"radial_clearance": 0.05}),
        ("clamp too short", {"clamp_span": 35}),
    ]:
        try:
            build({**deepcopy(config), **changes})
        except ValueError:
            print(f"PASS rejects {name}", flush=True)
        else:
            raise AssertionError(f"Invalid case accepted: {name}")


if __name__ == "__main__":
    main()
