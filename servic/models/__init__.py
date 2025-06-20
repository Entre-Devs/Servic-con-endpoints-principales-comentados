
'''
 El archivo __init__.py en la carpeta models (si tienes tus modelos divididos en varios archivos)
sirve para indicarle a Python que esa carpeta es un paquete y para importar los modelos que quieres que estén 
disponibles al hacer from .models import ....
Así, cuando haces from .models import User, Python sabe buscar en los archivos correctos dentro de la carpeta models.
'''


from .user import User, UserRoleChangeLog
from .provider import ServiceProviderProfile, ProviderRequest
from .service import ServiceCategory, Service, ServiceImage

__all__ = [
    "User",
    "UserRoleChangeLog",
    "ServiceProviderProfile",
    "ProviderRequest",
    "ServiceCategory",
    "Service",
    "ServiceImage",
]
