from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketClose
import uuid,asyncio
import concurrent
import time
from solace.messaging.messaging_service import MessagingService, RetryStrategy
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.resources.topic import Topic
from solace.messaging.receiver.message_receiver import MessageHandler, InboundMessage

broker_props = {
    "solace.messaging.transport.host": "tcp://192.168.0.165:55555",
    "solace.messaging.service.vpn-name": "default",
    "solace.messaging.authentication.scheme.basic.username":"admin",
    "solace.messaging.authentication.scheme.basic.password":"admin"
}

messaging_service = MessagingService.builder().from_properties(broker_props)\
                    .with_reconnection_retry_strategy(RetryStrategy.parametrized_retry(20,3))\
                    .build()

messaging_service.connect()
topic_receive = TopicSubscription.of("chats")
topic_publish = Topic.of("chats")
  
direct_publisher = messaging_service.create_direct_message_publisher_builder().build()
direct_receiver= messaging_service.create_direct_message_receiver_builder().with_subscriptions([topic_receive]).build()

direct_receiver.start()

direct_publisher.start()

connected_clients = {}

app = FastAPI()

@app.websocket("/")
async def websocket_endpoint(websocket:WebSocket):
    await websocket.accept()

    client_id = str(uuid.uuid4())

    connected_clients[client_id] = websocket

    def run_solace():
        handler = MessageHandlerImpl(connected_clients)
        while True:
            direct_receiver.receive_async(handler)
            time.sleep(0.5)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    _future = asyncio.get_event_loop().run_in_executor(executor, run_solace)

    try:
        while True:
            data = await websocket.receive_text()
            message = messaging_service.message_builder().with_property("client_id", client_id).build(data)
            direct_publisher.publish(destination=topic_publish, message=message)

    except WebSocketClose:
        print("connection closed")
        pass

    finally:
        del connected_clients[client_id]

class MessageHandlerImpl(MessageHandler):
    def __init__(self, connected_clients) -> None:
        self.connected_clients = connected_clients
        self.loop = asyncio.new_event_loop()

    def on_message(self, message: InboundMessage):
        payload = message.get_payload_as_string() if message.get_payload_as_string() !=None else message.get_payload_as_bytes()
        if isinstance(payload,bytearray):
            payload = payload.decode()
        
        for cli_id,client in self.connected_clients.items():
            if  cli_id!= message.get_property('client_id'):
                self.loop.run_until_complete(client.send_text(payload))  


