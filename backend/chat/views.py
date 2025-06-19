from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .mongo import messages_collection
from bson import ObjectId


class MessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sender = request.user.username
        receiver = request.data.get("receiver")
        content = request.data.get("content")

        message = {
            "sender": sender,
            "receiver": receiver,
            "content": content,
            "timestamp": request.data.get("timestamp") or None,
        }

        result = messages_collection.insert_one(message)
        message["_id"] = str(result.inserted_id)
        return Response(message)

    def get(self, request):
        sender = request.user.username
        receiver = request.query_params.get("receiver")

        messages = list(
            messages_collection.find(
                {
                    "$or": [
                        {"sender": sender, "receiver": receiver},
                        {"sender": receiver, "receiver": sender},
                    ]
                }
            ).sort("timestamp", -1)
        )

        for msg in messages:
            msg["_id"] = str(msg["_id"])

        return Response(messages)
