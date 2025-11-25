from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Device
from .serializers import DeviceSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite a los usuarios ver y registrar sus dispositivos.
    """
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Un usuario SOLO puede ver SUS propios dispositivos
        return Device.objects.filter(user=self.request.user)
    

    def create(self, request, *args, **kwargs):
        """
        Sobrescribe el método 'create' (POST) por completo.
        Esto nos permite implementar la lógica "Update or Create".
        """
        
        # 1. Validamos los datos que envía el móvil (name, device_identifier)
        #    (El serializador ya no falla por 'unique' gracias a tu corrección)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        device_identifier = validated_data.get('device_identifier')

        # 2. Lógica "Get, Create or Update"
        #    Busca un dispositivo por su ID único.
        device, created = Device.objects.update_or_create(
            device_identifier=device_identifier,
            defaults={
                'user': request.user, # Asigna/Reasigna al usuario actual
                'name': validated_data.get('name'),
                # (Opcional) Resetea el estado 'is_lost' al iniciar sesión
                'is_lost': False 
            }
        )
        
        # 3. Preparamos la respuesta JSON
        response_serializer = self.get_serializer(device)
        headers = self.get_success_headers(response_serializer.data)
        
        # 4. Devolvemos 201 si fue creado, 200 si fue actualizado
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        
        return Response(response_serializer.data, status=status_code, headers=headers)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def contacts_devices(self, request):
        """
        Obtiene los dispositivos de todos los contactos del usuario actual
        que están visibles y con los que el usuario tiene confianza mutua.
        """
        user = request.user
        
        # Obtener los contactos en los que el usuario confía (trustedContacts)
        trusted_contacts = user.trusted_contacts.all()
        
        # Obtener los dispositivos de esos contactos que son visibles
        contacts_devices = Device.objects.filter(
            user__in=trusted_contacts,
            is_visible_to_contacts=True
        )
        
        serializer = self.get_serializer(contacts_devices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_visibility(self, request, pk=None):
        """
        Actualiza la visibilidad de un dispositivo para los contactos.
        """
        device = self.get_object()
        
        # Verificar que el dispositivo pertenece al usuario actual
        if device.user != request.user:
            return Response(
                {'error': 'No tienes permiso para modificar este dispositivo'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        is_visible = request.data.get('is_visible_to_contacts')
        
        if is_visible is None:
            return Response(
                {'error': 'El campo is_visible_to_contacts es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        device.is_visible_to_contacts = is_visible
        device.save()
        
        serializer = self.get_serializer(device)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_lost_status(self, request, pk=None):
        """
        Actualiza el estado de perdido de un dispositivo.
        """
        device = self.get_object()
        
        # Verificar que el dispositivo pertenece al usuario actual
        if device.user != request.user:
            return Response(
                {'error': 'No tienes permiso para modificar este dispositivo'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        is_lost = request.data.get('is_lost')
        
        if is_lost is None:
            return Response(
                {'error': 'El campo is_lost es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        device.is_lost = is_lost
        device.save()
        
        serializer = self.get_serializer(device)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def perform_update(self, serializer):
        # 1. Guardar el cambio en la base de datos
        instance = serializer.save()
        
        # 2. Si el estado 'is_lost' cambió, notificar por WebSocket
        if 'is_lost' in serializer.validated_data:
            is_lost = serializer.validated_data['is_lost']
            
            channel_layer = get_channel_layer()
            # Enviamos el mensaje al grupo del usuario dueño del dispositivo
            async_to_sync(channel_layer.group_send)(
                f'user_{instance.user.id}',
                {
                    'type': 'location_message', # Reutilizamos tu handler existente
                    'command': 'update_status', # Nuevo comando
                    'device_id': instance.id,
                    'is_lost': is_lost
                }
            )