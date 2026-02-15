"""
Vapi Voice Agent Setup with Groq
Creates a medical drone delivery voice assistant using:
- Vapi for voice infrastructure
- Groq (Llama 3.1 70B) for ultra-fast LLM processing
- Deepgram for medical-grade speech recognition
"""

import os
from dotenv import load_dotenv
from vapi_python import Vapi

load_dotenv()

def create_medical_drone_assistant():
    """
    Create Vapi assistant with Groq LLM for medical drone delivery

    Returns:
        dict: Assistant configuration with ID
    """

    vapi = Vapi(api_key=os.getenv('VAPI_API_KEY'))

    print("🚀 Creating Medical Drone Delivery Assistant with Groq...")

    try:
        assistant = vapi.assistants.create(
            name="Medical Drone Dispatcher",

            # ============ GROQ CONFIGURATION (Ultra-fast LLM) ============
            model={
                "provider": "groq",
                "model": "llama-3.1-70b-versatile",  # Fastest + most capable Groq model
                "temperature": 0.1,  # Low temp for accuracy in medical context
                "maxTokens": 1000,
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a professional medical emergency drone delivery dispatcher.

CRITICAL INSTRUCTIONS:
1. Be concise, professional, and efficient - time matters in medical emergencies
2. Speak naturally but move the conversation forward quickly
3. ALWAYS confirm medication names by spelling them out to avoid errors
4. For controlled substances, note you'll need authorization codes (but still take the order)

CONVERSATION FLOW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1: GREETING & IDENTIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"Welcome to MedWing, your voice-controlled autonomous medical delivery system. Please state your name and facility."

Listen for:
- Caller name (e.g., "Dr. Sarah Chen")
- Facility name (e.g., "City General Hospital")
- Department (e.g., "Emergency Department" or "ICU")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2: COLLECT MEDICATION ORDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"What medications do you need?"

For EACH medication, extract:
- Generic or brand name
- Dosage/strength (e.g., "500mg", "10mcg/mL", "0.3mg auto-injector")
- Quantity (number of units)
- Form (tablet, capsule, injection, vial, auto-injector, etc.)

Examples of what they might say:
- "Amoxicillin 500 milligram, 20 tablets"
- "Epi pens, point three milligram, 3 auto injectors"
- "Normal saline 1 liter bags, 5 of them"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3: URGENCY LEVEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ask: "Is this STAT, urgent, or routine?"

- STAT = Life-threatening, drone will fly maximum speed
- Urgent = Needed soon, standard priority
- Routine = Regular restocking, lower priority

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 4: DELIVERY LOCATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"Where should we deliver?"

Get specific location:
- Building name/number
- Floor
- Department/unit
- Landing zone (rooftop, ground level, etc.)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 5: CONFIRM ORDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Read back COMPLETE order:
"Let me confirm: [medication name spelled out], [dosage], quantity [X], [urgency level], delivery to [specific location]. Is this correct?"

Wait for confirmation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 6: DISPATCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Once confirmed, call the dispatch_drone function.

After dispatch is confirmed:
"Order confirmed. Drone Unit [X] dispatched. ETA [Y] minutes. Your tracking code is [CODE]. The drone will announce arrival. Thank you for using MedWing. We're here to help when you need us."

Then end the call naturally.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT HANDLING NOTES:
- If they give multiple medications, collect ALL before confirming
- If unclear on dosage, ask: "What strength - 250 or 500 milligrams?"
- Common medication abbreviations:
  * NS = Normal Saline
  * D5W = 5% Dextrose in Water
  * Epi = Epinephrine
  * Amox = Amoxicillin
  * Insulin = specify type (regular, NPH, etc.)
- For controlled substances: note "authorization required" but take order

SAFETY:
- NEVER guess medication names - always confirm
- NEVER substitute similar-sounding medications
- If you can't understand medication name after 2 tries, say:
  "I'm having trouble hearing the medication name. Can you spell it letter by letter?"

Your tone should be: Professional, calm, efficient, reassuring."""
                    }
                ],

                # ============ FUNCTION CALLING (Structured Data Extraction) ============
                "functions": [
                    {
                        "name": "dispatch_drone",
                        "description": "Dispatch a drone with validated medical order after confirming all details with caller",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "caller_name": {
                                    "type": "string",
                                    "description": "Full name of the caller (e.g., 'Dr. Sarah Chen')"
                                },
                                "facility": {
                                    "type": "string",
                                    "description": "Hospital or facility name (e.g., 'City General Hospital')"
                                },
                                "department": {
                                    "type": "string",
                                    "description": "Specific department (e.g., 'Emergency Department', 'ICU', 'Cardiac Care Unit')"
                                },
                                "medications": {
                                    "type": "array",
                                    "description": "List of all medications being ordered",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "Generic or brand name of medication"
                                            },
                                            "dosage": {
                                                "type": "string",
                                                "description": "Strength/concentration (e.g., '500mg', '10mcg/mL', '0.3mg')"
                                            },
                                            "quantity": {
                                                "type": "integer",
                                                "description": "Number of units needed"
                                            },
                                            "form": {
                                                "type": "string",
                                                "enum": ["tablet", "capsule", "injection", "vial", "auto-injector", "bag", "ampule", "syringe", "patch", "inhaler", "other"],
                                                "description": "Physical form of medication"
                                            }
                                        },
                                        "required": ["name", "dosage", "quantity", "form"]
                                    }
                                },
                                "urgency": {
                                    "type": "string",
                                    "enum": ["STAT", "urgent", "routine"],
                                    "description": "Priority level: STAT (life-threatening), urgent (needed soon), routine (regular restocking)"
                                },
                                "delivery_location": {
                                    "type": "object",
                                    "properties": {
                                        "building": {"type": "string"},
                                        "floor": {"type": "string"},
                                        "specific_area": {"type": "string", "description": "Department name, room number, or landing zone"},
                                        "access_instructions": {"type": "string", "description": "Any special access notes"}
                                    },
                                    "required": ["building", "specific_area"]
                                }
                            },
                            "required": ["caller_name", "facility", "medications", "urgency", "delivery_location"]
                        }
                    }
                ]
            },

            # ============ VOICE CONFIGURATION (High-quality TTS) ============
            voice={
                "provider": "11labs",  # ElevenLabs for professional quality
                "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel - professional, calm female voice
                "stability": 0.5,  # Moderate stability for natural variation
                "similarityBoost": 0.75,  # High similarity to maintain consistent character
                "speed": 1.1  # Slightly faster for efficiency in emergencies
            },

            # ============ TRANSCRIBER CONFIGURATION (Medical-grade STT) ============
            transcriber={
                "provider": "deepgram",
                "model": "nova-2-medical",  # Medical-specific vocabulary
                "language": "en-US",
                "smartFormat": True,  # Automatic formatting of numbers, dates
                "keywords": [  # Boost recognition of common medications
                    "amoxicillin:3", "epinephrine:3", "insulin:3", "morphine:3",
                    "fentanyl:3", "atropine:3", "naloxone:3", "lidocaine:3",
                    "dopamine:3", "norepinephrine:3", "vasopressin:3",
                    "STAT:3", "milligram:2", "microgram:2", "auto-injector:2"
                ]
            },

            # ============ CONVERSATION SETTINGS ============
            firstMessage="Welcome to MedWing, your voice-controlled autonomous medical delivery system. Please state your name and facility.",

            # Phrases that will automatically end the call
            endCallPhrases=[
                "goodbye",
                "thank you goodbye",
                "that's all thank you",
                "end call"
            ],

            # Enable recording for compliance/review
            recordingEnabled=True,

            # Max call duration (10 minutes safety limit)
            maxDurationSeconds=600,

            # Silence timeout (if no speech for 10 seconds, prompt user)
            silenceTimeoutSeconds=10,

            # Background sound settings (reduce noise)
            backgroundSound="off",

            # Enable analysis for quality metrics
            analysisEnabled=True,

            # Server URL for webhooks (we'll set this up next)
            serverUrl=f"{os.getenv('WEBHOOK_BASE_URL')}/vapi-webhook",

            # What events to send to webhook
            serverUrlEvents=[
                "function-call",  # When dispatch_drone is called
                "end-of-call-report",  # Summary after call ends
                "transcript"  # Real-time transcript
            ]
        )

        print(f"✅ Assistant created successfully!")
        print(f"📋 Assistant ID: {assistant.id}")
        print(f"📞 Assistant Name: {assistant.name}")
        print(f"🤖 Model: Groq Llama 3.1 70B (ultra-fast)")
        print(f"🎤 Voice: ElevenLabs Rachel (professional)")
        print(f"👂 Transcriber: Deepgram Nova-2-Medical")

        # Save assistant ID to file for later use
        with open('/Users/julih/Drone-SLAM/voice_agent/assistant_id.txt', 'w') as f:
            f.write(assistant.id)

        return {
            "success": True,
            "assistant_id": assistant.id,
            "assistant": assistant
        }

    except Exception as e:
        print(f"❌ Error creating assistant: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def test_assistant_call(phone_number: str):
    """
    Make a test outbound call to verify assistant works

    Args:
        phone_number: Phone number to call (include country code, e.g., '+14155551234')
    """
    vapi = Vapi(api_key=os.getenv('VAPI_API_KEY'))

    # Load assistant ID
    try:
        with open('/Users/julih/Drone-SLAM/voice_agent/assistant_id.txt', 'r') as f:
            assistant_id = f.read().strip()
    except FileNotFoundError:
        print("❌ Assistant ID not found. Run create_medical_drone_assistant() first.")
        return

    print(f"📞 Calling {phone_number}...")

    try:
        call = vapi.calls.create(
            assistant_id=assistant_id,
            phone_number=phone_number,
            name="Test Call - Medical Drone"
        )

        print(f"✅ Call initiated!")
        print(f"📋 Call ID: {call.id}")
        print(f"📊 Status: {call.status}")
        print(f"\n🎯 Answer the call and try ordering:")
        print(f"   'This is Dr. Smith from City General ER.'")
        print(f"   'I need Amoxicillin 500mg, 20 tablets, STAT.'")

        return call

    except Exception as e:
        print(f"❌ Error making call: {str(e)}")


def get_assistant_details():
    """Print details of the created assistant"""
    vapi = Vapi(api_key=os.getenv('VAPI_API_KEY'))

    try:
        with open('/Users/julih/Drone-SLAM/voice_agent/assistant_id.txt', 'r') as f:
            assistant_id = f.read().strip()

        assistant = vapi.assistants.get(assistant_id)

        print(f"\n📋 ASSISTANT DETAILS")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"ID: {assistant.id}")
        print(f"Name: {assistant.name}")
        print(f"Model: {assistant.model.get('provider')} - {assistant.model.get('model')}")
        print(f"Voice: {assistant.voice.get('provider')}")
        print(f"Transcriber: {assistant.transcriber.get('provider')} - {assistant.transcriber.get('model')}")
        print(f"Webhook URL: {assistant.server_url}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        return assistant

    except Exception as e:
        print(f"❌ Error getting assistant details: {str(e)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "create":
            create_medical_drone_assistant()

        elif command == "test" and len(sys.argv) > 2:
            phone_number = sys.argv[2]
            test_assistant_call(phone_number)

        elif command == "details":
            get_assistant_details()

        else:
            print("Usage:")
            print("  python vapi_setup.py create              # Create the assistant")
            print("  python vapi_setup.py test +1234567890    # Test call to phone")
            print("  python vapi_setup.py details             # Show assistant info")
    else:
        # Default: create assistant
        create_medical_drone_assistant()
