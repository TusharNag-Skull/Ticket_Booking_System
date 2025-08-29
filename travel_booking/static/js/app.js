// Theme toggle with persistence
(function () {
  const storageKey = 'lykk-theme';
  const darkClass = 'theme-dark';
  const toggle = document.getElementById('themeToggle');
  const html = document.documentElement;

  function applyTheme(theme) {
    const isDark = theme === 'dark';
    html.classList.toggle(darkClass, isDark);
    const lightIcon = toggle?.querySelector('[data-light-icon]');
    const darkIcon = toggle?.querySelector('[data-dark-icon]');
    const label = toggle?.querySelector('[data-theme-label]');
    if (lightIcon && darkIcon && label) {
      lightIcon.classList.toggle('d-none', isDark);
      darkIcon.classList.toggle('d-none', !isDark);
      label.textContent = isDark ? 'Light' : 'Dark';
    }
  }

  function currentTheme() {
    return localStorage.getItem(storageKey) || 'light';
  }

  applyTheme(currentTheme());

  toggle?.addEventListener('click', function () {
    const next = currentTheme() === 'light' ? 'dark' : 'light';
    localStorage.setItem(storageKey, next);
    applyTheme(next);
  });
})();

// Destination/source suggestions
(function () {
  const destinationInput = document.getElementById('id_destination');
  if (!destinationInput) return;
  const datalistId = 'destinations-list';
  let debounceTimer;

  function updateDatalist(values) {
    let list = document.getElementById(datalistId);
    if (!list) return;
    list.innerHTML = '';
    values.forEach(function (val) {
      const opt = document.createElement('option');
      opt.value = val;
      list.appendChild(opt);
    });
    destinationInput.setAttribute('list', datalistId);
  }

  function fetchSuggestions(query) {
    const url = new URL(window.location.origin + '/api/suggest/');
    url.searchParams.set('q', query);
    url.searchParams.set('field', 'destination');
    fetch(url.toString(), { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (r) { return r.json(); })
      .then(function (data) { updateDatalist(data.results || []); })
      .catch(function () {});
  }

  destinationInput.addEventListener('input', function (e) {
    const q = e.target.value || '';
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () { fetchSuggestions(q); }, 150);
  });
})();

// Dynamic passenger fields based on seats
(function () {
  const seatsInput = document.getElementById('id_number_of_seats');
  const container = document.getElementById('passengerFields');
  const payload = document.getElementById('id_passenger_payload');
  if (!seatsInput || !container || !payload) return;

  function renderFields(count) {
    container.innerHTML = '';
    for (let i = 0; i < count; i += 1) {
      const row = document.createElement('div');
      row.className = 'row g-3 align-items-end mb-2';
      row.innerHTML = `
        <div class="col-md-7">
          <label class="form-label">Passenger ${i + 1} name</label>
          <input type="text" class="form-control" data-passenger-name placeholder="Full name" autocomplete="name">
        </div>
        <div class="col-md-3">
          <label class="form-label">Age</label>
          <input type="number" class="form-control" data-passenger-age min="1" max="120" value="18">
        </div>`;
      container.appendChild(row);
    }
  }

  function updatePayload() {
    const names = container.querySelectorAll('[data-passenger-name]');
    const ages = container.querySelectorAll('[data-passenger-age]');
    const passengers = [];
    for (let i = 0; i < names.length; i += 1) {
      passengers.push({ name: names[i].value || '', age: ages[i].value || '' });
    }
    payload.value = JSON.stringify(passengers);
  }

  seatsInput.addEventListener('input', function () {
    const n = Math.max(0, parseInt(seatsInput.value || '0', 10));
    renderFields(n);
  });

  // keep payload updated before submit
  const form = document.getElementById('bookingForm');
  form?.addEventListener('submit', function () {
    updatePayload();
  });
})();

// Copy shareable search link
(function () {
  const btn = document.getElementById('copySearchLink');
  if (!btn) return;
  function buildUrl() {
    const url = new URL(window.location.origin + '/');
    const params = new URLSearchParams();
    const fields = ['id_source','id_destination','id_type','id_date'];
    fields.forEach(function(fid){
      const el = document.getElementById(fid);
      if (el && el.value) params.set(el.name || fid.replace('id_',''), el.value);
    });
    url.search = params.toString();
    return url.toString();
  }
  btn.addEventListener('click', function(){
    const link = buildUrl();
    navigator.clipboard.writeText(link).then(function(){
      btn.classList.remove('btn-outline-primary');
      btn.classList.add('btn-success');
      btn.innerHTML = '<i class="bi bi-check2 me-1"></i>Link copied';
      setTimeout(function(){
        btn.classList.add('btn-outline-primary');
        btn.classList.remove('btn-success');
        btn.innerHTML = '<i class="bi bi-link-45deg me-1"></i>Copy link';
      }, 1800);
    });
  });
})();

