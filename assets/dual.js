const frame = document.getElementById('model-view');
const loadStatus = document.getElementById('load-status');
const caption = document.getElementById('view-caption');
const openViewer = document.getElementById('open-viewer');
const buttons = [...document.querySelectorAll('[data-mode]')];
const components = [
  ['carrier', 'aaba96'], ['upper_jaw', 'aaba96'], ['retainer', '8d9f78'],
  ['puck', '434a49'], ['sensor', '222827'], ['feet', '333333'],
  ['hardware', 'a8aaa5'], ['pads', '333333'], ['desk_pads', '333333'],
];
const references = [['keyboard_reference', 'dedfd9'], ['keycaps_reference', 'b7bdb2'], ['keyboard_feet_reference', '555555']];
const files = {
  flat: [...components, ...references, ['desk_reference', 'e9e3d8']]
    .map(([name, color]) => `flat_${name}.stl|${color}`),
  suspended: [...components, ...references]
    .map(([name, color]) => `suspended_${name}.stl|${color}`),
  attachment: components.map(([name, color]) => `preview_${name}.stl|${color}`),
  print: ['print_plate.stl|aaba96'],
  coupon: ['fit_coupon.stl|aaba96'],
};
const captions = {
  flat: 'Keyboard level on its own feet. The two puck soles meet the same desk plane; the thin clamp lip and screws stay above it. The puck keeps its 15° angle. Pale keyboard and foot positions are illustrative.',
  suspended: 'The same assembled parts in an illustrative 35° keyboard pose. The case clamp, puck ring, and desk legs all stay attached. Your suspension hardware is not modeled.',
  attachment: 'Thin under-case lip, side-entry clamp nuts, raised reinforcing webs, bolted puck ring, and two permanent desk legs. Drag underneath to inspect the contact pads.',
  print: 'Three printable pieces: carrier on its side, upper jaw, and retaining ring. Check local supports under the carrier in your slicer. Purchased hardware is excluded.',
  coupon: 'Three test pieces: lower clamp interface, upper jaw, and Ø46.5 mm bore gauge. Test with pads and bolts first. This coupon is not a usable suspended mount.',
};

function viewerURL(mode, embed = true) {
  const params = new URLSearchParams({ label: `Desk + suspended puck — ${mode}` });
  if (embed) params.set('embed', '1');
  for (const file of files[mode]) params.append('model', `models/corne_puck_dual_${file}`);
  return `viewer.html?${params}`;
}

buttons.forEach(button => button.addEventListener('click', () => {
  const mode = button.dataset.mode;
  buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  loadStatus.textContent = 'Loading the actual STL files…';
  caption.textContent = captions[mode];
  openViewer.href = viewerURL(mode, false);
  frame.src = viewerURL(mode);
}));
openViewer.href = viewerURL('flat', false);

window.addEventListener('message', event => {
  if (event.origin !== location.origin || event.source !== frame.contentWindow || event.data?.source !== 'rocklabs-viewer') return;
  if (event.data.type === 'loaded') loadStatus.textContent = '';
  if (event.data.type === 'error') loadStatus.textContent = 'Preview could not load. The download links are available below.';
});

fetch('models/corne_puck_dual_dimensions.json')
  .then(response => { if (!response.ok) throw new Error('Dimensions unavailable'); return response.json(); })
  .then(report => {
    document.getElementById('print-size').textContent = `STL · ${report.print_sizes.print_plate.map(v => v.toFixed(1)).join(' × ')} mm`;
    const angle = report.derived.tilt_degrees_relative_to_keyboard;
    document.getElementById('tilt').replaceChildren(document.createTextNode(`${angle}° `), Object.assign(document.createElement('small'), { textContent: 'inward' }));
    captions.flat = captions.flat.replace('15°', `${angle}°`);
    if (buttons.find(b => b.dataset.mode === 'flat').getAttribute('aria-pressed') === 'true') caption.textContent = captions.flat;
    document.getElementById('desk-clearance').textContent = `${report.derived.under_case_desk_clearance.toFixed(1)} mm`;
    const passed = report.checks.filter(check => check.pass).length;
    document.getElementById('validation').textContent = `${passed} of ${report.checks.length} CAD and STL checks pass, including desk clearance for every real component, both sole contacts, zero keyboard lift, and puck retention in all six directions.`;
    if (passed !== report.checks.length) document.getElementById('validation').textContent += ' Do not print until the failed checks are resolved.';
  })
  .catch(() => { document.getElementById('print-size').textContent = 'STL · see the dimension report'; });
