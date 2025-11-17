# tracking/token_auth_middleware.py

import jwt
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

@database_sync_to_async
def get_user_from_token(token_str):
    User = get_user_model() 
    try:
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=["HS256"]) 
        user_id = payload.get('user_id') 
        if user_id:
            return User.objects.get(id=user_id)
        return AnonymousUser()
    except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
        return AnonymousUser()

class TokenAuthMiddleware:
    """
    Middleware que toma un token de la cabecera 'Authorization'
    y autentica al usuario.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Obtiene las cabeceras de la conexión
        headers = dict(scope.get('headers', []))
        
        # Busca la cabecera 'authorization'
        auth_header = headers.get(b'authorization', b'').decode('utf-8')
        
        token = None
        # Si la cabecera existe y empieza con "Token "
        if auth_header.startswith('Token '):
            # Extrae el token
            token = auth_header.split(' ')[1]

        if token:
            # Si se encontró un token, obtén el usuario y ponlo en el 'scope'
            scope['user'] = await get_user_from_token(token)
        else:
            # Si no, el usuario es Anónimo
            scope['user'] = AnonymousUser()

        # Continúa con el siguiente middleware o el consumer
        return await self.inner(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)