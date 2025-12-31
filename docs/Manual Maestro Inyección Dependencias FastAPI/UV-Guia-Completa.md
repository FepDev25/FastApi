# UV - Gestor de Paquetes Ultra-Rápido para Python

> **UV** es un gestor de paquetes y entornos virtuales escrito en Rust, diseñado para ser **10-100x más rápido** que pip y otras herramientas tradicionales.

## Tabla de Contenidos

- [¿Qué es UV?](#qué-es-uv)
- [Instalación](#instalación)
- [Comandos Básicos](#comandos-básicos)
- [Gestión de Dependencias](#gestión-de-dependencias)
- [Archivos Generados](#archivos-generados)
- [Migración desde otros gestores](#migración-desde-otros-gestores)
- [Mejores Prácticas](#mejores-prácticas)

---

## ¿Qué es UV?

UV es una herramienta moderna para Python que combina:

- **Gestor de paquetes** (como pip)
- **Gestor de entornos virtuales** (como venv/virtualenv)
- **Gestor de versiones de Python** (como pyenv)
- **Gestor de proyectos** (como Poetry/PDM)

**Ventajas principales:**

- **Velocidad extrema** - Escrito en Rust
- **Lockfile automático** - Builds reproducibles
- **Gestión integral** - Todo en una herramienta
- **Compatibilidad** - Funciona con PyPI y proyectos existentes
- **Ligero** - Sin dependencias pesadas

---

## Instalación

### Linux/macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Verificar instalación

```bash
uv --version
```

---

## Comandos Básicos

### Crear un Nuevo Proyecto

```bash
# Crear proyecto con Python 3.12
uv init --python 3.12

# Esto genera automáticamente:
# ├── .python-version    # Versión de Python del proyecto
# ├── pyproject.toml     # Configuración y dependencias
# ├── README.md          # Documentación
# ├── main.py           # Archivo principal
# └── .venv/            # Entorno virtual (auto-creado)
```

**Ejemplo real del proyecto:**

```bash
uv init --python 3.12 fastapi-service-master
cd fastapi-service-master
```

Salida:

```bash
Initialized project `fastapi-service-master`
```

### Estructura Generada

```bash
fastapi-service-master/
├── .python-version      # 3.12.12
├── pyproject.toml       # Dependencias y metadata
├── README.md            # Documentación base
├── main.py             # Punto de entrada
└── .venv/              # Entorno virtual (gestionado automáticamente)
```

---

## Gestión de Dependencias

### Agregar Dependencias de Producción

```bash
# Agregar una dependencia
uv add fastapi

# Agregar múltiples dependencias
uv add fastapi pydantic-settings sqlmodel asyncpg
```

**Ejemplo real del proyecto:**

```bash
uv add fastapi pydantic-settings sqlmodel asyncpg
```

Salida:

```bash
Using CPython 3.12.12
Creating virtual environment at: .venv
Resolved 17 packages in 1.91s
Prepared 16 packages in 5.84s
Installed 16 packages in 20ms
 + annotated-doc==0.0.4
 + annotated-types==0.7.0
 + anyio==4.12.0
 + asyncpg==0.31.0
 + fastapi==0.128.0
 + greenlet==3.3.0
 + idna==3.11
 + pydantic==2.12.5
 + pydantic-core==2.41.5
 + pydantic-settings==2.12.0
 + python-dotenv==1.2.1
 + sqlalchemy==2.0.45
 + sqlmodel==0.0.31
 + starlette==0.50.0
 + typing-extensions==4.15.0
 + typing-inspection==0.4.2
```

**Agregar con extras:**

```bash
# Para uvicorn con soporte completo
uv add "uvicorn[standard]"
```

Salida:

```bash
Resolved 26 packages in 557ms
Prepared 8 packages in 3.13s
Installed 8 packages in 15ms
 + click==8.3.1
 + h11==0.16.0
 + httptools==0.7.1
 + pyyaml==6.0.3
 + uvicorn==0.40.0
 + uvloop==0.22.1
 + watchfiles==1.1.1
 + websockets==15.0.1
```

### Agregar Dependencias de Desarrollo

```bash
# Agregar dependencias solo para desarrollo
uv add --dev pytest pytest-asyncio httpx ruff
```

**Ejemplo real del proyecto:**

```bash
uv add --dev pytest pytest-asyncio httpx ruff greenlet
```

Salida:

```bash
Resolved 36 packages in 588ms
Prepared 10 packages in 8.26s
Installed 10 packages in 19ms
 + certifi==2025.11.12
 + httpcore==1.0.9
 + httpx==0.28.1
 + iniconfig==2.3.0
 + packaging==25.0
 + pluggy==1.6.0
 + pygments==2.19.2
 + pytest==9.0.2
 + pytest-asyncio>=1.3.0
 + ruff==0.14.10
```

### Otros Comandos de Dependencias

```bash
# Remover una dependencia
uv remove fastapi

# Actualizar todas las dependencias
uv lock --upgrade

# Instalar todas las dependencias del proyecto
uv sync

# Instalar sin dependencias de desarrollo
uv sync --no-dev
```

---

## Archivos Generados

### 1. `pyproject.toml`

Archivo de configuración del proyecto (equivalente a `requirements.txt` + `setup.py`):

```toml
[project]
name = "fastapi-service-master"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "asyncpg>=0.31.0",
    "fastapi>=0.128.0",
    "pydantic-settings>=2.12.0",
    "sqlmodel>=0.0.31",
    "uvicorn[standard]>=0.40.0",
]

[dependency-groups]
dev = [
    "greenlet>=3.3.0",
    "httpx>=0.28.1",
    "pytest>=9.0.2",
    "pytest-asyncio>=1.3.0",
    "ruff>=0.14.10",
]
```

### 2. `uv.lock`

**Lockfile** que garantiza builds reproducibles (como `package-lock.json` en Node.js):

- Contiene las versiones exactas de TODAS las dependencias (incluyendo transitivas)
- Debe ser versionado en Git
- Garantiza que todos los desarrolladores usen las mismas versiones
- Esencial para CI/CD

**IMPORTANTE:** Siempre versiona el `uv.lock` en Git.

### 3. `.python-version`

Especifica la versión exacta de Python del proyecto:

```bash
3.12.12
```

**Beneficios:**

- Consistencia entre desarrolladores
- Herramientas como `uv` y `pyenv` la usan automáticamente
- Evita problemas de compatibilidad

---

## Ejecutar Comandos en el Entorno

UV gestiona automáticamente el entorno virtual, no necesitas activarlo manualmente.

```bash
# Ejecutar un script Python
uv run python main.py

# Ejecutar un módulo instalado
uv run uvicorn main:app --reload

# Ejecutar tests
uv run pytest

# Ejecutar cualquier comando en el entorno
uv run python -m pip list
```

**Ventaja:** No necesitas activar/desactivar el entorno virtual, UV lo hace automáticamente.

---

## Migración desde otros Gestores

### Desde `pip + requirements.txt`

```bash
# Si tienes requirements.txt
uv init
uv add $(cat requirements.txt | grep -v '#' | xargs)

# O mejor, copiar manualmente las dependencias importantes
uv add fastapi uvicorn sqlalchemy
```

### Desde Poetry

```bash
# UV puede leer pyproject.toml de Poetry
uv sync  # Instala dependencias desde pyproject.toml existente
```

### Desde Conda

```bash
# Exportar dependencias de conda
conda list --export > conda-packages.txt

# Agregar manualmente las que sean de PyPI
uv add <paquete1> <paquete2>
```

---

## Mejores Prácticas

### 1. Versiona estos archivos en Git

```bash
git add pyproject.toml uv.lock .python-version
```

**Razones:**

- `pyproject.toml` - Define tu proyecto
- `uv.lock` - Garantiza reproducibilidad
- `.python-version` - Asegura la versión correcta de Python

### 2. NO versiones estos archivos

```gitignore
.venv/           # Entorno virtual local
__pycache__/     # Archivos compilados
*.pyc
.pytest_cache/
.env             # Variables de entorno sensibles
```

### 3. Usa `.env` para configuración sensible

```bash
# .env (NO versionar)
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=super-secret-key

# .env.example (SÍ versionar)
DATABASE_URL=postgresql://user:password@localhost/database
SECRET_KEY=change-me-in-production
```

### 4. Organiza dependencias por propósito

```toml
[project]
dependencies = [
    "fastapi>=0.100.0",      # Web framework
    "sqlmodel>=0.0.14",       # Database ORM
    "pydantic-settings>=2.0", # Configuration
]

[dependency-groups]
dev = [
    "pytest>=7.0",           # Testing
    "ruff>=0.1.0",           # Linting
    "httpx>=0.25",           # HTTP client for tests
]
```

---

## Comparación con otras Herramientas

| Característica | UV | pip | Poetry | Conda |
| --------------- | ---- | ---- | -------- | ------- |
| **Velocidad** | ⚡⚡⚡ | 🐌 | 🐌🐌 | 🐌 |
| **Lockfile** | ✅ | ❌ | ✅ | ✅ |
| **Gestión de Python** | ✅ | ❌ | ❌ | ✅ |
| **Resolución de deps** | ✅ | ⚠️ | ✅ | ✅ |
| **Entornos virtuales** | ✅ Auto | Manual | ✅ Auto | ✅ |
| **Escrito en** | Rust | Python | Python | Python/C |

---

## Comandos de Referencia Rápida

```bash
# Inicialización
uv init --python 3.12           # Crear nuevo proyecto

# Dependencias
uv add <paquete>                # Agregar dependencia
uv add --dev <paquete>          # Agregar dependencia de desarrollo
uv remove <paquete>             # Remover dependencia
uv sync                         # Instalar todas las dependencias
uv sync --no-dev               # Instalar solo producción

# Ejecución
uv run python script.py         # Ejecutar script
uv run uvicorn app:app         # Ejecutar servidor
uv run pytest                   # Ejecutar tests

# Mantenimiento
uv lock --upgrade              # Actualizar lockfile
uv pip list                    # Listar paquetes instalados
uv clean                       # Limpiar caché
```

---

## Recursos Adicionales

- **Documentación oficial:** <https://docs.astral.sh/uv/>
- **GitHub:** <https://github.com/astral-sh/uv>
- **Blog de Astral:** <https://astral.sh/blog>

---

## Ventajas Clave de UV

1. **Velocidad** - 10-100x más rápido que pip
2. **Reproducibilidad** - Lockfile automático garantiza builds idénticos
3. **Simplicidad** - Un solo comando para todo (`uv`)
4. **Todo incluido** - No necesitas pip, venv, pyenv por separado
5. **Compatible** - Funciona con PyPI y proyectos existentes
6. **Resolución inteligente** - Resuelve conflictos de dependencias automáticamente
7. **Caché eficiente** - Reutiliza paquetes descargados
8. **Mantenido activamente** - Por el equipo de Ruff/Astral

---

## Conclusión

UV representa el futuro de la gestión de paquetes en Python:

- **Para nuevos proyectos:** UV es la mejor opción
- **Para proyectos existentes:** Migración gradual es posible
- **Para equipos:** Mejora la experiencia de desarrollo significativamente

**El archivo `uv.lock` garantiza que todos los desarrolladores (y el entorno de CI/CD) tengan exactamente las mismas versiones de las librerías, byte a byte.**

---
