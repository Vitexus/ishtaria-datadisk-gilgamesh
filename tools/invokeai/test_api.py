#!/usr/bin/env python3
"""
Test InvokeAI API endpoints to find the correct one
"""

import requests
import json

BASE_URL = "http://localhost:9090"

# Common InvokeAI endpoints to test
ENDPOINTS = [
    # Health/Status
    "/",
    "/api",
    "/api/",
    "/api/health",
    "/api/v1/health",
    "/api/version",
    
    # Models
    "/api/models",
    "/api/v1/models",
    "/api/v1/models/list",
    
    # Generation (text to image)
    "/api/generation",
    "/api/v1/generation",
    "/api/v1/generation/text-to-image",
    "/api/v1/text2img",
    "/api/text2img",
    "/api/v1/images",
    "/api/images",
    "/api/v1/images/text-to-image",
    
    # Queue
    "/api/queue",
    "/api/v1/queue",
    
    # History
    "/api/history",
    "/api/v1/history",
]

print(f"Testing InvokeAI API at {BASE_URL}")
print("=" * 70)

for endpoint in ENDPOINTS:
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        status = response.status_code
        
        if status == 200:
            print(f"✅ GET  {endpoint} - {status}")
            try:
                data = response.json()
                if isinstance(data, dict) and len(str(data)) < 100:
                    print(f"   {json.dumps(data)[:80]}")
                elif isinstance(data, list) and len(data) < 5:
                    print(f"   {len(data)} items")
                else:
                    print(f"   Data length: {len(str(data))} chars")
            except:
                content_type = response.headers.get('Content-Type', '')
                print(f"   Type: {content_type}, Length: {len(response.text)} chars")
        elif status == 405:
            print(f"📌 {endpoint} - {status} (Method Not Allowed - but exists!)")
            # Try POST
            try:
                response2 = requests.post(url, json={"test": "ping"}, timeout=5)
                print(f"   → POST {endpoint} - {response2.status_code}")
            except:
                pass
        elif status == 404:
            print(f"❌ {endpoint} - {status} (Not Found)")
        else:
            print(f"⚠️  {endpoint} - {status}")
    except Exception as e:
        print(f"❌ {endpoint} - Connection error: {str(e)[:50]}")

print("=" * 70)

# Now test POST to common generation endpoints
print("\nTesting POST endpoints for text-to-image:")
print("=" * 70)

POST_ENDPOINTS = [
    "/api/v1/generation",
    "/api/v1/generation/text-to-image",
    "/api/v1/text2img",
    "/api/text2img",
    "/api/v1/images",
    "/api/images",
]

test_payload = {
    "prompt": "test portrait",
    "negative_prompt": "blurry",
    "width": 512,
    "height": 512,
    "steps": 1,
    "cfg_scale": 1
}

for endpoint in POST_ENDPOINTS:
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.post(url, json=test_payload, timeout=10)
        status = response.status_code
        
        if status == 200:
            print(f"✅ POST {endpoint} - {status} ✓")
            try:
                data = response.json()
                print(f"   Keys: {list(data.keys())[:5]}")
            except:
                print(f"   Raw: {response.text[:100]}")
        elif status in [400, 422]:
            print(f"📌 POST {endpoint} - {status} (Validation error - endpoint exists!)")
            print(f"   Error: {response.text[:100]}")
        else:
            print(f"❌ POST {endpoint} - {status}")
    except Exception as e:
        print(f"❌ POST {endpoint} - Error: {str(e)[:50]}")

print("=" * 70)

# Check if it's the Web UI only (no REST API)
print("\nChecking if Web UI is running (no REST API):")
try:
    response = requests.get(BASE_URL, timeout=5)
    if response.status_code == 200 and "InvokeAI" in response.text:
        print(f"✅ Web UI is running at {BASE_URL}")
        print("   You may need to use the Web UI directly or enable the REST API")
        print("   Start with: invokeai --host 0.0.0.0 --port 9090 --enable-rest-api")
except:
    pass

print("\n" + "=" * 70)
print("Recommendation:")
print("  If you see POST endpoints with 400/422 errors, those are the correct ones.")
print("  If all POST fail with 404/405, the REST API may not be enabled.")
print("  Use the Web UI at", BASE_URL, "or enable REST API with --enable-rest-api flag")
print("=" * 70)
