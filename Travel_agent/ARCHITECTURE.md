# Tourism AI Agent - Architecture Overview

## System Overview
Multi-agent tourism planning system that accepts natural language queries, retrieves real-time weather data and tourist attractions, and displays results on an interactive map.

## Technology Stack

### Backend
- **FastAPI** - REST API server
- **LangChain 0.3.7** - Tool orchestration framework
- **Pydantic 2.9.2** - Data validation and structured schemas
- **Mistral API (Qubrid)** - LLM provider with SSE streaming
- **Python 3.10** - Core runtime

### Frontend
- **Leaflet.js** - Interactive mapping library
- **OpenStreetMap** - Free map tiles
- **Vanilla JavaScript** - No frameworks

### External APIs (Free & Open Source)
- **Nominatim (OpenStreetMap)** - Geocoding service
- **Open-Meteo** - Weather data API
- **Overpass API (OpenStreetMap)** - Tourist attractions database

## Data Flow

### Request Pipeline
```
User Input → Frontend → FastAPI Endpoint → Tourism Agent → Tools → External APIs → Response → Frontend → Map Rendering
```

### Processing Steps

1. **Query Reception**
   - User enters natural language query or place name
   - Frontend sends POST request: `{"query": "Trip to Manali"}`

2. **Place Name Extraction**
   - Regex pattern matching extracts place name from natural language
   - Handles formats: "trip to X", "visiting X", "in X", or just "X"
   - Fallback to capitalized word detection

3. **Geocoding**
   - Nominatim API converts place name to coordinates
   - Returns: latitude, longitude, formatted address
   - Establishes main location for map centering

4. **Weather Retrieval**
   - Uses coordinates from geocoding
   - Open-Meteo API provides current temperature and precipitation
   - Returns formatted string with weather data

5. **Tourist Attractions Discovery**
   - Overpass API queries OpenStreetMap database
   - Searches 10km radius for tourism POIs
   - Categories: attractions, parks, historic sites, museums
   - Returns up to 5 places with names AND coordinates

6. **Response Structuring**
   - Parses tool outputs with regex
   - Extracts temperature, precipitation percentage
   - Builds two lists:
     - Simple string array for display
     - Coordinate objects for map markers
   - Creates Pydantic model with all data

7. **Map Initialization**
   - Leaflet creates map at main location coordinates
   - Loads OpenStreetMap tiles asynchronously
   - Adds red marker for main location

8. **Attraction Markers**
   - Blue markers added for each attraction
   - Markers have popups with attraction details
   - Map bounds auto-fit to show all markers

9. **Interactive Features**
   - Click attraction in list → map pans to marker
   - Click marker → highlights corresponding list item
   - Hover effects provide visual feedback

## Tool Architecture

### Tool Pattern
Each tool uses LangChain `@tool` decorator for automatic integration:
- Docstring becomes tool description
- Type hints define parameters
- Returns structured data (dict or formatted string)

### Tool Invocation Chain
```
Tourism Agent
    ├── get_coordinates(place_name)
    │   └── Nominatim API
    │
    ├── get_weather(place_name)
    │   ├── get_coordinates() [internal call]
    │   └── Open-Meteo API
    │
    └── get_tourist_places(place_name)
        ├── get_coordinates() [internal call]
        └── Overpass API
```

### Tool Reusability
- Weather and places tools both call geocoding internally
- Avoids redundant coordinate lookups
- Each tool returns structured data for parsing

## Data Schema Design

### Nested Pydantic Models
```
AttractionWithCoords
├── name: str
├── latitude: float
└── longitude: float

TourismResponse
├── place: str
├── latitude: float [main location]
├── longitude: float [main location]
├── temperature: Optional[float]
├── precipitation_chance: Optional[int]
├── attractions: List[str] [for UI display]
├── attractions_with_coords: List[AttractionWithCoords] [for mapping]
├── message: str [natural language summary]
├── success: bool
└── error: Optional[str]
```

### Dual Attraction Lists
- **attractions**: Simple names for UI rendering
- **attractions_with_coords**: Rich objects for map markers
- Enables graceful degradation if coordinate parsing fails

## Map Implementation

### Leaflet Integration
- CDN-loaded library (no build step)
- Tile layer from OpenStreetMap (no API key)
- Custom marker icons (colored markers from GitHub)

### Marker Strategy
- **Red markers**: Main location (city center)
- **Blue markers**: Tourist attractions (numbered)
- **Popups**: HTML content with attraction name and type

### Map Lifecycle
- Created on first successful result
- Destroyed and recreated on new search
- Old markers removed before adding new ones
- `invalidateSize()` called after DOM changes

### Bounds Calculation
- Collects coordinates of main marker + all attraction markers
- `fitBounds()` automatically adjusts zoom and center
- 50px padding for visual comfort

## API Integration Details

### Nominatim (Geocoding)
- **Endpoint**: `https://nominatim.openstreetmap.org/search`
- **Input**: Place name string
- **Output**: JSON with lat/lon and formatted address
- **Rate Limit**: 1 request/second (handled by tool delay)

### Open-Meteo (Weather)
- **Endpoint**: `https://api.open-meteo.com/v1/forecast`
- **Input**: Latitude, longitude
- **Output**: Current temperature, precipitation probability
- **No API key**: Completely free

### Overpass API (Tourist Places)
- **Endpoint**: `https://overpass-api.de/api/interpreter`
- **Query Language**: Overpass QL
- **Search Radius**: 10km around coordinates
- **Filters**: `tourism=*`, `leisure=park`, `historic=*`
- **Output**: OSM elements with names and coordinates
- **Returns**: Up to 5 results with center points

## Mistral API (SSE Streaming)

### Streaming Response Handling
- Mistral via Qubrid always returns Server-Sent Events
- Custom LLM wrapper extends LangChain base class
- Parses SSE format: `data: {json}\ndata: [DONE]`
- Extracts content from nested JSON structure
- Concatenates all chunks into single response

### Why Custom Wrapper?
- LangChain doesn't natively support this SSE format
- Custom `_call()` method handles streaming parse
- Maintains compatibility with LangChain agent system

## Frontend State Management

### State Variables
- `map`: Leaflet instance (null until first result)
- `markers`: Array of attraction marker objects
- `mainMarker`: Reference to main location marker

### State Flow
```
Initial State
    ↓
User Submits Query
    ↓
Loading State (spinner, disabled button)
    ↓
API Request
    ↓
Success → Results State (map + cards visible)
    OR
Error → Error State (message shown, form enabled)
```

### Map State Transitions
- **Null → Initialized**: On first successful result
- **Initialized → Updated**: On subsequent searches (destroy old, create new)
- **Updated → Cleaned**: Old markers removed before new ones added

## Natural Language Processing

### Place Name Extraction Patterns
1. `"trip to ([Place])"`
2. `"visit(ing)? ([Place])"`
3. `"go(ing)? to ([Place])"`
4. `"in|at|for ([Place])"`
5. **Fallback**: Detect capitalized words (proper nouns)

### Pattern Priority
- Specific patterns tried first (high confidence)
- Capitalized word detection as fallback
- Common words filtered ("I", "Am", "Hey", "The")

## Error Handling Strategy

### Four-Layer Error Handling

1. **Tool Layer**
   - Try-except blocks catch API failures
   - Return structured error messages
   - Example: "Place not found" vs API timeout

2. **Agent Layer**
   - Checks tool responses for error indicators
   - Sets `success=False` in response
   - Populates `error` field with details

3. **API Layer**
   - Pydantic validates request body
   - Returns 400 for invalid queries
   - Structured JSON error responses

4. **Frontend Layer**
   - Displays error in dedicated div
   - Hides results section
   - Re-enables form for retry

### Graceful Degradation
- Missing weather → Display "--"
- No attractions → Show "No attractions found"
- Coordinate parsing fails → Show names without map interaction
- Map initialization fails → Cards still display

## Performance Considerations

### Optimization Strategies
- **Lazy Loading**: Map only initializes when needed
- **Coordinate Reuse**: Geocoding called once, shared across tools
- **Tile Caching**: Browser caches OpenStreetMap tiles
- **Marker Cleanup**: Old markers removed to prevent memory leaks
- **Async Requests**: Frontend uses fetch API with async/await

### Potential Improvements
- Parallel tool execution (currently sequential)
- Client-side caching for repeated queries
- Debouncing for rapid searches
- Progressive map loading with placeholder

## Design Decisions

### Why Direct Tool Calls vs LLM Reasoning?
- **Speed**: Direct API calls faster than LLM inference
- **Cost**: No token usage for structured lookups
- **Reliability**: APIs more consistent than LLM parsing
- **Scalability**: No LLM rate limits for tool execution

### Why Leaflet Over Google Maps?
- **Free**: No API key, no billing
- **Open Source**: Community-driven
- **Lightweight**: 42KB vs 500KB+
- **Privacy**: No tracking

### Why Two Attraction Lists?
- **Backward Compatibility**: Old clients work with names only
- **UI Simplicity**: Display doesn't need coordinate logic
- **Graceful Fallback**: If coordinates fail, names still render

## Extensibility

### Easy Additions
- More POI categories (restaurants, hotels)
- Multi-day weather forecast
- Route planning between attractions
- User favorites/saved trips
- Offline map support

### Framework Supports
- Additional tool integrations (flights, hotels)
- LLM-based recommendations (when to visit, what to pack)
- Conversational refinement ("show parks only")
- Multi-city itineraries

## System Benefits

- **100% Open Source**: No proprietary dependencies
- **Zero API Costs**: All external APIs are free
- **Fast Response**: Direct API calls, minimal LLM usage
- **Interactive UX**: Real-time map interaction
- **Natural Input**: Accepts conversational queries
- **Structured Output**: Reliable JSON responses
