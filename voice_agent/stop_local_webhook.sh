#!/usr/bin/env bash
# Stop the local webhook server so Vapi sends webhooks only to Render.
# Then the Vercel dashboard will show the live transcript.
# Usage: ./stop_local_webhook.sh   or   bash stop_local_webhook.sh

PORT="${SERVER_PORT:-8000}"
if command -v lsof &>/dev/null; then
  PID=$(lsof -ti:"$PORT" 2>/dev/null)
  if [ -n "$PID" ]; then
    echo "Stopping process on port $PORT (PID $PID)..."
    kill "$PID" 2>/dev/null && echo "Done. Webhooks will now go to Render only (if Vapi Server URL is set to Render)." || echo "Try: kill -9 $PID"
  else
    echo "No process found on port $PORT. Local webhook server is not running."
  fi
else
  echo "lsof not found. Stop the terminal where you ran: python webhook_server.py (Ctrl+C)"
fi
