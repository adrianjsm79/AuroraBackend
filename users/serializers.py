from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializador actualizado para mostrar la información del usuario,
    incluyendo la última ubicación de su navegador.
    """
    class Meta:
        model = User
        fields = (
            'id', 'email', 'nombre', 'numero', 'date_joined',
            # --- CAMPOS NUEVOS AÑADIDOS ---
            'browser_latitude', 'browser_longitude', 'browser_last_seen'
        )
        read_only_fields = (
            'id', 'date_joined', 
            'browser_latitude', 'browser_longitude', 'browser_last_seen'
        )


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