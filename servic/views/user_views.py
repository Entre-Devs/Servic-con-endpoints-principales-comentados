from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import User, UserRoleChangeLog
from ..serializers import UserProfileSerializer, UserRoleChangeSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    '''
    Esta vista permite que un usuario autenticado consulte (GET) y actualice (PUT/PATCH)
    su propio perfil. Hereda de RetrieveUpdateAPIView, que ya implementa la lógica para
    obtener y actualizar un objeto.
    '''
    serializer_class = UserProfileSerializer  # Usa este serializer para transformar el usuario a JSON y validar datos de entrada
    permission_classes = [permissions.IsAuthenticated]  # Solo usuarios autenticados pueden acceder a esta vista

    # El objeto sobre el que se opera es siempre el usuario autenticado
    def get_object(self):
        # Retorna el usuario que hizo la petición (request.user)
        # Así, cada usuario solo puede ver y modificar su propio perfil
        return self.request.user


class UserRoleChangeView(generics.UpdateAPIView):
    serializer_class = UserRoleChangeSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()

    def get_object(self):
        user_id = self.kwargs.get("user_id")
        return get_object_or_404(User, id=user_id)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        # Guardar el rol anterior
        previous_role = user.user_type

        # Realizar el cambio de rol
        user.user_type = serializer.validated_data["user_type"]
        user.save()

        # Registrar el cambio
        UserRoleChangeLog.objects.create(
            user=user,
            previous_role=previous_role,
            new_role=user.user_type,
            reason=serializer.validated_data["reason"],
            changed_by=request.user,
        )

        return Response(
            {
                "message": "Rol de usuario actualizado exitosamente",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
