"""
Zoom Chat Notification Service

Sends chat notifications via Zoom Incoming Webhook.
This is a TreeHacks sponsor-aligned solution (Zoom x Render).
"""

import os
import requests
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class ZoomNotificationService:
    """
    Service for sending chat notifications via Zoom Incoming Webhook

    Uses Zoom Incoming Webhook (TreeHacks sponsor) to send professional
    chat messages after drone dispatch.
    """

    def __init__(self):
        """Initialize Zoom notification service"""

        # Get Zoom Webhook URL and verification token from environment
        self.webhook_url = os.getenv('ZOOM_WEBHOOK_URL', '')
        self.verification_token = os.getenv('ZOOM_VERIFICATION_TOKEN', '')

        # Feature flag
        self.enabled = os.getenv('ENABLE_ZOOM_NOTIFICATIONS', 'true').lower() == 'true'

        if self.enabled and not self.webhook_url:
            print("⚠️ ZOOM_WEBHOOK_URL not set - notifications disabled")
            self.enabled = False

        if self.enabled and not self.verification_token:
            print("⚠️ ZOOM_VERIFICATION_TOKEN not set - notifications disabled")
            self.enabled = False

        print(f"✅ Zoom Notification Service initialized")
        print(f"   Chat notifications: {'enabled' if self.enabled else 'disabled'}")
        if self.enabled:
            print(f"   Webhook configured: {self.webhook_url[:50]}...")

    def format_order_message(self, order_data: Dict) -> str:
        """
        Format order data into Zoom chat message

        Args:
            order_data (Dict): Complete order information

        Returns:
            str: Formatted text message for Zoom
        """

        # Extract order details
        tracking_code = order_data.get('confirmation_code', 'N/A')
        drone_id = order_data.get('drone_id', 'N/A')
        caller_name = order_data.get('caller_name', 'Doctor')
        facility = order_data.get('facility', 'Unknown Facility')
        department = order_data.get('department', 'Unknown Department')
        urgency = order_data.get('urgency', 'ROUTINE')
        medications = order_data.get('medications', [])
        delivery_location = order_data.get('delivery_location', {})
        transcript = order_data.get('transcript', '')
        call_duration = order_data.get('call_duration', 0)

        # Format ETA
        eta = order_data.get('eta', '')
        if eta:
            try:
                eta_time = datetime.fromisoformat(eta.replace('Z', '+00:00'))
                eta_str = eta_time.strftime('%I:%M %p')
            except:
                eta_str = 'Soon'
        else:
            eta_str = 'Soon'

        # Build medications list
        med_list = []
        for med in medications:
            name = med.get('name', 'Unknown')
            dosage = med.get('dosage', '')
            quantity = med.get('quantity', 0)
            form = med.get('form', 'unit')
            med_list.append(f"- {name} {dosage} x{quantity} {form}(s)")

        medications_text = "\n".join(med_list) if med_list else "- (No medications listed)"

        # Build delivery location
        building = delivery_location.get('building', '')
        floor = delivery_location.get('floor', '')
        area = delivery_location.get('specific_area', '')
        location_parts = [p for p in [building, f"Floor {floor}", area] if p]
        location_text = ", ".join(location_parts) if location_parts else "Main entrance"

        # Format transcript if available
        transcript_section = ""
        if transcript:
            # Truncate if too long (Zoom has message limits)
            max_transcript_length = 500
            if len(transcript) > max_transcript_length:
                transcript_preview = transcript[:max_transcript_length] + "..."
            else:
                transcript_preview = transcript

            transcript_section = f"""

Call Transcript ({call_duration}s):
---
{transcript_preview}
---"""

        # Create clean text message
        message = f"""ARIA DISPATCH: Drone #{drone_id} En Route

Order: {tracking_code}
Priority: {urgency}
ETA: {eta_str}

Requester: {caller_name}
Facility: {facility} - {department}

Medications:
{medications_text}

Delivery: {location_text}{transcript_section}"""

        return message

    def send_order_notification(self, order_data: Dict) -> Dict:
        """
        Send order confirmation via Zoom chat

        Args:
            order_data (Dict): Complete order information

        Returns:
            Dict: Result with status and delivery information
        """

        if not self.enabled:
            print("ℹ️ Zoom notifications disabled, skipping")
            return {"status": "disabled"}

        print(f"\n💬 Sending Zoom chat notification...")
        print(f"   Order: {order_data['confirmation_code']}")
        print(f"   Webhook: {self.webhook_url[:50]}...")

        try:
            # Format message as plain text
            message_text = self.format_order_message(order_data)

            # Send to Zoom webhook with simple message format
            # Using ?format=message sends text directly (not wrapped in JSON)
            webhook_url_with_format = f"{self.webhook_url}?format=message"

            response = requests.post(
                webhook_url_with_format,
                data=message_text,  # Send as raw text, not JSON
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': self.verification_token
                },
                timeout=10
            )

            # Check response
            if response.status_code == 200:
                print(f"✅ Zoom message sent successfully!")
                print(f"   Tracking: {order_data['confirmation_code']}")
                return {
                    "status": "success",
                    "tracking_code": order_data['confirmation_code'],
                    "provider": "zoom"
                }
            else:
                error_text = response.text
                print(f"❌ Zoom webhook error {response.status_code}: {error_text}")
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {error_text}"
                }

        except requests.exceptions.Timeout:
            print(f"❌ Request to Zoom webhook timed out")
            return {"status": "error", "error": "Request timeout"}

        except requests.exceptions.ConnectionError:
            print(f"❌ Could not connect to Zoom webhook")
            return {"status": "error", "error": "Connection failed"}

        except Exception as e:
            print(f"❌ Error sending notification: {str(e)}")
            return {"status": "error", "error": str(e)}


# Global instance
zoom_service = ZoomNotificationService()
