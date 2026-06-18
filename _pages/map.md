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
</script>
