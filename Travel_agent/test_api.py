"""
Test Mistral API - Simple test to verify API connection and model response
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mistral_api():
    """Test the Mistral API with a simple query"""
    print("🧪 Testing Mistral API with GPT-OSS-20B model")
    print("=" * 80)
    
    api_key = os.getenv("mistral_api_key")
    
    if not api_key:
        print("❌ ERROR: mistral_api_key not found in .env file")
        return False
    
    print(f"✅ API Key loaded: {api_key[:20]}...")
    print("\nSending test request to Mistral API...")
    
    url = "https://platform.qubrid.com/api/v1/qubridai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Add explicit headers to disable streaming
    headers["Accept"] = "application/json"
    
    data = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {
                "role": "user",
                "content": "Explain quantum computing simply in one sentence."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500,
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        response.raise_for_status()
        
        # Handle SSE stream response
        if 'text/event-stream' in response.headers.get('Content-Type', ''):
            print("\n📡 Handling SSE stream...")
            full_content = ""
            
            # Split response by lines and process SSE format
            lines = response.text.split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data_str = line[6:].strip()
                    if data_str and data_str != '[DONE]':
                        try:
                            chunk = json.loads(data_str)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    full_content += content
                        except json.JSONDecodeError:
                            continue
            
            print("-" * 80)
            if full_content:
                print(f"\n💬 Model Response:\n{full_content}")
                print("\n✅ Mistral API is working correctly!")
                return True
            else:
                print("\n❌ No content received from stream")
                return False
        else:
            # Regular JSON response
            result = response.json()
            print("\n✅ API Response received!")
            print("-" * 80)
            print("\nFull Response:")
            print(json.dumps(result, indent=2))
            print("-" * 80)
            
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0]["message"]["content"]
                print(f"\n💬 Model Response:\n{message}")
                print("\n✅ Mistral API is working correctly!")
                return True
            else:
                print("\n❌ Unexpected response format")
                return False
            
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        print(f"Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request Error: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_mistral_api()
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED: Mistral API is working correctly!")
        print("Ready to proceed with agent implementation.")
    else:
        print("❌ TEST FAILED: Please check your API key and connection.")
    print("=" * 80)
