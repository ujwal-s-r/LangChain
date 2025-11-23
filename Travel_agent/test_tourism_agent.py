"""
Test Tourism Agent with Tools and Structured Output
"""
from tourism_agent import create_tourism_agent_with_tools


def test_scenario(num, place_name):
    """Test a single scenario"""
    print(f"\n{'='*80}")
    print(f"TEST {num}")
    print(f"{'='*80}")
    print(f"Place: {place_name}")
    print("-"*80)
    
    agent = create_tourism_agent_with_tools()
    result = agent.run(place_name)
    
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
    
    # Validate - should always have both weather and places
    passed = True
    
    if not result.success:
        print(f"\n❌ FAILED: Request was not successful")
        passed = False
    
    if not (result.has_weather and result.temperature is not None):
        print(f"\n❌ FAILED: Expected weather information")
        passed = False
    
    if not (result.has_places and result.attractions):
        print(f"\n❌ FAILED: Expected places information")
        passed = False
    
    if passed:
        print(f"\n✅ TEST {num} PASSED")
    
    return passed


def run_all_tests():
    """Run all test scenarios - frontend sends only place name"""
    print("\n🚀 TESTING TOURISM AGENT - PLACE NAME INPUT ONLY\n")
    print("Agent automatically fetches both weather and attractions\n")
    
    results = []
    
    # Test 1: Bangalore
    results.append(test_scenario(1, "Bangalore"))
    
    # Test 2: Paris
    results.append(test_scenario(2, "Paris"))
    
    # Test 3: Tokyo
    results.append(test_scenario(3, "Tokyo"))
    
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
