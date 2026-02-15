"""
Test script for Zoom chat notifications

Quick test to verify Zoom Incoming Webhook is configured and working correctly.
"""

from datetime import datetime, timedelta
from zoom_notifications import zoom_service


def create_test_order():
    """Create sample order data for testing"""

    now = datetime.now()
    eta = now + timedelta(minutes=3)

    return {
        "order_id": "test-order-zoom-123",
        "confirmation_code": "ZOOM-TEST",
        "drone_id": 2,
        "caller_name": "Dr. Sarah Chen",
        "facility": "City General Hospital",
        "department": "Emergency Department",
        "medications": [
            {
                "name": "Amoxicillin",
                "dosage": "500mg",
                "quantity": 20,
                "form": "tablet"
            },
            {
                "name": "Ibuprofen",
                "dosage": "200mg",
                "quantity": 30,
                "form": "tablet"
            }
        ],
        "urgency": "STAT",
        "delivery_location": {
            "building": "Main Hospital",
            "floor": "1",
            "specific_area": "ER Bay 3"
        },
        "timestamp": now.isoformat(),
        "eta": eta.isoformat(),
        "status": "dispatched"
    }


def test_zoom_notification():
    """Test sending notification via Zoom webhook"""

    print("\n" + "="*60)
    print("ZOOM CHAT NOTIFICATION TEST")
    print("="*60)
    print()

    # Create test order
    order = create_test_order()

    print(f"📋 Test Order:")
    print(f"   Tracking Code: {order['confirmation_code']}")
    print(f"   Medications: {len(order['medications'])} items")
    print(f"   Priority: {order['urgency']}")
    print()

    # Send notification
    print("💬 Sending Zoom chat message...")
    print()

    result = zoom_service.send_order_notification(order)

    print()
    print("="*60)
    print("RESULT")
    print("="*60)
    print(f"Status: {result.get('status', 'unknown')}")

    if result.get('status') == 'success':
        print(f"✅ SUCCESS! Message sent to Zoom chat")
        print(f"   Tracking Code: {result.get('tracking_code')}")
        print(f"   Provider: {result.get('provider')}")
        print()
        print("💬 Check your Zoom chat channel for the notification!")
        return True

    elif result.get('status') == 'disabled':
        print("ℹ️ Zoom notifications are disabled")
        print()
        print("To enable:")
        print("  1. Install Incoming Webhook in Zoom (see ZOOM_SETUP.md)")
        print("  2. Connect webhook to a channel")
        print("  3. Set ZOOM_WEBHOOK_URL in .env")
        print("  4. Set ENABLE_ZOOM_NOTIFICATIONS=true in .env")
        return False

    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        print()
        print("Troubleshooting:")
        print("  1. Check ZOOM_WEBHOOK_URL in .env is correct")
        print("  2. Verify webhook is connected to a channel")
        print("  3. Test webhook with curl:")
        print('     curl -X POST "$ZOOM_WEBHOOK_URL" \\')
        print('       -H "Content-Type: application/json" \\')
        print('       -d \'{"text": "Test message"}\'')
        print("  4. See ZOOM_SETUP.md for detailed setup")
        return False


if __name__ == "__main__":
    success = test_zoom_notification()

    print()
    print("="*60)

    if success:
        print("🎉 All tests passed!")
        print()
        print("Next steps:")
        print("  1. Check your Zoom chat for the test notification")
        print("  2. Make a VAPI call to test end-to-end")
        print("  3. Apply for Zoom x Render prize on Devpost!")
    else:
        print("⚠️ Setup incomplete")
        print()
        print("Follow the setup guide:")
        print("  cat ZOOM_SETUP.md")

    print("="*60)
    print()
