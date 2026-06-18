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

<form id="event-form" class="event-submission-form">

  <h2>Submit a Science Festival or Event</h2>

  <p>
    Help us build a global database of science festivals, science communication initiatives,
    public engagement activities, and related events.
  </p>

  <!-- EVENT TITLE -->

  <label for="title">Event Title *</label>
  <input
    type="text"
    id="title"
    name="title"
    required
    maxlength="200"
  >

  <!-- CATEGORIES -->

  <fieldset>
    <legend>Categories *</legend>

    <label><input type="checkbox" name="category" value="Science"> Science</label><br>
    <label><input type="checkbox" name="category" value="Environment"> Environment</label><br>
    <label><input type="checkbox" name="category" value="Society"> Society</label><br>
    <label><input type="checkbox" name="category" value="Humanities"> Humanities</label><br>
    <label><input type="checkbox" name="category" value="Education"> Education</label><br>
    <label><input type="checkbox" name="category" value="Medicine"> Medicine</label><br>
    <label><input type="checkbox" name="category" value="Technology"> Technology</label>
  </fieldset>

  <!-- AUDIENCE -->

  <fieldset>
    <legend>Target Audience *</legend>

    <label><input type="checkbox" name="audience" value="General Public"> General Public</label><br>
    <label><input type="checkbox" name="audience" value="School Students"> School Students</label><br>
    <label><input type="checkbox" name="audience" value="Teachers"> Teachers</label><br>
    <label><input type="checkbox" name="audience" value="Business"> Business</label>
  </fieldset>

  <!-- MONTHS -->

  <fieldset>
    <legend>Months of Occurrence *</legend>

    <label><input type="checkbox" name="month" value="January"> January</label><br>
    <label><input type="checkbox" name="month" value="February"> February</label><br>
    <label><input type="checkbox" name="month" value="March"> March</label><br>
    <label><input type="checkbox" name="month" value="April"> April</label><br>
    <label><input type="checkbox" name="month" value="May"> May</label><br>
    <label><input type="checkbox" name="month" value="June"> June</label><br>
    <label><input type="checkbox" name="month" value="July"> July</label><br>
    <label><input type="checkbox" name="month" value="August"> August</label><br>
    <label><input type="checkbox" name="month" value="September"> September</label><br>
    <label><input type="checkbox" name="month" value="October"> October</label><br>
    <label><input type="checkbox" name="month" value="November"> November</label><br>
    <label><input type="checkbox" name="month" value="December"> December</label>
  </fieldset>

  <!-- EVENT TYPE -->

  <fieldset>
    <legend>Event Type</legend>

    <label>
      <input
        type="radio"
        name="event_type"
        value="Annual"
        checked
      >
      Annual Event
    </label><br>

    <label>
      <input
        type="radio"
        name="event_type"
        value="One-off"
      >
      One-off Event
    </label>
  </fieldset>

  <!-- COUNTRY -->

  <label for="country">Country *</label>

  <select id="country" name="country" required>
    <option value="">Select a country</option>
    <option value="Australia">Australia</option>
    <option value="Canada">Canada</option>
    <option value="France">France</option>
    <option value="Germany">Germany</option>
    <option value="India">India</option>
    <option value="Italy">Italy</option>
    <option value="Japan">Japan</option>
    <option value="Netherlands">Netherlands</option>
    <option value="Spain">Spain</option>
    <option value="United Kingdom">United Kingdom</option>
    <option value="United States">United States</option>
    <option value="Other">Other</option>
  </select>

  <!-- CITY -->

  <label for="city">City / Locality *</label>

  <input
    type="text"
    id="city"
    name="city"
    required
    maxlength="100"
  >

  <!-- ADDRESS -->

  <label for="address">Address / Venue</label>

  <input
    type="text"
    id="address"
    name="address"
    maxlength="250"
  >

  <!-- WEBSITE -->

  <label for="website">Official Website</label>

  <input
    type="url"
    id="website"
    name="website"
    placeholder="https://example.org"
  >

  <!-- DESCRIPTION -->

  <label for="description">Short Description</label>

  <textarea
    id="description"
    name="description"
    rows="6"
    maxlength="1000"
    placeholder="Describe the event, its objectives, activities and target audience..."
  ></textarea>

  <!-- FUTURE MAP SUPPORT -->

  <input type="hidden" id="event_id" name="event_id">
  <input type="hidden" id="latitude" name="latitude">
  <input type="hidden" id="longitude" name="longitude">

  <!-- SUBMITTER -->

  <h3>About You</h3>

  <label for="submitter_name">Name (optional)</label>

  <input
    type="text"
    id="submitter_name"
    name="submitter_name"
    maxlength="100"
  >

  <label for="submitter_email">Email (optional)</label>

  <input
    type="email"
    id="submitter_email"
    name="submitter_email"
  >

  <!-- NEWSLETTER -->

  <fieldset>
    <legend>Newsletter</legend>

    <label>
      <input
        type="checkbox"
        name="newsletter"
        value="yes"
      >
      I would like to receive updates about science festivals, public engagement activities and new additions to the database.
    </label>

  </fieldset>

  <!-- PRIVACY -->

  <fieldset>
    <legend>Privacy Notice</legend>

    <label>
      <input
        type="checkbox"
        name="privacy"
        required
      >
      I confirm that the information provided is publicly available or that I have permission to share it.
    </label>

  </fieldset>

  <!-- SUBMIT -->

  <button type="submit">
    Submit Event
  </button>

</form>