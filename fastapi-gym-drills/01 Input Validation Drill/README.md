# 01 - Input Validation Drill

## Objetivo

Dominar la validación de entrada con Pydantic v2 y patrones profesionales para schemas en FastAPI.

## Conceptos Clave

### 1. Configuración de Ejemplos en Pydantic v2

Forma antigua (Pydantic v1):

```python
class Config:
    schema_extra = {"example": {...}}
```

Forma correcta (Pydantic v2):

```python
from pydantic import BaseModel, ConfigDict

class PackageSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"weight": 2.5, "destination": "123 Main St", "tags": ["fragile"]}
            ]
        }
    )
```

### 2. Evitar Importaciones Circulares

Problema:

- `schemas.py` importa `models.py`
- Si `models.py` necesita importar algo de `schemas.py` → Circular Import

- Solución: TYPE_CHECKING + Lazy Import

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import Package  # Solo para type hints (IDEs/MyPy)

class PackageSchema(BaseModel):
    def to_model(self) -> "Package":
        # Lazy import: se importa solo cuando se ejecuta el método
        from models import Package
        return Package(...)
```

¿Por qué funciona?

- `TYPE_CHECKING` es `True` solo durante análisis estático (MyPy, IDE)
- En runtime es `False`, así que no importa `Package` al cargar la clase
- El import dentro de `to_model()` se ejecuta solo cuando llamas al método

### 3. Separación de Input/Output Schemas

No hacer esto:

```python
@app.post("/packages/")
async def create_package(package: PackageSchema):
    return {"data": package_model.__dict__}  # Evitar __dict__
```

Patrón profesional:

```python
# Input Schema
class PackageSchema(BaseModel):
    """Lo que recibe la API"""
    weight: float
    destination: str

# Output Schema
class PackageResponse(BaseModel):
    """Lo que devuelve la API"""
    weight: float
    destination: str
    
    @classmethod
    def from_model(cls, package: Package) -> "PackageResponse":
        return cls(weight=package.weight, destination=package.destination)

# Response estructurada
class PackageCreateResponse(BaseModel):
    message: str
    package_details: PackageResponse

# En el endpoint
@app.post("/packages/", response_model=PackageCreateResponse)
async def create_package(package: PackageSchema):
    model = package.to_model()
    return PackageCreateResponse(
        message="Package received",
        package_details=PackageResponse.from_model(model)
    )
```

### 4. Beneficios de Response Models

1. Type Safety: Todo validado por Pydantic
2. Documentación automática: FastAPI genera OpenAPI/Swagger perfecto
3. Control de serialización: Decides qué campos exponer
4. Versionado fácil: Puedes tener `PackageResponseV1` y `PackageResponseV2`
5. No más `__dict__`: Pydantic maneja la conversión a JSON

## Estructura del Proyecto

```bash
01 Input Validation Drill/
├── main.py          # Endpoints FastAPI
├── models.py        # Modelos de dominio (clases Python)
├── schemas.py       # Schemas Pydantic (validación + serialización)
└── README.md        # Esta guía
```

## Validaciones Implementadas

```python
weight: Annotated[float, Field(
    gt=0,           # Greater than 0
    lt=50,          # Less than 50
    description="Weight in kg"
)]

destination: Annotated[str, Field(
    min_length=3,   # Mínimo 3 caracteres
    max_length=100  # Máximo 100 caracteres
)]

tags: set[str]      # Set automáticamente elimina duplicados
```

## Ejecutar

```bash
# Instalar dependencias
pip install fastapi uvicorn pydantic

# Correr servidor
uvicorn main:app --reload

# Ver docs interactivas
http://localhost:8000/docs
```

## Referencias

- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [FastAPI Response Models](https://fastapi.tiangolo.com/tutorial/response-model/)
- [Python TYPE_CHECKING](https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING)
