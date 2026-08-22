// GyepMester – Fő JavaScript

/* === FLASH ÜZENET BEZÁRÁS === */
document.querySelectorAll('.flash-close').forEach(btn => {
  btn.addEventListener('click', () => {
    btn.closest('.flash').style.animation = 'slideOut 0.3s ease forwards';
    setTimeout(() => btn.closest('.flash').remove(), 300);
  });
});

// 5 másodperc után automatikus eltüntetés
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => {
    el.style.animation = 'slideOut 0.3s ease forwards';
    setTimeout(() => el.remove(), 300);
  });
}, 5000);


/* === TERMÉK AUTO-KITÖLTÉS – FŰMAG === */
const grassProductSelect = document.getElementById('grass_seed_product_id');
const grassTypeInput = document.getElementById('grass_type');
const grassAutoInfo = document.getElementById('grass-auto-info');

if (grassProductSelect) {
  grassProductSelect.addEventListener('change', async () => {
    const id = grassProductSelect.value;
    if (!id) {
      if (grassAutoInfo) grassAutoInfo.classList.remove('visible');
      return;
    }
    try {
      const resp = await fetch(`/api/grass-product/${id}`);
      const data = await resp.json();
      if (grassTypeInput) {
        grassTypeInput.value = data.grass_types;
        grassTypeInput.dispatchEvent(new Event('input'));
      }
      if (grassAutoInfo) {
        grassAutoInfo.textContent =
          `✅ Auto-kitöltve: ${data.brand} – ${data.product_name} | ` +
          `Fűtípus: ${data.grass_types} | Felhasználás: ${data.usage}`;
        grassAutoInfo.classList.add('visible');
      }
    } catch (e) {
      console.error('Grass product fetch error:', e);
    }
  });
}


/* === TERMÉK AUTO-KITÖLTÉS – MŰTRÁGYA === */
const fertProductSelect = document.getElementById('fertilizer_product_id');
const fertTypeInput = document.getElementById('fertilizer_type');
const fertNInput = document.getElementById('npk_n');
const fertPInput = document.getElementById('npk_p');
const fertKInput = document.getElementById('npk_k');
const fertAutoInfo = document.getElementById('fert-auto-info');

if (fertProductSelect) {
  fertProductSelect.addEventListener('change', async () => {
    const id = fertProductSelect.value;
    if (!id) {
      if (fertAutoInfo) fertAutoInfo.classList.remove('visible');
      return;
    }
    try {
      const resp = await fetch(`/api/fertilizer-product/${id}`);
      const data = await resp.json();
      if (fertTypeInput)  fertTypeInput.value  = data.fertilizer_type;
      if (fertNInput)     fertNInput.value     = data.npk_n;
      if (fertPInput)     fertPInput.value     = data.npk_p;
      if (fertKInput)     fertKInput.value     = data.npk_k;
      if (fertAutoInfo) {
        fertAutoInfo.innerHTML =
          `✅ <strong>${data.brand} – ${data.product_name}</strong> | ` +
          `NPK: <strong>${data.npk}</strong> | ` +
          `Típus: ${data.fertilizer_type} | Szezon: ${data.season}` +
          (data.description ? `<br><em style="opacity:.7">${data.description}</em>` : '');
        fertAutoInfo.classList.add('visible');
      }
    } catch (e) {
      console.error('Fertilizer product fetch error:', e);
    }
  });
}


/* === FORRÁS VÁLTÓ (termék vs kézi) === */
function initSourceToggle(radioName, productSection, manualSection) {
  const radios = document.querySelectorAll(`input[name="${radioName}"]`);
  const productEl = document.getElementById(productSection);
  const manualEl = document.getElementById(manualSection);

  if (!radios.length) return;

  function update() {
    const val = document.querySelector(`input[name="${radioName}"]:checked`)?.value;
    if (productEl) productEl.style.display = val === 'product' ? 'block' : 'none';
    if (manualEl)  manualEl.style.display  = val === 'manual'  ? 'block' : 'none';
  }

  radios.forEach(r => r.addEventListener('change', update));
  update();
}

initSourceToggle('grass_type_source',        'grass-product-section',  'grass-manual-section');
initSourceToggle('fertilizer_type_source',   'fert-product-section',   'fert-manual-section');


/* === KÉP ELŐNÉZET === */
document.querySelectorAll('input[type="file"]').forEach(input => {
  const preview = document.getElementById(input.id + '_preview');
  if (!preview) return;
  input.addEventListener('change', () => {
    const file = input.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = e => {
        preview.src = e.target.result;
        preview.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
  });
});


/* === TÖRLÉS MEGERŐSÍTÉS === */
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});


/* === CSÚSZÓANIMÁCIÓ (fade-in) === */
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('fade-in');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.card, .suggestion-card, .lawn-card').forEach(el => {
  observer.observe(el);
});


/* === NAPTÁR ESEMÉNYEK === */
window.initCalendar = function(events) {
  events.forEach(event => {
    const cell = document.querySelector(`[data-date="${event.date}"]`);
    if (!cell) return;
    cell.classList.add('has-events');
    const dot = document.createElement('div');
    dot.className = 'calendar-event-dot';
    dot.style.background = event.color;
    dot.title = event.label;
    cell.appendChild(dot);
  });
};
