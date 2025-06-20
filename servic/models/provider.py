from django.db import models
from .user import User
'''
  ServiceProviderProfile hereda de models.Model toda la funcionalidad de crear, leer, actualizar
 y borrar registros de la base de datos.
  Permite definir los campos(columnas) de la tabla usando atributos como Charfield, OnteToOneField, etc
 Usar el ORM de Django para consultas y operaciones '''


class ServiceProviderProfile(models.Model):
    '''
     User es como una "foreign key" especial: garantiza que no haya dos perfiles para el mismo usuario.
     OneToOneField crea una relación uno a uno entre ServiceProviderProfile y User.
     Significa que cada usuario puede tener un solo perfil de proveedor y cada perfil 
    pertenece a un solo usuario.
     La variable es related_name un argumento (atributo) que pasas como parámetro al campo OneToOneField
    (y también a ForeignKey en otros modelos).
    IMPORTANTE: EN RELATED_NAME ELIGES UN NOMBRE PARA QUE LUEGO DESDE UN OBJETO TIPO USER PUEDAS ACCEDER
    AL PERFIL(TABLA PROVEEDOR) Y A TODOS LOS CAMPOS DE LA CLASE ServiceProviderProfile.
    Ejemplo:
    
    usuario = User.objects.get(email="ejemplo@mail.com")
    perfil = usuario.provider_profile  # Aquí accedes al perfil de proveedor

    print(perfil.identification_type)

    '''
    
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="provider_profile"
    )
    identification_type = models.CharField(
        max_length=20,
        choices=[
            ("dni", "DNI"),
            ("ce", "Carné de Extranjería"),
            ("passport", "Pasaporte"),
        ],
    )
    identification_number = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    certification_file = models.FileField(upload_to="certifications/")
    certification_description = models.TextField()
    years_of_experience = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Perfil de {self.user.email}"
    '''
     Meta personaliza los nombres que se ven en el admin de Django.
    Meta es una clase interna especial que puedes definir dentro de tus modelos en Django
    para configurar opciones adicionales sobre cómo se comporta ese modelo.
      En el panel de administración de Django, en vez de ver "Service provider profiles", 
    se verá "Perfiles de Prestadores".
    '''
    class Meta:
        verbose_name = "Perfil de Prestador"
        verbose_name_plural = "Perfiles de Prestadores"


class ProviderRequest(models.Model):
    # status_display en el serializer mostrará "Pendiente", "Aprobada" o "Rechazada"
    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("approved", "Aprobada"),
        ("rejected", "Rechazada"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="provider_requests"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    request_reason = models.TextField(
        help_text="Razón por la que desea convertirse en prestador"
    )
    admin_response = models.TextField(
        blank=True, null=True, help_text="Respuesta del administrador"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="reviewed_requests"
    )

    class Meta:
        verbose_name = "Solicitud de Prestador"
        verbose_name_plural = "Solicitudes de Prestadores"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Solicitud de {self.user.email} - {self.get_status_display()}"
