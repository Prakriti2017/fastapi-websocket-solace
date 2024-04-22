from fastapi import FastAPI, WebSocket
from starlette import status
import uuid

app = FastAPI()
connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):
    await websocket.accept()
    client_id = str(uuid.uuid4())
    connected_clients.add((client_id,websocket))
    while True:
        for cli_id,client in connected_clients:
            data = websocket.receive_text()
            if client_id != cli_id:
                await client.send_text(data)
