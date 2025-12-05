from rest_framework import serializers
from .models import Device

class DeviceSerializer(serializers.ModelSerializer):
    # 1. Definimos los campos que vienen del usuario relacionado
    user_email = serializers.ReadOnlyField(source='user.email')
    
    # 2. Para la imagen, usamos SerializerMethodField.
    # IMPORTANTE: Este campo ya es ReadOnly por defecto.
    user_image = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = [
            'id', 
            'user',
            'user_email',    
            'user_image', 
            'name', 
            'device_identifier', 
            'is_lost', 
            'latitude', 
            'longitude', 
            'accuracy',
            'last_seen',
            'created_at'
        ]
        
        # 3. CORRECCIÓN: Quitamos 'user_image' de esta lista.
        # Solo dejamos los campos que SÍ existen en el modelo Device.
        read_only_fields = [
            'id', 
            'user',
            'user_email', 
            'latitude', 
            'longitude', 
            'accuracy', 
            'last_seen', 
            'created_at'
        ]
        
        extra_kwargs = {
            'device_identifier': {
                'validators': [], 
            }
        }

    # 3. Método para obtener la URL de la imagen
    def get_user_image(self, obj):
        try:
            if obj.user.image:
                return obj.user.image.url
        except:
            pass
        return None
