from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, ProfileView, TrustedContactsListView,
    AddTrustedContactView, RemoveTrustedContactView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('trusted-contacts/', TrustedContactsListView.as_view(), name='trusted_contacts'),
    path('trusted-contacts/add/', AddTrustedContactView.as_view(), name='add_trusted_contact'),
    path('trusted-contacts/<int:contact_id>/remove/', RemoveTrustedContactView.as_view(), name='remove_trusted_contact'),
]