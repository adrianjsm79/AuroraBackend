from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone  # <-- 1. Importar timezone
from .serializers import RegisterSerializer, UserSerializer, TrustedContactSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    # --- (Sin cambios) ---
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveAPIView):
    # --- (Sin cambios) ---
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user

# --- 2. VISTA NUEVA AÑADIDA ---
class UpdateBrowserLocationView(APIView):
    """
    Nueva vista para que la app web (React) pueda reportar
    la ubicación del navegador del usuario.
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def patch(self, request, *args, **kwargs):
        user = request.user
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if latitude is None or longitude is None:
            return Response(
                {'error': 'Latitud y longitud son requeridas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Actualiza los campos en el modelo User
        user.browser_latitude = latitude
        user.browser_longitude = longitude
        user.browser_last_seen = timezone.now() # <-- Usamos timezone.now()
        user.save()
        
        # Devuelve el perfil del usuario actualizado
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- VISTAS DE CONTACTOS (Sin cambios) ---

class TrustedContactsListView(generics.ListAPIView):
    serializer_class = TrustedContactSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return self.request.user.trusted_contacts.all()


class AddTrustedContactView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        numero = request.data.get('numero')
        
        if not numero:
            return Response(
                {'error': 'El número es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            contact = User.objects.get(numero=numero)
            
            if contact == request.user:
                return Response(
                    {'error': 'No puedes agregarte a ti mismo'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if contact in request.user.trusted_contacts.all():
                return Response(
                    {'error': 'Este contacto ya está en tu lista'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            request.user.trusted_contacts.add(contact)
            
            serializer = TrustedContactSerializer(contact)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'No se encontró un usuario con ese número'},
                status=status.HTTP_404_NOT_FOUND
            )


class RemoveTrustedContactView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def delete(self, request, contact_id):
        try:
            contact = User.objects.get(id=contact_id)
            request.user.trusted_contacts.remove(contact)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(
                {'error': 'Contacto no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )