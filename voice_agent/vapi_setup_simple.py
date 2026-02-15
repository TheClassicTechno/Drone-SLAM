"""
Vapi Voice Agent Setup using REST API (no SDK dependencies)

This module creates and manages a Vapi voice assistant configured with:
- Groq's Llama 3.3 70B for ultra-fast LLM responses
- Deepgram Nova-2-Medical for medical-grade speech recognition
- ElevenLabs Rachel voice for professional text-to-speech

The assistant is designed to handle medical drone delivery orders via phone calls.
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API credentials from environment
VAPI_API_KEY = os.getenv('VAPI_API_KEY')
WEBHOOK_URL = os.getenv('WEBHOOK_BASE_URL', 'https://your-ngrok-url.ngrok-free.app')

def create_assistant():
    """
    Create Vapi assistant with Groq using REST API

    This function sends a POST request to Vapi's API to create a new voice assistant
    configured specifically for medical drone delivery orders. The assistant uses:
    - Groq for fast LLM processing (approximately 0.2 second response time)
    - Deepgram for accurate medical term transcription
    - ElevenLabs for natural-sounding voice output

    Returns:
        dict: The created assistant object from Vapi, or None if creation fails
    """

    # Vapi API endpoint for creating assistants
    url = "https://api.vapi.ai/assistant"

    # Authentication headers required by Vapi API
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Complete assistant configuration
    assistant_config = {
        "name": "Medical Drone Dispatcher",

        # Groq LLM Configuration
        # Using Llama 3.3 70B for balance of speed and accuracy
        "model": {
            "provider": "groq",
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.1,  # Low temperature for consistent, focused responses
            "maxTokens": 1000,
            "messages": [
                {
                    "role": "system",
                    "content": """You are a warm, caring, and patient medical drone delivery dispatcher. Your voice should be gentle, reassuring, and kind - like speaking to someone you genuinely want to help.

TONE & MANNER:
- Speak warmly and patiently, never rushed
- Use gentle, reassuring language
- Show empathy and understanding
- Take your time - healthcare is important, not rushed
- Be encouraging and supportive

CONVERSATION FLOW:
1. GREETING: "Hello! Thank you for calling Medical Drone Delivery Service. I'm here to help you today. May I please have your name and facility?"

2. COLLECT ORDER: "Thank you so much. Now, I'd love to help you with your medication order. Could you please tell me what you need? I'll need the medication name, dosage, quantity, and form whenever you're ready."

3. URGENCY: "I understand. Just to make sure we prioritize this properly for you, would you say this is STAT, urgent, or routine? Please take your time."

4. LOCATION: "Perfect, thank you for that information. And where would you like us to deliver this to? Any specific area or room number would be helpful."

5. CONFIRM: "Wonderful! Let me just confirm everything with you to make sure I have it exactly right..."
   - Read back SLOWLY and clearly, SPELLING OUT medication names
   - Use a caring tone: "Does everything sound correct to you?"

6. FINALIZE: "Perfect! Your order is all confirmed. I've dispatched Drone Unit [1/2/3] for you, and it should arrive in approximately [2-5] minutes. You're all set! Is there anything else I can help you with today?"

Example confirmation (warm and patient):
"Alright, let me make sure I have everything correct for you. You need Amoxicillin - that's spelled A-M-O-X-I-C-I-L-L-I-N - 500 milligrams, quantity of 20 tablets, with STAT priority, for delivery to the emergency department, trauma bay 2. Does that all sound right to you?"

After they confirm, speak warmly:
"Wonderful! Your order is confirmed. Drone Unit [1/2/3] is on its way to you now. Estimated arrival time is [2-5] minutes. Thank you so much for using our service, and please don't hesitate to call again if you need anything else. Take care!"

Remember: Be patient, kind, and never rush. Healthcare workers are doing important work - treat them with warmth and respect.
"""
                }
            ]
        },

        # ElevenLabs Voice Configuration
        # Using Rachel voice with warm, caring settings
        "voice": {
            "provider": "11labs",
            "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice ID
            "stability": 0.7,  # Higher stability for calm, soothing tone
            "similarityBoost": 0.8,  # High clarity for warmth
            "speed": 0.95  # Slightly slower for patient, caring delivery
        },

        # Deepgram Transcriber Configuration
        # Using medical-specific model for accurate medication name recognition
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2-medical",  # Medical-grade speech recognition
            "language": "en-US",
            "smartFormat": True,  # Automatic formatting of numbers, dates, etc.
            # Keyword boosting: Format is "keyword:weight" where higher weight = higher priority
            "keywords": [
                "amoxicillin:3", "epinephrine:3", "insulin:3", "morphine:3",
                "STAT:3", "milligram:2", "microgram:2"
            ]
        },

        # First message spoken when call connects
        "firstMessage": "Hello! Thank you for calling Medical Drone Delivery Service. I'm here to help you today. May I please have your name and facility?",

        # Phrases that trigger call end
        "endCallPhrases": ["goodbye", "thank you goodbye", "that's all"],

        # Call recording and timeout settings
        "recordingEnabled": True,  # Record all calls for compliance/audit
        "maxDurationSeconds": 600,  # 10 minute maximum call duration
        "silenceTimeoutSeconds": 10,  # Hang up after 10 seconds of silence

        # Webhook configuration - sends order data to your server
        "serverUrl": f"{WEBHOOK_URL}/vapi-webhook"
    }

    print("\nCreating Medical Drone Delivery Assistant with Groq...\n")

    try:
        # Send POST request to create the assistant
        response = requests.post(url, headers=headers, json=assistant_config)
        response.raise_for_status()  # Raise exception for bad status codes

        # Parse response and extract assistant ID
        assistant = response.json()
        assistant_id = assistant.get('id')

        # Display success information
        print("SUCCESS: Assistant created successfully!")
        print(f"Assistant ID: {assistant_id}")
        print(f"Model: Groq Llama 3.1 70B (ultra-fast)")
        print(f"Voice: ElevenLabs Rachel (professional)")
        print(f"Transcriber: Deepgram Nova-2-Medical")
        print(f"Webhook: {WEBHOOK_URL}/vapi-webhook")

        # Save assistant ID to file for later reference
        with open('/Users/julih/Drone-SLAM/voice_agent/assistant_id.txt', 'w') as f:
            f.write(assistant_id)

        print(f"\nAssistant ID saved to: voice_agent/assistant_id.txt\n")

        return assistant

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (400, 401, 500, etc.)
        print(f"ERROR: Failed to create assistant: {e}")
        print(f"Response: {e.response.text}")
        return None
    except Exception as e:
        # Handle any other unexpected errors
        print(f"ERROR: Unexpected error occurred: {e}")
        return None


def test_call(phone_number):
    """
    Make a test outbound call to verify assistant functionality

    This function initiates an outbound call to the specified phone number
    using the previously created assistant. Useful for testing the voice
    agent before deploying it to a real phone number.

    Args:
        phone_number (str): Phone number to call (format: +1234567890)

    Returns:
        dict: Call object from Vapi, or None if call fails
    """

    # Load the previously saved assistant ID
    try:
        with open('/Users/julih/Drone-SLAM/voice_agent/assistant_id.txt', 'r') as f:
            assistant_id = f.read().strip()
    except FileNotFoundError:
        print("ERROR: Assistant ID not found. Run 'create' command first.")
        return

    # Vapi API endpoint for initiating phone calls
    url = "https://api.vapi.ai/call/phone"

    # Authentication headers
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Call configuration
    call_config = {
        "assistantId": assistant_id,  # Use our medical drone assistant
        "phoneNumber": phone_number,  # Number to call
        "name": "Test Call - Medical Drone"  # Label for this call
    }

    print(f"\nInitiating call to {phone_number}...\n")

    try:
        # Send POST request to initiate the call
        response = requests.post(url, headers=headers, json=call_config)
        response.raise_for_status()

        # Parse response
        call = response.json()
        print(f"SUCCESS: Call initiated!")
        print(f"Call ID: {call.get('id')}")
        print(f"Status: {call.get('status')}")

        return call

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors
        print(f"ERROR: Failed to initiate call: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        # Handle any other unexpected errors
        print(f"ERROR: Unexpected error occurred: {e}")


if __name__ == "__main__":
    import sys

    # Command line interface
    # Usage: python vapi_setup_simple.py create
    #        python vapi_setup_simple.py test +1234567890

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "create":
            # Create a new assistant
            create_assistant()
        elif command == "test" and len(sys.argv) > 2:
            # Make a test call to the provided phone number
            test_call(sys.argv[2])
        else:
            # Show usage information
            print("Usage:")
            print("  python vapi_setup_simple.py create")
            print("  python vapi_setup_simple.py test +1234567890")
    else:
        # Default action: create assistant
        create_assistant()
