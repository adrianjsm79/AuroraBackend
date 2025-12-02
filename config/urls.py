
from django.contrib import admin

from django.urls import path, include, re_path 
from django.conf import settings
from django.views.static import serve 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/tracking/', include('tracking.urls')),
    path('api/devices/', include('devices.urls')),

    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]
