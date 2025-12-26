# Todo Application - Complete RESTful API

API REST completa para gestión de tareas (Todos) construida con FastAPI, SQLAlchemy y autenticación JWT. Este proyecto implementa un sistema robusto con autenticación, autorización basada en roles y operaciones CRUD completas.

## Descripción General

Este proyecto es una aplicación de gestión de tareas que permite a los usuarios registrarse, autenticarse y administrar sus propias tareas. Incluye funcionalidades de administración para usuarios con rol de administrador y gestión de perfiles de usuario.

### Características Principales

- **Autenticación y Autorización**: Sistema completo de autenticación basado en JWT (JSON Web Tokens)
- **Gestión de Tareas (CRUD)**: Crear, leer, actualizar y eliminar tareas
- **Aislamiento por Usuario**: Cada usuario solo puede acceder a sus propias tareas
- **Panel de Administración**: Endpoints exclusivos para administradores
- **Gestión de Perfil**: Los usuarios pueden consultar y modificar su información
- **Validación de Datos**: Validación automática con Pydantic
- **Base de Datos**: SQLite con SQLAlchemy ORM

## Arquitectura del Proyecto

```bash
p06_project_3_complete_restful_apis/
├── main.py                 # Punto de entrada de la aplicación
├── database.py             # Configuración de base de datos
├── models.py               # Modelos SQLAlchemy (Users, Todos)
├── __init__.py
├── data/
│   └── mi_base.db         # Base de datos SQLite
├── docs/
│   ├── AUTH_DOCUMENTACION.md      # Documentación del módulo de autenticación
│   └── TODOS_DOCUMENTACION.md     # Documentación del módulo de tareas
└── routers/
    ├── __init__.py
    ├── auth.py            # Endpoints de autenticación (registro, login)
    ├── todos.py           # Endpoints CRUD de tareas
    ├── admin.py           # Endpoints administrativos
    └── users.py           # Endpoints de gestión de usuario
```

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y de alto rendimiento
- **SQLAlchemy**: ORM para interacción con base de datos
- **SQLite**: Base de datos relacional ligera
- **Pydantic**: Validación de datos y serialización
- **Passlib**: Hashing de contraseñas con bcrypt
- **Python-Jose**: Implementación de JWT
- **OAuth2**: Esquema de autenticación estándar

## Modelos de Datos

### Users (Usuarios)

Almacena la información de los usuarios registrados en el sistema.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | Identificador único (Primary Key) |
| email | String | Correo electrónico (único) |
| username | String | Nombre de usuario (único) |
| first_name | String | Nombre |
| last_name | String | Apellido |
| hashed_password | String | Contraseña hasheada con bcrypt |
| role | String | Rol del usuario (user, admin) |
| is_active | Boolean | Estado de activación del usuario |

### Todos (Tareas)

Almacena las tareas creadas por los usuarios.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | Identificador único (Primary Key) |
| title | String | Título de la tarea |
| description | String | Descripción detallada |
| priority | Integer | Prioridad (1-5) |
| complete | Boolean | Estado de completitud |
| owner_id | Integer | ID del usuario propietario (Foreign Key) |

## Endpoints de la API

### Autenticación (`/auth`)

#### POST /auth/

Registra un nuevo usuario en el sistema.

**Request Body:**

```json
{
  "username": "usuario123",
  "email": "usuario@email.com",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "password": "password123",
  "role": "user"
}
```

**Response:** `201 Created`

#### POST /auth/token

Autentica al usuario y retorna un token JWT.

**Request Body (form-urlencoded):**

```bash
username=usuario123
password=password123
```

**Response:** `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Tareas (`/todos` - requiere autenticación)

Todos los endpoints de tareas requieren el header de autorización:

```bash
Authorization: Bearer <token>
```

#### GET /

Lista todas las tareas del usuario autenticado.

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "title": "Completar proyecto",
    "description": "Finalizar el desarrollo de la API",
    "priority": 5,
    "complete": false,
    "owner_id": 1
  }
]
```

#### GET /todo/{todo_id}

Obtiene una tarea específica del usuario.

**Response:** `200 OK` - Retorna el objeto de la tarea

**Errores:**

- `404 Not Found` - Tarea no encontrada o no pertenece al usuario

#### POST /todo/

Crea una nueva tarea para el usuario autenticado.

**Request Body:**

```json
{
  "title": "Nueva tarea",
  "description": "Descripción de la tarea",
  "priority": 3,
  "complete": false
}
```

**Response:** `201 Created`

**Validaciones:**

- title: mínimo 3 caracteres
- description: entre 3 y 100 caracteres
- priority: entre 1 y 5
- complete: booleano obligatorio

#### PUT /todo/{todo_id}

Actualiza completamente una tarea existente.

**Request Body:**

```json
{
  "title": "Tarea actualizada",
  "description": "Nueva descripción",
  "priority": 4,
  "complete": true
}
```

**Response:** `204 No Content`

**Errores:**

- `404 Not Found` - Tarea no encontrada

#### DELETE /todo/{todo_id}

Elimina una tarea del usuario.

**Response:** `204 No Content`

**Errores:**

- `404 Not Found` - Tarea no encontrada

### Administración (`/admin` - requiere rol admin)

#### GET /admin/todo

Lista todas las tareas de todos los usuarios (solo administradores).

**Response:** `200 OK` - Array con todas las tareas del sistema

**Errores:**

- `401 Unauthorized` - Usuario no es administrador

#### DELETE /admin/todo/{todo_id}

Elimina cualquier tarea del sistema (solo administradores).

**Response:** `204 No Content`

**Errores:**

- `401 Unauthorized` - Usuario no es administrador
- `404 Not Found` - Tarea no encontrada

### Usuario (`/user` - requiere autenticación)

#### GET /user/

Obtiene la información del usuario autenticado.

**Response:** `200 OK`

```json
{
  "id": 1,
  "username": "usuario123",
  "email": "usuario@email.com",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "role": "user",
  "is_active": true
}
```

#### PUT /user/password

Cambia la contraseña del usuario autenticado.

**Request Body:**

```json
{
  "password": "contraseña_actual",
  "new_password": "nueva_contraseña"
}
```

**Response:** `204 No Content`

**Validaciones:**

- new_password: mínimo 6 caracteres

**Errores:**

- `401 Unauthorized` - Contraseña actual incorrecta

## Instalación y Configuración

### Requisitos Previos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. Clonar o descargar el proyecto

2. Instalar las dependencias:

```bash
pip install fastapi uvicorn sqlalchemy passlib python-jose python-multipart bcrypt
```

O si existe un archivo requirements.txt:

```bash
pip install -r requirements.txt
```

1. La base de datos SQLite se creará automáticamente en `data/mi_base.db` al ejecutar la aplicación por primera vez.

### Ejecutar la Aplicación

```bash
uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8000`

### Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## Seguridad

### Autenticación JWT

El sistema utiliza JSON Web Tokens para autenticación stateless:

- Los tokens tienen una duración de 20 minutos
- Se firman con el algoritmo HS256
- Contienen información del usuario (username, id, role)

### Hashing de Contraseñas

Las contraseñas se hashean utilizando bcrypt antes de almacenarse:

- Bcrypt es resistente a ataques de fuerza bruta
- Incluye salt automático
- Las contraseñas nunca se almacenan en texto plano

### Aislamiento de Datos

Cada usuario solo puede acceder a sus propios datos:

- Las queries incluyen filtros por `owner_id`
- Previene acceso no autorizado a tareas de otros usuarios
- Los administradores tienen acceso completo

### Validación de Entrada

Pydantic valida automáticamente todos los datos de entrada:

- Previene inyección SQL
- Garantiza tipos de datos correctos
- Valida rangos y longitudes

## Inyección de Dependencias

El proyecto hace uso extensivo del sistema de inyección de dependencias de FastAPI:

### Dependencia de Base de Datos

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

Gestiona automáticamente el ciclo de vida de las sesiones de base de datos:

- Crea una sesión antes de cada request
- La cierra después de cada request
- Garantiza liberación de recursos

### Dependencia de Usuario

```python
user_dependency = Annotated[dict, Depends(get_current_user)]
```

Valida y extrae información del usuario autenticado:

- Extrae el token del header Authorization
- Valida el token JWT
- Retorna información del usuario (id, username, role)
- Lanza error 401 si el token es inválido

## Códigos de Estado HTTP

La API utiliza códigos de estado HTTP estándar:

- **200 OK**: Solicitud exitosa con datos
- **201 Created**: Recurso creado exitosamente
- **204 No Content**: Operación exitosa sin datos de respuesta
- **401 Unauthorized**: No autenticado o token inválido
- **404 Not Found**: Recurso no encontrado
- **422 Unprocessable Entity**: Datos de entrada inválidos

## Ejemplos de Uso

### Registro e Inicio de Sesión

```bash
# 1. Registrar un nuevo usuario
curl -X POST "http://localhost:8000/auth/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "secure123",
    "role": "user"
  }'

# 2. Iniciar sesión y obtener token
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=secure123"
```

### Gestión de Tareas

```bash
# Variable con el token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 3. Crear una tarea
curl -X POST "http://localhost:8000/todo/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Estudiar FastAPI",
    "description": "Completar curso de FastAPI",
    "priority": 5,
    "complete": false
  }'

# 4. Listar todas las tareas
curl -X GET "http://localhost:8000/" \
  -H "Authorization: Bearer $TOKEN"

# 5. Actualizar una tarea
curl -X PUT "http://localhost:8000/todo/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Estudiar FastAPI - Completado",
    "description": "Curso completado exitosamente",
    "priority": 5,
    "complete": true
  }'

# 6. Eliminar una tarea
curl -X DELETE "http://localhost:8000/todo/1" \
  -H "Authorization: Bearer $TOKEN"
```

## Estructura de Rutas

Las rutas están organizadas en módulos mediante APIRouter:

- `main.py` incluye todos los routers
- Cada router gestiona un dominio específico
- Separación clara de responsabilidades
- Fácil mantenimiento y escalabilidad

```python
# En main.py
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
```

## Documentación Adicional

El proyecto incluye documentación detallada en la carpeta `docs/`:

- **AUTH_DOCUMENTACION.md**: Explicación completa del sistema de autenticación, JWT, bcrypt y OAuth2
- **TODOS_DOCUMENTACION.md**: Guía detallada del módulo de tareas con énfasis en inyección de dependencias

Estas documentaciones incluyen:

- Análisis línea por línea del código
- Explicaciones de conceptos clave
- Diagramas de flujo
- Ejemplos prácticos
- Consideraciones de seguridad

## Contribución

Este proyecto es parte de un curso de aprendizaje de FastAPI. El código está diseñado para ser educativo y demostrar las mejores prácticas en el desarrollo de APIs REST con FastAPI.

## Licencia

Proyecto educativo - Libre para uso académico y aprendizaje.
