from django.urls import path
from .views import DeviceLocationHistoryView # <-- 1. Importa la vista correcta

urlpatterns = [
    path('history/<int:device_id>/', DeviceLocationHistoryView.as_view(), name='get_location_history'),
]