// ── Tab switching ─────────────────────────────────────────────────────────
function show(id, el) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
}

// ── Jump to reference ─────────────────────────────────────────────────────
function jumpToRef(key) {
  const tab = [...document.querySelectorAll('.tab')]
    .find(t => t.textContent.trim().toLowerCase() === 'references');
  if (tab) show('references', tab);
  setTimeout(() => {
    const el = document.getElementById('ref-' + key);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 50);
}

// ── Jump to domain card (switches to Domains tab, opens + scrolls) ────────
function jumpToDomain(key) {
  const tab = [...document.querySelectorAll('.tab')]
    .find(t => t.textContent.trim().toLowerCase() === 'domains');
  if (tab) show('domains', tab);
  setTimeout(() => {
    const card = document.getElementById('domain-' + key);
    if (card) {
      const body    = document.getElementById('body-domain-'    + key);
      const chevron = document.getElementById('chevron-domain-' + key);
      const header  = document.getElementById('header-domain-'  + key);
      if (body && !body.classList.contains('open')) {
        body.classList.add('open');
        if (chevron) chevron.classList.add('open');
        if (header)  header.classList.add('open');
      }
      card.scrollIntoView({ behavior: 'smooth', block: 'start' });
      card.style.outline = '1px solid var(--accent)';
      setTimeout(() => { card.style.outline = ''; }, 1200);
    }
  }, 50);
}

// ── Card expand/collapse ──────────────────────────────────────────────────
function toggleCard(cardId) {
  const body    = document.getElementById('body-'    + cardId);
  const chevron = document.getElementById('chevron-' + cardId);
  const header  = document.getElementById('header-'  + cardId);
  const isOpen  = body.classList.contains('open');
  body.classList.toggle('open',    !isOpen);
  if (chevron) chevron.classList.toggle('open', !isOpen);
  if (header)  header.classList.toggle('open',  !isOpen);
}

// ── Blob download ─────────────────────────────────────────────────────────
function downloadText(filename, content) {
  const blob = new Blob([content], { type: 'text/plain' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

// ── Hash handling ─────────────────────────────────────────────────────────
if (window.location.hash) {
  const hash = window.location.hash.slice(1);
  if (hash.startsWith('ref-')) {
    const tab = [...document.querySelectorAll('.tab')]
      .find(t => t.textContent.trim().toLowerCase() === 'references');
    if (tab) show('references', tab);
  } else if (hash.startsWith('domain-')) {
    jumpToDomain(hash.slice(7));
  }
}
