import os
import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.endpoints import router as api_router
from backend.app.websocket.manager import manager

# Enable imports of app directories safely
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(
    title="ReelVault Backend Engine",
    description="Secure transit API and media extraction pipeline for instagram media assets.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include core router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root_ping():
    return {
        "status": "online",
        "service": "ReelVault Core Scraper FastAPI Microservice",
        "system": "Active Encrypted Transit"
    }

@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket, clientId: str = "anonymous"):
    """Active websocket path for real-time compilation progress logs streaming."""
    await manager.connect(clientId, websocket)
    try:
        while True:
            # Keep connection alive, listen for any client cancellation
            data = await websocket.receive_text()
            # Respond to ping to keep the socket fresh
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(clientId)
    except Exception as e:
        print(f"WS Exception triggered for {clientId}: {e}")
        manager.disconnect(clientId)
