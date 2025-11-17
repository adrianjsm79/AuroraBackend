import jwt
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

# --- 1. IMPORTACIONES CORREGIDAS ---
from rest_framework_simplejwt.tokens import AccessToken
# La excepción 'TokenError' es la base para todos los errores (incluido InvalidToken)
from rest_framework_simplejwt.exceptions import TokenError 

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_str):
    """
    Decodifica el token usando la librería 'simple-jwt' 
    y obtiene el usuario.
    """
    try:
        token = AccessToken(token_str)
        user_id = token.get('user_id')
        
        if user_id:
            return User.objects.get(id=user_id)
            
    # --- 2. EXCEPCIÓN CORREGIDA ---
    # Capturamos 'TokenError' (que incluye 'InvalidToken', 'ExpiredSignatureError', etc.)
    # y 'User.DoesNotExist' (si el usuario fue borrado).
    except (TokenError, User.DoesNotExist):
        return AnonymousUser()
    except Exception as e:
        print(f"Error inesperado en middleware de token: {e}")
        return AnonymousUser()

    return AnonymousUser()

class TokenAuthMiddleware:
    """
    Middleware de autenticación por Token para WebSockets.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        
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