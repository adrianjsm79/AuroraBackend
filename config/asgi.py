import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# 1. Configura el entorno de Django PRIMERO
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 2. LLAMA a get_asgi_application() INMEDIATAMENTE.
#    Esta línea es la que carga la configuración de Django
#    y prepara el "App Registry".
django_asgi_app = get_asgi_application()

# 3. AHORA es seguro importar tus módulos de Channels
#    que dependen de Django (como tu middleware y consumers).
from tracking.token_auth_middleware import TokenAuthMiddlewareStack 
from tracking.routing import websocket_urlpatterns

# 4. Construye tu aplicación
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})