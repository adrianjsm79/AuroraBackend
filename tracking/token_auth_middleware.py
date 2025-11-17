# tracking/token_auth_middleware.py

import jwt
from channels.db import database_sync_to_async
from django.conf import settings

# ¡Las importaciones de Django se han movido de aquí!

@database_sync_to_async
def get_user_from_token(token_str):
    # Las importaciones se hacen aquí, cuando la función es llamada
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import AnonymousUser

    User = get_user_model()
    try:
        # Tu lógica de JWT parece estar bien, así que la mantenemos
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get('user_id')
        if user_id:
            return User.objects.get(id=user_id)
        return AnonymousUser()
    except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Importamos AnonymousUser aquí también
        from django.contrib.auth.models import AnonymousUser

        headers = dict(scope.get('headers', []))
        auth_header = headers.get(b'authorization', b'').decode('utf-8')

        token = None
        if auth_header.startswith('Token '):
            token = auth_header.split(' ')[1]

        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)
