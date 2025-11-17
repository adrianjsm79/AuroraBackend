# tracking/token_auth_middleware.py

from channels.db import database_sync_to_async

# No se necesita 'import jwt' ni 'settings' aquí

@database_sync_to_async
def get_user_from_token(token_key):
    """
    Obtiene un usuario a partir de un token de Django REST Framework.
    """
    # Importaciones diferidas para evitar 'AppRegistryNotReady'
    from rest_framework.authtoken.models import Token
    from django.contrib.auth.models import AnonymousUser

    try:
        # Busca el token por su 'key' en la base de datos
        token = Token.objects.select_related('user').get(key=token_key)
        # Devuelve el usuario asociado a ese token
        return token.user
    except Token.DoesNotExist:
        # Si el token no existe, el usuario es anónimo
        return AnonymousUser()

class TokenAuthMiddleware:
    """
    Middleware que toma un token de la cabecera 'Authorization'
    y autentica al usuario para la conexión WebSocket.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser

        headers = dict(scope.get('headers', []))
        auth_header = headers.get(b'authorization', b'').decode('utf-8')

        token = None
        # Verifica que la cabecera sea "Token <key>"
        if auth_header.startswith('Token '):
            token = auth_header.split(' ')[1]

        if token:
            # Llama a la función correcta para validar el token
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)