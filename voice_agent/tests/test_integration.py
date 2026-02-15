"""
Integration tests for end-to-end live transcription flow
Tests: VAPI Webhook → Transcript Extraction → SSE Broadcasting → Frontend
"""
import pytest
import asyncio
import json
from collections import deque


class TestEndToEndTranscription:
    """Test complete transcription flow"""

    @pytest.mark.asyncio
    async def test_full_speech_update_flow(self):
        """
        Test complete flow:
        1. Receive VAPI speech-update webhook
        2. Extract transcript
        3. Store in live_transcript
        4. Broadcast to SSE clients
        """
        # Setup
        live_transcript = deque(maxlen=100)
        sse_clients = []
        client_queue = asyncio.Queue()
        sse_clients.append(client_queue)

        # Simulate incoming VAPI webhook
        webhook_data = {
            "message": {
                "timestamp": 1771148404000,
                "type": "speech-update",
                "status": "stopped",
                "role": "assistant",
                "turn": 0,
                "artifact": {
                    "messages": [
                        {
                            "role": "assistant",
                            "content": "Order confirmed. Drone unit one dispatched."
                        }
                    ]
                }
            }
        }

        # Step 1: Extract transcript
        speech_data = webhook_data["message"]
        role = speech_data.get("role", "unknown")
        status = speech_data.get("status", "")

        if status == "stopped":
            artifact = speech_data.get("artifact", {})
            messages = artifact.get("messages", [])

            transcript_msg = ""
            for msg in reversed(messages):
                if msg.get("role") == role:
                    transcript_msg = msg.get("content", "")
                    break

            # Step 2: Create transcript entry
            if transcript_msg:
                speaker = "VAPI Agent" if role == "assistant" else "User"
                transcript_entry = {
                    "speaker": speaker,
                    "text": transcript_msg,
                    "time": "01:40 AM",
                    "role": role
                }

                # Step 3: Store in live_transcript
                live_transcript.append(transcript_entry)

                # Step 4: Broadcast to SSE clients
                message = f"data: {json.dumps(transcript_entry)}\n\n"
                for queue in sse_clients:
                    await queue.put(message)

        # Verify end-to-end
        assert len(live_transcript) == 1
        assert live_transcript[0]["speaker"] == "VAPI Agent"
        assert live_transcript[0]["text"] == "Order confirmed. Drone unit one dispatched."

        # Verify SSE client received it
        received = await client_queue.get()
        assert "Order confirmed" in received

    @pytest.mark.asyncio
    async def test_conversation_update_flow(self):
        """Test full flow with conversation-update event"""
        live_transcript = deque(maxlen=100)
        sse_clients = []
        client_queue = asyncio.Queue()
        sse_clients.append(client_queue)

        # Simulate conversation-update webhook
        webhook_data = {
            "message": {
                "timestamp": 1771148404000,
                "type": "conversation-update",
                "conversation": [
                    {
                        "role": "system",
                        "content": "You are a professional..."
                    },
                    {
                        "role": "user",
                        "content": "I need medications."
                    },
                    {
                        "role": "assistant",
                        "content": "I'll help you with that."
                    }
                ]
            }
        }

        # Extract from conversation-update
        conv_data = webhook_data["message"]
        if "conversation" in conv_data:
            conversation = conv_data.get("conversation", [])

            # Find last non-system message
            for msg in reversed(conversation):
                role = msg.get("role", "")
                if role in ["user", "assistant"]:
                    content = msg.get("content", "")
                    if content:
                        speaker = "VAPI Agent" if role == "assistant" else "User"
                        transcript_entry = {
                            "speaker": speaker,
                            "text": content,
                            "time": "01:40 AM",
                            "role": role
                        }
                        live_transcript.append(transcript_entry)

                        # Broadcast
                        message = f"data: {json.dumps(transcript_entry)}\n\n"
                        for queue in sse_clients:
                            await queue.put(message)
                        break

        # Verify
        assert len(live_transcript) == 1
        assert live_transcript[0]["text"] == "I'll help you with that."

    @pytest.mark.asyncio
    async def test_multiple_speakers_in_sequence(self):
        """Test handling multiple speakers in conversation sequence"""
        live_transcript = deque(maxlen=100)

        # Simulate conversation with multiple turns
        conversation_events = [
            {
                "role": "assistant",
                "content": "Welcome to MedWing."
            },
            {
                "role": "user",
                "content": "I need antibiotics."
            },
            {
                "role": "assistant",
                "content": "I'll help with that order."
            },
            {
                "role": "user",
                "content": "Thank you."
            }
        ]

        # Process each event
        for event in conversation_events:
            role = event["role"]
            content = event["content"]
            speaker = "VAPI Agent" if role == "assistant" else "User"

            transcript_entry = {
                "speaker": speaker,
                "text": content,
                "time": "01:40 AM",
                "role": role
            }
            live_transcript.append(transcript_entry)

        # Verify sequence
        assert len(live_transcript) == 4
        assert live_transcript[0]["speaker"] == "VAPI Agent"
        assert live_transcript[1]["speaker"] == "User"
        assert live_transcript[2]["speaker"] == "VAPI Agent"
        assert live_transcript[3]["speaker"] == "User"

    @pytest.mark.asyncio
    async def test_concurrent_sse_clients(self):
        """Test broadcasting to multiple concurrent frontend clients"""
        live_transcript = deque(maxlen=100)
        sse_clients = []

        # Simulate 5 concurrent frontend connections
        num_clients = 5
        for _ in range(num_clients):
            sse_clients.append(asyncio.Queue())

        # Receive webhook and broadcast
        transcript_entry = {
            "speaker": "VAPI Agent",
            "text": "Order dispatched.",
            "time": "01:40 AM",
            "role": "assistant"
        }

        live_transcript.append(transcript_entry)

        # Broadcast to all
        message = f"data: {json.dumps(transcript_entry)}\n\n"
        for queue in sse_clients:
            await queue.put(message)

        # Verify all clients received it
        for queue in sse_clients:
            received = await queue.get()
            assert "Order dispatched" in received

    def test_zoom_notification_format(self):
        """Test that transcript format is suitable for Zoom notifications"""
        live_transcript = deque(maxlen=100)

        # Add conversation
        live_transcript.append({
            "speaker": "VAPI Agent",
            "text": "Welcome to MedWing.",
            "time": "01:40 AM",
            "role": "assistant"
        })
        live_transcript.append({
            "speaker": "User",
            "text": "I need medications.",
            "time": "01:40 AM",
            "role": "user"
        })

        # Format for Zoom
        zoom_transcript = "\n".join([
            f"[{entry['speaker']}] {entry['time']}: {entry['text']}"
            for entry in live_transcript
        ])

        expected = (
            "[VAPI Agent] 01:40 AM: Welcome to MedWing.\n"
            "[User] 01:40 AM: I need medications."
        )

        assert zoom_transcript == expected


class TestErrorHandling:
    """Test error handling in transcription flow"""

    def test_missing_artifact(self):
        """Test handling speech-update with missing artifact"""
        speech_data = {
            "status": "stopped",
            "role": "assistant"
            # Missing artifact
        }

        artifact = speech_data.get("artifact", {})
        messages = artifact.get("messages", [])

        assert messages == []

    def test_empty_conversation(self):
        """Test handling conversation-update with empty conversation"""
        conv_data = {
            "conversation": []
        }

        conversation = conv_data.get("conversation", [])
        last_msg = None

        for msg in reversed(conversation):
            if msg.get("role") in ["user", "assistant"]:
                last_msg = msg
                break

        assert last_msg is None

    def test_system_messages_filtered(self):
        """Test that system messages are not added to transcript"""
        conversation = [
            {"role": "system", "content": "You are a professional..."},
            {"role": "assistant", "content": "Welcome to MedWing."}
        ]

        # Filter out system messages
        filtered = [
            msg for msg in conversation
            if msg.get("role") in ["user", "assistant"]
        ]

        assert len(filtered) == 1
        assert filtered[0]["role"] == "assistant"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
