"""Exercise flat-desk fit, side-entry nuts, suspended retention and bad inputs."""
from copy import deepcopy
import json
import math

from generate_corne_dual import ROOT, build, verify, overlap, compound, cylinder, hexagon, box


def main():
    config = json.loads((ROOT / 'cad/corne_dual.json').read_text())
    cases = [
        ('default, original 2 mm keyboard feet', {}),
        ('thicker 3 mm keyboard feet', {'keyboard_foot_height': 3}),
        ('shallower 10 degree puck angle', {'tilt_degrees': 10}),
        ('20 degree puck angle with raised cradle', {'tilt_degrees': 20, 'touch_center_height': 24, 'puck_center_offset': 48}),
        ('thicker case and correct longer clamp bolts', {'keyboard_case_height': 11, 'keyboard_keycap_height_from_underside': 20, 'puck_center_offset': 48}),
    ]
    for name, changes in cases:
        c = {**deepcopy(config), **changes}
        design = build(c)
        checks = verify(design)
        assert design.derived['keyboard_lift'] == 0
        if c['keyboard_case_height'] == 11:
            assert design.derived['clamp_bolt_length'] == 16
        if not changes:
            parts = compound(design.parts.values())
            # Test the actual insertion motion from each open end; testing
            # only the final hex recess would miss an obstructed entry slot.
            for x, y in design.derived['clamp_bolt_centers']:
                for distance in (0, 2, 5, 8, 12):
                    tool = hexagon(x, y + math.copysign(distance, y), design.derived['clamp_nut_bottom_z'], 5.5, 2.4)
                    assert overlap(parts, tool) < 0.001, ('side nut insertion blocked', distance)
                key = cylinder(x, y, c['keyboard_case_height'] + c['pad_thickness'] + 4, 1.5, 30)
                assert overlap(parts, key) < 0.001
            tightened = design.parts['upper_jaw'].translate((0, 0, -0.2))
            assert overlap(tightened, design.parts['carrier']) < 0.001
            assert overlap(tightened, design.obstacles['pads']) > 1
            assert overlap(tightened, design.obstacles['keyboard case envelope']) < 0.001
            assert abs(design.derived['minimum_flat_non_sole_clearance'] - 0.3) < 1e-6
            # A 0.2 mm downward fit tolerance still leaves a gap below the
            # rigid carrier. Do not count the intentional rubber sole contact.
            desk_z = design.derived['desk_plane_z']
            desk = box(0, 0, desk_z - 20, 400, 250, 20)
            assert overlap(design.parts['carrier'].translate((0, 0, -0.2)), desk) < 0.001
            print('PASS side nut insertion, tool access, jaw travel and 0.2 mm desk-clearance margin', flush=True)
        print(f'PASS {name}: {len(checks)} solid geometry checks', flush=True)

    for name, changes in [
        ('keyboard feet too short', {'keyboard_foot_height': 1.8}),
        ('thick pads consume desk clearance', {'pad_thickness': 0.8}),
        ('thin unsupported lip', {'lower_lip_thickness': 0.8}),
        ('missing bare ledge', {'keyboard_upper_lip': 0}),
        ('nonfinite dimension', {'keyboard_foot_height': float('nan')}),
        ('boolean dimension', {'pad_thickness': True}),
        ('steeper angle without desk clearance', {'tilt_degrees': 20}),
    ]:
        try:
            verify(build({**deepcopy(config), **changes}))
        except ValueError:
            print(f'PASS rejects {name}', flush=True)
        else:
            raise AssertionError(f'Accepted invalid fit: {name}')


if __name__ == '__main__':
    main()
