from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics
from ..models import ServiceProviderProfile, ProviderRequest
from ..serializers import (
    ServiceProviderProfileSerializer,
    ProviderRequestSerializer,
    ProviderRequestCreateSerializer,
    ProviderRequestReviewSerializer,
)

# View de UpdateProfileProvider - usuario carga sus datos para terminar de ser provider
class ServiceProviderProfileView(APIView):
    # Solo usuarios autenticados pueden acceder a estos métodos
    permission_classes = [permissions.IsAuthenticated]
    # Permite manejar archivos y formularios en las peticiones
    parser_classes = (MultiPartParser, FormParser)

    # Obtener el perfil del provider autenticado (GET) (endpoint GetMeProviderProfile)
    def get(self, request, *args, **kwargs):
        try:
            # Busca el perfil de provider asociado al usuario autenticado
            profile = request.user.provider_profile
        except ServiceProviderProfile.DoesNotExist:
            # Si no existe, retorna error 404
            return Response(
                {"detail": "No se encontró un perfil de prestador de servicios"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Serializa el perfil encontrado y lo retorna como JSON
        serializer = ServiceProviderProfileSerializer(profile)
        return Response(serializer.data)

    # Crear un nuevo perfil de provider (POST) (endpoint updateProfileRequest)
    def post(self, request, *args, **kwargs):
        # Prints de depuración para ver archivos y datos recibidos
        print("FILES:", request.FILES) # Muestra los archivos enviados en la petición (por ejemplo, imágenes, PDFs, etc.).
        print("DATA:", request.data) # Muestra el diccionario con los datos enviados en el body de la petición (campos del formulario o JSON).
        # Solo los usuarios con user_type "provider" pueden crear perfil
        if request.user.user_type != "provider":
            return Response(
                {"detail": "Solo los prestadores de servicios pueden crear un perfil"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # No permitir que un usuario cree más de un perfil
        if hasattr(request.user, "provider_profile"):
            return Response(
                {"detail": "Ya existe un perfil de prestador de servicios"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Verifica que se haya enviado el archivo de certificación
        if "certification_file" not in request.FILES:
            return Response(
                {"certification_file": ["El archivo de certificación es obligatorio"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Crea el serializer con los datos recibidos (request.data es un diccionario con los datos del formulario/JSON)
        serializer = ServiceProviderProfileSerializer(data=request.data)
        if serializer.is_valid():
            # Guarda el perfil y lo asocia al usuario autenticado
            serializer.save(user=request.user)
            # Marca el perfil del usuario como completo
            request.user.is_profile_complete = True
            request.user.save()
            return Response(
                {"message": "Perfil creado exitosamente", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        # Si hay errores de validación, los retorna
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Actualizar el perfil del provider autenticado (PUT/PATCH) (endpoint UpdateUserProfile)
    def put(self, request, *args, **kwargs):
        try:
            # Busca el perfil de provider asociado al usuario autenticado
            profile = request.user.provider_profile
        except ServiceProviderProfile.DoesNotExist:
            # Si no existe, retorna error 404
            return Response(
                {"detail": "No se encontró un perfil de prestador de servicios"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Crea el serializer con los datos recibidos y el perfil existente (partial=True permite actualizar solo algunos campos)
        serializer = ServiceProviderProfileSerializer(
            profile, data=request.data, partial=True
        )
        if serializer.is_valid():
            # Guarda los cambios en el perfil
            serializer.save()
            return Response(
                {"message": "Perfil actualizado exitosamente", "data": serializer.data}
            )
        # Si hay errores de validación, los retorna
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Aqui llega la peticion del usuario para poder ser plomero
class ProviderRequestView(generics.CreateAPIView):
    # Usamos el serializer ProviderRequestCreateSerializer 
    # Se encarga de vallidar al usuario
    serializer_class = ProviderRequestCreateSerializer
    permission_classes = [permissions.IsAuthenticated] # Hacemos uso de la clase IsAuthenticated para verificar que solo el usuario autenticado pueda acceder a ese endpoint
    '''
    Cuando llega una petición al endpoint, DRF revisa si el usuario envió un token de autenticación válido (por ejemplo, un JWT en el header Authorization: Bearer <token>).
    Si el token es válido, DRF asigna el usuario correspondiente a request.user y permite el acceso.
    Si no hay token o el token es inválido/expirado, DRF responde automáticamente con un error 401 (no autorizado) y no ejecuta la vista.

    Si todo es valido, se crea una instancia de ProviderRequest con
    user: el usuario actual
    request_reason: lo enviado en el body
    status: por defecto "pending"
    El usuario NO es provider aún. Solo tiene una solicitud pendiente.
    Esta misma se crea mediante el perform_create y lo hace ya que 
    en el serializer ProviderRequestCreateSerializer le pusimos que trabaje con 
    class Meta:
        model = ProviderRequest
        fields = ["request_reason"]
    Cuando llamas a serializer.save(...), DRF sabe que debe crear un objeto del modelo que está en Meta.model del serializer.
    '''
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Permite mostrar las solicitudes pendientes al admin
class ProviderRequestListView(generics.ListAPIView):
    serializer_class = ProviderRequestSerializer
    # Lo hacemos gracias al uso de permissions.IsAdminUser
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        # Obtiene el parámetro 'status' de la URL si fue enviado (por ejemplo, ?status=pending)
        status_filter = self.request.query_params.get("status", None)
        # Obtiene todas las solicitudes de provider de la base de datos
        queryset = ProviderRequest.objects.all()

        # Si se envió un filtro de estado, filtra el queryset por ese estado
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Retorna el queryset final (filtrado o no)
        return queryset


class ProviderRequestDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProviderRequestReviewSerializer  # Usa este serializer para revisar/aprobar/rechazar solicitudes
    permission_classes = [permissions.IsAdminUser]      # Solo los usuarios admin pueden acceder a esta vista
    queryset = ProviderRequest.objects.all()            # Trabaja sobre todas las solicitudes de provider

    def update(self, request, *args, **kwargs):
        '''
        instance = self.get_object()
        obtiene la instancia específica de la solicitud de provider (ProviderRequest) que corresponde al <pk> 
        (id de la solicitud) que viene en la URL.
        Por ejemplo, si accedes a:
        PUT /api/provider/requests/5/
        self.get_object() obtiene la solicitud de provider con id=5
        user = instance.user
        '''
        instance = self.get_object()  # Obtiene la solicitud específica a actualizar según el <pk> de la URL
        serializer = self.get_serializer(instance, data=request.data, partial=True)  # Crea el serializer con los datos recibidos y la instancia existente
        serializer.is_valid(raise_exception=True)  # Valida los datos; si hay error, lanza excepción y retorna 400

        # Si la solicitud es aprobada, cambiar el rol del usuario
        if serializer.validated_data.get("status") == "approved":
            user = instance.user  # Obtiene el usuario que hizo la solicitud
            user.user_type = "provider"  # Cambia su tipo a provider
            user.save()  # Guarda el cambio en la base de datos

        # Guardar la respuesta del administrador (y el estado actualizado)
        serializer.save(reviewed_by=request.user)  # Guarda los cambios y registra qué admin revisó la solicitud

        return Response(
            {
                "message": "Solicitud actualizada exitosamente",  # Mensaje de éxito
                "request": ProviderRequestSerializer(instance).data,  # Devuelve los datos actualizados de la solicitud usando un serializer de solo lectura
            }
        )
