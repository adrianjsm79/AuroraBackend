import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.security.websocket import AllowedHostsOriginValidator # <-- YA NO LO NECESITAMOS

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from tracking.token_auth_middleware import TokenAuthMiddlewareStack 
from tracking.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    
    # --- VERSIÓN CORREGIDA ---
    # Quitamos el 'AllowedHostsOriginValidator' y dejamos que
    # el 'TokenAuthMiddlewareStack' maneje la seguridad.
    "websocket": TokenAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})