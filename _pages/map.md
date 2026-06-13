---
layout: page
title: science festivals
permalink: /map/
description: Interactive map of science festivals in Italy and Europe.
nav: true
nav_order: 2
---

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.css" />
<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.js"></script>

<div id="festival-filters" style="margin-bottom: 1rem; display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;">
  <select id="filter-theme" style="padding: 0.4rem 0.8rem; border-radius: 20px; border: 1px solid #ccc; font-size: 0.85rem; cursor: pointer;">
    <option value="">🏷️ All themes</option>
  </select>
  <select id="filter-public" style="padding: 0.4rem 0.8rem; border-radius: 20px; border: 1px solid #ccc; font-size: 0.85rem; cursor: pointer;">
    <option value="">👥 All audiences</option>
    <option value="general public">General public</option>
    <option value="school">Schools</option>
    <option value="business">Business</option>
    <option value="teachers">Teachers</option>
  </select>
  <select id="filter-country" style="padding: 0.4rem 0.8rem; border-radius: 20px; border: 1px solid #ccc; font-size: 0.85rem; cursor: pointer;">
    <option value="">🌍 All countries</option>
  </select>
  <span id="festival-count" style="font-size: 0.85rem; color: #666;"></span>
</div>

<div id="map" style="height: 580px; width: 100%; border-radius: 8px;"></div>

<script>
  const THEME_GROUPS = {
    science:     { group: 'Science',     color: '#3a86ff' },
    technology:  { group: 'Science',     color: '#3a86ff' },
    physics:     { group: 'Science',     color: '#3a86ff' },
    space:       { group: 'Science',     color: '#3a86ff' },
    geology:     { group: 'Science',     color: '#3a86ff' },
    research:    { group: 'Science',     color: '#3a86ff' },
    innovation:  { group: 'Science',     color: '#3a86ff' },
    environment: { group: 'Environment', color: '#57cc99' },
    biodiversity:{ group: 'Environment', color: '#57cc99' },
    water:       { group: 'Environment', color: '#57cc99' },
    climate:     { group: 'Environment', color: '#57cc99' },
    sustainability:{ group: 'Environment', color: '#57cc99' },
    landscape:   { group: 'Environment', color: '#57cc99' },
    animals:     { group: 'Environment', color: '#57cc99' },
    society:     { group: 'Society',     color: '#ff9f1c' },
    democracy:   { group: 'Society',     color: '#ff9f1c' },
    economy:     { group: 'Society',     color: '#ff9f1c' },
    journalism:  { group: 'Society',     color: '#ff9f1c' },
    humanities:  { group: 'Humanities',  color: '#9b5de5' },
    literature:  { group: 'Humanities',  color: '#9b5de5' },
    philosophy:  { group: 'Humanities',  color: '#9b5de5' },
    history:     { group: 'Humanities',  color: '#9b5de5' },
    teaching:    { group: 'Education',   color: '#f9c74f' },
    edu:         { group: 'Education',   color: '#f9c74f' },
    art:         { group: 'Entertainment', color: '#f72585' },
    food:        { group: 'Entertainment', color: '#f72585' },
    entertainment:{ group: 'Entertainment', color: '#f72585' },
    agriculture: { group: 'Entertainment', color: '#f72585' },
    medicine:    { group: 'Medicine',    color: '#e63946' },
    meteorology: { group: 'Science',     color: '#3a86ff' },
  };

  const GROUP_COLORS = {
    'Science':       '#3a86ff',
    'Environment':   '#57cc99',
    'Society':       '#ff9f1c',
    'Humanities':    '#9b5de5',
    'Education':     '#f9c74f',
    'Entertainment': '#f72585',
    'Medicine':      '#e63946',
    'Other':         '#adb5bd',
  };

  function getColor(tags) {
    for (const tag of tags) {
      if (THEME_GROUPS[tag]) return THEME_GROUPS[tag].color;
    }
    return GROUP_COLORS['Other'];
  }

  function getGroup(tags) {
    for (const tag of tags) {
      if (THEME_GROUPS[tag]) return THEME_GROUPS[tag].group;
    }
    return 'Other';
  }

  function makeCircleMarker(lat, lon, color) {
    return L.circleMarker([lat, lon], {
      radius: 7,
      fillColor: color,
      color: '#fff',
      weight: 1.5,
      opacity: 1,
      fillOpacity: 0.85
    });
  }

  function formatList(value) {
    if (!value) return '';
    return value.split(';').map(v => v.trim()).filter(Boolean).join(' · ');
  }

  function formatTags(value) {
    if (!value) return '';
    return value.split(';').map(v => v.trim()).filter(Boolean)
      .map(t => `<span class="tag">${t}</span>`).join(' ');
  }

  const map = L.map('map').setView([46, 12], 5);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 18
  }).addTo(map);

  // Legenda
  const legend = L.control({ position: 'bottomright' });
  legend.onAdd = function() {
    const div = L.DomUtil.create('div', 'map-legend');
    div.innerHTML = '<strong>Themes</strong><br>';
    Object.entries(GROUP_COLORS).forEach(([group, color]) => {
      div.innerHTML += `<span style="background:${color};display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:5px;"></span>${group}<br>`;
    });
    return div;
  };
  legend.addTo(map);

  let allMarkers = [];
  let festivals = [];

  fetch('/assets/data/festivals.json')
    .then(r => r.json())
    .then(data => {
      festivals = data;

      // Popola dropdown paesi
      const countries = [...new Set(data.map(f => f.country).filter(Boolean))].sort();
      const countrySelect = document.getElementById('filter-country');
      countries.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c; opt.textContent = c;
        countrySelect.appendChild(opt);
      });

      // Popola dropdown temi (gruppi macro)
      const themeSelect = document.getElementById('filter-theme');
      Object.keys(GROUP_COLORS).forEach(group => {
        const opt = document.createElement('option');
        opt.value = group; opt.textContent = group;
        themeSelect.appendChild(opt);
      });

      // Crea marker
      data.forEach(f => {
        const lat = parseFloat(f.lat);
        const lon = parseFloat(f.lon);
        if (isNaN(lat) || isNaN(lon)) return;

        const tags = f.theme ? f.theme.split(';').map(t => t.trim().toLowerCase()).filter(Boolean) : [];
        const color = getColor(tags);
        const group = getGroup(tags);

        const popup = `
          <div style="max-width:280px; font-family: inherit;">
            <strong style="font-size:1rem;">${f.name}</strong><br><br>
            <span>📍 ${f.location}</span><br>
            <span>🗓️ ${f.period}</span><br>
            <span>👥 ${formatList(f.public)}</span><br>
            <span>🌍 ${f.country}</span><br><br>
            ${formatTags(f.theme)}
            ${f.website ? `<br><br><a href="${f.website}" target="_blank" style="color:#2196F3;">🔗 Visit website</a>` : ''}
          </div>
        `;

        const marker = makeCircleMarker(lat, lon, color);
        marker.bindPopup(popup);
        marker.festivalData = { tags, group, public: f.public || '' };
        allMarkers.push(marker);
        marker.addTo(map);
      });

      updateCount();

      // Event listeners filtri
      ['filter-theme', 'filter-public', 'filter-country'].forEach(id => {
        document.getElementById(id).addEventListener('change', applyFilters);
      });
    });

  function applyFilters() {
    const theme = document.getElementById('filter-theme').value;
    const pub = document.getElementById('filter-public').value;
    const country = document.getElementById('filter-country').value;

    allMarkers.forEach((marker, i) => {
      const f = festivals[i];
      const d = marker.festivalData;
      const matchTheme = !theme || d.group === theme;
      const matchPublic = !pub || d.public.toLowerCase().includes(pub.toLowerCase());
      const matchCountry = !country || (f.country && f.country === country);

      if (matchTheme && matchPublic && matchCountry) marker.addTo(map);
      else map.removeLayer(marker);
    });

    updateCount();
  }

  function updateCount() {
    const visible = allMarkers.filter(m => map.hasLayer(m)).length;
    document.getElementById('festival-count').textContent = `${visible} festival`;
  }
</script>

<style>
  .map-legend {
    background: white;
    padding: 0.6rem 0.9rem;
    border-radius: 8px;
    font-size: 0.8rem;
    line-height: 1.8;
    box-shadow: 0 1px 5px rgba(0,0,0,0.2);
  }
  .tag {
    display: inline-block;
    background: #f0f0f0;
    border-radius: 10px;
    padding: 0.1rem 0.5rem;
    font-size: 0.75rem;
    margin: 0.15rem 0.1rem;
  }
  #filter-theme, #filter-public, #filter-country {
    background: white;
    transition: border-color 0.2s;
  }
  #filter-theme:focus, #filter-public:focus, #filter-country:focus {
    outline: none;
    border-color: #333;
  }
</style>