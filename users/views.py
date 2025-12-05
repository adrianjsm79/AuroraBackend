from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
import base64
from .models import LegalDocument
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    RegisterSerializer, 
    UserSerializer, 
    TrustedContactSerializer,
    TrustedContactWithDevicesSerializer,
    MyTokenObtainPairSerializer 
)

User = get_user_model()

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Vista de Login que usa el serializador personalizado
    para incluir 'user_id' en el token.
    """
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user

class UpdateBrowserLocationView(APIView):
    """
    Nueva vista para que React pueda reportar
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

        user.browser_latitude = latitude
        user.browser_longitude = longitude
        user.browser_last_seen = timezone.now()
        user.save()
        
        # Devuelve el perfil del usuario actualizado
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

class TrustedByContactsListView(generics.ListAPIView):
    """
    Devuelve la lista de usuarios que han agregado al usuario actual
    como contacto de confianza (quiénes confían en mí), incluyendo
    sus dispositivos que son visibles para contactos.
    """
    serializer_class = TrustedContactWithDevicesSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        # Usamos el related_name 'trusted_by' definido en tu modelo User
        return self.request.user.trusted_by.all()


class GetLegalDocumentView(APIView):
    """
    Devuelve un documento legal codificado en Base64.
    Permiso: AllowAny (porque el usuario aún no se ha registrado).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, code):
        try:
            document = LegalDocument.objects.get(code=code)
            
            # 1. Convertir el HTML a bytes
            html_bytes = document.content_html.encode('utf-8')
            # 2. Codificar a Base64
            base64_bytes = base64.b64encode(html_bytes)
            # 3. Decodificar a string para enviarlo en JSON
            base64_string = base64_bytes.decode('utf-8')
            
            return Response({
                'code': document.code,
                'title': document.title,
                'content_base64': base64_string,
                'updated_at': document.last_updated
            }, status=status.HTTP_200_OK)
            
        except LegalDocument.DoesNotExist:
            return Response(
                {'error': 'Documento legal no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )