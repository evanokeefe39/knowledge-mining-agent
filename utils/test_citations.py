#!/usr/bin/env python3
"""
Test script to verify citation functionality.
"""

import requests
import json

def test_citations():
    """Test that citations are returned in API responses."""
    try:
        # Test different types of questions
        test_questions = [
            'What are the three types of leverage?',
            'How should I approach sales conversations?',
            'What marketing methods work?',
            'Tell me about business'
        ]

        for question in test_questions:
            print(f"\n[TEST] Testing: '{question}'")
            print("-" * 50)

            response = requests.post(
                'http://localhost:5000/chat',
                json={'message': question},
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                data = response.json()
                print("[OK] API Response successful")
                print(f"Response preview: {data.get('response', '')[:100]}...")
                print(f"Citations count: {len(data.get('citations', []))}")

                if 'citations' in data and data['citations']:
                    print("[VIDEO] Citations found:")
                    for i, citation in enumerate(data['citations'], 1):
                        print(f"  {i}. {citation.get('title', 'Unknown')}")
                        print(f"     Video ID: {citation.get('video_id', 'N/A')}")
                        print(f"     URL: {citation.get('url', 'N/A')}")
                else:
                    print("[FAIL] No citations in response")

            else:
                print(f"[FAIL] API Error: {response.status_code}")
                print(response.text)

    except requests.exceptions.ConnectionError:
        print("[FAIL] Connection failed - is the Flask app running on http://localhost:5000?")
    except Exception as e:
        print(f"[FAIL] Test failed: {e}")

if __name__ == "__main__":
    test_citations()