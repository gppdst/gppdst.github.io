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
</script>
--- %Form
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
</style>

<style>

.submit-card{
  max-width:700px;
  margin:2rem auto 0;
  padding:1rem 1.2rem;
  border:1px solid var(--global-divider-color);
  border-radius:12px;
  background:var(--global-bg-color);
}

.submit-card p{
  margin-bottom:1rem;
  color:var(--global-text-color-light);
  font-size:.9rem;
}

.submit-card input[type=text],
.submit-card input[type=url]{
  width:100%;
  padding:.65rem .8rem;
  border:1px solid var(--global-divider-color);
  border-radius:8px;
  margin-bottom:.8rem;
}

.grid-2{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:.6rem;
}

.tag-row{
  display:flex;
  flex-wrap:wrap;
  gap:.4rem;
  margin-bottom:.8rem;
}

.tag-label{
  font-size:.8rem;
  color:#666;
  align-self:center;
  margin-right:.3rem;
}

.tag-btn{
  border:none;
  background:#f3f4f6;
  color:#444;
  border-radius:999px;
  padding:.3rem .8rem;
  font-size:.85rem;
  cursor:pointer;
}

.submit-btn{
  width:100%;
  padding:.75rem;
  border:none;
  border-radius:8px;
  cursor:pointer;
}

</style>

<div class="submit-card">

  <p>
    Know a festival that is missing?
    Help us improve the database.
  </p>

  <input
    type="text"
    placeholder="Festival title"
  >

  <div class="grid-2">

    <input
      type="text"
      placeholder="Country"
    >

    <input
      type="text"
      placeholder="City / Venue"
    >

  </div>

  <div class="tag-row">
    <span class="tag-label">Theme</span>

    <button class="tag-btn">Science</button>
    <button class="tag-btn">Environment</button>
    <button class="tag-btn">Society</button>
    <button class="tag-btn">Humanities</button>
    <button class="tag-btn">Education</button>
    <button class="tag-btn">Medicine</button>
    <button class="tag-btn">Technology</button>
  </div>

  <div class="tag-row">
    <span class="tag-label">Audience</span>

    <button class="tag-btn">General public</button>
    <button class="tag-btn">Schools</button>
    <button class="tag-btn">Teachers</button>
    <button class="tag-btn">Business</button>
  </div>

  <input
    type="url"
    placeholder="Website"
  >

  <label style="font-size:.85rem;">
    <input type="checkbox">
    Keep me informed about updates
  </label>

  <button class="submit-btn">
    Submit Festival
  </button>

</div>