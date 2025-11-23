// API endpoint - automatically uses current domain
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/plan-trip'
    : `${window.location.protocol}//${window.location.host}/plan-trip`;

// DOM elements
const tripForm = document.getElementById('tripForm');
const placeInput = document.getElementById('placeInput');
const searchBtn = document.getElementById('searchBtn');
const btnText = document.querySelector('.btn-text');
const loader = document.querySelector('.loader');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('resultsSection');
const placeName = document.getElementById('placeName');
const temperature = document.getElementById('temperature');
const precipitation = document.getElementById('precipitation');
const attractionsList = document.getElementById('attractionsList');
const fullMessage = document.getElementById('fullMessage');

// Map variables
let map = null;
let markers = [];
let mainMarker = null;

// Initialize map
function initMap(lat, lon, placeName) {
    // If map exists, remove it
    if (map) {
        map.remove();
        markers = [];
        mainMarker = null;
    }
    
    // Create new map
    map = L.map('map').setView([lat, lon], 13);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Add main location marker
    mainMarker = L.marker([lat, lon], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map);
    
    mainMarker.bindPopup(`<div class="map-popup-title">${placeName}</div><div class="map-popup-type">Main Location</div>`);
}

// Add attraction markers to map
function addAttractionMarkers(attractions) {
    // Clear existing attraction markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    if (!attractions || attractions.length === 0) return;
    
    const bounds = [];
    if (mainMarker) {
        bounds.push(mainMarker.getLatLng());
    }
    
    attractions.forEach((attraction, index) => {
        const marker = L.marker([attraction.latitude, attraction.longitude], {
            icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            })
        }).addTo(map);
        
        marker.bindPopup(`<div class="map-popup-title">${attraction.name}</div><div class="map-popup-type">Tourist Attraction #${index + 1}</div>`);
        markers.push(marker);
        bounds.push(marker.getLatLng());
        
        // Store reference for click handling
        marker.attractionIndex = index;
    });
    
    // Fit map to show all markers
    if (bounds.length > 1) {
        map.fitBounds(bounds, { padding: [50, 50] });
    }
}

// Focus map on specific attraction
function focusMapOnAttraction(index) {
    if (markers[index]) {
        map.setView(markers[index].getLatLng(), 15, {
            animate: true,
            duration: 1
        });
        markers[index].openPopup();
    }
}

// Form submission handler
tripForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const query = placeInput.value.trim();
    
    if (!query) {
        showError('Please enter a place name or trip query');
        return;
    }
    
    await planTrip(query);
});

// Main function to plan trip
async function planTrip(query) {
    // Show loading state
    setLoading(true);
    hideError();
    hideResults();
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            showError(data.error || 'Failed to fetch trip information');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to connect to the server. Please make sure the backend is running.');
    } finally {
        setLoading(false);
    }
}

// Display results
function displayResults(data) {
    // Set place name
    placeName.textContent = data.place;
    
    // Initialize map if coordinates available
    if (data.latitude && data.longitude) {
        initMap(data.latitude, data.longitude, data.place);
        
        // Add attraction markers if available
        if (data.attractions_with_coords && data.attractions_with_coords.length > 0) {
            addAttractionMarkers(data.attractions_with_coords);
        }
    }
    
    // Set weather information
    if (data.has_weather && data.temperature !== null) {
        temperature.textContent = data.temperature.toFixed(1);
        precipitation.textContent = data.precipitation_chance || 0;
    } else {
        temperature.textContent = '--';
        precipitation.textContent = '--';
    }
    
    // Set attractions with click handlers
    attractionsList.innerHTML = '';
    if (data.has_places && data.attractions && data.attractions.length > 0) {
        data.attractions.forEach((attraction, index) => {
            const li = document.createElement('li');
            li.textContent = attraction;
            li.style.cursor = 'pointer';
            
            // Add click handler to focus map on this attraction
            if (data.attractions_with_coords && data.attractions_with_coords[index]) {
                li.addEventListener('click', () => {
                    focusMapOnAttraction(index);
                    // Highlight selected attraction
                    document.querySelectorAll('.attractions-list li').forEach(item => {
                        item.style.backgroundColor = '';
                        item.style.transform = '';
                    });
                    li.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
                    li.style.transform = 'translateX(5px)';
                });
                
                // Add hover effect
                li.addEventListener('mouseenter', () => {
                    li.style.backgroundColor = 'rgba(102, 126, 234, 0.05)';
                });
                li.addEventListener('mouseleave', () => {
                    if (!li.style.transform) {
                        li.style.backgroundColor = '';
                    }
                });
            }
            
            attractionsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No attractions found';
        li.style.color = '#999';
        attractionsList.appendChild(li);
    }
    
    // Set full message
    fullMessage.textContent = data.response;
    
    // Show results
    showResults();
    
    // Fix map size after showing results (Leaflet needs this)
    setTimeout(() => {
        if (map) {
            map.invalidateSize();
        }
    }, 100);
}

// UI helper functions
function setLoading(isLoading) {
    searchBtn.disabled = isLoading;
    if (isLoading) {
        btnText.style.display = 'none';
        loader.style.display = 'inline-block';
    } else {
        btnText.style.display = 'inline';
        loader.style.display = 'none';
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function showResults() {
    resultsSection.style.display = 'block';
}

function hideResults() {
    resultsSection.style.display = 'none';
}

// Auto-capitalize first letter of input
placeInput.addEventListener('input', (e) => {
    const value = e.target.value;
    if (value.length === 1) {
        e.target.value = value.charAt(0).toUpperCase();
    }
});

// Example queries for placeholder cycling
const exampleQueries = [
    'Bangalore',
    'Plan trip to Manali',
    'I want to visit Paris',
    'Going to Tokyo, help me plan',
    'London'
];

// Add placeholder cycling
let placeholderIndex = 0;
setInterval(() => {
    if (document.activeElement !== placeInput) {
        placeholderIndex = (placeholderIndex + 1) % exampleQueries.length;
        placeInput.placeholder = `e.g., ${exampleQueries[placeholderIndex]}`;
    }
}, 3000);
