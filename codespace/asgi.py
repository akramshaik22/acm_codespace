"""
ASGI config for codespace project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codespace.settings')

application = get_asgi_application()

# import os

# from django.core.asgi import get_asgi_application
# from django.core.wsgi import get_wsgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter#, get_default_application
# from django.urls import path
# from codespace.consumer import CodeWarConsumer

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codespace.settings')

# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': URLRouter(
#         [
#             path('ws/game/', CodeWarConsumer),
#         ]
#     ),
# })