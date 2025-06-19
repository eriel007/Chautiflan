import json
from datetime import datetime, timezone  # no olvides importar esto si no lo tienes
from channels.generic.websocket import AsyncWebsocketConsumer
from .mongo import get_messages_collection, get_messages_for_room


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user is None or not user.is_authenticated:
            if not self.scope.get("test_user"):
                # Si no es un test, rechaza la conexión
                await self.close()
                return

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # historial para enviar de mongoDB y enviarlo
        message = get_messages_for_room(self.room_name)
        for message in reversed(message):
            message["_id"] = str(message["_id"])
            await self.send(text_data=json.dumps(message))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        sender = self.scope["user"].username
        receiver = data["receiver"]
        content = data["content"]
        timestamp = datetime.now(
            timezone.utc
        ).isoformat()  # Asegúrate de importar timezone si no lo tienes

        message = {
            "sender": sender,
            "receiver": receiver,
            "content": content,
            "timestamp": timestamp,
            "room_name": self.room_name,
        }

        # 💡 CORRECTO: obtener colección y usar insert_one
        collection = get_messages_collection()
        result = collection.insert_one(message)
        message["_id"] = str(result.inserted_id)

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))
