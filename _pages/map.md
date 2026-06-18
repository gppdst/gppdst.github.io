---
layout: page
title: science festivals map
permalink: /map/
description: Interactive map of science festivals in Italy and Europe.
nav: true
nav_order: 2
---

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.css" />
<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.js"></script>

<div id="filter-bar" style="margin-bottom: 1rem;">
  <div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.5rem;">
    <span style="font-size:0.8rem; color:#666; align-self:center; margin-right:0.3rem;">Theme</span>
    <button class="fbtn active" data-type="theme" data-value="">All</button>
    <button class="fbtn" data-type="theme" data-value="science" style="--c:#3a86ff">Science</button>
    <button class="fbtn" data-type="theme" data-value="environment" style="--c:#57cc99">Environment</button>
    <button class="fbtn" data-type="theme" data-value="society" style="--c:#ff9f1c">Society</button>
    <button class="fbtn" data-type="theme" data-value="humanities" style="--c:#9b5de5">Humanities</button>
    <button class="fbtn" data-type="theme" data-value="education" style="--c:#f9c74f">Education</button>
    <button class="fbtn" data-type="theme" data-value="medicine" style="--c:#e63946">Medicine</button>
    <button class="fbtn" data-type="theme" data-value="technology" style="--c:#3a86ff">Technology</button>
    <button class="fbtn" data-type="theme" data-value="journalism" style="--c:#ff9f1c">Journalism</button>
  </div>
  <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
    <span style="font-size:0.8rem; color:#666; align-self:center; margin-right:0.3rem;">Audience</span>
    <button class="fbtn active" data-type="public" data-value="">All</button>
    <button class="fbtn" data-type="public" data-value="general public">General public</button>
    <button class="fbtn" data-type="public" data-value="school">Schools</button>
    <button class="fbtn" data-type="public" data-value="teachers">Teachers</button>
    <button class="fbtn" data-type="public" data-value="business">Business</button>
  </div>
  <div style="margin-top: 0.5rem;">
    <span id="festival-count" style="font-size:0.8rem; color:#666;"></span>
  </div>
</div>

<div id="map" style="height: 560px; width: 100%; border-radius: 8px; margin-bottom: 2rem;"></div>

<div id="suggest-festival">
  <h3>something missing? submit a festival</h3>
  <form id="festival-form" action="https://formspree.io/f/xykaqnyg" method="POST">
    <div class="form-group">
      <label for="f-name">Title <span class="required">*</span></label>
      <input type="text" id="f-name" name="name" required>
    </div>
    <div class="form-group">
      <label>Theme</label>
      <div class="chip-group" data-name="theme[]">
        <button type="button" class="chip" data-value="science">Science</button>
        <button type="button" class="chip" data-value="environment">Environment</button>
        <button type="button" class="chip" data-value="society">Society</button>
        <button type="button" class="chip" data-value="humanities">Humanities</button>
        <button type="button" class="chip" data-value="education">Education</button>
        <button type="button" class="chip" data-value="medicine">Medicine</button>
        <button type="button" class="chip" data-value="technology">Technology</button>
        <button type="button" class="chip" data-value="journalism">Journalism</button>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label for="f-country">Country</label>
        <input type="text" id="f-country" name="country">
      </div>
      <div class="form-group">
        <label for="f-address">Address</label>
        <input type="text" id="f-address" name="address">
      </div>
    </div>
    <div class="form-group">
      <label>Audience</label>
      <div class="chip-group" data-name="public[]">
        <button type="button" class="chip" data-value="general public">General public</button>
        <button type="button" class="chip" data-value="school">Schools</button>
        <button type="button" class="chip" data-value="teachers">Teachers</button>
        <button type="button" class="chip" data-value="business">Business</button>
      </div>
    </div>
    <div class="form-group">
      <label for="f-description">Short description</label>
      <textarea id="f-description" name="description" rows="3" placeholder="A couple of sentences about the festival..."></textarea>
    </div>
    <div class="form-group">
      <label for="f-website">Website <span class="required">*</span></label>
      <input type="url" id="f-website" name="website" placeholder="https://" required>
    </div>
    <div class="form-group newsletter-opt">
      <label class="checkbox-label">
        <input type="checkbox" name="newsletter" value="yes">
        keep me updated
      </label>
    </div>
    <button type="submit" class="submit-btn">Submit festival</button>
    <p id="form-success" style="display:none;">Thanks! Your suggestion has been sent.</p>
  </form>
</div>

<script>
const THEME_COLORS = {
  science:     '#3a86ff',
  environment: '#57cc99',
  society:     '#ff9f1c',
  humanities:  '#9b5de5',
  education:   '#f9c74f',
  medicine:    '#e63946',
  technology:  '#3a86ff',
  journalism:  '#ff9f1c',
};

function getColor(theme) {
  return THEME_COLORS[theme] || '#adb5bd';
}

function formatList(arr) {
  if (!arr || !arr.length) return '';
  return arr.join(' · ');
}

function formatTags(arr) {
  if (!arr || !arr.length) return '';
  return arr.map(t => `<span class="tag">${t}</span>`).join(' ');
}

const map = L.map('map').setView([46, 12], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  maxZoom: 18
}).addTo(map);

let allMarkers = [];
let activeThemes = new Set();
let activePublic = new Set();

fetch('/assets/data/festivals.json')
  .then(r => r.json())
  .then(festivals => {
    festivals.forEach(f => {
      const lat = parseFloat(f.lat);
      const lon = parseFloat(f.lon);
      if (isNaN(lat) || isNaN(lon)) return;

      const color = getColor(f.theme);

      const marker = L.circleMarker([lat, lon], {
        radius: 6,
        fillColor: color,
        color: '#fff',
        weight: 1.5,
        opacity: 1,
        fillOpacity: 0.85
      });

      const pub = Array.isArray(f.public) ? f.public : [f.public];
      const tags = Array.isArray(f.tags) ? f.tags : (f.tags ? f.tags.split(';') : []);

      marker.bindPopup(`
        <div style="max-width:260px;">
          <strong style="font-size:0.95rem;">${f.name}</strong><br><br>
          📍 ${f.location}<br>
          🗓️ ${f.period}<br>
          👥 ${formatList(pub)}<br>
          🌍 ${f.country}<br><br>
          ${formatTags(tags)}
          ${f.website ? `<br><br><a href="${f.website}" target="_blank">🔗 Website</a>` : ''}
        </div>
      `);

      marker.festivalTheme = f.theme || '';
      marker.festivalPublic = pub.map(p => p.toLowerCase());
      allMarkers.push(marker);
      marker.addTo(map);
    });

    updateCount();
  });

function applyFilters() {
  allMarkers.forEach(marker => {
    const matchTheme = activeThemes.size === 0 || activeThemes.has(marker.festivalTheme);
    const matchPublic = activePublic.size === 0 || marker.festivalPublic.some(p => [...activePublic].some(a => p.includes(a)));
    if (matchTheme && matchPublic) marker.addTo(map);
    else map.removeLayer(marker);
  });
  updateCount();
}

function updateCount() {
  const n = allMarkers.filter(m => map.hasLayer(m)).length;
  document.getElementById('festival-count').textContent = `${n} festival shown`;
}

// Gestione pulsanti
document.querySelectorAll('.fbtn').forEach(btn => {
  btn.addEventListener('click', () => {
    const type = btn.dataset.type;
    const value = btn.dataset.value;

    if (type === 'theme') {
      if (value === '') {
        // All themes
        activeThemes.clear();
        document.querySelectorAll('.fbtn[data-type="theme"]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      } else {
        // Toggling multi-select
        document.querySelector('.fbtn[data-type="theme"][data-value=""]').classList.remove('active');
        if (activeThemes.has(value)) {
          activeThemes.delete(value);
          btn.classList.remove('active');
          if (activeThemes.size === 0) {
            document.querySelector('.fbtn[data-type="theme"][data-value=""]').classList.add('active');
          }
        } else {
          activeThemes.add(value);
          btn.classList.add('active');
        }
      }
    }

   if (type === 'public') {
      if (value === '') {
        activePublic.clear();
        document.querySelectorAll('.fbtn[data-type="public"]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      } else {
        document.querySelector('.fbtn[data-type="public"][data-value=""]').classList.remove('active');
        if (activePublic.has(value)) {
          activePublic.delete(value);
          btn.classList.remove('active');
          if (activePublic.size === 0) {
            document.querySelector('.fbtn[data-type="public"][data-value=""]').classList.add('active');
          }
        } else {
          activePublic.add(value);
          btn.classList.add('active');
        }
      }
    }

    applyFilters();
  });
});

// Gestione chip selezionabili (multi-select)
document.querySelectorAll('.chip-group').forEach(group => {
  group.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('active');
    });
  });
});

// Gestione invio form di segnalazione
document.getElementById('festival-form').addEventListener('submit', function(e) {
  e.preventDefault();
  const form = e.target;
  const data = new FormData(form);

  document.querySelectorAll('.chip-group').forEach(group => {
    const fieldName = group.dataset.name;
    group.querySelectorAll('.chip.active').forEach(chip => {
      data.append(fieldName, chip.dataset.value);
    });
  });

  fetch(form.action, {
    method: 'POST',
    body: data,
    headers: { 'Accept': 'application/json' }
  }).then(response => {
    if (response.ok) {
      form.style.display = 'none';
      document.getElementById('form-success').style.display = 'block';
    }
  });
});

</script>

<style>
.fbtn {
  padding: 0.25rem 0.7rem;
  border-radius: 20px;
  border: 1.5px solid #ccc;
  background: white;
  cursor: pointer;
  font-size: 0.78rem;
  transition: all 0.15s;
  color: #333;
}
.fbtn:hover { background: #f5f5f5; }
.fbtn.active {
  background: var(--c, #333);
  border-color: var(--c, #333);
  color: white;
}
.fbtn[data-value=""].active {
  background: #333;
  border-color: #333;
  color: white;
}
.tag {
  display: inline-block;
  background: #f0f0f0;
  border-radius: 10px;
  padding: 0.1rem 0.45rem;
  font-size: 0.72rem;
  margin: 0.1rem;
  color: #555;
}
#map { margin-bottom: 2rem; }
@media (max-width: 768px) {
  #map { height: 420px; margin-bottom: 4rem; }
}

#suggest-festival {
  margin-top: 1rem;
  padding: 1.8rem;
  border: 1px solid #d0d0d0;
  border-radius: 14px;
  background: #fafafa;
}
#suggest-festival h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #333;
}
.form-group {
  margin-bottom: 1.3rem;
}
.form-row {
  display: flex;
  gap: 1.2rem;
}
.form-row .form-group {
  flex: 1;
}
.form-group label {
  display: block;
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 0.4rem;
  font-weight: 500;
}
.required {
  color: #e63946;
}
.form-group input[type="text"],
.form-group input[type="url"],
.form-group textarea {
  width: 100%;
  padding: 0.6rem 0.8rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 0.85rem;
  font-family: inherit;
  box-sizing: border-box;
  transition: border-color 0.2s;
  resize: vertical;
}
.form-group input[type="text"]:focus,
.form-group input[type="url"]:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #888;
}
.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.chip {
  font-size: 0.78rem;
  color: #555;
  font-weight: 400;
  cursor: pointer;
  background: white;
  border: 1.5px solid #ddd;
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  transition: all 0.15s;
}
.chip:hover { border-color: #999; }
.chip.active {
  background: #333;
  border-color: #333;
  color: white;
}
.newsletter-opt {
  border-top: 1px solid #e8e8e8;
  padding-top: 1.2rem;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #555;
  cursor: pointer;
}
.submit-btn {
  background: #333;
  color: white;
  border: none;
  padding: 0.65rem 1.5rem;
  border-radius: 20px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
}
.submit-btn:hover { background: #555; }
#form-success {
  color: #57cc99;
  font-size: 0.85rem;
  margin-top: 0.9rem;
}
@media (max-width: 768px) {
  .form-row { flex-direction: column; gap: 1.3rem; }
}
</style>