from django.urls import re_path
from api import consumers
from django.urls import path
from api.consumers import LocationConsumer

websocket_urlpatterns = [
    path('ws/location/', LocationConsumer.as_asgi()),  # تحديد WebSocket
]