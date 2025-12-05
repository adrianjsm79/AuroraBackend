from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import GetLegalDocumentView
from .views import (
    RegisterView, 
    ProfileView, 
    TrustedContactsListView,
    AddTrustedContactView, 
    RemoveTrustedContactView,
    UpdateBrowserLocationView,
    MyTokenObtainPairView,
    TrustedByContactsListView,
    RequestPasswordResetView,
    VerifyResetCodeView,
    CompletePasswordResetView
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # La ruta para que la app web actualice la ubicación del navegador
    path('profile/update-browser-location/', UpdateBrowserLocationView.as_view(), name='update_browser_location'),
    
    # --- Rutas de Contactos ---
    path('trusted-contacts/', TrustedContactsListView.as_view(), name='trusted_contacts'),
    path('trusted-contacts/add/', AddTrustedContactView.as_view(), name='add_trusted_contact'),
    path('trusted-contacts/<int:contact_id>/remove/', RemoveTrustedContactView.as_view(), name='remove_trusted_contact'),
    path('trusted-contacts/trusted-by/', TrustedByContactsListView.as_view(), name='trusted_by_contacts'),
    path('legal/<int:code>/', GetLegalDocumentView.as_view(), name='get_legal_document'),
    
    path('password-reset/request/', RequestPasswordResetView.as_view(), name='password_reset_request'),
    path('password-reset/verify/', VerifyResetCodeView.as_view(), name='password_reset_verify'),
    path('password-reset/confirm/', CompletePasswordResetView.as_view(), name='password_reset_confirm'),
]