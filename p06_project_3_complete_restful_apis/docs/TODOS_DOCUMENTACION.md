# Documentación Detallada - todos.py

## Propósito General

Este módulo implementa un **CRUD completo (Create, Read, Update, Delete) de Tareas (Todos)** para una aplicación de lista de tareas. Cada usuario solo puede ver y gestionar sus propias tareas gracias a un sistema de autenticación y autorización integrado.

---

## Importaciones y Dependencias

### Typing y Anotaciones

```python
from typing import Annotated
```

- **Annotated**: Permite agregar metadata a los tipos (Python 3.9+)
- Se usa para crear tipos reutilizables con dependencias inyectadas
- Ejemplo: `Annotated[Session, Depends(get_db)]` = "Es una Session Y tiene esta dependencia"

### Pydantic

```python
from pydantic import BaseModel, Field
```

- **BaseModel**: Clase base para crear modelos de validación de datos
- **Field**: Permite agregar validaciones y restricciones a los campos
  - `min_length`: Longitud mínima de un string
  - `max_length`: Longitud máxima de un string
  - `gt` (greater than): Mayor que
  - `lt` (less than): Menor que

**¿Por qué Pydantic?**: Valida automáticamente los datos de entrada, convierte tipos y genera documentación automática.

### SQLAlchemy

```python
from sqlalchemy.orm import Session
```

- **Session**: Representa una "conversación" con la base de datos
- Permite hacer queries (consultas), insertar, actualizar y eliminar registros
- Gestiona transacciones y mantiene el estado de los objetos

### FastAPI

```python
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
```

- **APIRouter**: Permite organizar endpoints en módulos separados (como un mini-app dentro de la app principal)
- **Depends**: Sistema de inyección de dependencias (¡MUY IMPORTANTE!)
- **HTTPException**: Para lanzar errores HTTP con códigos de estado
- **Path**: Validador para parámetros de ruta (path parameters)
- **status**: Constantes para códigos de estado HTTP (200, 201, 404, etc.)

### Módulos Locales

```python
from models import Todos
from database import SessionLocal
from .auth import get_current_user
```

- **Todos**: Modelo SQLAlchemy de la tabla de tareas
- **SessionLocal**: Fábrica de sesiones de base de datos
- **get_current_user**: Función del módulo auth que valida tokens y extrae info del usuario
- **`.auth`**: El punto indica que es un módulo hermano en la misma carpeta `routers/`

---

## Configuración del Router

```python
router = APIRouter()
```

**¿Qué es un APIRouter?**

- Es como una "sub-aplicación" de FastAPI
- Agrupa endpoints relacionados (en este caso, todos los relacionados con tareas)
- Luego se incluye en la aplicación principal con `app.include_router(router)`

**Diferencia con el router de auth.py**:

```python
# En auth.py:
router = APIRouter(prefix="/auth", tags=['auth'])

# En todos.py:
router = APIRouter()  # Sin prefix ni tags
```

- Este router **no tiene prefix** porque el prefix se define al incluirlo en `main.py`
- Esto da más flexibilidad para organizar las rutas

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

**Propósito**: Crea y cierra sesiones de base de datos automáticamente

**Análisis detallado**:

1. **`db = SessionLocal()`**:
   - Crea una nueva sesión de base de datos
   - Es como abrir una conexión temporal para trabajar

2. **`try:`**:
   - Inicia un bloque de manejo de errores

3. **`yield db`**:
   - **CLAVE**: `yield` convierte esto en un generador
   - Pausa la ejecución aquí y "entrega" la sesión
   - El endpoint usa la sesión
   - Cuando el endpoint termina, la ejecución vuelve aquí

4. **`finally:`**:
   - Se ejecuta SIEMPRE, incluso si hay errores
   - Garantiza que la conexión se cierre

5. **`db.close()`**:
   - Cierra la sesión y libera recursos

**Flujo de ejecución**:

```bash
1. FastAPI llama a get_db()
2. Se crea SessionLocal()
3. yield pausa y entrega 'db'
   ↓
4. El endpoint ejecuta su código usando 'db'
   ↓
5. El endpoint termina (con éxito o error)
6. La ejecución vuelve a get_db()
7. finally: db.close() se ejecuta
8. La función termina
```

**¿Por qué es importante?**:

- Previene fugas de memoria (memory leaks)
- Evita errores por conexiones no cerradas
- Es una práctica estándar en aplicaciones de base de datos

---

## INYECCIÓN DE DEPENDENCIAS - Concepto Fundamental

### ¿Qué es la Inyección de Dependencias?

**Definición simple**: Es un patrón donde en lugar de crear objetos dentro de una función, se los "inyectan" desde fuera.

**Ejemplo sin inyección de dependencias**:

```python
def read_all():
    db = SessionLocal()  # Crear aquí
    try:
        todos = db.query(Todos).all()
        return todos
    finally:
        db.close()  # Cerrar aquí
```

**Problemas**:

- Código repetitivo en cada función
- Difícil de testear (no puedes mockear la BD fácilmente)
- Mezcla lógica de negocio con gestión de recursos

**Ejemplo CON inyección de dependencias**:

```python
def read_all(db: Session = Depends(get_db)):
    # db ya viene creada y se cerrará automáticamente
    todos = db.query(Todos).all()
    return todos
```

**Ventajas**:

- Código más limpio y simple
- Fácil de testear (inyectas una BD falsa)
- Separación de responsabilidades
- FastAPI gestiona el ciclo de vida automáticamente

---

### db_dependency - Dependencia de Base de Datos

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

**Desglose completo**:

1. **`Session`**:
   - El tipo de dato (de SQLAlchemy)
   - Indica que la variable será una sesión de base de datos

2. **`Depends(get_db)`**:
   - Le dice a FastAPI: "Llama a `get_db()` y usa lo que retorna"
   - FastAPI ejecutará `get_db()` antes del endpoint
   - FastAPI también ejecutará el código después del `yield` cuando termine

3. **`Annotated[...]`**:
   - Combina el tipo (`Session`) con la metadata (`Depends(get_db)`)
   - Es la forma moderna de declarar dependencias en Python 3.9+

4. **`db_dependency`**:
   - Es un "alias" reutilizable
   - Puedes usarlo en múltiples funciones sin repetir código

**Uso en un endpoint**:

```python
async def read_all(db: db_dependency):
    # FastAPI automáticamente:
    # 1. Llama a get_db()
    # 2. Obtiene la sesión con yield db
    # 3. Pasa la sesión como parámetro 'db'
    # 4. Ejecuta el código del endpoint
    # 5. Cierra la sesión con db.close()
```

**Forma antigua (antes de Python 3.9)**:

```python
async def read_all(db: Session = Depends(get_db)):
    # Mismo resultado, pero más verboso
```

**Comparación**:

```python
# Sin inyección: Tienes que gestionar todo manualmente
def endpoint():
    db = SessionLocal()
    try:
        # tu código
    finally:
        db.close()

# Con inyección: FastAPI lo hace por ti
async def endpoint(db: db_dependency):
    # tu código
    # db se cierra automáticamente
```

---

### user_dependency - Dependencia de Usuario

```python
user_dependency = Annotated[dict, Depends(get_current_user)]
```

**Desglose completo**:

1. **`dict`**:
   - El tipo de dato que se retorna
   - `get_current_user` retorna un diccionario: `{'username': '...', 'id': ..., 'user_role': '...'}`

2. **`Depends(get_current_user)`**:
   - Le dice a FastAPI: "Llama a `get_current_user()` primero"
   - `get_current_user` extrae y valida el token JWT
   - Si el token es inválido, lanza un error 401 automáticamente

3. **`user_dependency`**:
   - Alias reutilizable para inyectar el usuario autenticado

**¿Qué hace get_current_user()?** (del módulo auth.py):

1. Extrae el token del header `Authorization: Bearer <token>`
2. Decodifica el token JWT
3. Valida que no esté expirado
4. Extrae la información del usuario (username, id, role)
5. Retorna un diccionario con esa información
6. Si algo falla, lanza HTTPException 401

**Uso en un endpoint**:

```python
async def read_all(user: user_dependency, db: db_dependency):
    # FastAPI automáticamente:
    # 1. Extrae el token del header
    # 2. Llama a get_current_user(token)
    # 3. Valida el token
    # 4. Pasa el diccionario del usuario como 'user'
    # 5. Si el token es inválido, retorna 401 SIN ejecutar el endpoint
```

**Ejemplo de 'user'**:

```python
user = {
    'username': 'juan123',
    'id': 42,
    'user_role': 'user'
}

# Acceder a los valores:
user_id = user.get('id')  # 42
username = user.get('username')  # 'juan123'
```

---

### 🔗 Cadena de Dependencias

Cuando escribes:

```python
async def read_all(user: user_dependency, db: db_dependency):
```

FastAPI ejecuta esta secuencia:

```bash
1. Cliente hace petición: GET /todo/
   ↓
2. FastAPI ve que necesita 'user' y 'db'
   ↓
3. Ejecuta get_db()
   - Crea SessionLocal()
   - yield db (pausa)
   ↓
4. Ejecuta get_current_user()
   - Extrae token del header
   - Valida token JWT
   - Retorna diccionario de usuario
   ↓
5. Ejecuta read_all(user=dict, db=Session)
   - Lógica del endpoint
   ↓
6. Endpoint termina y retorna respuesta
   ↓
7. get_db() continúa
   - finally: db.close()
   ↓
8. Respuesta enviada al cliente
```

**Si algo falla**:

- Si el token es inválido → `get_current_user` lanza 401 → Endpoint NO se ejecuta
- Si hay error en el endpoint → `db.close()` se ejecuta de todos modos (finally)

---

## Modelo de Validación - TodoRequest

```python
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
```

**Propósito**: Define y valida la estructura de datos para crear/actualizar tareas

### Análisis campo por campo

#### 1. title (Título)

```python
title: str = Field(min_length=3)
```

- **Tipo**: `str` (string/texto)
- **Validación**: Mínimo 3 caracteres
- **Ejemplos válidos**: `"Comprar pan"`, `"Estudiar Python"`
- **Ejemplos inválidos**: `"ab"` (muy corto), `123` (no es string)

#### 2. description (Descripción)

```python
description: str = Field(min_length=3, max_length=100)
```

- **Tipo**: `str`
- **Validaciones**:
  - Mínimo 3 caracteres
  - Máximo 100 caracteres
- **Ejemplo válido**: `"Ir al supermercado y comprar leche, pan y huevos"`
- **Ejemplo inválido**: `"ab"` (muy corto) o un texto de 200 caracteres (muy largo)

#### 3. priority (Prioridad)

```python
priority: int = Field(gt=0, lt=6)
```

- **Tipo**: `int` (entero)
- **Validaciones**:
  - `gt=0`: Greater Than 0 → Mayor que 0
  - `lt=6`: Less Than 6 → Menor que 6
  - **Valores válidos**: 1, 2, 3, 4, 5
- **Ejemplo**: `3` = prioridad media
- **Ejemplos inválidos**: `0` (no mayor que 0), `6` (no menor que 6), `"3"` (string, no int)

#### 4. complete (Completada)

```python
complete: bool
```

- **Tipo**: `bool` (booleano)
- **Valores válidos**: `true` o `false`
- **Uso**: Indica si la tarea está completada o no

### Ejemplo de JSON válido

```json
{
  "title": "Estudiar FastAPI",
  "description": "Completar el curso de FastAPI y hacer los ejercicios",
  "priority": 4,
  "complete": false
}
```

### ¿Qué pasa si envías datos inválidos?

Ejemplo 1: Title muy corto

```json
{
  "title": "ab",
  "description": "Descripción válida",
  "priority": 3,
  "complete": false
}
```

**Respuesta**: Error 422 (Unprocessable Entity)

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 3 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

Ejemplo 2: Priority fuera de rango

```json
{
  "title": "Tarea válida",
  "description": "Descripción válida",
  "priority": 10,
  "complete": false
}
```

**Respuesta**: Error 422

```json
{
  "detail": [
    {
      "loc": ["body", "priority"],
      "msg": "ensure this value is less than 6",
      "type": "value_error.number.not_lt"
    }
  ]
}
```

**Ventajas de Pydantic**:

- ✅ Validación automática antes de ejecutar tu código
- ✅ Mensajes de error claros y descriptivos
- ✅ Conversión de tipos automática
- ✅ Documentación automática en Swagger UI

---

## Endpoints de la API

### 1. GET / - Listar Todas las Tareas del Usuario

```python
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
```

**Ruta completa**: `GET /` (o lo que se defina en main.py, ej: `GET /todos/`)

**Propósito**: Obtener todas las tareas del usuario autenticado

**Parámetros**:

- **user**: Usuario autenticado (inyectado por `user_dependency`)
- **db**: Sesión de base de datos (inyectada por `db_dependency`)

**Status Code**: `200 OK` - Solicitud exitosa

**Análisis línea por línea**:

#### 1. Verificación de autenticación

```python
if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
```

- **Propósito**: Doble verificación de que el usuario existe
- **¿Cuándo es None?**: Técnicamente `get_current_user` ya lanza 401 si falla, pero esto es una capa extra de seguridad
- **401 UNAUTHORIZED**: El usuario no está autenticado o el token es inválido

#### 2. Consulta a la base de datos

```python
return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
```

**Desglose completo**:

```python
db.query(Todos)  # 1. SELECT * FROM todos
.filter(Todos.owner_id == user.get('id'))  # 2. WHERE owner_id = <id_del_usuario>
.all()  # 3. Obtener TODOS los resultados
```

**¿Qué hace cada parte?**:

1. **`db.query(Todos)`**:
   - Inicia una consulta sobre la tabla Todos
   - Equivalente SQL: `SELECT * FROM todos`

2. **`.filter(Todos.owner_id == user.get('id'))`**:
   - Filtra solo las tareas que pertenecen al usuario autenticado
   - `user.get('id')` obtiene el ID del usuario del diccionario
   - Equivalente SQL: `WHERE owner_id = 42` (si el ID del usuario es 42)

3. **`.all()`**:
   - Ejecuta la query y retorna una lista con todos los resultados
   - Si no hay resultados, retorna `[]` (lista vacía)

**SQL equivalente completo**:

```sql
SELECT * FROM todos WHERE owner_id = 42;
```

**Ejemplo de respuesta**:

```json
[
  {
    "id": 1,
    "title": "Estudiar FastAPI",
    "description": "Completar el módulo 3",
    "priority": 4,
    "complete": false,
    "owner_id": 42
  },
  {
    "id": 2,
    "title": "Hacer ejercicio",
    "description": "30 minutos de cardio",
    "priority": 3,
    "complete": true,
    "owner_id": 42
  }
]
```

**Seguridad importante**:

- Cada usuario **solo ve sus propias tareas**
- El filtro `owner_id == user.get('id')` garantiza el aislamiento
- No hay forma de que un usuario vea tareas de otro

---

### 2. GET /todo/{todo_id} - Obtener Una Tarea Específica

```python
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()   
    if todo_model is not None:
        return todo_model
    
    raise HTTPException(status_code=404, detail="Todo not found")
```

**Ruta completa**: `GET /todo/5` (donde 5 es el ID de la tarea)

**Propósito**: Obtener los detalles de una tarea específica

**Parámetros**:

- **user**: Usuario autenticado (inyectado)
- **db**: Sesión de BD (inyectada)
- **todo_id**: ID de la tarea (extraído de la URL)

#### Parámetro de Path con validación

```python
todo_id: int = Path(gt=0)
```

**Desglose**:

- **`todo_id`**: Nombre del parámetro (debe coincidir con `{todo_id}` en la ruta)
- **`int`**: Tipo de dato esperado
- **`Path(gt=0)`**:
  - Indica que viene de la ruta (path parameter)
  - `gt=0`: Greater than 0 → Solo acepta números positivos

**Ejemplos**:

- ✅ `GET /todo/1` → todo_id = 1 (válido)
- ✅ `GET /todo/999` → todo_id = 999 (válido)
- ❌ `GET /todo/0` → Error 422 (no mayor que 0)
- ❌ `GET /todo/-5` → Error 422 (no mayor que 0)
- ❌ `GET /todo/abc` → Error 422 (no es entero)

#### Verificación de autenticación

```python
if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
```

- Misma verificación que en el endpoint anterior

#### Consulta con doble filtro

```python
todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
```

**Desglose completo**:

1. **`db.query(Todos)`**: Consultar la tabla Todos

2. **`.filter(Todos.id == todo_id)`**:
   - Primera condición: La tarea debe tener el ID solicitado

3. **`.filter(Todos.owner_id == user.get("id"))`**:
   - Segunda condición: La tarea debe pertenecer al usuario autenticado
   - **SEGURIDAD**: Esto previene que un usuario acceda a tareas de otros

4. **`.first()`**:
   - Retorna el primer resultado encontrado
   - Si no encuentra nada, retorna `None`

**SQL equivalente**:

```sql
SELECT * FROM todos 
WHERE id = 5 
  AND owner_id = 42 
LIMIT 1;
```

**¿Por qué dos filtros?**:

- **Filtro 1** (`id == todo_id`): Encuentra la tarea correcta
- **Filtro 2** (`owner_id == user.id`): Verifica que sea del usuario

**Ejemplo de ataque bloqueado**:

```bash
Usuario A (id=10) intenta acceder a:
GET /todo/50

La tarea 50 pertenece al Usuario B (id=20)

Query: SELECT * FROM todos WHERE id = 50 AND owner_id = 10
Resultado: None (no hay tarea con id=50 que pertenezca al usuario 10)

Respuesta: 404 Not Found
```

#### Manejo del resultado

```python
if todo_model is not None:
    return todo_model

raise HTTPException(status_code=404, detail="Todo not found")
```

**Flujo**:

1. Si `todo_model` contiene datos → Retornar la tarea (status 200)
2. Si `todo_model` es None → Lanzar error 404

**Respuesta exitosa** (200):

```json
{
  "id": 5,
  "title": "Estudiar FastAPI",
  "description": "Completar el módulo 3",
  "priority": 4,
  "complete": false,
  "owner_id": 42
}
```

**Respuesta de error** (404):

```json
{
  "detail": "Todo not found"
}
```

**Casos donde retorna 404**:

1. La tarea no existe en la base de datos
2. La tarea existe pero pertenece a otro usuario
3. El ID es válido pero no hay coincidencias

---

### 3. POST /todo/ - Crear Nueva Tarea

```python
@router.post("/todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))

    db.add(todo_model)
    db.commit()
```

**Ruta completa**: `POST /todo/`

**Propósito**: Crear una nueva tarea para el usuario autenticado

**Parámetros**:

- **user**: Usuario autenticado (inyectado)
- **db**: Sesión de BD (inyectada)
- **todo_request**: Datos de la tarea validados por Pydantic

**Status Code**: `201 CREATED` - Recurso creado exitosamente

#### Cuerpo de la petición (JSON)

```json
{
  "title": "Nueva tarea",
  "description": "Descripción de la tarea",
  "priority": 3,
  "complete": false
}
```

**Nota**: No se envía `owner_id`, se asigna automáticamente del usuario autenticado.

#### Verificación de autenticación POST

```python
if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
```

#### Creación del modelo - ANÁLISIS PROFUNDO

```python
todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))
```

Esta línea hace MUCHO. Vamos a desglosarla completamente:

**1. `todo_request.model_dump()`**:

- Convierte el objeto Pydantic a un diccionario
- Ejemplo de resultado:

  ```python
  {
      "title": "Nueva tarea",
      "description": "Descripción de la tarea",
      "priority": 3,
      "complete": False
  }
  ```

**2. `**todo_request.model_dump()`**:

- El `**` desempaqueta el diccionario en argumentos nombrados (keyword arguments)
- Es equivalente a escribir:

  ```python
  Todos(
      title="Nueva tarea",
      description="Descripción de la tarea",
      priority=3,
      complete=False
  )
  ```

**3. `, owner_id=user.get("id")`**:

- Agrega un argumento adicional: el ID del usuario actual
- Ejemplo: `owner_id=42`

**Resultado completo equivalente**:

```python
todo_model = Todos(
    title="Nueva tarea",
    description="Descripción de la tarea",
    priority=3,
    complete=False,
    owner_id=42
)
```

**¿Por qué es elegante?**:

- ✅ No tienes que escribir cada campo manualmente
- ✅ Si agregas más campos a TodoRequest, funcionará automáticamente
- ✅ El owner_id siempre viene del usuario autenticado (seguro)

**Alternativa manual (más verbosa)**:

```python
todo_model = Todos(
    title=todo_request.title,
    description=todo_request.description,
    priority=todo_request.priority,
    complete=todo_request.complete,
    owner_id=user.get("id")
)
```

#### Guardar en base de datos

```python
db.add(todo_model)
db.commit()
```

**1. `db.add(todo_model)`**:

- Agrega el objeto a la sesión de SQLAlchemy
- NO lo guarda todavía en la BD
- Lo marca como "pendiente de insertar"

**2. `db.commit()`**:

- Ejecuta todas las operaciones pendientes
- Hace el INSERT real en la base de datos
- Si hay error, hace rollback automático

**SQL equivalente**:

```sql
INSERT INTO todos (title, description, priority, complete, owner_id)
VALUES ('Nueva tarea', 'Descripción de la tarea', 3, false, 42);
```

**Flujo completo**:

```bash
1. Cliente envía: POST /todo/ + JSON con datos
   ↓
2. FastAPI valida con TodoRequest
   ↓
3. Se crea objeto Todos con los datos + owner_id del usuario
   ↓
4. db.add() agrega a la sesión
   ↓
5. db.commit() guarda en la BD
   ↓
6. Respuesta: 201 Created
```

**Nota sobre el retorno**:

- Este endpoint no retorna nada (solo status 201)
- Podría mejorarse retornando la tarea creada con su ID:

  ```python
  db.add(todo_model)
  db.commit()
  db.refresh(todo_model)  # Actualiza el objeto con el ID generado
  return todo_model
  ```

---

### 4. PUT /todo/{todo_id} - Actualizar Tarea

```python
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id : int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()
```

**Ruta completa**: `PUT /todo/5` (actualizar la tarea con ID 5)

**Propósito**: Actualizar completamente una tarea existente

**Parámetros**:

- **user**: Usuario autenticado
- **db**: Sesión de BD
- **todo_request**: Nuevos datos validados
- **todo_id**: ID de la tarea a actualizar (debe ser > 0)

**Status Code**: `204 NO CONTENT` - Actualización exitosa sin cuerpo de respuesta

#### HTTP PUT vs PATCH

**PUT**: Reemplaza completamente el recurso

- Debes enviar TODOS los campos
- Los campos no enviados se perderían (si no se manejan bien)

**PATCH**: Actualización parcial

- Solo envías los campos que quieres cambiar
- Los demás campos se mantienen

Este endpoint usa **PUT**, lo que significa que debes enviar todos los campos.

#### Cuerpo de la petición

```json
{
  "title": "Título actualizado",
  "description": "Nueva descripción",
  "priority": 5,
  "complete": true
}
```

#### Buscar la tarea a actualizar

```python
todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()

if todo_model is None:
    raise HTTPException(status_code=404, detail="Todo not found")
```

**Importante**:

- Busca la tarea con el ID especificado
- **Y** que pertenezca al usuario autenticado
- Si no existe o pertenece a otro usuario → 404

**SQL equivalente**:

```sql
SELECT * FROM todos 
WHERE id = 5 
  AND owner_id = 42 
LIMIT 1;
```

#### Actualizar campos uno por uno

```python
todo_model.title = todo_request.title
todo_model.description = todo_request.description
todo_model.priority = todo_request.priority
todo_model.complete = todo_request.complete
```

**¿Qué hace?**:

- Modifica el objeto Python en memoria
- Todavía no se guarda en la BD

**Ejemplo**:

```python
# Antes:
todo_model.title = "Tarea antigua"
todo_model.complete = False

# Después:
todo_model.title = "Título actualizado"
todo_model.complete = True
```

**Alternativa más elegante (no usada aquí)**:

```python
for key, value in todo_request.model_dump().items():
    setattr(todo_model, key, value)
```

#### Guardar cambios

```python
db.add(todo_model)
db.commit()
```

**Nota**: `db.add()` no es estrictamente necesario para updates

- SQLAlchemy ya está "trackeando" el objeto porque vino de una query
- Pero no hace daño incluirlo (es explícito)

**SQL equivalente**:

```sql
UPDATE todos 
SET title = 'Título actualizado',
    description = 'Nueva descripción',
    priority = 5,
    complete = true
WHERE id = 5 
  AND owner_id = 42;
```

#### Respuesta

**Status 204**: Significa "todo bien, pero no hay contenido que devolver"

- No hay cuerpo en la respuesta
- Solo el código de estado 204

**Si falla**:

- **404**: Tarea no encontrada o no pertenece al usuario
- **422**: Datos inválidos (ej: priority = 10)
- **401**: Usuario no autenticado

---

### 5. DELETE /todo/{todo_id} - Eliminar Tarea

```python
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id : int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()
    db.commit()
```

**Ruta completa**: `DELETE /todo/5` (eliminar la tarea con ID 5)

**Propósito**: Eliminar permanentemente una tarea

**Parámetros**:

- **user**: Usuario autenticado
- **db**: Sesión de BD
- **todo_id**: ID de la tarea a eliminar (> 0)

**Status Code**: `204 NO CONTENT` - Eliminación exitosa sin cuerpo de respuesta

#### Verificar que la tarea existe y pertenece al usuario

```python
todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()

if todo_model is None:
    raise HTTPException(status_code=404, detail="Todo not found")
```

**¿Por qué verificar primero?**:

- Para retornar 404 si la tarea no existe
- Para prevenir que un usuario elimine tareas de otros
- Si no verificamos, la eliminación sería "silenciosa" (no sabríamos si eliminó algo)

#### Eliminar la tarea

```python
db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()
db.commit()
```

**Desglose**:

1. **`db.query(Todos)`**: Consultar la tabla

2. **`.filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id"))`**:
   - Filtrar por ID y owner_id (seguridad)
   - **Importante**: Se repite el filtro (ya se hizo arriba)
   - Esto garantiza que no se elimine nada erróneo

3. **`.delete()`**:
   - Marca los registros coincidentes para eliminación
   - Retorna el número de filas eliminadas (no se usa aquí)

4. **`db.commit()`**:
   - Ejecuta la eliminación real en la BD
   - Sin esto, no se elimina nada

**SQL equivalente**:

```sql
DELETE FROM todos 
WHERE id = 5 
  AND owner_id = 42;
```

**Alternativa (usando el objeto ya obtenido)**:

```python
# Ya tienes todo_model de la verificación
db.delete(todo_model)
db.commit()
```

Esta alternativa es más eficiente (una sola query en lugar de dos), pero la forma actual es más explícita.

#### Respuesta DELETE

**Status 204**: Eliminación exitosa, sin cuerpo de respuesta

**Si falla**:

- **404**: Tarea no encontrada o no pertenece al usuario
- **401**: Usuario no autenticado

---

## Flujo Completo de Operaciones

### Crear una Tarea

```bash
1. Cliente                      2. API                          3. Base de Datos
   |                               |                                   |
   |-- POST /todo/ -------------->|                                   |
   |   + token en header          |                                   |
   |   + JSON con datos           |                                   |
   |                              |                                   |
   |                              |-- Validar token (get_current_user)|
   |                              |                                   |
   |                              |-- Validar datos (TodoRequest)     |
   |                              |                                   |
   |                              |-- Crear Todos con owner_id        |
   |                              |                                   |
   |                              |-- INSERT INTO todos ------------->|
   |                              |                                   |
   |                              |<-- Tarea guardada ----------------|
   |                              |                                   |
   |<-- 201 Created --------------|                                   |
```

### Actualizar una Tarea

```bash
1. Cliente                      2. API                          3. Base de Datos
   |                               |                                   |
   |-- PUT /todo/5 -------------->|                                   |
   |   + token                    |                                   |
   |   + JSON con nuevos datos    |                                   |
   |                              |                                   |
   |                              |-- Validar token                   |
   |                              |                                   |
   |                              |-- SELECT WHERE id=5 AND owner=...->|
   |                              |                                   |
   |                              |<-- Tarea encontrada --------------|
   |                              |                                   |
   |                              |-- Verificar que existe            |
   |                              |                                   |
   |                              |-- Actualizar campos               |
   |                              |                                   |
   |                              |-- UPDATE todos SET... ----------->|
   |                              |                                   |
   |                              |<-- Actualizada -------------------|
   |                              |                                   |
   |<-- 204 No Content -----------|                                   |
```

---

## Seguridad y Autorización

### 1. Aislamiento por Usuario

**Problema**: ¿Cómo evitar que un usuario vea/modifique tareas de otro?

**Solución**: Filtro `owner_id` en TODAS las queries

```python
# Siempre se incluye este filtro:
.filter(Todos.owner_id == user.get("id"))
```

**Ejemplo de ataque bloqueado**:

```bash
Usuario Malicioso (id=10):
GET /todo/999

La tarea 999 pertenece al Usuario Víctima (id=20)

Query ejecutada:
SELECT * FROM todos WHERE id = 999 AND owner_id = 10

Resultado: None (no hay tarea 999 que pertenezca al usuario 10)

Respuesta: 404 Not Found
```

El usuario malicioso no sabe si:

- La tarea no existe
- La tarea existe pero es de otro usuario

Esto es bueno para la seguridad (no revelar información).

### 2. Validación de Token en Cada Endpoint

```python
user: user_dependency
```

**¿Qué hace?**:

- Extrae el token del header `Authorization: Bearer <token>`
- Valida el token JWT
- Verifica que no esté expirado
- Si algo falla → 401 UNAUTHORIZED

**Sin token válido**, los endpoints ni siquiera se ejecutan.

### 3. Validación de Entrada

```python
todo_request: TodoRequest
```

**Pydantic valida**:

- Tipos de datos correctos
- Rangos válidos (priority: 1-5)
- Longitudes mínimas/máximas
- Campos requeridos

**Previene**:

- inyección SQL (indirectamente, SQLAlchemy también ayuda)
- Datos inconsistentes en la BD
- Errores por datos malformados

### 4. Códigos de Estado HTTP Apropiados

- **200 OK**: Operación exitosa con datos
- **201 CREATED**: Recurso creado exitosamente
- **204 NO CONTENT**: Operación exitosa sin datos
- **401 UNAUTHORIZED**: No autenticado
- **404 NOT FOUND**: Recurso no existe o no pertenece al usuario
- **422 UNPROCESSABLE ENTITY**: Datos inválidos

---

## Conceptos Clave de Inyección de Dependencias

### Ejemplo Completo de Ejecución

```python
@router.get("/")
async def read_all(user: user_dependency, db: db_dependency):
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
```

**Cuando un cliente hace**: `GET /todos/`

**FastAPI ejecuta esta secuencia**:

```bash
1. Llegar petición GET /todos/
   Header: Authorization: Bearer eyJhbGc...
   
2. Resolver dependencia 'db' (db_dependency)
   ├─ Llamar get_db()
   ├─ Ejecutar: db = SessionLocal()
   ├─ Ejecutar: yield db
   └─ PAUSA (db quedó creada)
   
3. Resolver dependencia 'user' (user_dependency)
   ├─ Llamar get_current_user()
   ├─ Extraer token del header
   ├─ Decodificar JWT con SECRET_KEY
   ├─ Validar que no esté expirado
   ├─ Extraer: username, id, role
   └─ Retornar: {'username': 'juan', 'id': 42, 'user_role': 'user'}
   
4. Ejecutar endpoint read_all(user=dict, db=Session)
   ├─ Verificar user is not None
   ├─ Ejecutar query: SELECT * FROM todos WHERE owner_id = 42
   └─ Retornar lista de tareas
   
5. Finalizar dependencia 'db'
   ├─ Continuar desde yield en get_db()
   ├─ Ejecutar: finally: db.close()
   └─ Sesión cerrada
   
6. Enviar respuesta al cliente
   └─ 200 OK + JSON con tareas
```

### Ventajas de Este Enfoque

#### 1. **Código más limpio**

**Sin inyección**:

```python
async def read_all():
    # Gestionar autenticación
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(401)
    token = token.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY)
        user_id = payload.get("id")
    except:
        raise HTTPException(401)
    
    # Gestionar BD
    db = SessionLocal()
    try:
        todos = db.query(Todos).filter(Todos.owner_id == user_id).all()
        return todos
    finally:
        db.close()
```

**Con inyección**:

```python
async def read_all(user: user_dependency, db: db_dependency):
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
```

#### 2. **Reutilización**

Las dependencias se definen una vez y se usan en todos los endpoints:

```python
# Definir una vez:
user_dependency = Annotated[dict, Depends(get_current_user)]

# Usar en muchos endpoints:
async def read_all(user: user_dependency, db: db_dependency): ...
async def create_todo(user: user_dependency, db: db_dependency): ...
async def update_todo(user: user_dependency, db: db_dependency): ...
async def delete_todo(user: user_dependency, db: db_dependency): ...
```

#### 3. **Testeable**

Puedes inyectar dependencias falsas (mocks) para testing:

```python
# Test
def fake_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def fake_get_current_user():
    return {'username': 'testuser', 'id': 1, 'user_role': 'user'}

# Reemplazar dependencias para test
app.dependency_overrides[get_db] = fake_get_db
app.dependency_overrides[get_current_user] = fake_get_current_user
```

#### 4. **Separación de responsabilidades**

- **get_db**: Solo gestiona sesiones de BD
- **get_current_user**: Solo gestiona autenticación
- **Endpoints**: Solo lógica de negocio

Cada función tiene una responsabilidad clara.

---

## Ejemplos de Uso con cURL

### 1. Login y obtener token

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=juan123&password=password123"
```

**Respuesta**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Guardar el token**:

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2. Listar todas las tareas

```bash
curl -X GET "http://localhost:8000/todos/" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Obtener una tarea específica

```bash
curl -X GET "http://localhost:8000/todos/todo/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Crear nueva tarea

```bash
curl -X POST "http://localhost:8000/todos/todo/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Aprender FastAPI",
    "description": "Completar el curso completo",
    "priority": 5,
    "complete": false
  }'
```

### 5. Actualizar tarea

```bash
curl -X PUT "http://localhost:8000/todos/todo/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Aprender FastAPI - Actualizado",
    "description": "Ya casi termino el curso",
    "priority": 4,
    "complete": true
  }'
```

### 6. Eliminar tarea

```bash
curl -X DELETE "http://localhost:8000/todos/todo/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Consideraciones y Posibles Mejoras

### Verificaciones Redundantes

```python
if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
```

- Esta verificación está en cada endpoint
- Técnicamente es redundante porque `get_current_user` ya lanza 401 si falla
- **¿Mantenerla?**: Es una defensa extra, no hace daño (defensa en profundidad)

### Repetición de Queries en Delete/Update

```python
# Se hace dos veces la misma query:
todo_model = db.query(Todos).filter(...).first()  # 1ª vez
db.query(Todos).filter(...).delete()  # 2ª vez (en delete)
```

**Mejora sugerida**:

```python
# Usar el objeto ya obtenido:
todo_model = db.query(Todos).filter(...).first()
if todo_model is None:
    raise HTTPException(status_code=404)

db.delete(todo_model)  # Usar el objeto
db.commit()
```

### Sin Paginación

**Problema**: `GET /` retorna TODAS las tareas del usuario

**Si un usuario tiene 10,000 tareas**:

- La respuesta será enorme
- Consumirá mucha memoria
- Será lenta

**Solución**: Implementar paginación

```python
@router.get("/")
async def read_all(user: user_dependency, db: db_dependency, skip: int = 0, limit: int = 100):
    return db.query(Todos)\
        .filter(Todos.owner_id == user.get('id'))\
        .offset(skip)\
        .limit(limit)\
        .all()
```

Uso: `GET /?skip=0&limit=20` (primeras 20 tareas)

### Sin Respuesta al Crear

**Actual**: POST retorna solo status 201, sin datos

**Mejora**: Retornar la tarea creada

```python
@router.post("/todo/", status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
async def create_todo(...):
    todo_model = Todos(...)
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)  # Obtiene el ID generado
    return todo_model
```

### Sin Filtros ni Búsqueda

**Limitación**: No puedes buscar tareas por título, filtrar por completadas, etc.

**Mejora**: Agregar query parameters

```python
@router.get("/")
async def read_all(
    user: user_dependency, 
    db: db_dependency,
    complete: bool = None,
    priority: int = None,
    search: str = None
):
    query = db.query(Todos).filter(Todos.owner_id == user.get('id'))
    
    if complete is not None:
        query = query.filter(Todos.complete == complete)
    if priority is not None:
        query = query.filter(Todos.priority == priority)
    if search:
        query = query.filter(Todos.title.contains(search))
    
    return query.all()
```

Uso: `GET /?complete=false&priority=5&search=FastAPI`

---

## Resumen

Este módulo implementa un **CRUD completo de tareas** con:

- ✅ **5 endpoints RESTful** (Listar, Obtener, Crear, Actualizar, Eliminar)
- ✅ **Autenticación JWT** en todos los endpoints
- ✅ **Aislamiento por usuario** (cada usuario solo ve sus tareas)
- ✅ **Validación de datos** con Pydantic
- ✅ **Inyección de dependencias** para código limpio y reutilizable
- ✅ **Gestión automática de sesiones** de base de datos
- ✅ **Códigos de estado HTTP apropiados**
- ✅ **Seguridad contra accesos no autorizados**

### Flujo típico de uso

1. Usuario se registra (`POST /auth/`)
2. Usuario hace login (`POST /auth/token`) → Recibe token
3. Usuario crea tareas (`POST /todo/`) con el token
4. Usuario lista sus tareas (`GET /`)
5. Usuario actualiza tareas (`PUT /todo/{id}`)
6. Usuario elimina tareas (`DELETE /todo/{id}`)

### Concepto más importante: **Inyección de Dependencias**

```python
async def endpoint(user: user_dependency, db: db_dependency):
    # FastAPI automáticamente:
    # 1. Valida el token y extrae el usuario
    # 2. Crea y cierra la sesión de BD
    # 3. Inyecta ambos como parámetros
    # 
    # Tú solo escribes la lógica de negocio
```

Este patrón hace que el código sea:

- Más limpio y legible
- Más fácil de testear
- Más mantenible
- Más reutilizable

**Es la base de cómo funcionan las aplicaciones FastAPI modernas.**
