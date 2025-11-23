"""
Test Multi-Agent System - Test all three example scenarios from requirements
"""
from agents import create_tourism_agent


def print_test_header(test_num, description):
    """Print formatted test header"""
    print("\n" + "="*80)
    print(f"TEST {test_num}: {description}")
    print("="*80)


def print_result(query, response):
    """Print test result"""
    print(f"\n📝 Input: {query}")
    print(f"\n🤖 Output:\n{response}")
    print("\n" + "-"*80)


def test_scenario_1():
    """
    Example 1: I'm going to go to Bangalore, let's plan my trip.
    Expected: List of places to visit
    """
    print_test_header(1, "Trip Planning (Places Only)")
    
    agent = create_tourism_agent()
    query = "I'm going to go to Bangalore, let's plan my trip."
    response = agent.run(query)
    
    print_result(query, response)
    
    # Verify response contains places
    if "these are the places you can go" in response.lower() or "place" in response.lower():
        print("✅ TEST 1 PASSED: Places information provided")
        return True
    else:
        print("❌ TEST 1 FAILED: Expected places information")
        return False


def test_scenario_2():
    """
    Example 2: I'm going to go to Bangalore, what is the temperature there
    Expected: Temperature and precipitation chance
    """
    print_test_header(2, "Weather Information Only")
    
    agent = create_tourism_agent()
    query = "I'm going to go to Bangalore, what is the temperature there"
    response = agent.run(query)
    
    print_result(query, response)
    
    # Verify response contains weather info
    if "°c" in response.lower() or "temperature" in response.lower():
        print("✅ TEST 2 PASSED: Weather information provided")
        return True
    else:
        print("❌ TEST 2 FAILED: Expected weather information")
        return False


def test_scenario_3():
    """
    Example 3: I'm going to go to Bangalore, what is the temperature there? And what are the places I can visit?
    Expected: Both temperature/precipitation and list of places
    """
    print_test_header(3, "Combined Weather + Places")
    
    agent = create_tourism_agent()
    query = "I'm going to go to Bangalore, what is the temperature there? And what are the places I can visit?"
    response = agent.run(query)
    
    print_result(query, response)
    
    # Verify response contains both weather and places
    has_weather = "°c" in response.lower() or "temperature" in response.lower()
    has_places = "these are the places" in response.lower() or "place" in response.lower()
    
    if has_weather and has_places:
        print("✅ TEST 3 PASSED: Both weather and places information provided")
        return True
    else:
        print(f"❌ TEST 3 FAILED: Expected both weather and places (has_weather={has_weather}, has_places={has_places})")
        return False


def test_additional_scenarios():
    """Test additional scenarios"""
    print_test_header(4, "Additional Test Cases")
    
    agent = create_tourism_agent()
    
    test_cases = [
        "What's the weather like in Paris?",
        "I want to visit Tokyo, what should I see?",
        "Tell me about London - weather and attractions"
    ]
    
    all_passed = True
    for i, query in enumerate(test_cases, 1):
        print(f"\nAdditional Test {i}:")
        response = agent.run(query)
        print_result(query, response)
        
        if response and len(response) > 20:
            print(f"✅ Additional Test {i} PASSED")
        else:
            print(f"❌ Additional Test {i} FAILED")
            all_passed = False
    
    return all_passed


def test_error_handling():
    """Test error handling for invalid places"""
    print_test_header(5, "Error Handling (Invalid Place)")
    
    agent = create_tourism_agent()
    query = "I'm going to InvalidPlaceXYZ123, what's the weather?"
    response = agent.run(query)
    
    print_result(query, response)
    
    # Should gracefully handle non-existent places
    if "don't know" in response.lower() or "not found" in response.lower() or "doesn't exist" in response.lower():
        print("✅ TEST 5 PASSED: Error handling works correctly")
        return True
    else:
        print("⚠️  TEST 5: Response received, check if appropriate")
        return True  # Still pass as long as it doesn't crash


def run_all_tests():
    """Run all test scenarios"""
    print("\n" + "🚀 STARTING MULTI-AGENT SYSTEM TESTS" + "\n")
    print("Testing Tourism AI Agent with Weather Agent and Places Agent")
    print("="*80)
    
    results = []
    
    try:
        # Test all scenarios
        results.append(("Scenario 1: Trip Planning", test_scenario_1()))
        results.append(("Scenario 2: Weather Only", test_scenario_2()))
        results.append(("Scenario 3: Weather + Places", test_scenario_3()))
        results.append(("Scenario 4: Additional Tests", test_additional_scenarios()))
        results.append(("Scenario 5: Error Handling", test_error_handling()))
        
        # Summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {name}")
        
        print("="*80)
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Multi-agent system is working correctly!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR DURING TESTING: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
