from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, 
    ProfileView, 
    TrustedContactsListView,
    AddTrustedContactView, 
    RemoveTrustedContactView,
    UpdateBrowserLocationView  # <-- 1. Importa la nueva vista
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # --- 2. AÑADE ESTA NUEVA RUTA ---
    # La ruta para que la app web actualice la ubicación del navegador
    path('profile/update-browser-location/', UpdateBrowserLocationView.as_view(), name='update_browser_location'),
    
    # --- Rutas de Contactos (ya estaban correctas) ---
    path('trusted-contacts/', TrustedContactsListView.as_view(), name='trusted_contacts'),
    path('trusted-contacts/add/', AddTrustedContactView.as_view(), name='add_trusted_contact'),
    path('trusted-contacts/<int:contact_id>/remove/', RemoveTrustedContactView.as_view(), name='remove_trusted_contact'),
]