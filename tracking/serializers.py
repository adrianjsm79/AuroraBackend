from rest_framework import serializers
from .models import Location
from devices.serializers import DeviceSerializer  # <-- 1. Importa el nuevo DeviceSerializer

class LocationSerializer(serializers.ModelSerializer):
    """
    Serializador para el *historial* de ubicaciones.
    Ahora está enlazado a un Dispositivo, no a un Usuario.
    """
    
    # 2. Enlaza con el DeviceSerializer para mostrar info del dispositivo
    device = DeviceSerializer(read_only=True)
    
    class Meta:
        model = Location
        # 3. Actualiza los campos para usar 'device' en lugar de 'user'
        fields = ('id', 'device', 'latitude', 'longitude', 'accuracy', 'timestamp')
        read_only_fields = ('id', 'timestamp', 'device')
    
