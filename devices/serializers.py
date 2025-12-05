from rest_framework import serializers
from .models import Device

class DeviceSerializer(serializers.ModelSerializer):
    """
    Serializador para crear, listar y ver detalles de un Dispositivo.
    """
    
    # Muestra el email del usuario en lugar de solo su ID (solo lectura)
    user_email = serializers.EmailField(source='user.email', read_only=True)

   class Meta:
        model = Device
        fields = [
            'id', 
            'user',          # Ahora sí se enviará
            'user_email',    
            'name', 
            'device_identifier', 
            'is_lost', 
            'latitude', 
            'longitude', 
            'accuracy',
            'last_seen',
            'created_at'
        ]
        
        read_only_fields = [
            'id', 
            'user',          # <--- MOVEMOS 'user' AQUÍ
            'user_email', 
            'latitude', 
            'longitude', 
            'accuracy', 
            'last_seen', 
            'created_at'
        ]
        
        extra_kwargs = {
            # Eliminamos 'user' de aquí porque ya está en read_only_fields
            
            'device_identifier': {
                'validators': [], 
            }
        }
