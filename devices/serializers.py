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
            'user',         # ID del usuario (necesario para la creación implícita)
            'user_email',   # Email (para mostrar en la API)
            'name', 
            'device_identifier', 
            'is_lost', 
            'latitude', 
            'longitude', 
            'accuracy',
            'last_seen',
            'created_at'
        ]
        
        # Oculta el campo 'user' al leer (ya mostramos 'user_email')
        # y hace que otros campos sean de solo lectura.
        read_only_fields = [
            'id', 
            'user_email', 
            'latitude', 
            'longitude', 
            'accuracy', 
            'last_seen', 
            'created_at'
        ]
        
        # El campo 'user' no debe ser editable por el cliente.
        # Se asignará automáticamente desde el usuario logueado.
        extra_kwargs = {
            'user': {'write_only': True, 'required': False},
            
            # Mi ViewSet (con update_or_create) se encargará de la lógica."
            'device_identifier': {
                'validators': [],  # Quitamos el validador 'unique'
            } 
        }