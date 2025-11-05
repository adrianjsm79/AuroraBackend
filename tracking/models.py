from django.db import models
# Importa el nuevo modelo de la app 'devices'
from devices.models import Device 

class Location(models.Model):

    # se enlaza al Dispositivo
    device = models.ForeignKey(
        Device, # Enlaza a la app 'devices', modelo 'Device'
        on_delete=models.CASCADE,
        related_name='location_history' # historial_de_ubicaciones
    )
    # -----------------------------------
    
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Historial de Ubicación'
        verbose_name_plural = 'Historiales de Ubicaciones'
    
    def __str__(self):
        return f"{self.device.name} - {self.timestamp}"