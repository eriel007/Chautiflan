import pytest
from channels.testing import WebsocketCommunicator
from config.asgi import application
from django.contrib.auth.models import User
from chat.mongo import get_messages_collection
from asgiref.sync import sync_to_async


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_chat_consumer_sends_and_receives_message():
    # Crear usuario de prueba
    user = await sync_to_async(User.objects.create_user)(
        username="eriel", password="test123"
    )
    # Limpiar la sala
    collection = get_messages_collection()
    collection.delete_many({"room_name": "sala_test"})

    communicator = WebsocketCommunicator(application, "/ws/chat/sala_test/")
    communicator.scope["user"] = user  # <-- simulate authenticated user

    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to(
        {
            "receiver": "usuario2",
            "content": "¡Hola desde el test!",
        }
    )

    # Recibe el mensaje (saltando historial si lo hubiera)
    while True:
        response = await communicator.receive_json_from()
        if response["content"] == "¡Hola desde el test!":
            break

    assert response["sender"] == "eriel"
    assert response["receiver"] == "usuario2"
    assert response["content"] == "¡Hola desde el test!"

    await communicator.disconnect()
