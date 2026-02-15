"""
Unit tests for transcript extraction from VAPI webhook events
"""
import pytest
from datetime import datetime


class TestTranscriptExtraction:
    """Test transcript extraction from various VAPI event formats"""

    def test_speech_update_with_stopped_status(self):
        """Test extracting transcript from speech-update event with status=stopped"""
        # Simulate VAPI speech-update event structure
        speech_data = {
            "timestamp": 1771148404000,
            "type": "speech-update",
            "status": "stopped",
            "role": "assistant",
            "turn": 0,
            "artifact": {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional medical emergency..."
                    },
                    {
                        "role": "assistant",
                        "content": "Order confirmed. Drone unit one dispatched."
                    }
                ]
            }
        }

        # Extract transcript
        role = speech_data.get("role", "unknown")
        artifact = speech_data.get("artifact", {})
        messages = artifact.get("messages", [])

        transcript_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == role:
                transcript_msg = msg.get("content", "")
                break

        # Verify
        assert transcript_msg == "Order confirmed. Drone unit one dispatched."
        assert role == "assistant"

    def test_speech_update_user_role(self):
        """Test extracting user transcript from speech-update event"""
        speech_data = {
            "status": "stopped",
            "role": "user",
            "artifact": {
                "messages": [
                    {"role": "user", "content": "Yes. Correct."}
                ]
            }
        }

        role = speech_data.get("role")
        artifact = speech_data.get("artifact", {})
        messages = artifact.get("messages", [])

        transcript_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == role:
                transcript_msg = msg.get("content", "")
                break

        assert transcript_msg == "Yes. Correct."
        assert role == "user"

    def test_conversation_update_extraction(self):
        """Test extracting transcript from conversation-update event"""
        conv_data = {
            "timestamp": 1771148404000,
            "type": "conversation-update",
            "conversation": [
                {
                    "role": "system",
                    "content": "You are a professional medical emergency..."
                },
                {
                    "role": "user",
                    "content": "I need to order medications."
                },
                {
                    "role": "assistant",
                    "content": "I'll help you with that order."
                }
            ]
        }

        conversation = conv_data.get("conversation", [])

        # Find last non-system message
        last_msg = None
        for msg in reversed(conversation):
            if msg.get("role") in ["user", "assistant"]:
                last_msg = msg
                break

        assert last_msg is not None
        assert last_msg["role"] == "assistant"
        assert last_msg["content"] == "I'll help you with that order."

    def test_empty_artifact_messages(self):
        """Test handling of empty artifact.messages array"""
        speech_data = {
            "status": "stopped",
            "role": "assistant",
            "artifact": {
                "messages": []
            }
        }

        artifact = speech_data.get("artifact", {})
        messages = artifact.get("messages", [])

        transcript_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == speech_data.get("role"):
                transcript_msg = msg.get("content", "")
                break

        assert transcript_msg == ""

    def test_speaker_label_mapping(self):
        """Test that roles map to correct speaker labels"""
        test_cases = [
            ("assistant", "VAPI Agent"),
            ("user", "User"),
            ("unknown", "Unknown")
        ]

        for role, expected_speaker in test_cases:
            speaker = "VAPI Agent" if role == "assistant" else "User"
            if role not in ["assistant", "user"]:
                speaker = "Unknown"

            assert speaker == expected_speaker


class TestTranscriptEntry:
    """Test transcript entry structure"""

    def test_transcript_entry_format(self):
        """Test that transcript entries have correct structure"""
        transcript_entry = {
            "speaker": "VAPI Agent",
            "text": "Order confirmed.",
            "time": "01:40 AM",
            "role": "assistant"
        }

        assert "speaker" in transcript_entry
        assert "text" in transcript_entry
        assert "time" in transcript_entry
        assert "role" in transcript_entry
        assert transcript_entry["speaker"] in ["VAPI Agent", "User"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
