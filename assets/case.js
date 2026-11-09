const frame = document.getElementById('model-view');
const loadStatus = document.getElementById('load-status');
const caption = document.getElementById('view-caption');
const openViewer = document.getElementById('open-viewer');
const buttons = [...document.querySelectorAll('[data-mode]')];
const colors = {
  sleeves: '3a3d41', sleeve: '3a3d41', bands: '151617', divider: 'd8ccb0',
  case: 'cfd2cb', keycaps: 'f0efe9', switches: '2a2b2d', knob: '8f9396', feet: '333333',
};
const keyboard = ['case', 'keycaps', 'switches', 'knob', 'feet'];
const files = {
  side: ['sleeves', 'bands'],
  stacked: ['sleeves', 'bands', 'divider'],
  sliding: ['sleeve', ...keyboard],
  cutaway: ['sleeves', 'bands', ...keyboard],
};
const labels = { side: 'side by side', stacked: 'stacked', sliding: 'sliding in', cutaway: 'cutaway' };
let report = null;

// Fallback numbers match the published report; they are replaced once it loads.
function captionFor(mode) {
  const packed = report ? report.derived.packed : { side_by_side: [144, 211, 33], stacked: [144, 107, 64] };
  const size = values => values.map(Math.round).join(' × ');
  return {
    side: `Long edges together, openings facing out. Two elastic loops run across both sleeves and hold both openings shut. Packed it is ${size(packed.side_by_side)} mm, about the size of an A5 notebook.`,
    stacked: `One sleeve on the other with a thin, stiff divider between them, so the keycaps never press into each other. Packed it is ${size(packed.stacked)} mm.`,
    sliding: 'Each half slides into its own sleeve through the opening. The fit is snug; the neoprene stretches enough to get it in.',
    cutaway: 'Cut through the front sleeve at the encoder knob, the tallest part of the half. 3 mm of fabric all round and 1 mm of play at the sides.',
  }[mode];
}

function viewerURL(mode, embed = true) {
  const params = new URLSearchParams({ label: `Corne neoprene case — ${labels[mode]}` });
  if (embed) params.set('embed', '1');
  for (const part of files[mode]) params.append('model', `models/corne_case_${mode}_${part}.stl|${colors[part]}`);
  return `viewer.html?${params}`;
}

function currentMode() {
  return buttons.find(button => button.getAttribute('aria-pressed') === 'true').dataset.mode;
}

buttons.forEach(button => button.addEventListener('click', () => {
  const mode = button.dataset.mode;
  buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  loadStatus.textContent = 'Loading the actual STL files…';
  caption.textContent = captionFor(mode);
  openViewer.href = viewerURL(mode, false);
  frame.src = viewerURL(mode);
}));
openViewer.href = viewerURL('side', false);

window.addEventListener('message', event => {
  if (event.origin !== location.origin || event.source !== frame.contentWindow || event.data?.source !== 'rocklabs-viewer') return;
  if (event.data.type === 'loaded') loadStatus.textContent = '';
  if (event.data.type === 'error') loadStatus.textContent = 'Preview could not load. The pattern and measurements below still apply.';
});

function format(value) {
  if (Array.isArray(value)) return value.map(Math.round).join(' × ');
  return Number.isInteger(value) ? String(value) : value.toFixed(1).replace(/\.0$/, '');
}

fetch('models/corne_case_dimensions.json')
  .then(response => { if (!response.ok) throw new Error('Dimensions unavailable'); return response.json(); })
  .then(data => {
    report = data;
    for (const el of document.querySelectorAll('[data-fill]')) {
      const value = el.dataset.fill.split('.').reduce((node, key) => node?.[key], report);
      if (typeof value === 'number' || Array.isArray(value)) el.textContent = format(value);
    }
    caption.textContent = captionFor(currentMode());
    const passed = report.checks.filter(check => check.pass).length;
    const validation = document.getElementById('validation');
    validation.textContent = `${passed} of ${report.checks.length} CAD and mesh checks pass, including both halves fitting inside their sleeves, every key inside the case outline, and the elastic staying within 1 m.`;
    if (passed !== report.checks.length) validation.textContent += ' Check the failed items in the report before cutting.';
  })
  .catch(() => {});
