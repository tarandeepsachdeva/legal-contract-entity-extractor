#!/usr/bin/env python3
"""
Simple test to check API response
"""

import requests

# Test the API
response = requests.post('http://localhost:5001/extract', 
                       json={'text': 'MANAGEMENT ADVISORS, INC shall continue until October 31, 2004 in New York, USA for 5 years at 0.65% annually.'})

print("API Response:")
print(f"Status: {response.status_code}")
print(f"Entity Count: {response.json().get('entity_count', 0)}")
print(f"Entities Length: {len(response.json().get('entities', []))}")

if response.status_code == 200:
    result = response.json()
    print(f"\nActual Entities: {len(result.get('entities', []))}")
    for i, entity in enumerate(result.get('entities', [])):
        print(f"{i+1}: {entity}")
else:
    print("API Error:", response.text)
