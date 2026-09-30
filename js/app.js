/* ==========================================================================
   Beki River Catchment StoryMap & Dashboard - Application Logic
   ========================================================================== */

document.addEventListener('DOMContentLoaded', async () => {
  console.log("Initializing Beki River StoryMap Application...");

  // Application State
  let storyData = null;
  let map = null;
  let markers = {};
  let riverPathLayer = null;
  let floodOverlaysLayer = null;
  let politicalMapLayer = null;
  let currentActiveId = null;

  // Basemap Tile Layers (Open data tiles)
  const basemaps = {
    topo: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
      maxZoom: 17,
      attribution: '&copy; <a href="https://opentopomap.org">OpenTopoMap</a> (&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>)'
    }),
    esri: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 18,
      attribution: '&copy; Esri World Imagery'
    }),
    osm: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    })
  };

  let activeBasemapKey = 'topo';

  // 1. Fetch Data Files
  try {
    const storyRes = await fetch('data/story_data.json');
    storyData = await storyRes.json();

    const riverRes = await fetch('data/beki_river_path.geojson');
    const riverGeojson = await riverRes.json();

    const floodRes = await fetch('data/flood_overlays.geojson');
    const floodGeojson = await floodRes.json();

    // 2. Initialize Leaflet Map
    map = L.map('map', {
      center: [26.75, 91.0],
      zoom: 9,
      layers: [basemaps[activeBasemapKey]],
      zoomControl: false
    });

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // 3. Render Story Cards and Map Markers
    renderStoryCards(storyData.pois);
    renderMapMarkers(storyData.pois);

    // Add River Path GeoJSON
    riverPathLayer = L.geoJSON(riverGeojson, {
      style: {
        color: '#00b4d8',
        weight: 4,
        opacity: 0.8,
        dashArray: '6, 6'
      }
    });

    // Add Flood Overlays GeoJSON
    floodOverlaysLayer = L.geoJSON(floodGeojson, {
      style: (feature) => ({
        color: feature.properties.fillColor || '#e63946',
        fillColor: feature.properties.fillColor || '#e63946',
        fillOpacity: 0.35,
        weight: 2
      }),
      onEachFeature: (feature, layer) => {
        layer.bindPopup(`
          <div style="color: #0f172a; font-family: sans-serif;">
            <h4 style="margin:0 0 4px 0; color: #0f4c81;">Year ${feature.properties.year} Flood Extent</h4>
            <p style="margin:0; font-size:12px;"><strong>Event:</strong> ${feature.properties.event}</p>
            <p style="margin:0; font-size:12px;"><strong>Severity:</strong> ${feature.properties.severity}</p>
          </div>
        `);
      }
    });

    // Initialize Political Map GeoTIFF Layer Overlay (Off by default)
    const politicalMapBounds = [[25.942706, 89.866644], [28.889546, 92.661001]];
    politicalMapLayer = L.imageOverlay('assets/layers/political_map.jpg', politicalMapBounds, {
      opacity: 0.75,
      interactive: false
    });

    // Populate POI Dropdown Select
    populatePoiDropdown(storyData.pois);

    // 4. Setup Intersection Observer for Scrollytelling
    setupScrollObserver();

    // 5. Setup UI Event Listeners
    setupUIEventListeners(floodGeojson);

  } catch (error) {
    console.error("Error loading StoryMap data:", error);
  }

  // --- Helper Functions ---

  function renderStoryCards(pois) {
    const container = document.getElementById('story-cards-container');
    container.innerHTML = '';

    pois.forEach((poi, index) => {
      const card = document.createElement('article');
      card.className = 'story-card';
      card.id = `story-card-${poi.id}`;
      card.setAttribute('data-poi-id', poi.id);

      card.innerHTML = `
        <div class="card-step-badge">
          <span>Point ${poi.id} of ${pois.length}</span>
        </div>
        <h3 class="card-title">${poi.title}</h3>
        <div class="card-subtitle">${poi.subtitle}</div>
        <div class="card-coords-pill">
          <span>📍</span>
          <span>${poi.lat_str} | ${poi.lon_str}</span>
        </div>
        <div class="card-media-wrapper">
          <div class="media-placeholder-icon">📷</div>
          <div class="media-placeholder-text">Field Media Slot: ${poi.media.alt}</div>
          <div class="media-caption">${poi.media.caption}</div>
        </div>
        <div class="card-narrative">${poi.text}</div>
      `;

      container.appendChild(card);
    });
  }

  function renderMapMarkers(pois) {
    pois.forEach(poi => {
      const customIcon = L.divIcon({
        className: 'custom-leaflet-marker',
        html: `<div class="marker-pin" id="marker-pin-${poi.id}"><span>${poi.id}</span></div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18]
      });

      const marker = L.marker([poi.lat, poi.lon], { icon: customIcon }).addTo(map);

      marker.bindPopup(`
        <div style="font-family: sans-serif; min-width: 180px;">
          <h4 style="margin: 0 0 4px 0; color: #0f4c81;">#${poi.id} ${poi.title}</h4>
          <p style="margin: 0 0 6px 0; font-size: 11px; color: #64748b;">${poi.subtitle}</p>
          <button style="background:#00b4d8; color:#fff; border:none; padding:4px 8px; border-radius:4px; font-size:11px; cursor:pointer;" onclick="document.getElementById('story-card-${poi.id}').scrollIntoView({behavior:'smooth'})">
            Jump to Narrative ↓
          </button>
        </div>
      `);

      marker.on('click', () => {
        const targetCard = document.getElementById(`story-card-${poi.id}`);
        if (targetCard) {
          targetCard.scrollIntoView({ behavior: 'smooth' });
        }
      });

      markers[poi.id] = marker;
    });
  }

  function populatePoiDropdown(pois) {
    const select = document.getElementById('poi-select');
    select.innerHTML = '<option value="">-- Jump to Location --</option>';
    pois.forEach(poi => {
      const option = document.createElement('option');
      option.value = poi.id;
      option.textContent = `${poi.id}. ${poi.title}`;
      select.appendChild(option);
    });
  }

  function setupScrollObserver() {
    const cards = document.querySelectorAll('.story-card');

    const observerOptions = {
      root: document.getElementById('narrative-panel'),
      rootMargin: '-20% 0px -40% 0px',
      threshold: 0.2
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const poiId = parseInt(entry.target.getAttribute('data-poi-id'));
          activatePOI(poiId);
        }
      });
    }, observerOptions);

    cards.forEach(card => observer.observe(card));
  }

  function activatePOI(id) {
    if (currentActiveId === id) return;
    currentActiveId = id;

    // 1. Highlight active card
    document.querySelectorAll('.story-card').forEach(c => c.classList.remove('active'));
    const activeCard = document.getElementById(`story-card-${id}`);
    if (activeCard) activeCard.classList.add('active');

    // 2. Update select dropdown
    const select = document.getElementById('poi-select');
    if (select) select.value = id;

    // 3. Highlight marker pin
    document.querySelectorAll('.marker-pin').forEach(p => p.classList.remove('active'));
    const activePin = document.getElementById(`marker-pin-${id}`);
    if (activePin) activePin.classList.add('active');

    // 4. Fly map to POI coordinates
    const poi = storyData.pois.find(p => p.id === id);
    if (poi && map) {
      map.flyTo([poi.lat, poi.lon], 12, {
        animate: true,
        duration: 1.2
      });
    }
  }

  function setupUIEventListeners(floodGeojson) {
    // POI Dropdown Jump
    const select = document.getElementById('poi-select');
    select.addEventListener('change', (e) => {
      const val = parseInt(e.target.value);
      if (val) {
        const card = document.getElementById(`story-card-${val}`);
        if (card) card.scrollIntoView({ behavior: 'smooth' });
      }
    });

    // Basemap Switcher Buttons
    const basemapBtns = document.querySelectorAll('[data-basemap]');
    basemapBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const targetBasemap = e.currentTarget.getAttribute('data-basemap');
        if (basemaps[targetBasemap] && targetBasemap !== activeBasemapKey) {
          map.removeLayer(basemaps[activeBasemapKey]);
          basemaps[targetBasemap].addTo(map);
          activeBasemapKey = targetBasemap;

          basemapBtns.forEach(b => b.classList.remove('active'));
          e.currentTarget.classList.add('active');
        }
      });
    });

    // Dashboard Drawer Toggle Button
    const dashboardToggleBtn = document.getElementById('toggle-dashboard-btn');
    const dashboardDrawer = document.getElementById('dashboard-drawer');

    dashboardToggleBtn.addEventListener('click', () => {
      dashboardDrawer.classList.toggle('hidden');
      dashboardToggleBtn.classList.toggle('active');
    });

    // Layer Checkboxes
    const riverToggle = document.getElementById('chk-river-path');
    riverToggle.addEventListener('change', (e) => {
      if (e.target.checked) {
        riverPathLayer.addTo(map);
      } else {
        map.removeLayer(riverPathLayer);
      }
    });

    const floodToggle = document.getElementById('chk-flood-overlays');
    floodToggle.addEventListener('change', (e) => {
      if (e.target.checked) {
        floodOverlaysLayer.addTo(map);
      } else {
        map.removeLayer(floodOverlaysLayer);
      }
    });

    const politicalToggle = document.getElementById('chk-political-map');
    if (politicalToggle) {
      politicalToggle.addEventListener('change', (e) => {
        if (e.target.checked) {
          politicalMapLayer.addTo(map);
        } else {
          map.removeLayer(politicalMapLayer);
        }
      });
    }

    // Timeline Slider
    const timelineSlider = document.getElementById('timeline-slider');
    const timelineYearDisplay = document.getElementById('timeline-year-display');

    timelineSlider.addEventListener('input', (e) => {
      const selectedYear = e.target.value;
      timelineYearDisplay.textContent = selectedYear === '0' ? 'All Years' : selectedYear;

      if (floodOverlaysLayer) {
        map.removeLayer(floodOverlaysLayer);

        const filteredFeatures = selectedYear === '0'
          ? floodGeojson.features
          : floodGeojson.features.filter(f => f.properties.year.toString() === selectedYear);

        floodOverlaysLayer = L.geoJSON({ type: 'FeatureCollection', features: filteredFeatures }, {
          style: (feature) => ({
            color: feature.properties.fillColor || '#e63946',
            fillColor: feature.properties.fillColor || '#e63946',
            fillOpacity: 0.4,
            weight: 2
          }),
          onEachFeature: (feature, layer) => {
            layer.bindPopup(`
              <div style="color: #0f172a; font-family: sans-serif;">
                <h4 style="margin:0 0 4px 0; color: #0f4c81;">Year ${feature.properties.year} Flood Extent</h4>
                <p style="margin:0; font-size:12px;"><strong>Event:</strong> ${feature.properties.event}</p>
              </div>
            `);
          }
        }).addTo(map);
      }
    });
  }
});
