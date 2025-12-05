from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LegalDocument

# 1. Registro simple para LegalDocument (Sin decorador, o como función directa)
admin.site.register(LegalDocument)

# 2. Registro personalizado para User (Usando el decorador correctamente con la clase Admin)
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'nombre', 'numero', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'numero', 'image')}), # Añadí 'image' aquí para que puedas verla/editarla en admin
        ('Ubicación Navegador', {'fields': ('browser_latitude', 'browser_longitude', 'browser_last_seen')}), # Añadí los campos de ubicación
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Contactos', {'fields': ('trusted_contacts',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'numero', 'password1', 'password2'),
        }),
    )
    
    search_fields = ('email', 'nombre', 'numero')
    ordering = ('email',)
    filter_horizontal = ('trusted_contacts', 'groups', 'user_permissions')
