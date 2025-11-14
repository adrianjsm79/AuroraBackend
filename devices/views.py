from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Device
from .serializers import DeviceSerializer # (El serializer que ya creamos)

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