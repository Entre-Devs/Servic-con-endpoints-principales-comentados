'''Importa la clase AbstractUser, que ya tiene la lógica de autenticación incluida (contraseña, login, etc.),
y que se puede extender con nuevos campos.'''
from django.contrib.auth.models import AbstractUser
#  Importa las herramientas para definir modelos de base de datos.
from django.db import models
''' 
 Aqui se crea una clase User que hereda de AbstractUser(ya tiene tiene todo lo necesario para manejar contraseñas y autenticacion)
lo que permite conservar la funcionalidad de autentificacion de Django
y agregar campos personalizados como email, user_type, etc'''

'''Internamente, AbstractUser hereda de AbstractBaseUser, que a su vez hereda de models.Model.'''
class User(AbstractUser):
    '''
     Tupla de opciones para el campo user_type
     El primer valor de cada tupla es lo que se guarda en la base de datos en 
    la columna user_type definida mas abajo dependiendo de si es usuario comun o trabajador
     El segundo valor de cada tupla son descripciones amigables que se ven en el admin de Django
    una interfaz web automatica que viene incluida con Django y permite gestionar los datos
    de los modelos de forma sencilla'''
    
    USER_TYPE_CHOICES = (
        ('common', 'Usuario Común'), 
        ('provider', 'Prestador de Servicios'),
    )
    # Define las caracteristicas que tendran las columnas que se guardaran en la base de datos
    email = models.EmailField(unique=True)
    #  null=True permite valores nulos en la base de datos y blank=True permite dejar campo vacio en formularios
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, null=True, blank=True)
    is_profile_complete = models.BooleanField(default=False)
    
    # AQUI LE DICES A DJANGO QUE EL EMAIL SERA EL IDENTIFICADOR PRINCIPAL PARA EL LOGIN Y AUTENTICACION
    USERNAME_FIELD = 'email'
    # AQUI TE PEDIRA TAMBIEN EL USERNAME AL CREAR USUARIOS DESDE LA TERMINAL
    # ES UTIL PARA MANTENER COMPATIBILIDAD CON EL SISTEMA DE USUARIOS DE DJANGO, QUE ESPERA QUE CADA USUARIO
    # TENGA UN USEARNAME AUINQUE NO SE USE PARA LOGIN
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email


class UserRoleChangeLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="role_changes"
    )
    previous_role = models.CharField(max_length=10, choices=User.USER_TYPE_CHOICES)
    new_role = models.CharField(max_length=10, choices=User.USER_TYPE_CHOICES)
    reason = models.TextField()
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="role_changes_made"
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de cambio de rol"
        verbose_name_plural = "Registros de cambios de rol"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"Cambio de rol de {self.user.email} de {self.previous_role} a {self.new_role}"
