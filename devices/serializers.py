from rest_framework import serializers
from .models import Device

class DeviceSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

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
        
        read_only_fields = [
            'id', 
            'user',
            'user_email',
            'user_image',
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
