from django.urls import path
from .views import MessageView

urlpatterns = [
    path("messages/", MessageView.as_view(), name="messages"),
]
