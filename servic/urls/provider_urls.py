from django.urls import path
from ..views import (
    ServiceProviderProfileView,
    ProviderRequestView,
    ProviderRequestListView,
    ProviderRequestDetailView,
)

urlpatterns = [
    # Permite a un usuario provider crear o actualizar su perfil de proveedor
    path(
        "provider/profile/",
        ServiceProviderProfileView.as_view(),
        name="provider-profile",
    ),
    # Permite a un usuario común enviar una solicitud para convertirse en provider
    path(
        "provider/request/",
        ProviderRequestView.as_view(),
        name="create-provider-request",
    ),
    # Permite al admin listar todas las solicitudes de provider (pendientes, aprobadas, rechazadas)
    path(
        "provider/requests/",
        ProviderRequestListView.as_view(),
        name="list-provider-requests",
    ),
    # Permite al admin revisar, aprobar o rechazar una solicitud específica de provider
    path(
        "provider/requests/<int:pk>/",
        ProviderRequestDetailView.as_view(),
        name="review-provider-request",
    ),
]
