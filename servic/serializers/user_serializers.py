# Importa serializers
from rest_framework import serializers
'''
 Importa la función get_user_model, que retorna el modelo de usuario activo en el proyecto.
 Esto es útil si se tiene un modelo de usuario personalizado, así siempre se usa el modelo correcto.
'''
from django.contrib.auth import get_user_model
'''
 Importa la función validate_password, que valida que la contraseña cumpla con las reglas de seguridad 
 definidas en el proyecto (longitud, complejidad, etc.).
'''
from django.contrib.auth.password_validation import validate_password
'''
 Importa el serializer de SimpleJWT para obtener tokens de acceso y refresh (login con JWT).
 Permite personalizar la respuesta del login y agregar datos extra al token si lo necesitas.
'''
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

'''
 La función get_user_model() siempre retorna el modelo de usuario principal que está configurado
en tu proyecto Django, no importa cuántos modelos tengas.
Django usa este valor para saber cuál es el modelo de usuario principal.
Cuando llamas a get_user_model(), Django busca ese modelo y lo retorna.
'''

from ..models import User


'''
Django REST Framework
 REST significa Representational State Transfer.

 Es un estilo de arquitectura para diseñar servicios web (APIs) que permite que diferentes aplicaciones se comuniquen entre sí usando HTTP (como GET, POST, PUT, DELETE).
 En Django REST Framework, un serializer convierte los datos de los modelos (objetos Python) a JSON (y viceversa), 
para que puedan ser enviados y recibidos por la API.

La API la forman principalmente las views (vistas), que usan los serializers para procesar los datos.

JSON significa JavaScript Object Notation. Es un formato de texto muy usado para intercambiar datos entre aplicaciones, 
especialmente entre un servidor y un frontend (como React, Insomnia, Postman, etc.).
En las views, estos serializers se usan para manejar los datos de entrada y salida de los endpoints de registro, 
login y perfil.
En Insomnia, cuando envías un JSON para registrar o actualizar un usuario, el serializer valida y transforma esos 
datos JSON recibidos por a API(La API es el conjunto de endpoints (URLs) que exponen tus datos y lógica al exterior, views) 
a objetos Python.


En Insomnia envías un JSON a una URL de tu API.
La view recibe ese JSON.
La view usa el serializer para validar y transformar el JSON a objetos Python (y viceversa).
La view guarda, actualiza o responde según la lógica.

'''
# Serializador para registrar un usuario
'''
Para registrar usuarios nuevos.
Valida que las contraseñas coincidan y que el email sea único.
Crea el usuario usando create_user (que maneja el hash de la contraseña).
Si no se pasa username, lo genera a partir del email.
'''

'''
serializers.ModelSerializer es una clase de Django REST Framework que automatiza la creación de serializers basados
en tus modelos de Django.

'''
class UserRegisterSerializer(serializers.ModelSerializer):
    # Aqui en el argumento validators, le pasamos la funcion validate_password que importamos para validar las reglas de seguridad de la pass
    # Documentacion de los argumentos que se pueden agregar a CharField shttps://www.django-rest-framework.org/api-guide/fields/#charfield
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        error_messages={"required": "La contraseña es obligatoria"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "La contraseña no coincide"},
    )
    first_name = serializers.CharField(
        required=True, error_messages={"required": "El nombre es obligatorio"}
    )
    last_name = serializers.CharField(
        required=True, error_messages={"required": "El apellido es obligatorio"}
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "El email es obligatorio",
            "invalid": "El email no es valido",
            "unique": "El email ya esta registrado",
        },
    )
    '''
    En el caso de un ModelSerializer, la clase Meta es obligatoria y sirve principalmente para:
    '''
    class Meta:
        model = User
        fields = ("email", "password", "password2", "first_name", "last_name")
    '''
    serializer.is_valid(): llama aumaticamente al metodo validate y serializer.save() llama al metodo create
    debe llamarse validate y create para el framework lo detecte
    attrs es simplemente un diccionario que contiene todos los datos validados del serializer hasta ese momento.
    el 'attrs'  se genera en los views cuando se recibe una peticion(por ejemplo, un POST con los datos JSON), y se crea una instancia del 
    serializer con esos datos -> ver en user_views.py
    
    El usuario envía un JSON con sus credenciales (por ejemplo, desde Insomnia o el frontend)
    La view recibe esos datos y crea una instancia del serializer con ellos:
    Cuando se llama a serializer.is_valid(), DRF valida los campos y llama a validate(self, attrs) en el serializer, pasando los datos recibidos (ya validados campo por campo) como el diccionario attrs.
    

    si el serializer recibe de JSON {
    "email": "juan@mail.com",
    "password": "12345678",
    "password2": "12345678",
    "first_name": "Juan",
    "last_name": "Pérez"
    }

    entonces en el metodo validate, el parametro attrs sera
    {
    'email': 'juan@mail.com',
    'password': '12345678',
    'password2': '12345678',
    'first_name': 'Juan',
    'last_name': 'Pérez'
    }
    '''
    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden"}
            )
        return attrs
    '''
    validated_data es otro diccionario que contiene todos los datos que ya pasaron todas las validaciones del serializer.
    Solo contiene los datos que son válidos y listos para crear o actualizar un objeto en la base de datos.
    '''
    def create(self, validated_data):
        validated_data.pop('password2')
        if 'username' not in validated_data:
            validated_data['username'] = validated_data['email'].split('@')[0] # sino se ingresa un usuario, split separa el email en dos, con @ como intermediario y 0 seria la parte antes del @
        # Aqui usando ** delante del diccionario, desempaquetamos el mismo y le pasamos cada clave valor
        # create_user es el método estándar para crear usuarios y viene con el modelo que obtienes usando get_user_model().
        user = User.objects.create_user(**validated_data) # esto crea el objeto y lo guarda en la base de datos
        return user # devolvemos la variable creada a la view

# Serializador para loguear un usuario 

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    '''
    El método get_token es un @classmethod que SimpleJWT usa internamente para crear el token JWT cuando un usuario hace login.
    Cuando haces login desde una view usando SimpleJWT, el framework llama a get_token para construir el token JWT.
    '''
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token
    '''
    aqui llamamos al metodo validate de la clase padre TokenObtainPairSerializer 
    '''
    def validate(self, attrs):
        data = super().validate(attrs)
        # este metodo valida los datos attrs que vienen del view email (o username) exista en la base de datos.
        # Valida que la contraseña sea correcta para ese usuario.
        #Si todo es correcto, genera los tokens JWT:
        # Un token refresh
        # Un token access
        # Aqui le agregamos otro diccionario con el valor de user que contienen los datos publicos del usuario autenticado
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "username": self.user.username,
            "user_type": self.user.user_type,
        }
        return data

#Serializador para mostrar y actualizar el perfil
#Aqui definimos los campos que queremos mostrar y actualizar en el perfil
#El email no se puede cambiar desde aquí
# API (Insomnia, frontend, apps móviles)
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "user_type")
        read_only_fields = ("email", "user_type")


class UserRoleChangeSerializer(serializers.ModelSerializer):
    user_type = serializers.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        error_messages={
            "invalid_choice": 'El tipo de usuario debe ser "common" o "provider"'
        },
    )
    reason = serializers.CharField(
        required=True,
        max_length=500,
        error_messages={
            "required": "Debe proporcionar una razón para el cambio de rol",
            "max_length": "La razón no puede exceder los 500 caracteres",
        },
    )

    class Meta:
        model = User
        fields = ("user_type", "reason")
        read_only_fields = ("id",)

    def validate(self, attrs):
        user = self.instance
        new_role = attrs["user_type"]

        if user.user_type == new_role:
            raise serializers.ValidationError(
                {"user_type": "El usuario ya tiene asignado este rol"}
            )

        if user.is_superuser:
            raise serializers.ValidationError(
                {"user_type": "No se puede cambiar el rol de un superusuario"}
            )

        return attrs
