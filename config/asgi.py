# config/asgi.py

import os
from django.core.asgi import get_asgi_application

# 1. Primero, se configura el entorno de Django y se obtiene la aplicación principal.
#    Esto inicializa Django completamente.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django_asgi_app = get_asgi_application()

# 2. AHORA, con Django ya cargado, importamos de forma segura los componentes de Channels.
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from tracking.token_auth_middleware import TokenAuthMiddlewareStack
from tracking.routing import websocket_urlpatterns


# 3. Finalmente, se construye el enrutador principal de la aplicación.
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
