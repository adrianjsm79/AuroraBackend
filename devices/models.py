from django.db import models
from django.conf import settings

class Device(models.Model):

    # Propietario Enlace al modelo User (un usuario puede tener muchos dispositivos)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name="devices", 
        on_delete=models.CASCADE,
        verbose_name="Usuario Propietario"
    )
    
    # Nombre del dispositivo dado por el usuario
    name = models.CharField(
        max_length=100, 
        verbose_name="Nombre del Dispositivo"
    )
    
    # El ID único del teléfono (ej. ANDROID_ID)
    device_identifier = models.CharField(
        max_length=255, 
        unique=True, 
        db_index=True,
        verbose_name="Identificador Único"
    )
    
    #estado
    is_lost = models.BooleanField(
        default=False, 
        verbose_name="Reportado como perdido"
    )
    
    # ubicacion
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    
    #fechas
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de registro"
    )
    last_seen = models.DateTimeField(
        auto_now=True, 
        verbose_name="Última vez visto"
    )

    class Meta:
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"
        ordering = ['user', 'name'] # Ordena los dispositivos por usuario y nombre

    def __str__(self):
        return f"{self.name} ({self.user.email})"