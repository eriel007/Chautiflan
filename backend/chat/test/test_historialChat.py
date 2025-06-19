import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from chat.mongo import get_messages_collection
from config.asgi import application

User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_chat_consumer_sends_history_on_connect():
    # Crear usuario de prueba
    user = await sync_to_async(User.objects.create_user)(
        username="historial_user", password="test123"
    )

    room_name = "sala_historial"
    collection = get_messages_collection()
    collection.delete_many({"room_name": room_name})

    # Insertar mensajes de historial
    await sync_to_async(collection.insert_many)(
        [
            {
                "sender": "historial_user",
                "receiver": "usuario_destino",
                "content": f"Mensaje número {i}",
                "timestamp": "2024-06-01T12:00:00Z",
                "room_name": room_name,
            }
            for i in range(3)
        ]
    )

    # Conexión WebSocket
    communicator = WebsocketCommunicator(application, f"/ws/chat/{room_name}/")
    communicator.scope["user"] = user

    connected, _ = await communicator.connect()
    assert connected

    # Recibir los 3 mensajes de historial
    mensajes_recibidos = []
    for _ in range(3):
        respuesta = await communicator.receive_json_from()
        mensajes_recibidos.append(respuesta["content"])

    assert mensajes_recibidos == [
        "Mensaje número 2",
        "Mensaje número 1",
        "Mensaje número 0",
    ]

    await communicator.disconnect()
