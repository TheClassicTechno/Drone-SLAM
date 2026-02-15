"""
Start ngrok tunnel and get public URL

This simple utility script starts an ngrok tunnel to expose the local
webhook server to the internet, allowing Vapi to send webhook events
to your local development machine.

Note: This requires ngrok to be installed and authenticated.
Install with: brew install ngrok (macOS) or download from ngrok.com
Authenticate with: ngrok config add-authtoken YOUR_TOKEN
"""

from pyngrok import ngrok
import time

# Clean up any existing tunnels before starting
# This prevents port conflicts if script was previously interrupted
try:
    ngrok.kill()
except:
    pass  # Ignore errors if no tunnels exist

print("Starting ngrok tunnel on port 8000...")

# Start ngrok tunnel pointing to local port 8000 (where webhook server runs)
public_url = ngrok.connect(8000)

# Display tunnel information
print(f"\nSUCCESS: Ngrok tunnel started!")
print(f"Public URL: {public_url}")
print(f"\nUse this URL in your .env file:")
print(f"   WEBHOOK_BASE_URL={public_url}")
print(f"\nIMPORTANT: Keep this script running to maintain the tunnel!")
print(f"   Press Ctrl+C to stop\n")

# Keep the tunnel alive indefinitely
# The tunnel will close when this script exits
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # User pressed Ctrl+C to stop
    print("\n\nStopping ngrok tunnel...")
    ngrok.kill()
    print("Tunnel closed")
