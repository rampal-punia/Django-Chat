from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/image_chat/(?P<conversation_id>[^/]+)?/$', consumers.ImageChatConsumer.as_asgi()),
]
