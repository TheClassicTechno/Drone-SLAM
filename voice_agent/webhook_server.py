"""
Vapi Webhook Server for Medical Drone Delivery

This FastAPI server receives webhook events from Vapi voice calls and processes
medication orders by dispatching drones. It provides:
- Webhook endpoint for Vapi function calls
- Order validation and processing
- Drone selection and dispatch logic
- REST API for monitoring orders and fleet status

The server is designed to integrate with your existing ROS/Tello drone system.
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List
from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from collections import deque

# Import your existing drone control (placeholder for future integration)
# from your_drone_system import DroneDispatcher

# Import Zoom notification service for post-call confirmations (TreeHacks sponsor!)
from zoom_notifications import zoom_service

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application
app = FastAPI(title="Medical Drone Voice Agent Webhook")

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Live transcription storage
live_transcript = deque(maxlen=100)  # Keep last 100 messages
sse_clients = []  # Connected SSE clients

# In-memory storage for orders and drone fleet
# TODO: Replace with persistent database (PostgreSQL, MongoDB, etc.) in production
active_orders = {}

# Simulated drone fleet with battery and location status
# In production, this would query your actual ROS/Tello system
drone_fleet = {
    1: {"status": "available", "battery": 95, "location": "depot"},
    2: {"status": "available", "battery": 88, "location": "depot"},
    3: {"status": "available", "battery": 92, "location": "depot"},
}


class DroneDispatcher:
    """
    Interface to drone control system

    This class handles the logic for selecting, dispatching, and tracking drones.
    Currently uses simulated dispatch - integrate with your ROS/Tello system
    by uncommenting and implementing the TODO sections.
    """

    def __init__(self):
        """Initialize the drone dispatcher"""
        self.base_location = "pharmacy_depot"

        # TODO: Initialize ROS node connection
        # Example:
        # import rospy
        # rospy.init_node('medical_delivery_dispatcher')

    def select_optimal_drone(self, urgency: str) -> int:
        """
        Select best available drone based on urgency and battery level

        For STAT (emergency) orders, we prioritize drones with highest battery.
        For routine orders, we use the first available drone to balance usage.

        Args:
            urgency (str): Order urgency level ("STAT", "urgent", or "routine")

        Returns:
            int: Drone ID number

        Raises:
            Exception: If no drones are available
        """
        # Find all drones that are available and have sufficient battery
        available = [
            drone_id for drone_id, status in drone_fleet.items()
            if status["status"] == "available" and status["battery"] > 30
        ]

        if not available:
            raise Exception("No drones available")

        # For STAT (emergency) orders, select drone with highest battery
        # This ensures maximum reliability for critical deliveries
        if urgency == "STAT":
            return max(available, key=lambda d: drone_fleet[d]["battery"])

        # For non-emergency orders, return first available
        return available[0]

    def calculate_eta(self, drone_id: int, destination: Dict) -> int:
        """
        Calculate estimated time of arrival in minutes

        Args:
            drone_id (int): ID of the dispatched drone
            destination (Dict): Delivery location information

        Returns:
            int: Estimated arrival time in minutes

        TODO: Use actual SLAM/mapping data for accurate route planning
              This should calculate based on:
              - Distance from current location to pharmacy
              - Distance from pharmacy to hospital
              - Drone speed and any no-fly zones
        """
        # Simplified ETA based on urgency level
        # In production, calculate using actual GPS coordinates and flight path
        urgency_eta = {"STAT": 2, "urgent": 3, "routine": 5}
        return urgency_eta.get(destination.get("urgency", "routine"), 5)

    def dispatch_mission(self, order_data: Dict) -> Dict:
        """
        Dispatch drone mission for medication delivery

        This is the main entry point for drone dispatch. It:
        1. Selects optimal drone
        2. Updates drone status
        3. Calculates ETA
        4. Creates order record
        5. Sends mission to drone (TODO: integrate with ROS)

        Args:
            order_data (Dict): Complete order information including medications,
                             urgency, and delivery location

        Returns:
            Dict: Dispatch result with order ID, drone ID, ETA, and tracking code

        TODO: Integrate with your actual drone control system
              This should:
              1. Generate waypoints (depot -> pharmacy -> hospital)
              2. Send mission to ROS/Tello controller
              3. Start SLAM navigation
              4. Monitor progress with status callbacks
        """

        urgency = order_data["urgency"]

        # Select the best drone for this mission
        drone_id = self.select_optimal_drone(urgency)

        # Update drone status to prevent double-booking
        drone_fleet[drone_id]["status"] = "dispatched"

        # Calculate estimated arrival time
        eta_minutes = self.calculate_eta(drone_id, order_data)

        # Generate unique tracking code
        # Format: First 3 letters of facility + random 4-char hex
        confirmation_code = f"{order_data['facility'][:3].upper()}-{uuid.uuid4().hex[:4].upper()}"

        # Create order record
        order_id = str(uuid.uuid4())
        active_orders[order_id] = {
            "order_id": order_id,
            "drone_id": drone_id,
            "confirmation_code": confirmation_code,
            "timestamp": datetime.now().isoformat(),
            "eta": (datetime.now() + timedelta(minutes=eta_minutes)).isoformat(),
            "status": "dispatched",
            **order_data  # Include all order data (medications, location, etc.)
        }

        # Log dispatch information
        print(f"\nDRONE DISPATCHED")
        print(f"=" * 40)
        print(f"Order ID: {order_id}")
        print(f"Drone: Unit {drone_id}")
        print(f"Urgency: {urgency}")
        print(f"Medications: {len(order_data['medications'])} items")
        print(f"Destination: {order_data['facility']} - {order_data['department']}")
        print(f"ETA: {eta_minutes} minutes")
        print(f"Tracking Code: {confirmation_code}")
        print(f"=" * 40 + "\n")

        # TODO: Actually dispatch the drone
        # Example integration with ROS system:
        """
        from geometry_msgs.msg import PoseStamped
        import rospy

        # Create ROS publisher for this drone's mission
        mission_pub = rospy.Publisher(f'/drone_{drone_id}/mission', PoseStamped, queue_size=10)

        # Waypoint 1: Pharmacy (pickup location)
        waypoint_pharmacy = PoseStamped()
        waypoint_pharmacy.pose.position.x = PHARMACY_X
        waypoint_pharmacy.pose.position.y = PHARMACY_Y
        waypoint_pharmacy.pose.position.z = PHARMACY_Z
        mission_pub.publish(waypoint_pharmacy)

        # Waypoint 2: Hospital (delivery location)
        waypoint_hospital = PoseStamped()
        waypoint_hospital.pose.position.x = order_data['delivery_location']['x']
        waypoint_hospital.pose.position.y = order_data['delivery_location']['y']
        waypoint_hospital.pose.position.z = order_data['delivery_location']['z']
        mission_pub.publish(waypoint_hospital)
        """

        return {
            "order_id": order_id,
            "drone_id": drone_id,
            "eta_minutes": eta_minutes,
            "confirmation_code": confirmation_code,
            "status": "dispatched"
        }


# Initialize drone dispatcher instance
dispatcher = DroneDispatcher()


@app.post("/vapi-webhook")
async def handle_vapi_webhook(request: Request):
    """
    Main webhook endpoint that receives events from Vapi

    Vapi sends different types of events during a call:
    - function-call: When assistant calls dispatch_drone() function
    - end-of-call-report: Summary after call ends (includes transcript, cost, etc.)
    - transcript: Real-time transcript updates during the call

    Args:
        request: FastAPI request object containing webhook payload

    Returns:
        JSONResponse: Response back to Vapi (for function calls, this is spoken to caller)
    """

    try:
        # Parse incoming webhook data
        data = await request.json()
        message_type = data.get("message", {}).get("type")

        print(f"\nWebhook received: {message_type}")

        # Handle function call event - this is when assistant wants to dispatch a drone
        # VAPI may send either "function-call" or "tool-calls"
        if message_type in ["function-call", "tool-calls"]:
            # Debug: print the raw event data
            print(f"\n🔍 DEBUG: tool-calls event received")
            print(f"   Raw message: {json.dumps(data['message'], indent=2)[:500]}")

            # Handle both old and new VAPI event formats
            function_call = data["message"].get("functionCall") or data["message"].get("toolCalls", [{}])[0]
            print(f"   Extracted function_call: {function_call}")

            # Extract function name from nested structure
            if function_call:
                # New format: toolCalls[0].function.name
                function_name = function_call.get("function", {}).get("name") or function_call.get("name")
            else:
                function_name = None
            print(f"   Function name: {function_name}")

            if function_name == "dispatch_drone":
                # Extract order data from function parameters (handle both formats)
                order_data = function_call.get("parameters") or function_call.get("function", {}).get("arguments", {})

                # Log incoming order
                print(f"\nORDER RECEIVED VIA VOICE CALL")
                print(f"=" * 40)
                print(f"Caller: {order_data['caller_name']}")
                print(f"Facility: {order_data['facility']}")
                print(f"Department: {order_data['department']}")
                print(f"Urgency: {order_data['urgency']}")
                print(f"\nMedications:")
                for idx, med in enumerate(order_data['medications'], 1):
                    print(f"  {idx}. {med['name']} {med['dosage']}")
                    print(f"     Quantity: {med['quantity']} {med['form']}(s)")
                print(f"\nDelivery Location:")
                loc = order_data['delivery_location']
                print(f"  Building: {loc.get('building', 'N/A')}")
                print(f"  Floor: {loc.get('floor', 'N/A')}")
                print(f"  Area: {loc.get('specific_area', 'N/A')}")
                print(f"=" * 40 + "\n")

                # Validate order before dispatching
                validation_result = validate_order(order_data)
                if not validation_result["valid"]:
                    # Return error message - Vapi will speak this to the caller
                    return JSONResponse({
                        "result": f"Order validation failed: {validation_result['reason']}. Please call back with corrected information."
                    })

                # Dispatch the drone
                try:
                    dispatch_result = dispatcher.dispatch_mission(order_data)

                    # Return success message - Vapi will speak this to the caller
                    return JSONResponse({
                        "result": f"Order confirmed. Drone Unit {dispatch_result['drone_id']} dispatched. Estimated arrival: {dispatch_result['eta_minutes']} minutes. Your tracking code is {dispatch_result['confirmation_code']}."
                    })

                except Exception as e:
                    # Handle dispatch errors (no drones available, system error, etc.)
                    print(f"ERROR: Dispatch failed: {str(e)}")
                    return JSONResponse({
                        "result": f"I apologize, but we're experiencing a system issue. Please try again or call our emergency line."
                    })

        # Handle end of call report - useful for logging and analytics
        elif message_type == "end-of-call-report":
            call_data = data["message"]

            print(f"\nCALL COMPLETED")
            print(f"=" * 40)
            print(f"Call ID: {call_data.get('callId', 'N/A')}")
            print(f"Duration: {call_data.get('durationSeconds', 0)} seconds")
            print(f"Status: {call_data.get('status', 'N/A')}")
            print(f"Cost: ${call_data.get('cost', 0):.4f}")

            # Get transcript summary
            transcript = call_data.get("transcript", "No transcript available")
            print(f"\nTranscript Preview:")
            print(f"{transcript[:200]}..." if len(transcript) > 200 else transcript)
            print(f"=" * 40 + "\n")

            # Send post-call email notification via Cloudflare (TreeHacks sponsor!)
            # Find order associated with this call (if any)
            call_id = call_data.get('callId', '')
            order_for_call = None

            # Search through active orders to find one from this call
            for order_id, order in active_orders.items():
                # Match by timestamp proximity (order created during the call)
                order_time = datetime.fromisoformat(order['timestamp'])
                call_ended = datetime.now()
                time_diff = (call_ended - order_time).total_seconds()

                # If order was created within last 10 minutes, it's likely from this call
                if time_diff < 600 and order.get('status') == 'dispatched':
                    order_for_call = order
                    break

            # Send chat notification if order found
            if order_for_call:
                print(f"\n💬 Sending Zoom chat notification for order {order_for_call['confirmation_code']}...")
                try:
                    # Add transcript to order data for notification
                    order_for_call['transcript'] = transcript
                    order_for_call['call_duration'] = call_data.get('durationSeconds', 0)

                    # Send chat notification via Zoom webhook
                    notification_result = zoom_service.send_order_notification(
                        order_data=order_for_call
                    )

                    if notification_result.get('status') == 'success':
                        print(f"✅ Chat notification sent via Zoom!")
                    elif notification_result.get('status') == 'disabled':
                        print(f"ℹ️ Zoom notifications are disabled")
                    else:
                        print(f"⚠️ Chat notification failed: {notification_result.get('error')}")

                except Exception as e:
                    print(f"⚠️ Error sending notification: {str(e)}")
                    # Continue processing - notifications are not critical to core functionality
            else:
                print(f"ℹ️ No order found for this call - skipping notifications")

            # TODO: Store in database for analytics/compliance
            # save_call_record(call_data)

        # Handle real-time speech updates (VAPI transcription)
        elif message_type == "speech-update":
            speech_data = data["message"]
            role = speech_data.get("role", "unknown")
            status = speech_data.get("status", "")

            # Only process completed speech segments
            if status == "stopped":
                # Extract transcript from artifact.messages
                artifact = speech_data.get("artifact", {})
                messages = artifact.get("messages", [])

                # Find the last message from this role
                transcript_msg = ""
                for msg in reversed(messages):
                    if msg.get("role") == role:
                        transcript_msg = msg.get("content", "")
                        break

                if transcript_msg:
                    timestamp = datetime.now().strftime("%I:%M %p")

                    # Determine speaker
                    speaker = "VAPI Agent" if role == "assistant" else "User"

                    # Add to live transcript
                    transcript_entry = {
                        "speaker": speaker,
                        "text": transcript_msg,
                        "time": timestamp,
                        "role": role
                    }
                    live_transcript.append(transcript_entry)

                    # Print to terminal
                    print(f"\n🎙️ [{speaker}] {timestamp}: {transcript_msg}")

                    # Broadcast to SSE clients
                    asyncio.create_task(broadcast_transcript(transcript_entry))

        # Handle conversation updates
        elif message_type == "conversation-update":
            conv_data = data["message"]
            # Extract last message if available
            if "conversation" in conv_data:
                conversation = conv_data.get("conversation", [])
                # Find the last user or assistant message (skip system messages)
                for msg in reversed(conversation):
                    role = msg.get("role", "")
                    if role in ["user", "assistant"]:
                        content = msg.get("content", "")
                        if content:
                            timestamp = datetime.now().strftime("%I:%M %p")
                            speaker = "VAPI Agent" if role == "assistant" else "User"

                            transcript_entry = {
                                "speaker": speaker,
                                "text": content,
                                "time": timestamp,
                                "role": role
                            }
                            live_transcript.append(transcript_entry)
                            print(f"\n🎙️ [{speaker}] {timestamp}: {content}")
                            asyncio.create_task(broadcast_transcript(transcript_entry))
                            break  # Only process the last message

        # Handle real-time transcript updates (older format)
        elif message_type == "transcript":
            transcript_data = data["message"]
            role = transcript_data.get("role", "unknown")
            text = transcript_data.get("transcript", "")

            print(f"[{role.upper()}]: {text}")

        # Handle other event types
        else:
            print(f"INFO: Received event: {message_type}")
            print(f"   Data: {json.dumps(data, indent=2)[:200]}...")

        return JSONResponse({"status": "ok"})

    except Exception as e:
        # Handle any unexpected errors
        print(f"ERROR: Webhook processing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


async def broadcast_transcript(entry: Dict):
    """Broadcast transcript entry to all connected SSE clients"""
    message = f"data: {json.dumps(entry)}\n\n"
    for queue in sse_clients:
        await queue.put(message)


def validate_order(order_data: Dict) -> Dict:
    """
    Validate medication order against inventory, regulations, etc.

    Args:
        order_data (Dict): Order information to validate

    Returns:
        Dict: {"valid": bool, "reason": str} - validation result

    TODO: Add real validation:
    - Check medication inventory
    - Verify caller credentials against authorized personnel database
    - Check for drug interactions
    - Validate controlled substance authorizations
    - Verify dosage is within safe ranges
    """

    # Example validation: Check if medications list exists
    if not order_data.get("medications"):
        return {"valid": False, "reason": "No medications specified"}

    # Example validation: Check if delivery location exists
    if not order_data.get("delivery_location"):
        return {"valid": False, "reason": "No delivery location specified"}

    # All validations passed
    return {"valid": True}


@app.get("/")
async def root():
    """
    Health check endpoint

    Returns basic system status including number of active orders
    and available drones. Useful for monitoring and load balancers.
    """
    return {
        "status": "online",
        "service": "Medical Drone Voice Agent",
        "active_orders": len(active_orders),
        "available_drones": sum(1 for d in drone_fleet.values() if d["status"] == "available")
    }


@app.get("/orders")
async def get_orders():
    """
    Get all active orders

    Returns a list of all current orders with their status, drone assignments,
    and tracking information. Useful for monitoring dashboard.
    """
    return {
        "total_orders": len(active_orders),
        "orders": list(active_orders.values())
    }


@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    """
    Get specific order details by order ID

    Args:
        order_id (str): Unique order identifier

    Returns:
        Dict: Complete order information

    Raises:
        HTTPException: 404 if order not found
    """
    if order_id not in active_orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return active_orders[order_id]


@app.get("/drones")
async def get_drones():
    """
    Get drone fleet status

    Returns current status of all drones including battery levels,
    locations, and availability. Useful for fleet management dashboard.
    """
    return {
        "total_drones": len(drone_fleet),
        "available": sum(1 for d in drone_fleet.values() if d["status"] == "available"),
        "drones": drone_fleet
    }


@app.get("/live-transcript")
async def get_live_transcript():
    """
    SSE endpoint for live transcription updates

    Frontend connects to this endpoint to receive real-time
    speech-to-text updates as they happen during VAPI calls
    """
    async def event_generator():
        queue = asyncio.Queue()
        sse_clients.append(queue)

        try:
            # Send recent transcript history
            for entry in live_transcript:
                yield f"data: {json.dumps(entry)}\n\n"

            # Stream new updates
            while True:
                message = await queue.get()
                yield message
        except asyncio.CancelledError:
            sse_clients.remove(queue)
            raise

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "http://localhost:5173",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )


@app.get("/transcript-history")
async def get_transcript_history():
    """Get recent transcript history"""
    return {"transcript": list(live_transcript)}


@app.post("/simulate-order")
async def simulate_order(order: Dict):
    """
    Simulate an order for testing (bypass voice call)

    This endpoint allows you to test drone dispatch without making a phone call.
    Useful for development and debugging.

    Example POST body:
    {
      "caller_name": "Dr. Smith",
      "facility": "City General Hospital",
      "department": "Emergency Department",
      "medications": [
        {
          "name": "Amoxicillin",
          "dosage": "500mg",
          "quantity": 20,
          "form": "tablet"
        }
      ],
      "urgency": "STAT",
      "delivery_location": {
        "building": "Main Hospital",
        "floor": "1",
        "specific_area": "ER Bay 3"
      }
    }

    Args:
        order (Dict): Complete order information

    Returns:
        JSONResponse: Dispatch result

    Raises:
        HTTPException: 500 if dispatch fails
    """
    try:
        dispatch_result = dispatcher.dispatch_mission(order)
        return JSONResponse({
            "status": "success",
            "message": "Order dispatched",
            **dispatch_result
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Get port from environment variable or default to 8000
    port = int(os.getenv("SERVER_PORT", 8000))

    # Display server startup information
    print(f"\nStarting Medical Drone Voice Agent Webhook Server")
    print(f"=" * 50)
    print(f"Server running on: http://0.0.0.0:{port}")
    print(f"Webhook endpoint: http://0.0.0.0:{port}/vapi-webhook")
    print(f"Dashboard: http://0.0.0.0:{port}/orders")
    print(f"Fleet status: http://0.0.0.0:{port}/drones")
    print(f"=" * 50 + "\n")
    print(f"Next steps:")
    print(f"   1. Run this server")
    print(f"   2. Expose with ngrok: ngrok http {port}")
    print(f"   3. Update .env WEBHOOK_BASE_URL with ngrok URL")
    print(f"   4. Create Vapi assistant: python vapi_setup.py create")
    print(f"   5. Test with: python vapi_setup.py test +YOUR_PHONE\n")

    # Start the server
    # host="0.0.0.0" makes it accessible from other machines on the network
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
