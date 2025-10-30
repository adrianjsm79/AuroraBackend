from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Location
from .serializers import LocationSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UpdateLocationView(generics.CreateAPIView):
    serializer_class = LocationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class GetLocationsView(generics.ListAPIView):
    serializer_class = LocationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        user = self.request.user
        
        # Obtener IDs de contactos de confianza
        trusted_ids = list(user.trusted_contacts.values_list('id', flat=True))
        trusted_ids.append(user.id)  # Incluir al usuario actual
        
        # Obtener la última ubicación de cada usuario
        locations = []
        for user_id in trusted_ids:
            latest_location = Location.objects.filter(user_id=user_id).first()
            if latest_location:
                locations.append(latest_location)
        
        return locations