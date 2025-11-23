"""
Test Tourism Agent with Tools and Structured Output
"""
from tourism_agent import create_tourism_agent_with_tools


def test_scenario(num, query, expected_features):
    """Test a single scenario"""
    print(f"\n{'='*80}")
    print(f"TEST {num}")
    print(f"{'='*80}")
    print(f"Query: {query}")
    print("-"*80)
    
    agent = create_tourism_agent_with_tools()
    result = agent.run(query)
    
    print(f"\n✅ Structured Response:")
    print(f"  Place: {result.place}")
    print(f"  Success: {result.success}")
    print(f"  Has Weather: {result.has_weather}")
    print(f"  Has Places: {result.has_places}")
    
    if result.temperature is not None:
        print(f"  Temperature: {result.temperature}°C")
    if result.precipitation_chance is not None:
        print(f"  Precipitation: {result.precipitation_chance}%")
    if result.attractions:
        print(f"  Attractions: {len(result.attractions)} places")
        for attraction in result.attractions:
            print(f"    - {attraction}")
    
    print(f"\n💬 Display Message:")
    print(f"  {result.message}")
    
    if result.error:
        print(f"\n❌ Error: {result.error}")
    
    # Validate
    passed = True
    if "weather" in expected_features:
        if not (result.has_weather and result.temperature is not None):
            print(f"\n❌ FAILED: Expected weather information")
            passed = False
    
    if "places" in expected_features:
        if not (result.has_places and result.attractions):
            print(f"\n❌ FAILED: Expected places information")
            passed = False
    
    if passed:
        print(f"\n✅ TEST {num} PASSED")
    
    return passed


def run_all_tests():
    """Run all test scenarios from requirements"""
    print("\n🚀 TESTING TOURISM AGENT WITH TOOLS AND STRUCTURED OUTPUT\n")
    
    results = []
    
    # Test 1: Trip planning (places only)
    results.append(test_scenario(
        1,
        "I'm going to go to Bangalore, let's plan my trip.",
        ["places"]
    ))
    
    # Test 2: Weather only
    results.append(test_scenario(
        2,
        "I'm going to go to Bangalore, what is the temperature there",
        ["weather"]
    ))
    
    # Test 3: Weather + Places
    results.append(test_scenario(
        3,
        "I'm going to go to Bangalore, what is the temperature there? And what are the places I can visit?",
        ["weather", "places"]
    ))
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print(f"{'='*80}\n")


if __name__ == "__main__":
    run_all_tests()
