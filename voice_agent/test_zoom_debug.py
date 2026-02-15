"""
Debug Zoom Webhook Connection

Tests Zoom webhook and provides diagnostic information
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_zoom_connection():
    """Test if Zoom webhook is working"""

    webhook_url = os.getenv('ZOOM_WEBHOOK_URL', '')
    verification_token = os.getenv('ZOOM_VERIFICATION_TOKEN', '')

    if not webhook_url:
        print("❌ ZOOM_WEBHOOK_URL not set in .env")
        return False

    if not verification_token:
        print("❌ ZOOM_VERIFICATION_TOKEN not set in .env")
        return False

    print("🔍 Testing Zoom webhook connection...\n")
    print(f"Webhook URL: {webhook_url}")
    print(f"Token: {verification_token[:10]}...\n")

    # Test 1: Simple text message
    print("📤 Test 1: Sending simple text message...")
    test_message = f"""🚨 ZOOM CONNECTION TEST

If you see this message, your Zoom webhook IS working!

Timestamp: {os.popen('date').read().strip()}
Connection: medical-drone-delivery
Status: ACTIVE

If you don't see this in your Zoom channel within 5 seconds, there's a problem."""

    try:
        response = requests.post(
            f"{webhook_url}?format=message",
            data=test_message,
            headers={
                'Content-Type': 'application/json',
                'Authorization': verification_token
            },
            timeout=10
        )

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}\n")

        if response.status_code == 200:
            print("✅ Webhook accepted the message!")
            print("\n⚠️ IMPORTANT: Check your Zoom app NOW")
            print("   1. Look in the channel where you ran '/inc connect medical-drone-delivery'")
            print("   2. Try refreshing the Zoom app (Cmd+R or restart)")
            print("   3. Check both desktop and web Zoom")
            print("   4. Make sure you're not in DND mode\n")
            return True
        else:
            print(f"❌ Webhook returned error {response.status_code}")
            print(f"Error: {response.text}\n")
            return False

    except Exception as e:
        print(f"❌ Request failed: {str(e)}\n")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ZOOM WEBHOOK DEBUG TOOL")
    print("=" * 60)
    print()

    result = test_zoom_connection()

    if result:
        print("=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("1. Open your Zoom app and find #medical-drone-alerts channel")
        print("2. You should see the test message above")
        print("3. If you DON'T see it, try:")
        print("   - Run '/inc list' in Zoom to verify connection exists")
        print("   - Reconnect with '/inc connect medical-drone-delivery'")
        print("   - Make sure the channel name matches where you connected")
        print("4. If you DO see it, the webhook is working!")
        print("   The VAPI notifications should also work now.")
    else:
        print("=" * 60)
        print("FIX YOUR .ENV FILE:")
        print("=" * 60)
        print("Make sure these variables are set correctly:")
        print("ZOOM_WEBHOOK_URL=https://integrations.zoom.us/chat/webhooks/incomingwebhook/...")
        print("ZOOM_VERIFICATION_TOKEN=your_token_here")
        print("ENABLE_ZOOM_NOTIFICATIONS=true")
