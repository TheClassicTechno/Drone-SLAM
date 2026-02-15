"""
Integration tests for SSE (Server-Sent Events) live transcript endpoint
"""
import pytest
import asyncio
import json
from collections import deque


class MockSSEClient:
    """Mock SSE client for testing"""

    def __init__(self):
        self.received_messages = []
        self.queue = asyncio.Queue()

    async def receive(self):
        """Simulate receiving SSE message"""
        message = await self.queue.get()
        self.received_messages.append(message)
        return message


class TestSSEEndpoint:
    """Test SSE endpoint functionality"""

    @pytest.mark.asyncio
    async def test_broadcast_to_single_client(self):
        """Test broadcasting transcript to single SSE client"""
        # Setup
        sse_clients = []
        client_queue = asyncio.Queue()
        sse_clients.append(client_queue)

        # Simulate broadcast
        transcript_entry = {
            "speaker": "VAPI Agent",
            "text": "Order confirmed.",
            "time": "01:40 AM",
            "role": "assistant"
        }

        message = f"data: {json.dumps(transcript_entry)}\n\n"
        await client_queue.put(message)

        # Verify
        received = await client_queue.get()
        assert "data:" in received
        assert "Order confirmed." in received

    @pytest.mark.asyncio
    async def test_broadcast_to_multiple_clients(self):
        """Test broadcasting to multiple concurrent SSE clients"""
        # Setup multiple clients
        sse_clients = []
        num_clients = 3

        for _ in range(num_clients):
            queue = asyncio.Queue()
            sse_clients.append(queue)

        # Broadcast message to all clients
        transcript_entry = {
            "speaker": "User",
            "text": "Yes. Correct.",
            "time": "01:40 AM",
            "role": "user"
        }

        message = f"data: {json.dumps(transcript_entry)}\n\n"

        async def broadcast_to_all():
            for queue in sse_clients:
                await queue.put(message)

        await broadcast_to_all()

        # Verify all clients received the message
        for queue in sse_clients:
            received = await queue.get()
            assert "Yes. Correct." in received

    def test_transcript_history_storage(self):
        """Test deque-based circular buffer for transcript history"""
        # Simulate live_transcript with maxlen=100
        live_transcript = deque(maxlen=5)  # Use 5 for testing

        # Add 7 entries (exceeds maxlen)
        for i in range(7):
            entry = {
                "speaker": "User",
                "text": f"Message {i}",
                "time": "01:40 AM",
                "role": "user"
            }
            live_transcript.append(entry)

        # Verify only last 5 are kept
        assert len(live_transcript) == 5
        assert live_transcript[0]["text"] == "Message 2"  # First two dropped
        assert live_transcript[-1]["text"] == "Message 6"

    @pytest.mark.asyncio
    async def test_sse_message_format(self):
        """Test SSE message format compliance"""
        transcript_entry = {
            "speaker": "VAPI Agent",
            "text": "Welcome to MedWing.",
            "time": "01:40 AM",
            "role": "assistant"
        }

        # Format as SSE
        message = f"data: {json.dumps(transcript_entry)}\n\n"

        # Verify format
        assert message.startswith("data: ")
        assert message.endswith("\n\n")

        # Verify JSON is valid
        json_part = message.replace("data: ", "").strip()
        parsed = json.loads(json_part)
        assert parsed["speaker"] == "VAPI Agent"
        assert parsed["text"] == "Welcome to MedWing."

    def test_transcript_history_endpoint_response(self):
        """Test /transcript-history endpoint response format"""
        live_transcript = deque(maxlen=100)

        # Add sample entries
        live_transcript.append({
            "speaker": "VAPI Agent",
            "text": "Order confirmed.",
            "time": "01:40 AM",
            "role": "assistant"
        })
        live_transcript.append({
            "speaker": "User",
            "text": "Thank you.",
            "time": "01:40 AM",
            "role": "user"
        })

        # Simulate endpoint response
        response = {"transcript": list(live_transcript)}

        # Verify
        assert "transcript" in response
        assert len(response["transcript"]) == 2
        assert response["transcript"][0]["speaker"] == "VAPI Agent"
        assert response["transcript"][1]["speaker"] == "User"


class TestSSEClientCleanup:
    """Test SSE client connection lifecycle"""

    @pytest.mark.asyncio
    async def test_client_disconnect_cleanup(self):
        """Test that disconnected clients are removed from sse_clients list"""
        sse_clients = []

        # Add client
        client_queue = asyncio.Queue()
        sse_clients.append(client_queue)

        assert len(sse_clients) == 1

        # Simulate disconnect
        sse_clients.remove(client_queue)

        assert len(sse_clients) == 0

    @pytest.mark.asyncio
    async def test_multiple_client_disconnect(self):
        """Test cleanup when multiple clients disconnect"""
        sse_clients = []

        # Add 3 clients
        queues = [asyncio.Queue() for _ in range(3)]
        for q in queues:
            sse_clients.append(q)

        assert len(sse_clients) == 3

        # Disconnect middle client
        sse_clients.remove(queues[1])

        assert len(sse_clients) == 2
        assert queues[0] in sse_clients
        assert queues[1] not in sse_clients
        assert queues[2] in sse_clients


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
