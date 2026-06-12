---
layout: page
title: Map
permalink: /map/
description: Interactive map of science festivals in Italy and Europe.
nav: true
nav_order: 2
---

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.css" />
<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.js"></script>

<div id="festival-filters" style="margin-bottom: 1rem; display: flex; flex-wrap: wrap; gap: 0.5rem;"></div>

<div id="map" style="height: 580px; width: 100%; border-radius: 8px;"></div>

<script>
  // Inizializza la mappa centrata sull'Italia
  const map = L.map('map').setView([44.5, 11.5], 5);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 18
  }).addTo(map);

  let allMarkers = [];
  let activeFilters = new Set();

  fetch('/assets/data/festivals.json')
    .then(r => r.json())
    .then(festivals => {
      // Raccoglie tutti i tag unici
      const allTags = new Set();
      festivals.forEach(f => {
        if (f.theme) f.theme.split(';').forEach(t => allTags.add(t.trim()));
      });

      // Crea i pulsanti filtro
      const filterDiv = document.getElementById('festival-filters');
      
      const allBtn = document.createElement('button');
      allBtn.textContent = 'All';
      allBtn.className = 'filter-btn active';
      allBtn.onclick = () => {
        activeFilters.clear();
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        allBtn.classList.add('active');
        updateMarkers();
      };
      filterDiv.appendChild(allBtn);

      [...allTags].sort().forEach(tag => {
        const btn = document.createElement('button');
        btn.textContent = tag;
        btn.className = 'filter-btn';
        btn.onclick = () => {
          if (activeFilters.has(tag)) {
            activeFilters.delete(tag);
            btn.classList.remove('active');
          } else {
            activeFilters.add(tag);
            btn.classList.add('active');
            allBtn.classList.remove('active');
          }
          if (activeFilters.size === 0) allBtn.classList.add('active');
          updateMarkers();
        };
        filterDiv.appendChild(btn);
      });

      // Crea i marker
      festivals.forEach(f => {
        const lat = parseFloat(f.lat);
        const lon = parseFloat(f.lon);
        if (isNaN(lat) || isNaN(lon)) return;

        const tags = f.theme ? f.theme.split(';').map(t => t.trim()) : [];
        
        const popup = `
          <div style="max-width: 260px;">
            <strong style="font-size: 1rem;">${f.name}</strong><br>
            <span style="color: #666;">📍 ${f.location}</span><br>
            <span style="color: #666;">🗓️ ${f.period}</span><br>
            <span style="color: #666;">👥 ${f.public}</span><br>
            ${tags.map(t => `<span class="tag">${t}</span>`).join(' ')}
            ${f.website ? `<br><a href="${f.website}" target="_blank" style="color: #2196F3;">🔗 Website</a>` : ''}
          </div>
        `;

        const marker = L.marker([lat, lon]).bindPopup(popup);
        marker.festivalTags = tags;
        allMarkers.push(marker);
        marker.addTo(map);
      });
    });

  function updateMarkers() {
    allMarkers.forEach(marker => {
      if (activeFilters.size === 0) {
        marker.addTo(map);
      } else {
        const hasTag = marker.festivalTags.some(t => activeFilters.has(t));
        if (hasTag) marker.addTo(map);
        else map.removeLayer(marker);
      }
    });
  }
</script>

<style>
  .filter-btn {
    padding: 0.3rem 0.8rem;
    border: 1px solid #ccc;
    border-radius: 20px;
    background: white;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.2s;
  }
  .filter-btn:hover { background: #f0f0f0; }
  .filter-btn.active { background: #333; color: white; border-color: #333; }
  .tag {
    display: inline-block;
    background: #f0f0f0;
    border-radius: 10px;
    padding: 0.1rem 0.5rem;
    font-size: 0.75rem;
    margin: 0.2rem 0.1rem;
  }
</style>