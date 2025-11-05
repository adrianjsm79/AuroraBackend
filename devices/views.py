from rest_framework import viewsets, permissions
from .models import Device
from .serializers import DeviceSerializer
from django.db.models import Q

class DeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a los usuarios:
    1. Registrar (POST) nuevos dispositivos.
    2. Ver (GET) los dispositivos que pueden rastrear.
    3. Editar (PATCH) o eliminar (DELETE) sus propios dispositivos.
    """
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Esta es la lógica clave para tu mapa web.
        Devuelve los dispositivos que pertenecen al usuario actual
        Y los dispositivos que pertenecen a sus contactos de confianza.
        """
        user = self.request.user
        
        # 1. Obtener la lista de usuarios en los que el usuario confía
        trusted_users = user.trusted_contacts.all()
        
        # 2. Crear una consulta que traiga:
        #    - Dispositivos que pertenecen AL USUARIO ACTUAL (user=user)
        #    - O dispositivos que pertenecen A SUS CONTACTOS (user__in=trusted_users)
        queryset = Device.objects.filter(
            Q(user=user) | Q(user__in=trusted_users)
        )
        
        # Devuelve los dispositivos (el serializador mostrará sus últimas ubicaciones)
        return queryset.distinct()

    def perform_create(self, serializer):
        """
        Al registrar (POST) un nuevo dispositivo, asigna automáticamente
        al usuario logueado como el propietario.
        """
        serializer.save(user=self.request.user)