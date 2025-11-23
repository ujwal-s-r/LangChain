"""
Test Script - Tests all tools individually to ensure they work correctly
"""
import sys
import json
from tools import get_coordinates, get_weather, get_tourist_places


def print_separator():
    """Print a visual separator"""
    print("\n" + "="*80 + "\n")


def test_geocoding_tool():
    """Test the geocoding tool"""
    print("🌍 TESTING GEOCODING TOOL")
    print_separator()
    
    test_places = ["Bangalore", "Paris", "Tokyo", "InvalidPlaceXYZ123"]
    
    for place in test_places:
        print(f"Testing: {place}")
        try:
            result = get_coordinates.invoke({"place_name": place})
            print(f"Result: {json.dumps(result, indent=2)}")
            
            if result["success"]:
                print(f"✅ Success! Found coordinates for {result['place']}")
            else:
                print(f"❌ Place not found: {result['error']}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 80)
    
    print_separator()


def test_weather_tool():
    """Test the weather tool"""
    print("🌤️  TESTING WEATHER TOOL")
    print_separator()
    
    test_places = ["Bangalore", "Paris", "New York", "InvalidPlaceXYZ123"]
    
    for place in test_places:
        print(f"Testing weather for: {place}")
        try:
            result = get_weather.invoke({"place_name": place})
            print(f"Result: {result}")
            
            if "it's currently" in result or "°C" in result:
                print(f"✅ Success! Weather data retrieved")
            elif "don't know" in result:
                print(f"❌ Place not found (expected for invalid places)")
            else:
                print(f"⚠️  Unexpected response format")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 80)
    
    print_separator()


def test_places_tool():
    """Test the tourist places tool"""
    print("🏛️  TESTING TOURIST PLACES TOOL")
    print_separator()
    
    test_places = ["Bangalore", "Paris", "London", "InvalidPlaceXYZ123"]
    
    for place in test_places:
        print(f"Testing tourist places for: {place}")
        try:
            result = get_tourist_places.invoke({"place_name": place})
            print(f"Result:\n{result}")
            
            if "these are the places you can go" in result:
                print(f"✅ Success! Tourist places retrieved")
            elif "don't know" in result:
                print(f"❌ Place not found (expected for invalid places)")
            elif "couldn't find specific" in result:
                print(f"⚠️  No tourist data available but place exists")
            else:
                print(f"⚠️  Unexpected response format")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 80)
    
    print_separator()


def run_all_tests():
    """Run all tests"""
    print("\n" + "🚀 STARTING TOURISM AGENT TOOLS TEST SUITE" + "\n")
    print("="*80)
    
    try:
        # Test 1: Geocoding Tool
        test_geocoding_tool()
        
        # Test 2: Weather Tool
        test_weather_tool()
        
        # Test 3: Places Tool
        test_places_tool()
        
        print("\n✅ ALL TESTS COMPLETED!")
        print("="*80)
        print("\nSummary:")
        print("- Geocoding Tool: Tests location resolution")
        print("- Weather Tool: Tests weather API integration")
        print("- Places Tool: Tests tourist attraction finding")
        print("\nIf all tools show ✅ for valid places, they are working correctly!")
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR DURING TESTING: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
