from rest_framework import generics, permissions
from .models import Location
from .serializers import LocationSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# --- VISTA OBSOLETA ---
# Tu 'UpdateLocationView' ya no es necesaria.
# El 'LocationConsumer' (WebSocket) es ahora el responsable
# de recibir actualizaciones y crear tanto el historial (Location)
# como de actualizar la última ubicación (Device).


class DeviceLocationHistoryView(generics.ListAPIView):
    """
    Vista de API para obtener el *historial completo* de ubicaciones
    de UN SOLO dispositivo.
    
    Se accede a través de la URL: /api/tracking/history/<device_id>/
    """
    serializer_class = LocationSerializer # <-- Este SÍ usa el LocationSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        user = self.request.user
        
        # 1. Obtener el ID del dispositivo desde la URL (ej. /api/tracking/history/5/)
        device_id = self.kwargs.get('device_id')
        if not device_id:
            return Location.objects.none() # No devolver nada si no hay ID
            
        # 2. Obtener la lista de usuarios permitidos (él mismo y sus contactos)
        #    Esto asegura que no puedas espiar el historial de un dispositivo
        #    que no te pertenece o que no es de un contacto de confianza.
        trusted_users = user.trusted_contacts.all()
        allowed_users = list(trusted_users) + [user]
        
        # 3. Devolver el historial SOLO SI el dispositivo solicitado
        #    pertenece al usuario o a uno de sus contactos.
        return Location.objects.filter(
            device_id=device_id,
            device__user__in=allowed_users
        ).order_by('-timestamp') # Ordenado por más reciente