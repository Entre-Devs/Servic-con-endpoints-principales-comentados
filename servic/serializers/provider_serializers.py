from rest_framework import serializers
from ..models import ServiceProviderProfile, ProviderRequest

# Serializer para la creación del perfil de provider(endpoint updateProfileRequest)
class ServiceProviderProfileSerializer(serializers.ModelSerializer):
    # Campo para subir el archivo de certificación, obligatorio y con mensajes de error personalizados
    certification_file = serializers.FileField(
        required=True,
        error_messages={
            "required": "El archivo de certificación es obligatorio",
            "invalid": "El archivo de certificación no es válido",
        },
    )

    class Meta:
        model = ServiceProviderProfile  # Modelo con el que trabaja el serializer
        fields = [
            "id",                       # ID del perfil (solo lectura)
            "identification_type",      # Tipo de documento (DNI, Pasaporte, etc.)
            "identification_number",    # Número de documento
            "phone_number",             # Teléfono de contacto
            "address",                  # Dirección
            "city",                     # Ciudad
            "state",                    # Estado/Provincia
            "country",                  # País
            "certification_file",       # Archivo de certificación (PDF o imagen)
            "certification_description",# Descripción del certificado
            "years_of_experience",      # Años de experiencia
            "is_verified",              # Si el perfil fue verificado por el admin (solo lectura)
            "created_at",               # Fecha de creación (solo lectura)
            "updated_at",               # Fecha de actualización (solo lectura)
        ]
        # Estos campos no pueden ser modificados por el usuario, solo lectura
        read_only_fields = ["id", "is_verified", "created_at", "updated_at"]

    # Validación personalizada para el archivo de certificación
    def validate_certification_file(self, value):
        allowed_types = ["image/jpeg", "image/png", "application/pdf"]
        # Verifica que el archivo sea de un tipo permitido
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "El archivo debe ser una imagen (JPEG, PNG) o un PDF"
            )
        # Verifica que el archivo no supere los 5MB
        if value.size > 5 * 1024 * 1024:  # 5MB en bytes
            raise serializers.ValidationError("El archivo no debe superar los 5MB")
        return value

    # Validación personalizada para el número de identificación
    def validate_identification_number(self, value):
        # Verifica que no exista otro perfil con el mismo número de identificación
        if ServiceProviderProfile.objects.filter(identification_number=value).exists():
            raise serializers.ValidationError(
                "Este número de identificación ya está registrado"
            )
        return value

    # Validación personalizada para el número de teléfono
    def validate_phone_number(self, value):
        # Permite solo dígitos, espacios, guiones y el símbolo +
        if not value.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            raise serializers.ValidationError(
                "El número de teléfono debe contener solo dígitos, espacios, guiones y el símbolo +"
            )
        return value
    
class ProviderRequestSerializer(serializers.ModelSerializer):
    # Campo solo lectura que muestra el email del usuario que hizo la solicitud
    user_email = serializers.EmailField(source="user.email", read_only=True)
    # Campo solo lectura que muestra el nombre completo del usuario (usando un método personalizado)
    user_name = serializers.SerializerMethodField(read_only=True)
    # Campo solo lectura que muestra el estado en formato legible (por ejemplo, "Pendiente" en vez de "pending")
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    #status_display en el serializer mostrará "Pendiente", "Aprobada" o "Rechazada"

    class Meta:
        model = ProviderRequest  # El modelo con el que trabaja este serializer
        fields = [
            "id",                # ID de la solicitud
            "user_email",        # Email del usuario solicitante
            "user_name",         # Nombre completo del usuario solicitante
            "status",            # Estado interno (pending, approved, rejected)
            "status_display",    # Estado legible para humanos
            "request_reason",    # Motivo de la solicitud
            "admin_response",    # Respuesta del admin (si la hay)
            "created_at",        # Fecha de creación
            "updated_at",        # Fecha de última actualización
        ]
        # Estos campos solo pueden ser leídos, no modificados por el usuario
        read_only_fields = ["status", "admin_response", "created_at", "updated_at"]

    # Método para obtener el nombre completo del usuario
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class ProviderRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderRequest # aqui indicamos que trabajara con el modelo de ProviderRequest
        fields = ["request_reason"] #  es el nombre del campo que espera la API

    def validate(self, attrs):
        user = self.context["request"].user # ["request"] es una clave del diccionario context que Django REST Framework (DRF) pasa automáticamente al serializer cuando lo usas desde una vista.
        # Es basicamente el usuario que esta haciendo la peticion para ser trabajor
        # Se valida si el usuario ya es provider o si tiene una solicitud pendiente
        if user.user_type == "provider":
            raise serializers.ValidationError("Ya eres un prestador de servicios")

        if ProviderRequest.objects.filter(user=user, status="pending").exists():
            raise serializers.ValidationError("Ya tienes una solicitud pendiente")
        # Se devuelve un diccionario con los datos que el usuario envió y que pasaron la validación de tipos y formato.
        return attrs


# Serializer para que el admin revise (apruebe o rechace) una solicitud de provider
class ProviderRequestReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderRequest  # Modelo con el que trabaja el serializer
        fields = ["status", "admin_response"]  # Solo permite actualizar el estado y la respuesta del admin

    # Validación personalizada para los datos recibidos
    def validate(self, attrs):
        # Si el admin rechaza la solicitud pero no proporciona una razón, lanza un error
        if attrs["status"] == "rejected" and not attrs.get("admin_response"):
            raise serializers.ValidationError(
                {"admin_response": "Debe proporcionar una razón para el rechazo"}
            )
        # Si todo está bien, retorna los datos validados
        return attrs