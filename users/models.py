from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
import random
from django.utils import timezone
from datetime import timedelta

class LegalDocument(models.Model):
    """
    Guarda documentos legales como Términos y Privacidad.
    code: 100 (Términos), 101 (Privacidad), etc.
    """
    code = models.IntegerField(unique=True, verbose_name="Código del Documento")
    title = models.CharField(max_length=200, verbose_name="Título")
    content_html = models.TextField(verbose_name="Contenido HTML")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.code})"

class UserManager(BaseUserManager):
    # --- Tu UserManager (sin cambios) ---
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número debe estar en formato: '+999999999'. Hasta 15 dígitos."
    )
    
    email = models.EmailField(unique=True, verbose_name='Email')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    numero = models.CharField(
        validators=[phone_regex],
        max_length=17,
        unique=True,
        verbose_name='Número de teléfono'
    )
    image = models.ImageField(
        upload_to='profile_pics/', 
        null=True, 
        blank=True, 
        verbose_name='Foto de Perfil'
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # Contactos de confianza
    trusted_contacts = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='trusted_by',
        blank=True
    )
    
    # Campos para guardar la ubicación del navegador del usuario (el "observador")
    browser_latitude = models.FloatField(null=True, blank=True)
    browser_longitude = models.FloatField(null=True, blank=True)
    browser_last_seen = models.DateTimeField(null=True, blank=True)
    # --- Fin de campos nuevos ---

    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'numero']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return self.email
    
class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        # El código expira en 15 minutos
        return timezone.now() < self.created_at + timedelta(minutes=15)

    @classmethod
    def generate_code(cls, user):
        # Borra códigos anteriores del usuario
        cls.objects.filter(user=user).delete()
        # Genera uno nuevo de 6 dígitos
        code = str(random.randint(100000, 999999))
        return cls.objects.create(user=user, code=code)
