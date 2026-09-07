const frame = document.getElementById('model-view');
const loadStatus = document.getElementById('load-status');
const caption = document.getElementById('view-caption');
const openViewer = document.getElementById('open-viewer');
const buttons = [...document.querySelectorAll('[data-mode]')];
const files = {
  assembly: [
    'corne_puck_dock_print.stl|aaba96',
    'corne_puck_dock_preview_puck.stl|434a49',
    'corne_puck_dock_preview_sensor.stl|222827',
    'corne_puck_dock_preview_feet.stl|333333',
    'corne_puck_dock_preview_hardware.stl|a8aaa5',
    'corne_puck_dock_preview_keyboard_reference.stl|dedfd9',
    'corne_puck_dock_preview_keycaps_reference.stl|b7bdb2',
  ],
  dock: ['corne_puck_dock_print.stl|aaba96'],
  coupon: ['corne_puck_dock_fit_coupon.stl|aaba96'],
};
const captions = {
  assembly: 'Green: printed dock. Dark: your existing puck. Pale: upstream Corne outline and illustrative keycaps; not a measured Keebart fit model.',
  dock: 'One connected printable part. The large underside opening clears the puck feet; four top pockets hold the magnets.',
  coupon: 'Print this first. It preserves the full tongue, magnet positions, puck ledge, and foot clearance with a shorter rim.',
};

function viewerURL(mode, embed = true) {
  const params = new URLSearchParams({ label: `Corne puck dock — ${mode}` });
  if (embed) params.set('embed', '1');
  for (const file of files[mode]) params.append('model', `models/${file}`);
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
openViewer.href = viewerURL('assembly', false);

window.addEventListener('message', event => {
  if (event.origin !== location.origin || event.source !== frame.contentWindow || event.data?.source !== 'rocklabs-viewer') return;
  if (event.data.type === 'loaded') loadStatus.textContent = '';
  if (event.data.type === 'error') loadStatus.textContent = 'Preview could not load. The download links are available below.';
});

fetch('models/corne_puck_dock_dimensions.json')
  .then(response => { if (!response.ok) throw new Error('Dimensions unavailable'); return response.json(); })
  .then(report => {
    document.getElementById('print-size').textContent = `STL · ${report.print_size.map(v => v.toFixed(1)).join(' × ')} mm`;
    document.getElementById('bore').replaceChildren(document.createTextNode(`Ø${report.derived.cradle_inner_diameter.toFixed(1)} `), Object.assign(document.createElement('small'), { textContent: 'mm' }));
    document.getElementById('touch-height').replaceChildren(document.createTextNode(`${report.derived.touch_plane_z.toFixed(1)} `), Object.assign(document.createElement('small'), { textContent: 'mm' }));
    const passed = report.checks.filter(check => check.pass).length;
    document.getElementById('validation').textContent = `${passed} of ${report.checks.length} CAD and STL checks pass: connected printable solids, closed meshes, enclosure clearance, feet, screws, USB access, and the configured alignment.`;
  })
  .catch(() => { document.getElementById('print-size').textContent = 'STL · see the dimension report'; });
