from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Device
from .serializers import DeviceSerializer

# --- PERMISO PERSONALIZADO ---
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permite leer a cualquiera (que esté en el queryset),
    pero solo permite escribir/borrar al dueño del dispositivo.
    """
    def has_object_permission(self, request, view, obj):
        # Si es GET, HEAD o OPTIONS, permitimos acceso (Read-Only)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Si es DELETE, PATCH, PUT, solo permitimos si es el dueño
        return obj.user == request.user


class DeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a los usuarios ver, registrar y gestionar sus dispositivos.
    """
    serializer_class = DeviceSerializer
    # Añadimos nuestro permiso personalizado además de IsAuthenticated
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Devuelve:
        1. Mis dispositivos.
        2. Dispositivos de usuarios que me han añadido a SU lista de confianza.
        """
        user = self.request.user
        
        # A. Usuarios que confían en mí
        users_who_trust_me = user.trusted_by.all()
        
        # B. Filtro combinado
        return Device.objects.filter(
            Q(user=user) | Q(user__in=users_who_trust_me)
        ).distinct()

    def create(self, request, *args, **kwargs):
        """
        Sobrescribe el método 'create' (POST) para implementar "Update or Create".
        """
        # 1. Validamos los datos
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        device_identifier = validated_data.get('device_identifier')

        # 2. Lógica "Get, Create or Update"
        device, created = Device.objects.update_or_create(
            device_identifier=device_identifier,
            defaults={
                'user': request.user, # Asigna/Reasigna al usuario actual
                'name': validated_data.get('name'),
                # (Opcional) Podrías resetear 'is_lost' aquí si quisieras
                # 'is_lost': False 
            }
        )
        
        # 3. Respuesta
        response_serializer = self.get_serializer(device)
        headers = self.get_success_headers(response_serializer.data)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        
        return Response(response_serializer.data, status=status_code, headers=headers)

    def perform_update(self, serializer):
        """
        Se ejecuta en PATCH/PUT estándar (/api/devices/{id}/).
        Aquí detectamos si se marcó como perdido para enviar la alerta WebSocket.
        """
        # 1. Guardar el cambio en la base de datos
        instance = serializer.save()
        
        # 2. Si el estado 'is_lost' cambió (o se envió en la petición), notificar
        if 'is_lost' in serializer.validated_data:
            is_lost = serializer.validated_data['is_lost']
            self._send_lost_status_notification(instance, is_lost)

    def _send_lost_status_notification(self, device_instance, is_lost):
        """
        Método auxiliar para enviar la notificación por WebSocket.
        """
        channel_layer = get_channel_layer()
        # Enviamos el mensaje al grupo del usuario dueño del dispositivo
        async_to_sync(channel_layer.group_send)(
            f'user_{device_instance.user.id}',
            {
                'type': 'location_message', # Llama a la función location_message del consumer
                'command': 'update_status', # Nuevo comando
                'device_id': device_instance.id,
                'is_lost': is_lost
            }
        )

    # --- ACCIONES PERSONALIZADAS (Tus métodos existentes) ---

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def contacts_devices(self, request):
        """
        Obtiene los dispositivos de todos los contactos del usuario actual
        (versión filtrada específica, aunque get_queryset ya hace algo similar).
        """
        user = request.user
        trusted_contacts = user.trusted_contacts.all()
        
        # Aquí asumo que tienes un campo 'is_visible_to_contacts' en tu modelo.
        # Si no lo tienes en el modelo Device que definimos antes, esto dará error.
        # Por seguridad, filtro solo por usuario si el campo no existe, o lo comento.
        contacts_devices = Device.objects.filter(
            user__in=trusted_contacts
            # , is_visible_to_contacts=True  <-- Descomenta si agregaste este campo al modelo
        )
        
        serializer = self.get_serializer(contacts_devices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_visibility(self, request, pk=None):
        """
        Actualiza la visibilidad (requiere campo en modelo).
        """
        device = self.get_object()
        if device.user != request.user:
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        
        is_visible = request.data.get('is_visible_to_contacts')
        if is_visible is None:
            return Response({'error': 'Campo requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        # device.is_visible_to_contacts = is_visible <-- Asegúrate que el campo exista
        # device.save()
        
        serializer = self.get_serializer(device)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_lost_status(self, request, pk=None):
        """
        Endpoint específico para actualizar solo el estado de perdido.
        """
        device = self.get_object()
        
        if device.user != request.user:
            return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
        
        is_lost = request.data.get('is_lost')
        if is_lost is None:
            return Response({'error': 'Campo requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        device.is_lost = is_lost
        device.save()
        
        # --- IMPORTANTE: Enviar notificación también aquí ---
        self._send_lost_status_notification(device, is_lost)
        # --------------------------------------------------
        
        serializer = self.get_serializer(device)
        return Response(serializer.data)
