from rest_framework import serializers
from .models import Location
from users.serializers import UserSerializer

class LocationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Location
        fields = ('id', 'user', 'latitude', 'longitude', 'accuracy', 'timestamp')
        read_only_fields = ('id', 'timestamp')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)