# Documentación Detallada - auth.py

## Propósito General

Este módulo implementa un **sistema completo de autenticación y autorización** para una API REST construida con FastAPI. Maneja el registro de usuarios, inicio de sesión, generación de tokens JWT (JSON Web Tokens) y validación de usuarios autenticados.

---

## Importaciones y Dependencias

### Librerías Estándar de Python

```python
from datetime import timedelta, datetime, timezone
```

- **datetime**: Maneja fechas y horas para calcular la expiración de tokens
- **timedelta**: Representa duraciones de tiempo (ej: 20 minutos)
- **timezone**: Proporciona información de zona horaria (UTC)

### FastAPI y Pydantic

```python
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
```

- **Annotated**: Permite agregar metadata a los tipos (nuevo en Python 3.9+)
- **APIRouter**: Permite organizar endpoints en módulos separados
- **Depends**: Sistema de inyección de dependencias de FastAPI
- **HTTPException**: Para lanzar errores HTTP con códigos de estado
- **BaseModel**: Clase base de Pydantic para validación de datos
- **status**: Códigos de estado HTTP (200, 201, 401, etc.)

### SQLAlchemy

```python
from sqlalchemy.orm import Session
```

- **Session**: Tipo de dato que representa una sesión de base de datos para hacer queries

### Seguridad y Autenticación

```python
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
```

- **CryptContext**: De la librería `passlib`, maneja el hashing de contraseñas con bcrypt
- **OAuth2PasswordRequestForm**: Formulario estándar OAuth2 para login (username + password)
- **OAuth2PasswordBearer**: Esquema de autenticación que extrae el token del header
- **jwt**: Para crear y decodificar JSON Web Tokens
- **JWTError**: Excepción cuando hay problemas al decodificar tokens

### Módulos Locales

```python
from database import SessionLocal
from models import Users
```

- **SessionLocal**: Fábrica de sesiones de base de datos
- **Users**: Modelo SQLAlchemy de la tabla de usuarios

---

## Configuración del Router

```python
router = APIRouter(
    prefix="/auth",
    tags=['auth']
)
```

- **prefix="/auth"**: Todos los endpoints de este router tendrán el prefijo `/auth`
  - Ejemplo: `@router.post("/")` se convierte en `POST /auth/`
  - Ejemplo: `@router.post("/token")` se convierte en `POST /auth/token`
- **tags=['auth']**: Agrupa estos endpoints bajo la etiqueta "auth" en la documentación automática (Swagger UI)

---

## Configuración de Seguridad

### Constantes de JWT

```python
SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'
```

- **SECRET_KEY**: Clave secreta para firmar y verificar tokens JWT
  - ⚠️ **Importante**: En producción, esta clave debe estar en variables de entorno, no hardcodeada
  - Esta clave garantiza que los tokens no puedan ser falsificados
- **ALGORITHM**: Algoritmo de firma. HS256 (HMAC-SHA256) es simétrico (misma clave para firmar y verificar)

### Contexto de Bcrypt

```python
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
```

- **CryptContext**: Maneja el hashing de contraseñas
- **schemes=['bcrypt']**: Usa el algoritmo bcrypt (muy seguro para passwords)
- **deprecated='auto'**: Actualiza automáticamente hashes antiguos si se mejora el esquema
- **¿Por qué bcrypt?**: Es lento intencionalmente, lo que dificulta ataques de fuerza bruta

### OAuth2 Bearer

```python
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
```

- **OAuth2PasswordBearer**: Define el esquema de autenticación
- **tokenUrl='auth/token'**: Indica dónde obtener el token (endpoint de login)
- Este objeto se usa como dependencia para extraer el token del header `Authorization: Bearer <token>`

---

## Modelos Pydantic

### CreateUserRequest

```python
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
```

**Propósito**: Define la estructura de datos para crear un nuevo usuario

**Campos**:

- **username**: Nombre de usuario único
- **email**: Correo electrónico único
- **first_name**: Nombre del usuario
- **last_name**: Apellido del usuario
- **password**: Contraseña en texto plano (se hasheará antes de guardar)
- **role**: Rol del usuario (ej: "admin", "user")

**Validación automática**: Pydantic valida que todos los campos sean strings y estén presentes

### Token

```python
class Token(BaseModel):
    access_token: str
    token_type: str
```

**Propósito**: Define la estructura de respuesta al hacer login

**Campos**:

- **access_token**: El token JWT generado
- **token_type**: Tipo de token (siempre "bearer" en este caso)

**Ejemplo de respuesta**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## Gestión de Base de Datos

### Función get_db()

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Propósito**: Crea y cierra sesiones de base de datos de forma segura

**Funcionamiento**:

1. **Crea** una nueva sesión de base de datos con `SessionLocal()`
2. **yield db**: Entrega la sesión (pausa aquí hasta que termine el endpoint)
3. **finally**: Garantiza que la sesión se cierre, incluso si hay errores

**¿Por qué yield?**: Es un generador. FastAPI lo maneja automáticamente:

- El código antes de `yield` se ejecuta antes del endpoint
- El código después de `yield` se ejecuta después del endpoint

### Dependencia db_dependency

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

**Propósito**: Crea un tipo anotado reutilizable para inyectar la base de datos

**Uso en endpoints**:

```python
async def create_user(db: db_dependency, ...):
    # db es una sesión de base de datos inyectada automáticamente
```

**Ventajas**:

- Código más limpio y reutilizable
- FastAPI automáticamente llama a `get_db()` y gestiona el ciclo de vida

---

## Funciones de Autenticación

### authenticate_user()

```python
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user
```

**Propósito**: Verifica si las credenciales (usuario y contraseña) son válidas

**Parámetros**:

- **username**: Nombre de usuario a verificar
- **password**: Contraseña en texto plano
- **db**: Sesión de base de datos

**Proceso paso a paso**:

1. **Buscar usuario en la BD**:

   ```python
   user = db.query(Users).filter(Users.username == username).first()
   ```

   - Busca un usuario con ese username
   - `.first()` devuelve el primer resultado o `None` si no existe

2. **Verificar existencia**:

   ```python
   if not user:
       return False
   ```

   - Si el usuario no existe, retorna `False`

3. **Verificar contraseña**:

   ```python
   if not bcrypt_context.verify(password, user.hashed_password):
       return False
   ```

   - `bcrypt_context.verify()` compara la contraseña en texto plano con el hash almacenado
   - Si no coinciden, retorna `False`

4. **Autenticación exitosa**:

   ```python
   return user
   ```

   - Si todo es correcto, retorna el objeto completo del usuario

**Retorno**:

- `False`: Credenciales inválidas
- `user`: Objeto Users si las credenciales son correctas

---

### create_access_token()

```python
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
```

**Propósito**: Genera un token JWT con la información del usuario

**Parámetros**:

- **username**: Nombre de usuario
- **user_id**: ID único del usuario
- **role**: Rol del usuario (admin, user, etc.)
- **expires_delta**: Duración de validez del token (ej: 20 minutos)

**Proceso paso a paso**:

1. **Crear payload del token**:

   ```python
   encode = {'sub': username, 'id': user_id, 'role': role}
   ```

   - **sub**: "Subject" - estándar JWT para el identificador principal (username)
   - **id**: ID numérico del usuario
   - **role**: Rol para autorización

2. **Calcular fecha de expiración**:

   ```python
   expires = datetime.now(timezone.utc) + expires_delta
   ```

   - Toma la hora actual en UTC
   - Le suma la duración especificada (ej: 20 minutos)

3. **Agregar expiración al payload**:

   ```python
   encode.update({'exp': expires})
   ```

   - **exp**: Claim estándar JWT para la fecha de expiración
   - JWT automáticamente invalida tokens expirados

4. **Codificar y firmar el token**:

   ```python
   return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
   ```

   - Convierte el diccionario a formato JWT
   - Firma con la SECRET_KEY usando HS256
   - Retorna un string como: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**Ejemplo de token decodificado**:

```json
{
  "sub": "juan123",
  "id": 42,
  "role": "user",
  "exp": 1703165400
}
```

---

### get_current_user()

```python
async def get_current_user(token : Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user")
        
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user")
```

**Propósito**: Valida el token JWT y extrae la información del usuario actual

**Parámetros**:

- **token**: Extraído automáticamente del header `Authorization: Bearer <token>` por `oauth2_bearer`

**Proceso paso a paso**:

1. **Decodificar el token**:

   ```python
   payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
   ```

   - Verifica la firma del token con la SECRET_KEY
   - Verifica que no esté expirado (claim 'exp')
   - Si es inválido o expirado, lanza `JWTError`

2. **Extraer datos del payload**:

   ```python
   username: str = payload.get('sub')
   user_id: int = payload.get('id')
   user_role: str = payload.get('role')
   ```

   - Obtiene los valores que se pusieron al crear el token

3. **Validar datos mínimos**:

   ```python
   if username is None or user_id is None:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                       detail="Could not validate user")
   ```

   - Si faltan datos esenciales, retorna error 401 (No autorizado)

4. **Retornar información del usuario**:

   ```python
   return {'username': username, 'id': user_id, 'user_role': user_role}
   ```

   - Retorna un diccionario con la información del usuario autenticado

5. **Manejo de errores**:

   ```python
   except JWTError:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                       detail="Could not validate user")
   ```

   - Captura cualquier error de JWT (token inválido, expirado, etc.)
   - Retorna error 401

**Uso como dependencia**:

```python
@router.get("/perfil")
async def get_profile(user: dict = Depends(get_current_user)):
    # user contiene: {'username': '...', 'id': ..., 'user_role': '...'}
    return user
```

---

## Endpoints de la API

### 1. POST /auth/ - Crear Usuario

```python
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
```

**Ruta completa**: `POST /auth/`

**Propósito**: Registra un nuevo usuario en el sistema

**Parámetros**:

- **db**: Sesión de base de datos (inyectada automáticamente)
- **create_user_request**: Datos del usuario a crear (validados por Pydantic)

**Status Code**: `201 CREATED` - Indica que se creó un nuevo recurso

**Cuerpo de la petición (JSON)**:

```json
{
  "username": "juan123",
  "email": "juan@email.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "password": "mipassword123",
  "role": "user"
}
```

**Proceso paso a paso**:

1. **Crear instancia del modelo**:

   ```python
   create_user_model = Users(
       email = create_user_request.email,
       username = create_user_request.username,
       first_name = create_user_request.first_name,
       last_name = create_user_request.last_name,
       role = create_user_request.role,
       hashed_password = bcrypt_context.hash(create_user_request.password),
       is_active = True
   )
   ```

   - Crea un objeto `Users` (modelo SQLAlchemy)
   - **IMPORTANTE**: La contraseña se hashea con bcrypt antes de guardar
   - `is_active = True`: El usuario está activo por defecto

2. **Guardar en base de datos**:

   ```python
   db.add(create_user_model)
   db.commit()
   ```

   - `db.add()`: Agrega el usuario a la sesión
   - `db.commit()`: Guarda los cambios en la base de datos

**Respuesta**: Status 201 (sin cuerpo de respuesta)

**Posibles mejoras** (no implementadas aquí):

- Validar que username/email no existan ya
- Retornar el usuario creado
- Validar fortaleza de la contraseña

---

### 2. POST /auth/token - Login

```python
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
```

**Ruta completa**: `POST /auth/token`

**Propósito**: Autentica al usuario y genera un token de acceso

**Parámetros**:

- **form_data**: Formulario OAuth2 con username y password (inyectado automáticamente)
- **db**: Sesión de base de datos

**response_model=Token**: FastAPI valida y documenta que la respuesta sigue el modelo `Token`

**Formato de la petición**:

```bash
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=juan123&password=mipassword123
```

**Nota**: OAuth2 requiere `application/x-www-form-urlencoded`, no JSON

**Proceso paso a paso**:

1. **Autenticar usuario**:

   ```python
   user = authenticate_user(form_data.username, form_data.password, db)
   ```

   - Llama a la función que verifica credenciales
   - Retorna el usuario o `False`

2. **Verificar autenticación**:

   ```python
   if not user:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                           detail='Could not validate user.')
   ```

   - Si las credenciales son incorrectas, retorna error 401

3. **Generar token**:

   ```python
   token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
   ```

   - Crea un token JWT válido por 20 minutos
   - Incluye username, id y role del usuario

4. **Retornar respuesta**:

   ```python
   return {'access_token': token, 'token_type': 'bearer'}
   ```

   - Retorna el token en formato estándar OAuth2

**Respuesta exitosa** (JSON):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqdWFuMTIzIiwiaWQiOjQyLCJyb2xlIjoidXNlciIsImV4cCI6MTcwMzE2NTQwMH0.xyz...",
  "token_type": "bearer"
}
```

**Cómo usar el token**:

```bash
GET /api/endpoint
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Flujo Completo de Autenticación

### Registro de Usuario

```bash
1. Cliente                  2. API                    3. Base de Datos
    |                          |                            |
    |--- POST /auth/ --------->|                            |
    |    {username, password}  |                            |
    |                          |                            |
    |                          |-- Hash password con bcrypt |
    |                          |                            |
    |                          |-- INSERT INTO users ------>|
    |                          |                            |
    |                          |<-- Usuario guardado -------|
    |                          |                            |
    |<--- 201 Created ---------|                            |
```

### Inicio de Sesión

```bash
1. Cliente                  2. API                    3. Base de Datos
    |                          |                            |
    |-- POST /auth/token ----->|                            |
    |   username & password    |                            |
    |                          |                            |
    |                          |-- SELECT * FROM users ---->|
    |                          |    WHERE username=...      |
    |                          |                            |
    |                          |<-- Usuario encontrado -----|
    |                          |                            |
    |                          |-- Verificar password       |
    |                          |   con bcrypt               |
    |                          |                            |
    |                          |-- Crear JWT token          |
    |                          |   con exp: 20 min          |
    |                          |                            |
    |<-- {access_token} -------|                            |
```

### Usar Endpoint Protegido

```bash
1. Cliente                  2. API
    |                          |
    |-- GET /api/recurso ----->|
    |   Header: Authorization  |
    |   Bearer <token>         |
    |                          |
    |                          |-- Extraer token del header
    |                          |
    |                          |-- Decodificar y verificar JWT
    |                          |   ✓ Firma correcta?
    |                          |   ✓ No expirado?
    |                          |
    |                          |-- Extraer user info del token
    |                          |
    |                          |-- Ejecutar lógica del endpoint
    |                          |
    |<-- 200 OK + datos -------|
```

---

## Seguridad Implementada

### 1. Hashing de Contraseñas (Bcrypt)

**¿Qué es?**: Nunca se guardan contraseñas en texto plano

**Cómo funciona**:

- Usuario envía: `password123`
- Se guarda: `$2b$12$KIXx8v4Y9f5G.../...` (hash irreversible)
- Para verificar: Bcrypt compara el hash, no la contraseña

**Ventajas de bcrypt**:

- Computacionalmente costoso (lento intencionalmente)
- Incluye "salt" automático (previene rainbow tables)
- Ajustable en dificultad

### 2. JSON Web Tokens (JWT)

**¿Qué es?**: Token autofirmado que contiene información del usuario

**Estructura de un JWT**:

```bash
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9  ← Header (algoritmo)
.
eyJzdWIiOiJqdWFuMTIzIiwiaWQiOjQyLCJl  ← Payload (datos)
eHAiOjE3MDMxNjU0MDB9
.
h3BxXYZ...                              ← Signature (firma)
```

**Ventajas**:

- Stateless: No requiere almacenar sesiones en el servidor
- Autocontenido: Incluye toda la info necesaria
- Verificable: La firma previene falsificación

### 3. OAuth2 Password Bearer

**¿Qué es?**: Estándar de la industria para autenticación

**Flujo**:

1. Usuario envía credenciales a `/token`
2. Recibe un token de acceso
3. Incluye el token en cada petición: `Authorization: Bearer <token>`

### 4. Expiración de Tokens

```python
timedelta(minutes=20)
```

- Los tokens solo son válidos por 20 minutos
- Después se debe hacer login nuevamente
- Reduce el riesgo si un token es robado

---

## Diagrama de Dependencias

```bash
┌─────────────────────────────────────────────┐
│              Endpoint Handler                │
│    async def create_user(db: db_dependency)  │
└────────────────┬────────────────────────────┘
                 │ inyecta
                 ▼
┌─────────────────────────────────────────────┐
│          db_dependency                       │
│   Annotated[Session, Depends(get_db)]       │
└────────────────┬────────────────────────────┘
                 │ ejecuta
                 ▼
┌─────────────────────────────────────────────┐
│            get_db()                          │
│   Crea SessionLocal() y garantiza .close()  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│     oauth2_bearer (extrae token)             │
│                  │                           │
└──────────────────┼───────────────────────────┘
                   │ pasa a
                   ▼
┌─────────────────────────────────────────────┐
│       get_current_user(token)                │
│   Decodifica JWT y valida                   │
└─────────────────────────────────────────────┘
```

---

## Ejemplos de Uso

### Con cURL

**1. Crear usuario**:

```bash
curl -X POST "http://localhost:8000/auth/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan123",
    "email": "juan@email.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "password": "securepass123",
    "role": "user"
  }'
```

**2. Login (obtener token)**:

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=juan123&password=securepass123"
```

**Respuesta**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
```

**3. Usar endpoint protegido**:

```bash
curl -X GET "http://localhost:8000/api/recurso" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1..."
```

### Con Python (requests)

```python
import requests

# 1. Registrar usuario
response = requests.post("http://localhost:8000/auth/", json={
    "username": "maria456",
    "email": "maria@email.com",
    "first_name": "María",
    "last_name": "González",
    "password": "password123",
    "role": "user"
})
print(response.status_code)  # 201

# 2. Login
response = requests.post("http://localhost:8000/auth/token", data={
    "username": "maria456",
    "password": "password123"
})
token = response.json()["access_token"]

# 3. Usar API con token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/recurso", headers=headers)
print(response.json())
```

---

## Consideraciones Importantes

### Seguridad

1. **SECRET_KEY hardcodeada**:
   - ❌ Mala práctica para producción
   - ✅ Usar variables de entorno: `os.getenv("SECRET_KEY")`

2. **Sin validación de duplicados**:
   - El endpoint de registro no verifica si el username/email ya existe
   - Puede causar errores de base de datos

3. **Sin rate limiting**:
   - No hay protección contra ataques de fuerza bruta
   - Considerar `slowapi` o middleware similar

### Funcionalidad

1. **Expiración del token**:
   - 20 minutos puede ser corto o largo según el caso de uso
   - Considerar implementar refresh tokens

2. **Sin logout**:
   - JWT es stateless, no hay forma de "invalidar" un token
   - El token seguirá siendo válido hasta que expire

3. **Sin validación de rol**:
   - El campo `role` se acepta sin validación
   - Considerar usar Enum: `role: Literal["admin", "user"]`

---

## Conceptos Clave para Aprender

### 1. ¿Por qué JWT en lugar de sesiones?

**Sesiones tradicionales**:

- Servidor guarda sesión en memoria/BD
- Cookie contiene solo el ID de sesión
- Requiere lookup en cada petición

**JWT**:

- No requiere almacenamiento en servidor (stateless)
- Token contiene toda la información
- Más escalable (no compartir sesiones entre servidores)

### 2. ¿Por qué async/await?

```python
async def create_user(...)
```

- FastAPI soporta código asíncrono
- Permite manejar muchas peticiones simultáneas
- No es obligatorio (puede ser `def` en lugar de `async def`)

### 3. ¿Qué es OAuth2?

- **OAuth2**: Protocolo estándar de autorización
- **Password Flow**: Usuario envía username/password directamente
- **Bearer Token**: Token que "porta" (bear) los permisos del usuario

### 4. Sistema de inyección de dependencias

```python
async def endpoint(db: db_dependency):
    # FastAPI automáticamente:
    # 1. Llama a get_db()
    # 2. Pasa la sesión como 'db'
    # 3. Cierra la sesión al terminar
```

**Ventajas**:

- Código más limpio y reutilizable
- Testeable (fácil mockear dependencias)
- Gestión automática de recursos

---

## Próximos Pasos

### Mejoras sugeridas

1. **Variables de entorno**:

   ```python
   from dotenv import load_dotenv
   import os
   
   SECRET_KEY = os.getenv("SECRET_KEY")
   ```

2. **Validación de duplicados**:

   ```python
   existing = db.query(Users).filter(
       (Users.username == username) | (Users.email == email)
   ).first()
   if existing:
       raise HTTPException(status_code=400, detail="User exists")
   ```

3. **Refresh tokens**:
   - Token de acceso de corta duración (15 min)
   - Refresh token de larga duración (7 días)
   - Permite renovar sin volver a hacer login

4. **Middleware de autenticación**:

   ```python
   user = Depends(get_current_user)
   ```

   - Proteger endpoints automáticamente

5. **Roles y permisos**:

   ```python
   def require_admin(user: dict = Depends(get_current_user)):
       if user["user_role"] != "admin":
           raise HTTPException(status_code=403)
       return user
   ```

---

## Recursos Adicionales

- **FastAPI Security**: <https://fastapi.tiangolo.com/tutorial/security/>
- **JWT**: <https://jwt.io/>
- **OAuth2**: <https://oauth.net/2/>
- **Passlib**: <https://passlib.readthedocs.io/>
- **SQLAlchemy**: <https://docs.sqlalchemy.org/>

---

## Resumen

Este módulo implementa un **sistema robusto de autenticación** con:

- ✅ Registro de usuarios con contraseñas hasheadas (bcrypt)
- ✅ Login que genera tokens JWT
- ✅ Validación de tokens para proteger endpoints
- ✅ Estándar OAuth2 para compatibilidad
- ✅ Inyección de dependencias para código limpio
- ✅ Expiración automática de tokens

**Flujo básico**:

1. Usuario se registra → Contraseña hasheada en BD
2. Usuario hace login → Recibe token JWT
3. Usuario usa token → Accede a recursos protegidos

Es un sistema de autenticación **listo para producción** con pequeños ajustes de seguridad.
