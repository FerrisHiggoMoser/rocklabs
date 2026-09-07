"""Exercise physical-fit scenarios and input guards, without exporting assets."""
import copy
import json

from generate_corne_dock import DEFAULT_CONFIG, build, verify


def main():
    baseline = json.loads(DEFAULT_CONFIG.read_text())
    scenarios = [
        ("default keycap alignment", {}, 0.0, 18.0),
        ("case-rim alignment retains existing feet", {"alignment": "case"}, 7.8, 18.0),
        ("short keyboard feet get magnet clearance", {"keyboard_foot_height": 1.0}, 1.0, 18.0),
        ("taller keycaps raise the supported puck", {"keyboard_keycap_height_from_underside": 18.0}, 0.0, 20.0),
        ("measured keyboard foot gets a relief", {"keyboard_feet_in_mount": [[7.0, 0.0]]}, 0.0, 18.0),
    ]
    total = 0
    for name, changes, expected_lift, expected_top in scenarios:
        config = copy.deepcopy(baseline)
        config.update(changes)
        design = build(config)
        checks = verify(design)
        assert abs(design.derived["keyboard_lift"] - expected_lift) < 1e-6, name
        assert abs(design.derived["touch_plane_z"] - expected_top) < 1e-6, name
        assert len(design.risers) == (4 if expected_lift else 0), name
        for riser in design.risers:
            assert riser.val().isValid() and riser.solids().size() == 1
            assert abs(riser.val().BoundingBox().zlen - expected_lift) < 1e-6
        total += len(checks) + 3
        print(f"PASS {name}: {len(checks)} geometry checks")
    for name, changes in [
        ("foot/magnet collision", {"keyboard_feet_in_mount": [[18, -9]]}),
        ("wrong source puck dimensions", {"puck_diameter": 45}),
        ("unprintable thin wall", {"wall": 0.8}),
        ("non-finite dimensions", {"keyboard_foot_height": float("nan")}),
        ("keycaps below case", {"keyboard_keycap_height_from_underside": 8}),
    ]:
        config = copy.deepcopy(baseline)
        config.update(changes)
        try:
            build(config)
        except ValueError:
            print(f"PASS rejects {name}")
        else:
            raise AssertionError(name)
        total += 1
    print(f"{total} checks passed across five fit scenarios and five invalid inputs")


if __name__ == "__main__":
    main()
