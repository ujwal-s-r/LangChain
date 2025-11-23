Inkle Assignment: AI Intern
Problem Statement
Build a multi-agent tourism system where:
User input: Enter a place they want to visit
Parent Agent: Tourism AI Agent (orchestrates the system)
Child Agent 1: Weather Agent (checks current/forecast weather)
Child Agent 2: Places Agent (suggests up to 5 tourist attractions)
Error Handling: For non-existent places, let AI respond that It doesn’t know this place exist
Open-Source API Recommendations
You can figure out your own APIs, requirement is Child Agents or (Tools) should use some API source instead of using the AI’s own knowledge
Weather APIs
Open-Meteo API (Recommended)
Endpoint: https://api.open-meteo.com/v1/forecast
Documentation: https://open-meteo.com/en/docs
Places/Tourism APIs
Overpass API (Recommended)
Base URL: https://overpass-api.de/api/interpreter
Documentation: https://wiki.openstreetmap.org/wiki/Overpass_API
Get the coordinates of the place entered using Nominatim API mentioned below
Geocoding
Nominatim API (Recommended)
Base URL: https://nominatim.openstreetmap.org/search
Documentation: https://nominatim.org/release-docs/develop/api/Search/





Example 1
Input: I’m going to go to Bangalore, let’s plan my trip.
Output:
In Bangalore these are the places you can go, 
Lalbagh
Sri Chamarajendra Park
Bangalore palace
Bannerghatta National Park
Jawaharlal Nehru Planetarium

Example 2 
Input: I’m going to go to Bangalore, what is the temperature there
Output:
In Bangalore it’s currently 24°C with a chance of 35% to rain.

Example 3
Input: I’m going to go to Bangalore, what is the temperature there? And what are the places I can visit?
Output:
In Bangalore it’s currently 24°C with a chance of 35% to rain. And these are the places you can go:
Lalbagh
Sri Chamarajendra Park
Bangalore palace
Bannerghatta National Park
Jawaharlal Nehru Planetarium
