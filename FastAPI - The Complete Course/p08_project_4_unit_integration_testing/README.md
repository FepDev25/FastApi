# Unit and Integration Testing - FastAPI Project

Este proyecto es una extensión de la aplicación de gestión de tareas que implementa una suite completa de **pruebas unitarias e integradas** utilizando pytest. El objetivo es demostrar cómo implementar testing profesional en aplicaciones FastAPI, cubriendo todos los componentes críticos de la aplicación.

## Descripción General

El testing es una práctica fundamental en el desarrollo de software que garantiza la calidad, estabilidad y confiabilidad del código. Este proyecto implementa:

- **Pruebas Unitarias**: Validan funciones y métodos individuales de forma aislada
- **Pruebas de Integración**: Verifican que los componentes funcionen correctamente en conjunto
- **Pruebas de API**: Validan los endpoints HTTP y sus respuestas
- **Base de Datos de Prueba**: Entorno aislado que no afecta datos de producción
- **Fixtures**: Datos de prueba reutilizables y limpios para cada test
- **Dependency Overrides**: Reemplazo de dependencias para aislar componentes

## Estructura del Proyecto

```bash
p08_project_4_unit_integration_testing/
├── main.py                    # Aplicación FastAPI principal
├── database.py                # Configuración de base de datos
├── models.py                  # Modelos SQLAlchemy
├── routers/
│   ├── auth.py               # Endpoints de autenticación
│   ├── todos.py              # CRUD de tareas
│   ├── admin.py              # Panel administrativo
│   └── users.py              # Gestión de usuarios
└── test/
    ├── __init__.py
    ├── utils.py              # Configuración compartida y fixtures
    ├── test_example.py       # Ejemplos básicos de pytest
    ├── test_main.py          # Tests del endpoint principal
    ├── test_auth.py          # Tests de autenticación
    ├── test_todos.py         # Tests del CRUD de tareas
    ├── test_admin.py         # Tests de administración
    └── test_users.py         # Tests de gestión de usuarios
```

## Tecnologías de Testing

### pytest

Framework de testing para Python que proporciona:

- Sintaxis simple y clara
- Fixtures para gestión de datos de prueba
- Marcadores para categorizar tests
- Ejecución paralela de tests
- Informes detallados de fallos

### TestClient (FastAPI)

Cliente de pruebas proporcionado por FastAPI:

- Simula peticiones HTTP sin servidor real
- No requiere ejecutar uvicorn
- Mantiene el contexto de la aplicación
- Ideal para pruebas de integración

### pytest-asyncio

Extensión de pytest para código asíncrono:

- Permite probar funciones async/await
- Decorador `@pytest.mark.asyncio`
- Gestión automática de event loops

## Configuración de Testing

### Base de Datos de Prueba

El archivo `test/utils.py` configura una base de datos SQLite separada para testing:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
```

**Características:**

- Base de datos SQLite independiente (`testdb.db`)
- `StaticPool`: Mantiene una única conexión persistente
- `check_same_thread=False`: Permite múltiples hilos con SQLite
- Tablas creadas automáticamente al inicio

### Override de Dependencias

FastAPI permite reemplazar dependencias durante testing:

```python
def override_get_db():
    """Proporciona sesión de base de datos de prueba"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    """Simula un usuario autenticado"""
    return {'username': 'FepDev25', 'id': 1, 'user_role': 'admin'}

# Aplicar overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
```

**Propósito:**

- `override_get_db`: Usa la base de datos de prueba en lugar de producción
- `override_get_current_user`: Evita requerir tokens JWT reales en tests
- Permite testing sin configuración compleja de autenticación

### TestClient

Cliente HTTP para simular peticiones:

```python
from fastapi.testclient import TestClient

client = TestClient(app)

# Uso en tests
response = client.get("/endpoint")
assert response.status_code == 200
```

## Fixtures de pytest

Los fixtures son funciones que proporcionan datos de prueba y se ejecutan antes de cada test que los utilice.

### Fixture: test_todo

```python
@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn FastAPI",
        description="Need to learn everyday",
        priority=5,
        complete=False,
        owner_id=1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    yield todo

    # Limpieza después del test
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()
```

**Funcionamiento:**

1. **Setup**: Crea y guarda una tarea en la BD de prueba
2. **yield**: Entrega la tarea al test (pausa)
3. **Test**: Se ejecuta el test usando la tarea
4. **Teardown**: Limpia la tabla `todos` después del test

**Ventajas:**

- Datos limpios para cada test
- No hay interferencia entre tests
- Código reutilizable

### Fixture: test_user

```python
@pytest.fixture
def test_user():
    user = Users(
        username="FepDev25",
        email="felipe@gmail.com",
        first_name="Felipe",
        last_name="Peralta",
        hashed_password=bcrypt_context.hash("test123"),
        role="admin",
        phone_number="0987654321"
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user

    # Limpieza después del test
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()
```

**Características:**

- Crea un usuario administrador con contraseña hasheada
- Limpia la tabla `users` después de cada test
- Garantiza estado limpio entre tests

## Tipos de Tests Implementados

### 1. Tests Básicos de pytest (test_example.py)

Ejemplos fundamentales de assertions en pytest:

#### Comparaciones

```python
def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 1
```

#### Verificación de Tipos

```python
def test_is_instance():
    assert isinstance('this is a string', str)
    assert not isinstance('10', int)
```

#### Valores Booleanos

```python
def test_boolean():
    validated = True
    assert validated is True
    assert ('hello' == 'world') is False
```

#### Comparaciones Numéricas

```python
def test_greater_and_less_than():
    assert 7 > 3
    assert 4 < 10
```

#### Operaciones con Listas

```python
def test_list():
    num_list = [1, 2, 3, 4, 5]
    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)  # Todos los elementos son truthy
```

#### Test con Fixtures Personalizados

```python
class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years

@pytest.fixture
def default_employee() -> Student:
    return Student("Felipe", "Peralta", "Computer Science", 3)

def test_person_initialization(default_employee: Student):
    assert default_employee.first_name == "Felipe"
    assert default_employee.last_name == 'Peralta'
    assert default_employee.major == 'Computer Science'
    assert default_employee.years == 3
```

### 2. Tests de Autenticación (test_auth.py)

#### Test de Autenticación de Usuario

```python
def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    # Usuario válido
    authenticated_user = authenticate_user(test_user.username, "test123", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    # Usuario inexistente
    non_existent_user = authenticate_user('WrongUserName', 'testpassword', db)
    assert non_existent_user is False

    # Contraseña incorrecta
    wrong_password_user = authenticate_user(test_user.username, 'wrongpassword', db)
    assert wrong_password_user is False
```

**Validaciones:**

- Autenticación exitosa con credenciales correctas
- Retorna `False` para usuario inexistente
- Retorna `False` para contraseña incorrecta

#### Test de Creación de Token JWT

```python
def test_create_access_token():
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                               options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role
```

**Validaciones:**

- Token se crea correctamente
- Payload contiene username, id y role
- Token puede decodificarse con la clave secreta

#### Test de Validación de Token (Asíncrono)

```python
@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'user_role': 'admin'}
```

**Validaciones:**

- Token válido retorna información del usuario
- Estructura de datos correcta

#### Test de Token Inválido

```python
@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'user'}  # Falta 'sub' e 'id'
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user.'
```

**Validaciones:**

- Token sin datos requeridos lanza HTTPException 401
- Mensaje de error correcto

### 3. Tests del CRUD de Tareas (test_todos.py)

#### Test: Listar Todas las Tareas

```python
def test_read_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'complete': False,
            'title': 'Learn FastAPI',
            'description': 'Need to learn everyday',
            'id': 1,
            'priority': 5,
            'owner_id': 1
        }
    ]
```

**Validaciones:**

- Status code 200
- Retorna lista con la tarea del fixture
- Estructura JSON correcta

#### Test: Obtener Una Tarea

```python
def test_read_one_authenticated(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'complete': False,
        'title': 'Learn FastAPI',
        'description': 'Need to learn everyday',
        'id': 1,
        'priority': 5,
        'owner_id': 1
    }
```

**Validaciones:**

- Status code 200
- Retorna la tarea correcta
- Todos los campos presentes

#### Test: Tarea No Encontrada

```python
def test_read_one_authenticated_not_found():
    response = client.get("/todo/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}
```

**Validaciones:**

- Status code 404 para ID inexistente
- Mensaje de error apropiado

#### Test: Crear Tarea

```python
def test_create_todo(test_todo):
    request_data = {
        'title': 'New Todo',
        'description': 'New todo description',
        'priority': 5,
        'complete': False,
    }

    response = client.post("/todo/", json=request_data)
    assert response.status_code == 201

    # Verificar en base de datos
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')
```

**Validaciones:**

- Status code 201 (Created)
- Tarea se guarda correctamente en BD
- Todos los campos coinciden con los enviados

#### Test: Actualizar Tarea

```python
def test_update_todo(test_todo):
    request_data = {
        'title': 'Change the title of the todo already saved',
        'description': 'Need to learn everyday',
        'priority': 5,
        'complete': False,
    }

    response = client.put("/todo/1", json=request_data)
    assert response.status_code == 204

    # Verificar cambios en BD
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == 'Change the title of the todo already saved'
```

**Validaciones:**

- Status code 204 (No Content)
- Tarea se actualiza correctamente en BD
- Cambios persisten

#### Test: Actualizar Tarea Inexistente

```python
def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Change the title of the todo already saved',
        'description': 'Need to learn everyday',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/todo/999', json=request_data)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}
```

**Validaciones:**

- Status code 404
- Mensaje de error correcto

#### Test: Eliminar Tarea

```python
def test_delete_todo(test_todo):
    response = client.delete("/todo/1")
    assert response.status_code == 204

    # Verificar eliminación en BD
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None
```

**Validaciones:**

- Status code 204
- Tarea eliminada de la BD
- Query retorna None

#### Test: Eliminar Tarea Inexistente

```python
def test_delete_todo_not_found():
    response = client.delete('/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}
```

**Validaciones:**

- Status code 404
- Mensaje de error apropiado

### 4. Tests de Administración (test_admin.py)

#### Test: Admin Lista Todas las Tareas

```python
def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'complete': False,
            'title': 'Learn FastAPI',
            'description': 'Need to learn everyday',
            'id': 1,
            'priority': 5,
            'owner_id': 1
        }
    ]
```

**Validaciones:**

- Admin puede ver todas las tareas del sistema
- Status code 200
- Estructura de datos correcta

#### Test: Admin Elimina Tarea

```python
def test_admin_delete_todo(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None
```

**Validaciones:**

- Admin puede eliminar cualquier tarea
- Status code 204
- Tarea eliminada de la BD

#### Test: Admin Elimina Tarea Inexistente

```python
def test_admin_delete_todo_not_found():
    response = client.delete("/admin/todo/9999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}
```

**Validaciones:**

- Status code 404
- Mensaje de error apropiado

### 5. Tests de Gestión de Usuarios (test_users.py)

#### Test: Obtener Información del Usuario

```python
def test_return_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'FepDev25'
    assert response.json()['email'] == 'felipe@gmail.com'
    assert response.json()['first_name'] == 'Felipe'
    assert response.json()['last_name'] == 'Peralta'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '0987654321'
```

**Validaciones:**

- Status code 200
- Todos los campos del usuario presentes
- Datos coinciden con el fixture

#### Test: Cambiar Contraseña Exitosamente

```python
def test_change_password_success(test_user):
    response = client.put("/user/password", json={
        "password": "test123",
        "new_password": "newpassword"
    })
    assert response.status_code == status.HTTP_204_NO_CONTENT
```

**Validaciones:**

- Status code 204
- Contraseña se cambia correctamente

#### Test: Cambiar Contraseña con Contraseña Actual Incorrecta

```python
def test_change_password_invalid_current_password(test_user):
    response = client.put("/user/password", json={
        "password": "wrong_password",
        "new_password": "newpassword"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}
```

**Validaciones:**

- Status code 401 con contraseña incorrecta
- Mensaje de error apropiado
- Contraseña no se cambia

#### Test: Cambiar Número de Teléfono

```python
def test_change_phone_number_success(test_user):
    response = client.put("/user/phone", params={
        "new_phone_number": "09123456777"
    })
    assert response.status_code == status.HTTP_204_NO_CONTENT
```

**Validaciones:**

- Status code 204
- Número de teléfono actualizado

### 6. Test del Endpoint Principal (test_main.py)

#### Test: Health Check

```python
def test_return_health_check():
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'Healthy'}
```

**Validaciones:**

- Endpoint de salud responde correctamente
- Status code 200
- Mensaje correcto

## Ejecutar los Tests

### Instalación de Dependencias

```bash
pip install pytest pytest-asyncio
```

### Ejecutar Todos los Tests

```bash
pytest
```

**Salida esperada:**

```bash
======================== test session starts =========================
collected 25 items

test/test_admin.py ...                                         [ 12%]
test/test_auth.py ....                                         [ 28%]
test/test_example.py .......                                   [ 56%]
test/test_main.py .                                            [ 60%]
test/test_todos.py ........                                    [ 92%]
test/test_users.py ....                                        [100%]

========================= 25 passed in 2.53s =========================
```

### Ejecutar Tests Específicos

```bash
# Un archivo específico
pytest test/test_todos.py

# Un test específico
pytest test/test_todos.py::test_create_todo

# Tests que contengan una palabra
pytest -k "password"
```

### Opciones Útiles

```bash
# Modo verbose (detallado)
pytest -v

# Mostrar print statements
pytest -s

# Detener en el primer fallo
pytest -x

# Mostrar cobertura de código
pytest --cov=. --cov-report=html

# Ejecutar tests en paralelo
pytest -n auto

# Ver tests lentos
pytest --durations=10
```

### Salida Detallada

```bash
pytest -v
```

```bash
test/test_auth.py::test_authenticate_user PASSED                    [ 16%]
test/test_auth.py::test_create_access_token PASSED                  [ 33%]
test/test_auth.py::test_get_current_user_valid_token PASSED         [ 50%]
test/test_auth.py::test_get_current_user_missing_payload PASSED     [ 66%]
test/test_todos.py::test_read_all_authenticated PASSED              [ 83%]
test/test_todos.py::test_create_todo PASSED                         [100%]
```

## Conceptos Clave de Testing

### 1. Aislamiento de Tests

Cada test debe ser independiente:

- No debe depender del orden de ejecución
- Los fixtures limpian datos después de cada test
- Base de datos separada para testing

### 2. Arrange-Act-Assert (AAA Pattern)

Patrón común en testing:

```python
def test_create_todo():
    # Arrange: Preparar datos
    request_data = {'title': 'New Todo', 'description': 'Description', ...}
    
    # Act: Ejecutar acción
    response = client.post("/todo/", json=request_data)
    
    # Assert: Verificar resultado
    assert response.status_code == 201
```

### 3. Test Coverage (Cobertura)

Porcentaje del código cubierto por tests:

- **Alta cobertura** no garantiza calidad, pero es un buen indicador
- Objetivo recomendado: 80% o más
- Enfocarse en código crítico

### 4. Tests Positivos y Negativos

**Tests Positivos**: Verifican el comportamiento correcto

```python
def test_create_todo(test_todo):
    response = client.post("/todo/", json=valid_data)
    assert response.status_code == 201
```

**Tests Negativos**: Verifican el manejo de errores

```python
def test_create_todo_not_found():
    response = client.get("/todo/999")
    assert response.status_code == 404
```

### 5. Mocking y Dependency Override

Reemplazar componentes reales con versiones de prueba:

- Base de datos → Base de datos de prueba
- Autenticación → Usuario simulado
- APIs externas → Respuestas predefinidas

### 6. Tests Asíncronos

Para funciones `async`:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected_value
```

## Buenas Prácticas de Testing

### 1. Nombres Descriptivos

```python
# Bien
def test_create_todo_with_valid_data_returns_201():
    ...

# Menos claro
def test_todo_creation():
    ...
```

### 2. Un Assert por Concepto

Evitar demasiados asserts no relacionados:

```python
# Bien
def test_user_has_correct_username(test_user):
    assert test_user.username == "FepDev25"

def test_user_has_correct_email(test_user):
    assert test_user.email == "felipe@gmail.com"

# Menos ideal (aunque aceptable)
def test_user_fields(test_user):
    assert test_user.username == "FepDev25"
    assert test_user.email == "felipe@gmail.com"
    assert test_user.role == "admin"
```

### 3. Tests Rápidos

Los tests deben ejecutarse rápidamente:

- Usar SQLite en memoria cuando sea posible
- Evitar sleeps innecesarios
- Mockear servicios externos

### 4. Documentar Tests Complejos

```python
def test_complex_scenario():
    """
    Verifica que cuando un usuario actualiza una tarea:
    1. La tarea solo se actualiza si pertenece al usuario
    2. Todos los campos se actualizan correctamente
    3. La respuesta es 204 No Content
    """
    # Test implementation
```

### 5. Organización Clara

```bash
test/
├── conftest.py           # Fixtures compartidos
├── utils.py              # Utilidades de testing
├── test_auth.py          # Tests de un módulo
├── test_todos.py         # Tests de otro módulo
└── integration/          # Tests de integración
    └── test_full_flow.py
```

## Ventajas del Testing

### 1. Confianza en el Código

- Detecta regresiones inmediatamente
- Permite refactorizar con seguridad
- Documenta el comportamiento esperado

### 2. Desarrollo Más Rápido

- Menos tiempo debuggeando
- Feedback inmediato
- Facilita cambios futuros

### 3. Mejor Diseño

- Código más modular
- Dependencias explícitas
- Interfaces claras

### 4. Documentación Viva

- Los tests muestran cómo usar el código
- Siempre actualizados
- Ejemplos reales de uso

### 5. Facilita Colaboración

- Nuevos desarrolladores entienden el código
- Cambios seguros
- CI/CD automatizado

## Integración Continua (CI/CD)

Los tests se pueden integrar en pipelines de CI/CD:

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest
```

### GitLab CI

```yaml
test:
  script:
    - pip install -r requirements.txt
    - pytest
```

## Cobertura de Tests del Proyecto

Este proyecto incluye tests para:

- **Autenticación**: Login, creación de tokens, validación
- **CRUD de Tareas**: Create, Read, Update, Delete
- **Administración**: Operaciones privilegiadas
- **Gestión de Usuarios**: Perfil, cambio de contraseña
- **Endpoints principales**: Health checks
- **Casos de error**: 404, 401, validaciones

**Total**: 25 tests cubriendo los componentes principales de la aplicación.

## Conclusión

El testing es una práctica esencial en el desarrollo de software profesional. Este proyecto demuestra:

- Cómo estructurar tests en FastAPI
- Uso de fixtures para datos de prueba limpios
- Override de dependencias para aislamiento
- Tests unitarios y de integración
- Manejo de tests asíncronos
- Validación de casos positivos y negativos
- Base de datos separada para testing

Los tests proporcionan confianza para realizar cambios, detectan bugs tempranamente y sirven como documentación del comportamiento esperado de la aplicación.

Una suite de tests bien diseñada es una inversión que paga dividendos a lo largo de toda la vida del proyecto, facilitando el mantenimiento, las nuevas características y la colaboración en equipo.
