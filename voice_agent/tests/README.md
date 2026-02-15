# Live Transcription Tests

Unit and integration tests for the MedWing live speech-to-text transcription system.

## Test Coverage

### 1. `test_transcript_extraction.py`
Tests transcript extraction logic from VAPI webhook events.

**Coverage:**
- ✅ Extract from `speech-update` events with `status="stopped"`
- ✅ Handle both `assistant` and `user` roles
- ✅ Extract from `conversation-update` events
- ✅ Handle empty artifact.messages arrays
- ✅ Correct speaker label mapping (VAPI Agent / User)
- ✅ Transcript entry structure validation

### 2. `test_sse_endpoint.py`
Tests Server-Sent Events (SSE) endpoint functionality.

**Coverage:**
- ✅ Broadcast to single SSE client
- ✅ Broadcast to multiple concurrent clients
- ✅ Transcript history storage (circular buffer with deque)
- ✅ SSE message format compliance
- ✅ `/transcript-history` endpoint response format
- ✅ Client disconnect cleanup
- ✅ Multiple client disconnect handling

### 3. `test_integration.py`
End-to-end integration tests for complete transcription flow.

**Coverage:**
- ✅ Full flow: Webhook → Extract → Store → Broadcast
- ✅ `speech-update` event flow
- ✅ `conversation-update` event flow
- ✅ Multiple speakers in sequence
- ✅ Concurrent SSE clients
- ✅ Zoom notification format
- ✅ Error handling (missing artifact, empty conversation)
- ✅ System message filtering

## Running Tests

### Install Dependencies
```bash
pip install pytest pytest-asyncio
```

### Run All Tests
```bash
# From voice_agent directory
pytest tests/ -v

# Or from project root
cd voice_agent && pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_transcript_extraction.py -v
pytest tests/test_sse_endpoint.py -v
pytest tests/test_integration.py -v
```

### Run Specific Test
```bash
pytest tests/test_integration.py::TestEndToEndTranscription::test_full_speech_update_flow -v
```

## Test Output Example

```
tests/test_transcript_extraction.py::TestTranscriptExtraction::test_speech_update_with_stopped_status PASSED
tests/test_transcript_extraction.py::TestTranscriptExtraction::test_speech_update_user_role PASSED
tests/test_sse_endpoint.py::TestSSEEndpoint::test_broadcast_to_multiple_clients PASSED
tests/test_integration.py::TestEndToEndTranscription::test_full_speech_update_flow PASSED

========================= 25 passed in 0.45s =========================
```

## Architecture Tested

```
VAPI Webhook
     ↓
webhook_server.py
     ↓
[Extract Transcript]
     ↓
live_transcript (deque)
     ↓
[Broadcast to SSE]
     ↓
Multiple Frontend Clients
```

## Key Test Scenarios

1. **Real VAPI Event Structure**: Tests use actual event structures observed from live calls
2. **Concurrent Clients**: Ensures multiple browser tabs can receive transcripts simultaneously
3. **Memory Management**: Validates circular buffer (deque) prevents memory leaks
4. **Error Resilience**: Tests graceful handling of malformed/missing data
5. **Speaker Identification**: Verifies correct User vs VAPI Agent labeling

## Test Data

Tests use realistic data from actual MedWing calls:
- Order confirmations
- User responses ("Yes. Correct.", "Thank you.")
- Full dispatch messages with tracking codes
- Multi-turn conversations

## Integration Points Tested

- ✅ Terminal logging (🎙️ emoji format)
- ✅ Frontend SSE endpoint (`/live-transcript`)
- ✅ Transcript history API (`/transcript-history`)
- ✅ Zoom notification formatting
