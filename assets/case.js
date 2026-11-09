const frame = document.getElementById('model-view');
const loadStatus = document.getElementById('load-status');
const caption = document.getElementById('view-caption');
const openViewer = document.getElementById('open-viewer');
const buttons = [...document.querySelectorAll('[data-mode]')];
const colors = {
  sleeves: '3a3d41', strap: '151617', divider: 'd8ccb0',
  case: 'cfd2cb', keycaps: 'f0efe9', switches: '2a2b2d', knob: '8f9396', feet: '333333',
};
const keyboard = ['case', 'keycaps', 'switches', 'knob', 'feet'];
const files = {
  closed: ['sleeves', 'strap', 'divider'],
  open: ['sleeves', ...keyboard],
  cutaway: ['sleeves', 'strap', 'divider', ...keyboard],
};
const labels = { closed: 'closed', open: 'open', cutaway: 'cutaway' };
let report = null;

// Fallback numbers match the published report; they are replaced once it loads.
function captionFor(mode) {
  const packed = report ? report.derived.packed : { closed: [144, 125, 72], open: [144, 256, 38] };
  const size = values => values.map(Math.round).join(' × ');
  return {
    closed: `Folded shut at the middle seam, which rolls round the spine. The cable pocket sits on top under the strap, and the strap also holds both openings shut on the far side. Closed it is ${size(packed.closed)} mm.`,
    open: `Open flat, it is one tube with the middle seam across it: two pockets, openings at both ends, and the cable pocket underneath. Here the left half slides into its pocket. ${size(packed.open)} mm.`,
    cutaway: 'Closed and cut through both encoder knobs. The halves meet key over key and knob over knob, with 3 mm of fabric each and the divider between them.',
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
openViewer.href = viewerURL('closed', false);

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
    validation.textContent = `${passed} of ${report.checks.length} CAD and mesh checks pass, including both halves fitting inside their pockets, the strap sitting on the closed case, and every key inside the case outline.`;
    if (passed !== report.checks.length) validation.textContent += ' Check the failed items in the report before cutting.';
  })
  .catch(() => {});
