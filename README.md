# Servic App - Backend

Este repositorio contiene el backend de una plataforma de servicios desarrollada en Django y Django REST Framework.  
Permite que usuarios se registren, soliciten ser proveedores, sean aprobados por un administrador y gestionen servicios.

---

## 📦 Estructura principal

### models/
Define las tablas principales:
- **User**: usuario común o provider, autenticación por email.
- **ProviderRequest**: solicitud para convertirse en provider.
- **ServiceProviderProfile**: perfil de proveedor (datos, archivos, verificación).
- **Service**, **ServiceCategory**, **ServiceImage**: servicios ofrecidos y sus imágenes.

### serializers/
Transforman modelos a JSON y validan datos de entrada/salida:
- **UserRegisterSerializer**, **UserProfileSerializer**: registro y perfil de usuario.
- **ProviderRequestCreateSerializer**, **ProviderRequestReviewSerializer**: solicitud y revisión de provider.
- **ServiceProviderProfileSerializer**: creación y actualización de perfil de provider.
- **ServiceSerializer**, **ServiceListSerializer**: gestión de servicios.

### views/
Lógica de la API:
- Registro y login de usuarios (`auth_views.py`).
- Perfil de usuario (`user_views.py`).
- Solicitud y gestión de provider (`provider_views.py`).
- Administración de solicitudes y servicios (`admin_views.py`).
- Gestión de servicios y categorías (`service_views.py`).

### urls/
Rutas agrupadas por funcionalidad:
- **auth_urls.py**: registro y login.
- **user_urls.py**: perfil de usuario.
- **provider_urls.py**: solicitud y perfil de provider.
- **admin_urls.py**: endpoints de administración.
- **service_urls.py**: servicios y categorías.

---

## 🚦 Flujos principales

### 1. Registro y autenticación
- Un usuario se registra (`/api/register/`) y obtiene tokens JWT.
- Puede loguearse (`/api/login/`) para obtener nuevos tokens.

### 2. Solicitud para ser provider
- Usuario común envía una solicitud (`POST /api/provider/request/`) con el motivo.
- El sistema valida que no tenga otra solicitud pendiente ni sea ya provider.

### 3. Revisión por el admin
- El admin lista todas las solicitudes (`GET /api/provider/requests/`).
- Puede aprobar o rechazar una solicitud (`PUT /api/provider/requests/<id>/`).
  - Si aprueba, el usuario pasa a ser provider.
  - Si rechaza, debe dejar una razón.

### 4. Creación de perfil de provider
- Un usuario aprobado como provider crea su perfil (`POST /api/provider/profile/`), subiendo archivos y completando datos.
- Solo puede tener un perfil y debe adjuntar la certificación.

### 5. Gestión de servicios
- Providers verificados pueden crear, actualizar y listar servicios.
- Admin puede aprobar o rechazar servicios y verificar providers.

---

## 🛡️ Seguridad y permisos

- Endpoints protegidos con JWT (`IsAuthenticated`).
- Acciones de administración solo para usuarios admin (`IsAdminUser`).
- Validaciones estrictas en serializers para evitar duplicados y asegurar integridad de datos.

---

## 📚 Ejemplo de flujo resumido

1. Usuario se registra y se loguea.
2. Solicita ser provider.
3. Admin revisa y aprueba la solicitud.
4. Usuario crea su perfil de provider.
5. Provider crea servicios y los administra.
6. Admin verifica providers y aprueba servicios.
