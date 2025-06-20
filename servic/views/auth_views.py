from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import IntegrityError
from ..serializers import UserRegisterSerializer, CustomTokenObtainPairSerializer


# Aqui definimos la logica de la API similar al archivo "usersController.js"
# Creamos las funciones que vamos a usar en la API
# Crear un usuario

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer  # Usa este serializer para validar y crear usuarios

    def post(self, request, *args, **kwargs):
        # Crea una instancia del serializer con los datos recibidos en el request (JSON)
        serializer = self.get_serializer(data=request.data)
        # Valida los datos recibidos; llama automáticamente al método validate del serializer
        serializer.is_valid(raise_exception=True)
        try:
            # Si los datos son válidos, llama al método create del serializer para crear el usuario
            user = serializer.save()
        except IntegrityError:
            # Si el email ya existe, retorna un error personalizado
            return Response(
                {"email": ["El email ya está registrado."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Genera los tokens JWT para el usuario recién creado
        refresh = RefreshToken.for_user(user)

        # Retorna la respuesta con los datos del usuario y los tokens
        return Response(
            {
                "user": serializer.data,  # serializer.data convierte el usuario a JSON usando el serializer
                "refresh": str(refresh),  # Token de refresco JWT
                "access": str(refresh.access_token),  # Token de acceso JWT
                "message": "Usuario registrado exitosamente",
            },
            status=status.HTTP_201_CREATED,
        )

# ---------------------------
# FLUJO DEL REGISTRO DE USUARIO
# ---------------------------
# 1. El usuario envía un JSON con sus datos (email, password, etc.) al endpoint de registro.
# 2. La vista crea una instancia del serializer con esos datos.
# 3. Al llamar a serializer.is_valid(), se ejecuta el método validate del serializer (UserRegisterSerializer).
#    - Aquí se valida, por ejemplo, que las contraseñas coincidan.
# 4. Si todo es válido, serializer.save() llama al método create del serializer.
#    - Aquí se crea el usuario en la base de datos.
# 5. Se generan los tokens JWT y se retorna la respuesta con los datos del usuario y los tokens.

# ---------------------------
# LOGIN DE USUARIO
# ---------------------------

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer  # Usa este serializer personalizado para el login

# FLUJO DEL LOGIN DE USUARIO
# ---------------------------
# 1. El usuario envía su email y contraseña al endpoint de login.
# 2. La vista usa el serializer CustomTokenObtainPairSerializer.
# 3. Al llamar a serializer.is_valid(), se ejecuta el método validate del serializer padre (TokenObtainPairSerializer).
#    - Aquí se valida que el usuario exista y la contraseña sea correcta.
# 4. Si todo es válido, se generan los tokens JWT y se retorna la respuesta con los tokens y los datos públicos del usuario.