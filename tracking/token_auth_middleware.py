import jwt
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_str):
    """
    Decodifica el token JWT y obtiene el usuario.
    """
    try:
        # Asegúrate de que el algoritmo coincida con tu config de simple_jwt
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=["HS256"])
        
        # CAMBIA 'user_id' si tu token usa un nombre diferente (ej. 'id')
        user_id = payload.get('user_id')
        
        if user_id:
            return User.objects.get(id=user_id)
        return AnonymousUser()
        
    except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
        # Si el token es inválido o el usuario no existe
        return AnonymousUser()

class TokenAuthMiddleware:
    """
    Middleware de autenticación por Token para WebSockets.
    Lee un token JWT de la query string (?token=...)
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Obtener el token de la query string
        query_string = scope.get('query_string', b"").decode("utf-8")
        query_params = dict(param.split("=") for param in query_string.split("&") if "=" in param)
        token = query_params.get('token')

        if token:
            # Si hay token, intenta autenticar al usuario
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)

# Helper para envolverlo fácilmente en asgi.py
def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)