from django.urls import path
from .views import UpdateLocationView, GetLocationsView

urlpatterns = [
    path('update/', UpdateLocationView.as_view(), name='update_location'),
    path('locations/', GetLocationsView.as_view(), name='get_locations'),
]