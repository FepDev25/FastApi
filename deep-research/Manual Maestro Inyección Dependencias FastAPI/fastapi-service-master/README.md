# ServiceMaster API - Tutorial de Inyección de Dependencias

> **Proyecto educativo** enfocado en dominar la **Inyección de Dependencias** en FastAPI y aplicar una arquitectura limpia y escalable.

## Objetivo Principal

Este proyecto es un tutorial práctico para aprender:

1. **Inyección de Dependencias (DI) en FastAPI** - El concepto central del proyecto
2. **Arquitectura en capas** - Repository → Service → Router
3. **Gestión de sesiones de base de datos** con patrones modernos
4. **Separación de responsabilidades** entre modelos, schemas y lógica de negocio

## Arquitectura

Este proyecto implementa el patrón **Repository-Service-Router** con inyección de dependencias:

```bash
┌─────────────────────────────────────────────────────┐
│                    Router Layer                     │
│  (Endpoints HTTP - Validación de entrada/salida)   │
│                                                     │
│  • Define rutas HTTP (GET, POST, PUT, DELETE)      │
│  • Maneja request/response                         │
│  • Usa Schemas (Pydantic) para validación         │
└──────────────────┬──────────────────────────────────┘
                   │ Depends(TicketService)
                   ▼
┌─────────────────────────────────────────────────────┐
│                   Service Layer                     │
│         (Lógica de Negocio - Casos de Uso)         │
│                                                     │
│  • Contiene reglas de negocio                      │
│  • Valida y procesa datos                          │
│  • Coordina operaciones complejas                  │
└──────────────────┬──────────────────────────────────┘
                   │ Depends(TicketRepository)
                   ▼
┌─────────────────────────────────────────────────────┐
│                 Repository Layer                    │
│           (Acceso a Datos - Persistencia)          │
│                                                     │
│  • Operaciones CRUD con la base de datos           │
│  • Abstrae la lógica de SQLModel/SQLAlchemy       │
│  • Maneja queries y transacciones                  │
└──────────────────┬──────────────────────────────────┘
                   │ Depends(get_db_session)
                   ▼
┌─────────────────────────────────────────────────────┐
│                  Database Layer                     │
│        (PostgreSQL con SQLModel + AsyncPG)         │
└─────────────────────────────────────────────────────┘
```

### Flujo de Inyección de Dependencias

```python
# 1. DATABASE LAYER - Gestión de sesión
async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session  # FastAPI inyecta esto

# 2. REPOSITORY LAYER - Acceso a datos
class TicketRepository:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session  # Sesión inyectada automáticamente

# 3. SERVICE LAYER - Lógica de negocio
class TicketService:
    def __init__(self, repo: TicketRepository = Depends()):
        self.repo = repo  # Repository inyectado automáticamente

# 4. ROUTER LAYER - Endpoints HTTP
@router.post("/")
async def create_ticket(
    ticket_in: TicketCreate,
    service: TicketServiceDep  # Service inyectado automáticamente
):
    return await service.create_ticket(ticket_in)
```

**La magia:** FastAPI resuelve la cadena completa de dependencias automáticamente:

- Router → Service → Repository → Database Session

## Conceptos Clave de Dependency Injection

### 1. **Depends() - El corazón de la DI**

```python
from fastapi import Depends
from typing import Annotated

# Forma tradicional
def endpoint(service: TicketService = Depends()):
    pass

# Forma moderna con Annotated (recomendada)
TicketServiceDep = Annotated[TicketService, Depends()]

def endpoint(service: TicketServiceDep):
    pass
```

### 2. **Generadores con yield - Gestión del ciclo de vida**

```python
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session  # ANTES del yield: setup
        finally:
            await session.close()  # DESPUÉS del yield: cleanup
```

### 3. **Cache de dependencias con lru_cache**

```python
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()  # Solo se ejecuta UNA vez
```

## Estructura del Proyecto

```bash
fastapi-service-master/
├── main.py                    # Punto de entrada - FastAPI app
├── .env                       # Variables de entorno (NO versionado)
├── .env.example              # Template de configuración
├── pyproject.toml            # Dependencias (UV)
├── pytest.ini                # Configuración de pytest
├── .python-version           # Versión de Python (3.12)
│
├── src/
│   ├── __init__.py           # Exporta el router principal
│   ├── config.py             # Configuración con Pydantic Settings
│   ├── database.py           # Motor DB y dependency de sesión
│   │
│   └── tickets/              # Módulo de tickets
│       ├── __init__.py
│       ├── models.py         # SQLModel (tabla DB)
│       ├── schemas.py        # Pydantic schemas (API)
│       ├── repository.py     # Capa de acceso a datos
│       ├── service.py        # Lógica de negocio
│       └── router.py         # Endpoints HTTP
│
└── tests/                    # Suite completa de tests
    ├── __init__.py
    ├── conftest.py           # Fixtures compartidos
    ├── test_config.py        # Tests de configuración
    ├── test_repository.py    # Tests capa Repository
    ├── test_service.py       # Tests capa Service (con mocks)
    ├── test_endpoints.py     # Tests de integración (API)
    └── README.md             # Documentación de tests
```

## Conceptos Importantes

### Models vs Schemas

```python
# MODELS (models.py) - Representan la tabla en la DB
from sqlmodel import SQLModel, Field

class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str

# SCHEMAS (schemas.py) - Representan datos de la API
from pydantic import BaseModel, Field

class TicketCreate(BaseModel):  # Input de la API
    title: str = Field(..., min_length=1)
    description: str

class TicketRead(BaseModel):    # Output de la API
    id: int
    title: str
    description: str
    
    class Config:
        from_attributes = True  # Permite convertir desde SQLModel
```

### Lifespan Events - Gestión del ciclo de vida

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Se ejecuta al iniciar la app
    await create_db_and_tables()
    print("✅ Database initialized")
    
    yield  # La app está corriendo
    
    # SHUTDOWN: Se ejecuta al cerrar la app
    await close_db_connection()
    print("✅ Database closed")

app = FastAPI(lifespan=lifespan)
```

## Instalación y Uso

### 1. Requisitos previos

- Python 3.12+
- PostgreSQL
- UV (gestor de paquetes)

### 2. Clonar y configurar

```bash
# Instalar UV (si no lo tienes)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navegar al proyecto
cd fastapi-service-master

# Instalar dependencias (UV crea automáticamente el .venv)
uv sync

# Configurar variables de entorno
cp .env.example .env
# Edita .env con tus credenciales de PostgreSQL
```

### 3. Configurar base de datos

Crea la base de datos en PostgreSQL:

```sql
CREATE DATABASE servicemaster;
```

Actualiza el `.env`:

```env
DATABASE_URL=postgresql+asyncpg://tu_usuario:tu_password@localhost/servicemaster
SECRET_KEY=genera-una-clave-segura
DEBUG_MODE=True
```

### 4. Ejecutar la aplicación

```bash
# Con UV
uv run uvicorn main:app --reload

# Acceder a la documentación interactiva
# http://localhost:8000/docs
```

## Ejemplos de Uso de la API

### Crear un ticket

```bash
curl -X POST "http://localhost:8000/tickets/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "CRITICAL Bug en producción",
    "description": "Error 500 en /api/users",
    "priority": 3
  }'
```

**Lógica de negocio automática:** Si el título contiene "CRITICAL" o "URGENTE", la prioridad se establece automáticamente en 5.

### Obtener todos los tickets

```bash
curl "http://localhost:8000/tickets/?skip=0&limit=10"
```

### Obtener un ticket específico

```bash
curl "http://localhost:8000/tickets/1"
```

### Actualizar un ticket

```bash
curl -X PUT "http://localhost:8000/tickets/1" \
  -H "Content-Type: application/json" \
  -d '{
    "is_completed": true,
    "priority": 5
  }'
```

### Eliminar un ticket

```bash
curl -X DELETE "http://localhost:8000/tickets/1"
```

## Testing

### Suite Completa de Tests

El proyecto incluye **35 tests** con **95% de cobertura de código**:

```bash
# Ejecutar todos los tests
uv run pytest

# Ejecutar con verbose
uv run pytest -v

# Ejecutar con coverage
uv run pytest --cov=src --cov-report=term-missing

# Ejecutar con reporte HTML
uv run pytest --cov=src --cov-report=html
# Abrir: htmlcov/index.html
```

### Tipos de Tests Incluidos

#### 1. **Tests Unitarios**

- `test_config.py` - Configuración y settings
- `test_repository.py` - Operaciones CRUD de la DB
- `test_service.py` - Lógica de negocio (con mocks)

#### 2. **Tests de Integración**

- `test_endpoints.py` - Flujo completo de la API

### Cobertura de Tests

Los tests cubren:

- CRUD completo de tickets
- Validación de datos (Pydantic)
- Lógica de negocio (prioridad automática en tickets CRITICAL/URGENTE)
- Manejo de errores (404, validación 422)
- Paginación de resultados
- Inyección de dependencias
- Override de dependencias en tests

### Ejecutar Tests Específicos

```bash
# Un archivo específico
uv run pytest tests/test_endpoints.py

# Un test específico
uv run pytest tests/test_endpoints.py::TestTicketEndpoints::test_create_ticket

# Tests con marker asyncio
uv run pytest -m asyncio
```

### Base de Datos de Pruebas

- Usa **SQLite in-memory** para tests
- Aislamiento total entre tests
- Override automático de dependencias
- No afecta la base de datos de producción

## Tecnologías Utilizadas

- **FastAPI** - Framework web asíncrono
- **SQLModel** - ORM (combina SQLAlchemy + Pydantic)
- **AsyncPG** - Driver asíncrono para PostgreSQL
- **Pydantic Settings** - Gestión de configuración
- **UV** - Gestor de paquetes ultra-rápido
- **Pytest + Pytest-Asyncio** - Testing framework
- **Httpx** - Cliente HTTP asíncrono para tests
- **SQLite (aiosqlite)** - Base de datos para tests

## Recursos de Aprendizaje

### Inyección de Dependencias

- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Advanced Dependencies](https://fastapi.tiangolo.com/advanced/advanced-dependencies/)

### Recursos de Arquitectura

- [Repository Pattern](https://www.cosmicpython.com/book/chapter_02_repository.html)
- [Service Layer Pattern](https://www.cosmicpython.com/book/chapter_04_service_layer.html)

### Herramientas

- [UV Documentation](https://docs.astral.sh/uv/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

## Ventajas de esta Arquitectura

**Testeable** - Fácil de mockear dependencias  
**Mantenible** - Separación clara de responsabilidades  
**Escalable** - Agregar nuevas features es simple  
**Reutilizable** - Las dependencias se pueden compartir  
**Type-safe** - Todo está tipado con Python 3.12+  
**Asíncrono** - Aprovecha async/await de Python  

## Próximos Pasos

Para seguir aprendiendo, intenta:

1. Agregar autenticación con JWT
2. Agregar paginación avanzada
3. Implementar filtros y búsqueda
4. Agregar migraciones con Alembic
5. Dockerizar la aplicación

## Licencia

Este es un proyecto educativo. Siéntete libre de usarlo para aprender.
