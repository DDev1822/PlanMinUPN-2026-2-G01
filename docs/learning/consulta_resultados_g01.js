(() => {
  'use strict';
  const D = window.G01_STUDENT_RESULTS;
  const P = window.G01_PRODUCTS;
  const $ = id => document.getElementById(id);
  const status = $('status');
  if (!D || !P || D.group !== 'G01' ||
      D.s11_run_id !== P.S11?.run_id || D.s12_run_id !== P.S12?.run_id ||
      P.S11?.status !== 'VALIDATED' || P.S12?.status !== 'VALIDATED' ||
      D.fields.length !== 26 || D.blocks.length !== 19734) {
    status.textContent = 'La consulta no coincide con los modelos verificados. Solicita a Kai revisar esta distribución.';
    status.dataset.ready = 'false';
    return;
  }
  status.textContent = 'Resultados verificados de Cerro Azul G01. Puedes consultar las cifras sin abrir archivos técnicos.';
  status.dataset.ready = 'true';
  const columns = new Map(D.block_columns.map((name, index) => [name, index]));
  const blocks = new Map(D.blocks.map(row => [row[0], row]));
  const positions = new Map(D.blocks.map(row => [`${row[1]}:${row[2]}:${row[3]}`, row[0]]));
  const numeric = (value, places) => value === null || value === undefined ? 'Sin estimación / no aplica' :
    new Intl.NumberFormat('es-PE', {minimumFractionDigits: places, maximumFractionDigits: places}).format(value);
  const fieldColumn = {
    'S11.B.CU': 'cu_pct_est', 'S11.B.RHO': 'density_t_m3_est',
    'S11.B.V': 'rock_volume_m3', 'S11.B.T': 'tonnage_t',
    'S11.B.H': 'cu_pct_holes', 'S11.B.MO': 'mo_pct_est',
    'S11.B.AU': 'au_gt_est', 'S12.B.ALLOC': 'allocated_moved_t',
    'S12.B.OPEX': 'total_opex_usd'
  };
  const blockFields = D.fields.filter(f => Boolean(f.block));
  function makeCard(field, value, target) {
    const card = document.createElement('article');
    card.className = 'metric'; card.id = `campo-${field.id}`;
    card.dataset.fieldId = field.id;
    card.dataset.stage = field.stage;
    const label = document.createElement('span'); label.textContent = field.label;
    const strong = document.createElement('strong'); strong.textContent = numeric(value, field.places);
    const unit = document.createElement('small'); unit.textContent = field.unit;
    card.append(label, strong, unit); target.append(card);
  }
  for (const field of D.fields.filter(f => !f.block)) {
    makeCard(field, field.value, $(field.stage.toLowerCase() + '-summary'));
  }
  const viewerBase = {};
  for (const stage of ['S11', 'S12']) {
    viewerBase[stage] = `VISOR_${stage}_G01.html`;
    $(stage.toLowerCase() + '-3d').href = viewerBase[stage];
  }
  let current = null;
  function renderLocator(row) {
    const locator = $('locator'); locator.replaceChildren();
    const [i, j, k] = row.slice(1, 4);
    $('block-position').textContent = `Nivel ${k}; columna este ${i}, columna norte ${j}. Selecciona un vecino para comparar.`;
    for (let dj = 2; dj >= -2; dj--) for (let di = -2; di <= 2; di++) {
      const id = positions.get(`${i + di}:${j + dj}:${k}`);
      const button = document.createElement('button');
      button.type = 'button'; button.disabled = !id;
      button.textContent = id ? `${i + di}, ${j + dj}` : '·';
      button.title = id || 'Fuera de la malla';
      button.setAttribute('aria-label', id ? `Bloque ${id}` : 'Sin bloque');
      if (id === row[0]) button.className = 'active';
      if (id) button.addEventListener('click', () => inspect(id));
      locator.append(button);
    }
  }
  function inspect(id) {
    const row = blocks.get(id.toUpperCase());
    if (!row) { $('block-message').textContent = 'No se encontró ese bloque. Comprueba el identificador o elige una coincidencia.'; return; }
    current = row[0]; $('block-input').value = current;
    $('block-message').textContent = `Bloque ${current} localizado en los modelos verificados S11 y S12.`;
    for (const stage of ['S11', 'S12']) {
      $(stage.toLowerCase() + '-3d').href = viewerBase[stage] + '?bloque=' + encodeURIComponent(current);
    }
    $('suggestions').replaceChildren();
    for (const stage of ['S11', 'S12']) $(stage.toLowerCase() + '-block').replaceChildren();
    for (const field of blockFields) {
      const value = row[columns.get(fieldColumn[field.id])];
      makeCard(field, value, $(field.stage.toLowerCase() + '-block'));
    }
    renderLocator(row);
  }
  $('block-search').addEventListener('click', () => inspect($('block-input').value.trim()));
  $('block-input').addEventListener('keydown', event => { if (event.key === 'Enter') inspect(event.target.value.trim()); });
  $('block-input').addEventListener('input', event => {
    const query = event.target.value.trim().toUpperCase();
    const suggestions = $('suggestions'); suggestions.replaceChildren();
    if (query.length < 5 || blocks.has(query)) return;
    let found = 0;
    for (const id of blocks.keys()) {
      if (!id.includes(query)) continue;
      const button = document.createElement('button'); button.type = 'button'; button.textContent = id;
      button.addEventListener('click', () => inspect(id)); suggestions.append(button);
      if (++found === 6) break;
    }
  });
  const requested = new URLSearchParams(location.search).get('bloque') || D.example_block;
  inspect(requested);
  if (location.hash.startsWith('#campo-')) {
    requestAnimationFrame(() => document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView());
  }
  window.G01_STUDENT_VIEW_READY = true;
})();
