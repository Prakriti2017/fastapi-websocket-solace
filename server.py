from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uuid

app = FastAPI()
connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):
    await websocket.accept()
    client_id = str(uuid.uuid4())
    connected_clients.add((client_id,websocket))
    try:
        while True:
            data = await websocket.receive_text()
            for cli_id, client in connected_clients:
                if client_id != cli_id:
                    await client.send_text(data)
    except WebSocketDisconnect:
        print("connection closed")
        pass

    finally:
        connected_clients.remove((client_id,websocket))
