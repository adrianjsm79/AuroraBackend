from django.db import models
from django.conf import settings

class Location(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='locations'
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
    
    def __str__(self):
        return f"{self.user.nombre} - {self.timestamp}"