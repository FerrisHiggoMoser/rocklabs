const frame = document.getElementById('model-view');
const loadStatus = document.getElementById('load-status');
const caption = document.getElementById('view-caption');
const openViewer = document.getElementById('open-viewer');
const buttons = [...document.querySelectorAll('[data-mode]')];
const components = [
  ['carrier', 'aaba96'], ['upper_jaw', 'aaba96'], ['retainer', '8d9f78'],
  ['puck', '434a49'], ['sensor', '222827'], ['feet', '333333'],
  ['hardware', 'a8aaa5'], ['pads', '333333'],
];
const files = {
  suspended: [...components, ['keyboard_reference', 'dedfd9'], ['keycaps_reference', 'b7bdb2']]
    .map(([name, color]) => `suspended_${name}.stl|${color}`),
  attachment: components.map(([name, color]) => `preview_${name}.stl|${color}`),
  print: ['print_plate.stl|aaba96'],
  coupon: ['fit_coupon.stl|aaba96'],
};
const captions = {
  suspended: 'Illustrative 35° keyboard tent, with the puck tilted another 15° toward the keyboard. Green: new attachment. Pale: reference Corne and keys. Your suspension hardware is not modeled.',
  attachment: 'The complete attachment: padded case jaws, two reinforcing webs, and a three-bolt ring around the intact puck. Drag underneath to see the clamp nuts and open foot clearance.',
  print: 'Three printable pieces: carrier on its side, upper jaw, and retaining ring. Check local supports under the carrier in your slicer. Purchased hardware is excluded.',
  coupon: 'Three test pieces: lower clamp interface, upper jaw, and Ø46.5 mm bore gauge. Test with pads and bolts first. This coupon is not a usable suspended mount.',
};

function viewerURL(mode, embed = true) {
  const params = new URLSearchParams({ label: `Suspended puck — ${mode}` });
  if (embed) params.set('embed', '1');
  for (const file of files[mode]) params.append('model', `models/corne_puck_suspended_${file}`);
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
openViewer.href = viewerURL('suspended', false);

window.addEventListener('message', event => {
  if (event.origin !== location.origin || event.source !== frame.contentWindow || event.data?.source !== 'rocklabs-viewer') return;
  if (event.data.type === 'loaded') loadStatus.textContent = '';
  if (event.data.type === 'error') loadStatus.textContent = 'Preview could not load. The download links are available below.';
});

fetch('models/corne_puck_suspended_dimensions.json')
  .then(response => { if (!response.ok) throw new Error('Dimensions unavailable'); return response.json(); })
  .then(report => {
    document.getElementById('print-size').textContent = `STL · ${report.print_sizes.print_plate.map(v => v.toFixed(1)).join(' × ')} mm`;
    const angle = report.derived.tilt_degrees_relative_to_keyboard;
    document.getElementById('tilt').replaceChildren(document.createTextNode(`${angle}° `), Object.assign(document.createElement('small'), { textContent: 'inward' }));
    captions.suspended = captions.suspended.replace('15°', `${angle}°`);
    if (buttons.find(b => b.dataset.mode === 'suspended').getAttribute('aria-pressed') === 'true') caption.textContent = captions.suspended;
    const passed = report.checks.filter(check => check.pass).length;
    document.getElementById('validation').textContent = `${passed} of ${report.checks.length} CAD and STL checks pass: connected parts, printable meshes, device and fastener clearance, puck insertion, and mechanical retention stops.`;
    if (passed !== report.checks.length) document.getElementById('validation').textContent += ' Do not print until the failed checks are resolved.';
  })
  .catch(() => { document.getElementById('print-size').textContent = 'STL · see the dimension report'; });
