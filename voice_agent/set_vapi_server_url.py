#!/usr/bin/env python3
"""
Set the Vapi phone number Server URL via API (bypasses UI validation).
Use this when the Vapi dashboard won't save the URL (e.g. Render cold start timeout).

Usage:
  export VAPI_API_KEY=your_key   # or use .env
  python set_vapi_server_url.py [phone_number_id]

  Phone number ID: from Vapi Dashboard → Phone Numbers → your number (e.g. a7bac1a9-10b0-4531-ad74-1ed4f50961ca)
  If omitted, set VAPI_PHONE_NUMBER_ID in .env or env.
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_API_KEY")
PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID") or (sys.argv[1] if len(sys.argv) > 1 else None)
SERVER_URL = "https://drone-slam.onrender.com/vapi-webhook"

def main():
    if not API_KEY:
        print("❌ Set VAPI_API_KEY in .env or environment")
        sys.exit(1)
    if not PHONE_ID:
        print("❌ Set VAPI_PHONE_NUMBER_ID in .env, or run: python set_vapi_server_url.py <phone_number_id>")
        print("   Phone number ID is in Vapi Dashboard → Phone Numbers → your number (UUID)")
        sys.exit(1)

    resp = requests.patch(
        f"https://api.vapi.ai/phone-number/{PHONE_ID}",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={"server": {"url": SERVER_URL}},
        timeout=30,
    )

    if resp.status_code == 200:
        print("✅ Server URL updated via API")
        print(f"   {SERVER_URL}")
    else:
        print(f"❌ API returned {resp.status_code}")
        print(resp.text)
        sys.exit(1)

if __name__ == "__main__":
    main()
