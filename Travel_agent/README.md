# 🌍 Tourism AI Agent

An intelligent multi-agent tourism planning system built with **LangChain** and **FastAPI** that helps users discover destinations with real-time weather data, tourist attractions, and interactive maps.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.3.7-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.4-teal)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🗣️ **Natural Language Input** - Ask naturally: "Plan a trip to Manali" or just "Paris"
- 🌤️ **Real-time Weather** - Current temperature and precipitation forecast
- 🏛️ **Tourist Attractions** - Top 5 places to visit with coordinates
- 🗺️ **Interactive Maps** - Leaflet.js maps with clickable markers
- 🎯 **Click-to-Focus** - Click attractions to zoom on map
- 🚀 **Fast Response** - Direct API calls, minimal LLM overhead
- 💰 **100% Free** - All APIs are open-source and cost-free

## 🏗️ Architecture

### System Flow
```
┌─────────────┐
│  User Input │
│ "Trip to X" │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   FastAPI Server    │
│  /plan-trip endpoint│
└──────┬──────────────┘
       │
       ▼
┌─────────────────────────────┐
│   LangChain Agent System    │
│  ┌─────────────────────┐    │
│  │ Place Extraction    │    │
│  │ (Regex Patterns)    │    │
│  └──────┬──────────────┘    │
│         │                    │
│         ▼                    │
│  ┌─────────────────────┐    │
│  │  Tool Orchestration │    │
│  │                     │    │
│  │  ┌──────────────┐   │    │
│  │  │ Geocoding    │───┼────┼──► Nominatim API
│  │  │ Tool         │   │    │    (Place → Coords)
│  │  └──────────────┘   │    │
│  │                     │    │
│  │  ┌──────────────┐   │    │
│  │  │ Weather      │───┼────┼──► Open-Meteo API
│  │  │ Tool         │   │    │    (Coords → Weather)
│  │  └──────────────┘   │    │
│  │                     │    │
│  │  ┌──────────────┐   │    │
│  │  │ Places       │───┼────┼──► Overpass API
│  │  │ Tool         │   │    │    (Coords → POIs)
│  │  └──────────────┘   │    │
│  │                     │    │
│  └──────┬──────────────┘    │
│         │                    │
│         ▼                    │
│  ┌─────────────────────┐    │
│  │ Response Builder    │    │
│  │ (Pydantic Schema)   │    │
│  └──────┬──────────────┘    │
└─────────┼──────────────────┘
          │
          ▼
┌─────────────────────┐
│   JSON Response     │
│  {place, coords,    │
│   weather, pois}    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Frontend          │
│  ┌───────────────┐  │
│  │ Leaflet Map   │  │
│  │ + Markers     │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ Weather Card  │  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ Attractions   │  │
│  │ List          │  │
│  └───────────────┘  │
└─────────────────────┘
```

## 🔧 Technology Stack

### Backend
| Component | Purpose | Version |
|-----------|---------|---------|
| **LangChain** | Agent framework & tool orchestration | 0.3.7 |
| **FastAPI** | REST API server | 0.115.4 |
| **Pydantic** | Data validation & schemas | 2.9.2 |
| **Mistral API** | LLM provider (via Qubrid) | - |
| **Python** | Runtime | 3.10 |

### Frontend
| Component | Purpose |
|-----------|---------|
| **Leaflet.js** | Interactive mapping |
| **OpenStreetMap** | Map tiles |
| **Vanilla JavaScript** | UI logic |

### External APIs (Free)
| API | Purpose | Rate Limit |
|-----|---------|------------|
| **Nominatim** | Geocoding (place → coords) | 1/sec |
| **Open-Meteo** | Weather data | Unlimited |
| **Overpass** | Tourist POIs | Fair use |

## 🧠 LangChain Integration

### Agent Architecture

The system uses **LangChain's tool-calling pattern** with custom tools:

```python
from langchain.tools import tool

@tool
def get_coordinates(place_name: str) -> Dict:
    """Convert place name to latitude/longitude coordinates."""
    # Calls Nominatim API
    return {"latitude": lat, "longitude": lon, "success": True}

@tool
def get_weather(place_name: str) -> str:
    """Get current weather for a location."""
    # Internally calls get_coordinates
    # Then calls Open-Meteo API
    return "In Paris it's currently 15.2°C with 20% chance of rain"

@tool
def get_tourist_places(place_name: str) -> str:
    """Find top 5 tourist attractions."""
    # Internally calls get_coordinates
    # Then queries Overpass API
    return "Place1\nPlace2\nCOORDS:\nPlace1|lat|lon\nPlace2|lat|lon"
```

### Tool Orchestration Flow

1. **Tool Registration**
   ```python
   tools = [get_coordinates, get_weather, get_tourist_places]
   ```

2. **Tool Invocation**
   ```python
   weather_result = get_weather.invoke({"place_name": "Paris"})
   places_result = get_tourist_places.invoke({"place_name": "Paris"})
   ```

3. **Response Parsing**
   - Regex extracts temperature, precipitation from weather string
   - Split attractions text by "COORDS:" marker
   - Parse coordinates: `"Place|lat|lon"` format

4. **Structured Output**
   ```python
   class TourismResponse(BaseModel):
       place: str
       latitude: float
       longitude: float
       temperature: Optional[float]
       precipitation_chance: Optional[int]
       attractions: List[str]
       attractions_with_coords: List[AttractionWithCoords]
   ```

### Why This Architecture?

**Direct Tool Calling vs LLM Reasoning:**
- ✅ **Faster**: No LLM inference for simple lookups
- ✅ **Cheaper**: Zero token usage for API calls
- ✅ **Reliable**: Structured APIs > LLM parsing
- ✅ **Scalable**: No LLM rate limits

The agent uses **deterministic tool execution** rather than letting the LLM decide which tools to call. This ensures consistent, fast responses.

## 📦 Installation

### Prerequisites
- Python 3.10+
- pip or uv package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ujwal-s-r/LangChain.git
   cd LangChain/Travel_agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Create .env file
   echo "mistral_api_key=your_api_key_here" > .env
   ```
   
   Get your Mistral API key from [Qubrid Platform](https://platform.qubrid.com/)

5. **Run the server**
   ```bash
   python main.py
   ```
   
   Server starts at: `http://localhost:8000`

6. **Open in browser**
   ```
   http://localhost:8000
   ```

## 🚀 Usage

### Web Interface

1. Open `http://localhost:8000` in your browser
2. Enter a query:
   - Simple: `"Manali"`
   - Natural: `"Plan a trip to Paris"`
   - Conversational: `"I want to visit Tokyo"`
3. View results:
   - 🗺️ Interactive map with markers
   - 🌤️ Current weather data
   - 🏛️ Top 5 tourist attractions
4. Click attractions to zoom map

### API Usage

**Endpoint:** `POST /plan-trip`

**Request:**
```bash
curl -X POST "http://localhost:8000/plan-trip" \
  -H "Content-Type: application/json" \
  -d '{"query": "Manali"}'
```

**Response:**
```json
{
  "place": "Manali",
  "latitude": 32.2454608,
  "longitude": 77.1872926,
  "temperature": 3.2,
  "precipitation_chance": 0,
  "attractions": [
    "PWD Guest house Kothi",
    "Village House",
    "Sarthak Resorts",
    "Riyali Thach Shepherd Hut",
    "Riyali Thach"
  ],
  "attractions_with_coords": [
    {
      "name": "PWD Guest house Kothi",
      "latitude": 32.2234567,
      "longitude": 77.1876543
    }
  ],
  "success": true,
  "response": "In Manali it's currently 3.2°C with 0% chance of rain..."
}
```

### Python Client

```python
from tourism_agent import create_tourism_agent_with_tools

# Create agent
agent = create_tourism_agent_with_tools()

# Plan trip
result = agent.run("Manali")

print(f"Place: {result.place}")
print(f"Temperature: {result.temperature}°C")
print(f"Attractions: {len(result.attractions)}")
print(f"Coordinates: {result.latitude}, {result.longitude}")
```

## 🔍 How It Works

### 1. Natural Language Processing

**Input:** "Plan a trip to Manali"

**Extraction Patterns:**
```python
patterns = [
    r"trip to ([A-Z][a-zA-Z\s]+?)",      # "trip to Manali"
    r"visit(ing)? ([A-Z][a-zA-Z\s]+?)",  # "visiting Paris"
    r"go(ing)? to ([A-Z][a-zA-Z\s]+?)",  # "going to Tokyo"
]
```

**Output:** `"Manali"`

### 2. Geocoding (Nominatim)

**Request:**
```
GET https://nominatim.openstreetmap.org/search?q=Manali&format=json
```

**Response:**
```json
{
  "lat": "32.2454608",
  "lon": "77.1872926",
  "display_name": "Manali, Himachal Pradesh, India"
}
```

### 3. Weather Fetching (Open-Meteo)

**Request:**
```
GET https://api.open-meteo.com/v1/forecast
    ?latitude=32.2454608
    &longitude=77.1872926
    &current_weather=true
```

**Response:**
```json
{
  "current_weather": {
    "temperature": 3.2,
    "weathercode": 0
  },
  "hourly": {
    "precipitation_probability": [0, 0, 5, ...]
  }
}
```

### 4. Tourist Places (Overpass API)

**Overpass QL Query:**
```javascript
[out:json][timeout:25];
(
  node["tourism"](around:10000,32.2454608,77.1872926);
  way["tourism"](around:10000,32.2454608,77.1872926);
  node["leisure"="park"](around:10000,32.2454608,77.1872926);
  node["historic"](around:10000,32.2454608,77.1872926);
);
out body center;
```

**Response:**
```json
{
  "elements": [
    {
      "type": "node",
      "id": 123456789,
      "lat": 32.2234567,
      "lon": 77.1876543,
      "tags": {
        "name": "PWD Guest house Kothi",
        "tourism": "attraction"
      }
    }
  ]
}
```

### 5. Response Assembly

**LangChain Agent:**
```python
# Execute tools
weather = get_weather.invoke({"place_name": "Manali"})
places = get_tourist_places.invoke({"place_name": "Manali"})

# Parse results
temp = extract_temperature(weather)      # 3.2
precip = extract_precipitation(weather)  # 0

# Build response
response = TourismResponse(
    place="Manali",
    latitude=32.2454608,
    longitude=77.1872926,
    temperature=temp,
    precipitation_chance=precip,
    attractions=["Place1", "Place2", ...],
    attractions_with_coords=[...]
)
```

### 6. Map Rendering

**Leaflet.js:**
```javascript
// Initialize map
map = L.map('map').setView([32.2454608, 77.1872926], 13);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Add main marker (red)
L.marker([32.2454608, 77.1872926], {icon: redIcon}).addTo(map);

// Add attraction markers (blue)
data.attractions_with_coords.forEach((attraction, i) => {
    L.marker([attraction.latitude, attraction.longitude], {icon: blueIcon})
        .bindPopup(attraction.name)
        .addTo(map);
});

// Fit bounds to show all markers
map.fitBounds(bounds, {padding: [50, 50]});
```

## 🎯 Project Structure

```
Travel_agent/
├── tools/
│   ├── __init__.py
│   ├── geocoding_tool.py      # Nominatim API wrapper
│   ├── weather_tool.py         # Open-Meteo API wrapper
│   └── places_tool.py          # Overpass API wrapper
├── agents/
│   ├── parent_agent.py         # (Legacy, not used)
│   ├── weather_agent.py        # (Legacy, not used)
│   └── places_agent.py         # (Legacy, not used)
├── static/
│   ├── style.css               # UI styling
│   └── script.js               # Frontend logic + Leaflet
├── templates/
│   └── index.html              # Main UI
├── schemas.py                  # Pydantic models
├── tourism_agent.py            # LangChain agent + tools
├── main.py                     # FastAPI server
├── requirements.txt            # Dependencies
├── .env                        # API keys
├── test_tools.py               # Tool tests
├── test_api.py                 # API tests
├── test_tourism_agent.py       # Agent tests
├── ARCHITECTURE.md             # Detailed architecture
└── README.md                   # This file
```

## 🧪 Testing

### Test Individual Tools
```bash
python test_tools.py
```

### Test API Connection
```bash
python test_api.py
```

### Test Complete Agent
```bash
python test_tourism_agent.py
```

### Test API Endpoint
```bash
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/plan-trip" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query": "Manali"}' | ConvertTo-Json -Depth 10

# Bash
curl -X POST "http://localhost:8000/plan-trip" \
  -H "Content-Type: application/json" \
  -d '{"query": "Manali"}'
```

## 📊 API Endpoints

### `POST /plan-trip`
Plan a trip to a destination

**Request Body:**
```json
{
  "query": "string"  // Place name or natural language
}
```

**Response:**
```json
{
  "place": "string",
  "latitude": number,
  "longitude": number,
  "temperature": number,
  "precipitation_chance": number,
  "attractions": ["string"],
  "attractions_with_coords": [
    {
      "name": "string",
      "latitude": number,
      "longitude": number
    }
  ],
  "success": boolean,
  "response": "string",
  "error": "string | null"
}
```

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy"
}
```

### `GET /api/info`
API information

**Response:**
```json
{
  "name": "Tourism AI Agent API",
  "version": "1.0.0",
  "endpoints": [...]
}
```

## 🛠️ Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Mistral API (Required)
mistral_api_key=your_qubrid_api_key

# Optional: Server Configuration
HOST=0.0.0.0
PORT=8000

# Optional: API Rate Limits
NOMINATIM_DELAY=1.0  # seconds between requests
```

### API Keys

**Mistral API (Qubrid):**
1. Sign up at [platform.qubrid.com](https://platform.qubrid.com/)
2. Generate API key
3. Add to `.env` file

**No other keys needed** - All other APIs are completely free!

## 🚦 Rate Limits & Best Practices

### Nominatim (Geocoding)
- **Limit:** 1 request per second
- **Solution:** 1-second delay implemented in tool
- **Policy:** [Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/)

### Open-Meteo (Weather)
- **Limit:** Unlimited for non-commercial use
- **No API key required**

### Overpass API (Places)
- **Limit:** Fair use policy
- **Timeout:** 25 seconds per query
- **Best Practice:** Cache results for repeated queries

## 🎨 Customization

### Add More POI Categories

Edit `tools/places_tool.py`:
```python
query = f"""
[out:json][timeout:25];
(
  node["tourism"](around:{radius},{lat},{lon});
  node["amenity"="restaurant"](around:{radius},{lat},{lon});  # Add restaurants
  node["amenity"="hotel"](around:{radius},{lat},{lon});       # Add hotels
);
out body center;
"""
```

### Change Map Style

Edit `static/script.js`:
```javascript
// Use different tile provider
L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: 'OpenTopoMap'
}).addTo(map);
```

### Modify Search Radius

Edit `tools/places_tool.py`:
```python
radius = 15000  # 15km instead of 10km
```

## 🐛 Troubleshooting

### Map Not Loading
**Problem:** Leaflet map shows blank white box

**Solution:**
1. Check browser console for errors
2. Verify coordinates in API response
3. Ensure Leaflet CSS is loaded
4. Check `map.invalidateSize()` is called

### No Attractions Found
**Problem:** Response shows empty attractions list

**Solution:**
1. Try different location (some places have limited OSM data)
2. Check Overpass API status
3. Increase search radius in `places_tool.py`

### Weather Data Missing
**Problem:** Temperature shows "--"

**Solution:**
1. Verify coordinates are valid
2. Check Open-Meteo API status
3. Ensure temperature extraction regex is correct

### API Connection Failed
**Problem:** Frontend shows "Failed to connect to server"

**Solution:**
1. Verify server is running: `python main.py`
2. Check URL matches: `http://localhost:8000`
3. Verify CORS is enabled in `main.py`
4. Check firewall settings

## 📈 Performance

**Typical Response Times:**
- Geocoding: ~200-500ms
- Weather API: ~100-300ms
- Overpass API: ~1-3s (varies by location)
- **Total:** ~2-4 seconds

**Optimization Tips:**
- Implement caching for repeated queries
- Use parallel tool execution
- Add client-side caching
- Implement debouncing on search input

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain** - Agent framework
- **OpenStreetMap** - Map data
- **Nominatim** - Geocoding service
- **Open-Meteo** - Weather data
- **Leaflet.js** - Mapping library
- **FastAPI** - Web framework

## 📧 Contact

**Developer:** Ujwal S R  
**GitHub:** [@ujwal-s-r](https://github.com/ujwal-s-r)  
**Repository:** [LangChain/Travel_agent](https://github.com/ujwal-s-r/LangChain/tree/main/Travel_agent)

---

**Built with ❤️ using LangChain and Open Source APIs**
