const searchEl = document.getElementById('search');
const rows     = [...document.querySelectorAll('.problem-row')];
const noRes    = document.getElementById('no-results');

// Active tag chips
const activeTags = new Set();

// Active dropdown selections: { ipc: Set, lang: Set }
const dropdownSel = { ipc: new Set(), lang: new Set() };

// ── Tag chips ────────────────────────────────────────────────────────────────
document.querySelectorAll('.tf').forEach(btn => {
  btn.addEventListener('click', () => {
    const tag = btn.dataset.tag, style = btn.dataset.style;
    if (activeTags.has(tag)) { activeTags.delete(tag); btn.classList.remove(style); }
    else                      { activeTags.add(tag);    btn.classList.add(style); }
    filter();
  });
});

// ── Dropdowns ────────────────────────────────────────────────────────────────
function toggleDropdown(id) {
  const dd   = document.getElementById(id);
  const btn  = dd.querySelector('.dropdown-btn');
  const menu = dd.querySelector('.dropdown-menu');
  const isOpen = menu.classList.contains('open');
  // Close all first
  document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('open'));
  document.querySelectorAll('.dropdown-btn').forEach(b => b.classList.remove('open'));
  if (!isOpen) { menu.classList.add('open'); btn.classList.add('open'); }
}

// Close dropdowns when clicking outside
document.addEventListener('click', e => {
  if (!e.target.closest('.dropdown')) {
    document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('open'));
    document.querySelectorAll('.dropdown-btn').forEach(b => b.classList.remove('open'));
  }
});

document.querySelectorAll('.dropdown-item').forEach(item => {
  item.addEventListener('click', e => {
    e.stopPropagation();
    const group = item.dataset.group;   // 'ipc' or 'lang'
    const value = item.dataset.value;
    const sel   = dropdownSel[group];
    if (sel.has(value)) { sel.delete(value); item.classList.remove('selected'); }
    else                { sel.add(value);    item.classList.add('selected'); }
    // Update button highlight
    const btn = document.getElementById('btn-' + group);
    btn.classList.toggle('has-selection', sel.size > 0);
    filter();
  });
});

// ── Search input ─────────────────────────────────────────────────────────────
searchEl.addEventListener('input', filter);

// ── Filter function ───────────────────────────────────────────────────────────
function filter() {
  const q = searchEl.value.trim().toLowerCase();
  let visible = 0;

  rows.forEach(row => {
    const rowTags = (row.dataset.tags || '').split(',').map(s => s.trim());
    const rowIpc  = (row.dataset.ipc  || '').split(',').map(s => s.trim());
    const rowLang = (row.dataset.lang || '').split(',').map(s => s.trim());
    const hay     = (row.dataset.search || '') + ' ' + row.textContent.toLowerCase();

    const textOk = !q || hay.includes(q);
    const tagOk  = activeTags.size === 0      || [...activeTags].every(t => rowTags.includes(t));
    const ipcOk  = dropdownSel.ipc.size === 0 || [...dropdownSel.ipc].some(t => rowIpc.includes(t));
    const langOk = dropdownSel.lang.size === 0|| [...dropdownSel.lang].some(t => rowLang.includes(t));

    const show = textOk && tagOk && ipcOk && langOk;
    row.style.display = show ? '' : 'none';
    if (show) visible++;
  });

  noRes.style.display = visible === 0 ? 'block' : 'none';
}
