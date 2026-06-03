from typing import Dict, List
import json
import requests
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # We don't need active connections locally anymore since Node manages WS!
        self.active_connections = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_progress(self, client_id: str, status: str, progress: float, stage: str, data: dict = None):
        print(f"[FastAPI WS Proxy] Local progress update: {client_id} -> {status} ({progress}%)")
        
        # 1. First, push to the direct Python websockets if any are locally active
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                payload = {
                    "type": "progress",
                    "status": status,
                    "progress": progress,
                    "stage": stage,
                }
                if data:
                    payload["data"] = data
                await websocket.send_text(json.dumps(payload))
            except Exception as e:
                print(f"[FastAPI WS Proxy] Direct python WS error: {e}")

        # 2. Push to the main Node.js WS transit gateway
        try:
            payload = {
                "clientId": client_id,
                "status": status,
                "progress": progress,
                "stage": stage,
            }
            if data:
                payload["data"] = data
            
            # Send HTTP POST to the local Express gateway on port 3000
            requests.post("http://127.0.0.1:3000/api/progress-update", json=payload, timeout=2)
        except Exception as e:
            print(f"[FastAPI WS Proxy] Node gateway notification failed: {e}")

manager = ConnectionManager()

