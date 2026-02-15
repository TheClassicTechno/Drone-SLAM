#!/usr/bin/env python3
"""
Set the Vapi phone number AND assistant Server URL via API.
Vapi uses the ASSISTANT server URL first (it overrides phone number), so we set both.

Usage:
  # Point to Render (for transcript on drone-slam.vercel.app):
  python set_vapi_server_url.py

  # Point to ngrok for LOCAL transcript (localhost dashboard + terminal log):
  python set_vapi_server_url.py https://YOUR-NGROK-URL.ngrok-free.app

  Required in .env: VAPI_API_KEY, VAPI_PHONE_NUMBER_ID, VAPI_ASSISTANT_ID
  (Assistant ID is in Vapi Dashboard → Assistants → Medical Drone Dispatcher → copy ID)
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_API_KEY")
PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
# Optional: first arg = phone id, last arg = base URL (for local/ngrok)
if len(sys.argv) >= 2 and not sys.argv[1].startswith("http"):
    PHONE_ID = sys.argv[1]
if len(sys.argv) >= 2 and sys.argv[-1].startswith("http"):
    _base = sys.argv[-1].rstrip("/")
    SERVER_URL = f"{_base}/vapi-webhook"
else:
    SERVER_URL = "https://drone-slam.onrender.com/vapi-webhook"

def main():
    if not API_KEY:
        print("❌ Set VAPI_API_KEY in .env or environment")
        sys.exit(1)
    if not PHONE_ID:
        print("❌ Set VAPI_PHONE_NUMBER_ID in .env")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = {"server": {"url": SERVER_URL}, "serverUrl": SERVER_URL}

    # 1. Phone number (required)
    resp = requests.patch(
        f"https://api.vapi.ai/phone-number/{PHONE_ID}",
        headers=headers,
        json={"server": {"url": SERVER_URL}},
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"❌ Phone number API returned {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    print("✅ Phone number Server URL updated")

    # 2. Assistant – set BOTH server.url AND serverUrl (Vapi uses serverUrl for webhook delivery)
    if ASSISTANT_ID:
        resp2 = requests.patch(
            f"https://api.vapi.ai/assistant/{ASSISTANT_ID}",
            headers=headers,
            json=body,
            timeout=30,
        )
        if resp2.status_code != 200:
            print(f"⚠️ Assistant API returned {resp2.status_code} (continuing)")
        else:
            print("✅ Assistant Server URL updated (server.url + serverUrl)")
    else:
        print("⚠️ VAPI_ASSISTANT_ID not set in .env – assistant may still point to Render, so no POST webhooks to local. Add it and re-run.")

    print(f"   {SERVER_URL}")

if __name__ == "__main__":
    main()
