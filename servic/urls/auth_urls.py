from django.urls import path
from ..views import RegisterView, CustomTokenObtainPairView

urlpatterns = [
    # Permite registrar el usuario
    path("register/", RegisterView.as_view(), name="register"),
    # Permite loguear al usuario
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
]
