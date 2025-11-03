import jwt
from channels.db import database_sync_to_async
from django.conf import settings

@database_sync_to_async
def get_user_from_token(token_str):
    # --- Importaciones movidas aquí dentro ---
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import AnonymousUser
    
    User = get_user_model() # Se llama a la función aquí dentro
    
    try:
        # Asegúrate de que el algoritmo coincida
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=["HS256"]) 
        
        # Revisa que 'user_id' sea el nombre correcto en tu token
        user_id = payload.get('user_id') 
        
        if user_id:
            return User.objects.get(id=user_id)
        return AnonymousUser()
        
    except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
        return AnonymousUser()

class TokenAuthMiddleware:
    """
    Middleware de autenticación por Token para WebSockets.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # --- Importación movida aquí dentro ---
        from django.contrib.auth.models import AnonymousUser 
        
        query_string = scope.get('query_string', b"").decode("utf-8")
        query_params = dict(param.split("=") for param in query_string.split("&") if "=" in param)
        token = query_params.get('token')

        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)