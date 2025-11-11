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

    def perform_create(self, serializer):
        # Esta es la lógica clave para "Registrar si no existe"
        
        # Obtenemos el ID único del dispositivo desde los datos validados
        device_identifier = serializer.validated_data.get('device_identifier')
        
        # Usamos update_or_create para manejar todos los casos
        # 1. Si no existe: Lo crea.
        # 2. Si ya existe: Actualiza el 'user' y el 'name'.
        device, created = Device.objects.update_or_create(
            device_identifier=device_identifier,
            defaults={
                'user': self.request.user,
                'name': serializer.validated_data.get('name')
                # (is_lost se pondrá a False por default)
            }
        )
        
        # Devolvemos los datos del dispositivo (ya sea nuevo o actualizado)
        # Usamos el serializador para devolver el objeto completo
        serializer = self.get_serializer(device)
        
        # Devolvemos 201 si fue creado, 200 si fue actualizado
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        
        # Sobreescribimos la respuesta estándar
        # Nota: Estamos devolviendo una respuesta aquí, lo cual es un
        # pequeño truco para evitar que perform_create intente guardar dos veces.
        # Una forma más limpia es mover esta lógica al método 'create'.
        
        # --- Lógica de 'create' mejorada (reemplazando perform_create) ---
        pass # Borra 'perform_create' y usa el método 'create' de abajo

    def create(self, request, *args, **kwargs):
        # Validamos los datos que envía el móvil (name, device_identifier)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        device_identifier = validated_data.get('device_identifier')

        # Lógica "Get, Create or Update"
        device, created = Device.objects.update_or_create(
            device_identifier=device_identifier,
            defaults={
                'user': request.user,
                'name': validated_data.get('name'),
                'is_lost': False 
            }
        )
        
        # Preparamos la respuesta JSON
        response_serializer = self.get_serializer(device)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        
        return Response(response_serializer.data, status=status_code)