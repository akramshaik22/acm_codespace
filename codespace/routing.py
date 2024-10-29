# import os

# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter, get_default_application
# from channels.security.websocket import AllowedHostsOriginValidator
# from django.core.asgi import get_asgi_application

# from app.routing import websocket_urlpatterns

# django_asgi_app = get_asgi_application()

# application = ProtocolTypeRouter(
#     {
#         "websocket": URLRouter(websocket_urlpatterns),
#     }
# )

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from codespace.consumer import CodeWarConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codespace.settings')

application = ProtocolTypeRouter({
    'websocket': URLRouter(
        [
            path('ws/game/', CodeWarConsumer),
        ]
    ),
})