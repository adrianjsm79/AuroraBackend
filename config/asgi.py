import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# 1. IMPORTA TU MIDDLEWARE DE TOKEN
from tracking.token_auth_middleware import TokenAuthMiddlewareStack 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

# Importa tus rutas de websocket DESPUÉS de setdefault
from tracking.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # El tráfico HTTP normal va a Django
    "http": django_asgi_app,
    
    # El tráfico WebSocket va a Channels
    "websocket": AllowedHostsOriginValidator(
        # 2. USA TU MIDDLEWARE
        # TokenAuthMiddlewareStack se encarga de la autenticación
        TokenAuthMiddlewareStack(
            # URLRouter dirige a tu LocationConsumer
            URLRouter(websocket_urlpatterns)
        )
    ),
})