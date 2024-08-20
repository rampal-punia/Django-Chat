# # apps/audio_interface/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/audio/(?P<conversation_id>[^/]+)?/$', consumers.AudioConsumer.as_asgi()),
]
