from rest_framework import serializers
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from devices.serializers import DeviceSerializer


User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Llama al método original para obtener el token
        token = super().get_token(user)
        token['user_id'] = user.id
        token['email'] = user.email
        token['nombre'] = user.nombre
        
        return token

class UserSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'nombre', 'numero', 'date_joined',
            'browser_latitude', 'browser_longitude', 'browser_last_seen',
            'image', 'password'
        )
        read_only_fields = (
            'id', 'date_joined', 
            'browser_latitude', 'browser_longitude', 'browser_last_seen'
        )
    
    def update(self, instance, validated_data):
        
        password = validated_data.pop('password', None)
        
        # Actualizamos el resto de campos (nombre, email, numero, imagen)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Si había contraseña nueva, la encriptamos y guardamos
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    """
    Tu RegisterSerializer (sin cambios, es perfecto).
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ('email', 'nombre', 'numero', 'password', 'password2')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class TrustedContactSerializer(serializers.ModelSerializer):
    """
    Tu TrustedContactSerializer (sin cambios, es perfecto).
    """
    class Meta:
        model = User
        fields = ('id', 'nombre', 'email', 'numero')


class TrustedContactWithDevicesSerializer(serializers.ModelSerializer):
    """
    Serializador que incluye los dispositivos de un contacto que son visibles
    para el usuario actual.
    """
    devices = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'nombre', 'email', 'numero', 'devices')
    
    def get_devices(self, obj):
        """
        Devuelve solo los dispositivos visibles para contactos.
        """
        visible_devices = obj.devices.filter(is_visible_to_contacts=True)
        return DeviceSerializer(visible_devices, many=True).data