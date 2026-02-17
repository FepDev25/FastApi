# Database Migration with Alembic - FastAPI Project

Este proyecto es una extensión del sistema de gestión de tareas (Todos Application) que incorpora **Alembic** como herramienta de migración de base de datos. El objetivo principal es demostrar cómo gestionar cambios en el esquema de la base de datos de forma controlada, versionada y reversible.

## Descripción General

Alembic es una herramienta de migración de bases de datos para SQLAlchemy. Permite versionar el esquema de la base de datos mediante scripts de migración, facilitando la evolución del esquema a lo largo del ciclo de vida de la aplicación sin perder datos existentes.

Este proyecto extiende la aplicación de tareas del módulo anterior agregando un campo `phone_number` a la tabla de usuarios, utilizando Alembic para gestionar esta migración de forma profesional.

## Qué es Alembic

Alembic es un framework de migración de bases de datos ligero para SQLAlchemy, desarrollado por el mismo autor de SQLAlchemy. Proporciona las siguientes capacidades:

- **Versionado del esquema**: Cada cambio en la base de datos se registra como una revisión
- **Migraciones reversibles**: Permite aplicar (upgrade) y revertir (downgrade) cambios
- **Historial de cambios**: Mantiene un registro completo de todas las modificaciones del esquema
- **Generación automática**: Puede detectar cambios en los modelos y generar scripts de migración automáticamente
- **Control de versiones**: Integra perfectamente con sistemas como Git

## Estructura del Proyecto

```bash
p07_project_3_5_alembic_data_migration/
├── main.py                    # Aplicación FastAPI
├── database.py                # Configuración de SQLAlchemy
├── models.py                  # Modelos con el nuevo campo phone_number
├── alembic.ini                # Archivo de configuración de Alembic
├── alembic/
│   ├── env.py                 # Script de entorno de Alembic (configurado)
│   ├── script.py.mako         # Template para generar nuevas revisiones
│   └── versions/
│       └── 53ac98ccbddc_create_phone_number_for_user_column.py
├── data/
│   └── mi_base.db            # Base de datos SQLite
├── docs/
│   └── Alembic-Fast-guide.md # Guía rápida de Alembic
└── routers/
    ├── auth.py               # Autenticación
    ├── todos.py              # CRUD de tareas
    ├── admin.py              # Panel administrativo
    └── users.py              # Gestión de usuarios
```

## Cambios Realizados

### Modificación del Modelo

Se agregó el campo `phone_number` al modelo `Users` en `models.py`:

```python
class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=True)
    phone_number = Column(String)  # Nuevo campo agregado
```

Este cambio requiere una modificación en el esquema de la base de datos existente, lo cual se gestiona mediante Alembic.

## Configuración de Alembic

### 1. Inicialización de Alembic

El primer paso es inicializar Alembic en el proyecto:

```bash
alembic init alembic
```

Este comando crea:

- Directorio `alembic/` con la estructura necesaria
- Archivo `alembic.ini` con la configuración
- Subdirectorio `alembic/versions/` para las migraciones
- Archivo `alembic/env.py` para el entorno de ejecución

**Salida del comando:**

```bash
Creating directory /path/to/project/alembic ...  done
Creating directory /path/to/project/alembic/versions ...  done
Generating /path/to/project/alembic/env.py ...  done
Generating /path/to/project/alembic.ini ...  done
Generating /path/to/project/alembic/README ...  done
Generating /path/to/project/alembic/script.py.mako ...  done
Please edit configuration/connection/logging settings in alembic.ini before proceeding.
```

### 2. Configuración de la Conexión a la Base de Datos

En el archivo `alembic.ini`, se debe configurar la URL de la base de datos:

```ini
# alembic.ini
sqlalchemy.url = sqlite:///./data/mi_base.db
```

Esta línea indica a Alembic dónde se encuentra la base de datos SQLite. Para otras bases de datos, el formato sería:

- PostgreSQL: `postgresql://user:password@localhost/dbname`
- MySQL: `mysql://user:password@localhost/dbname`

### 3. Configuración del Entorno de Migración

En el archivo `alembic/env.py`, se deben importar los modelos y configurar la metadata:

```python
# alembic/env.py
import models  # Importar los modelos de SQLAlchemy

# Configurar target_metadata para que Alembic conozca el esquema
target_metadata = models.Base.metadata
```

Esta configuración es crucial porque permite a Alembic:

- Conocer la estructura actual de los modelos
- Comparar el esquema de la base de datos con los modelos
- Generar migraciones automáticas (con `--autogenerate`)

## Proceso de Migración

### Paso 1: Crear una Nueva Revisión

Para crear una nueva migración, se utiliza el comando `alembic revision`:

```bash
alembic revision -m "Create phone number for user column"
```

**Salida:**

```bash
Generating /path/to/project/alembic/versions/53ac98ccbddc_create_phone_number_for_user_column.py ...  done
```

Este comando genera un archivo de revisión con:

- Un identificador único (`53ac98ccbddc`)
- Un mensaje descriptivo
- Funciones `upgrade()` y `downgrade()` vacías para implementar

**Estructura del archivo generado:**

```python
"""Create phone number for user column

Revision ID: 53ac98ccbddc
Revises: 
Create Date: 2025-12-26 17:46:13.270115

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '53ac98ccbddc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Implementar cambios hacia adelante
    pass


def downgrade() -> None:
    # Implementar reversión de cambios
    pass
```

### Paso 2: Implementar la Función upgrade()

La función `upgrade()` contiene las operaciones que se ejecutan al aplicar la migración:

```python
def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('phone_number', sa.String(length=15), nullable=True))
```

**Explicación:**

- `op.add_column()`: Operación de Alembic para agregar una columna
- `'users'`: Nombre de la tabla a modificar
- `sa.Column()`: Define la nueva columna con SQLAlchemy
- `phone_number`: Nombre del campo
- `sa.String(length=15)`: Tipo de dato con longitud máxima
- `nullable=True`: La columna acepta valores NULL (importante para datos existentes)

### Paso 3: Implementar la Función downgrade()

La función `downgrade()` revierte los cambios realizados por `upgrade()`:

```python
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'phone_number')
```

**Explicación:**

- `op.drop_column()`: Elimina la columna especificada
- Esta operación es la inversa de `add_column()`
- Permite deshacer la migración si es necesario

### Paso 4: Aplicar la Migración

Para aplicar la migración a la base de datos:

```bash
alembic upgrade 53ac98ccbddc
```

O para aplicar todas las migraciones pendientes:

```bash
alembic upgrade head
```

**Salida:**

```bash
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 53ac98ccbddc, Create phone number for user column
```

Esta operación:

1. Conecta a la base de datos
2. Verifica el estado actual de las migraciones
3. Ejecuta la función `upgrade()` del script de migración
4. Actualiza la tabla `alembic_version` con la nueva revisión

### Paso 5: Revertir la Migración (Opcional)

Si se necesita deshacer la migración:

```bash
alembic downgrade -1
```

**Salida:**

```bash
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running downgrade 53ac98ccbddc -> , Create phone number for user column
```

Opciones de downgrade:

- `alembic downgrade -1`: Retrocede una revisión
- `alembic downgrade <revision_id>`: Retrocede a una revisión específica
- `alembic downgrade base`: Retrocede todas las migraciones

## Comandos Útiles de Alembic

### Información y Estado

```bash
# Ver el historial de migraciones
alembic history

# Ver la revisión actual
alembic current

# Ver migraciones pendientes
alembic show head
```

### Gestión de Migraciones

```bash
# Crear una nueva revisión manualmente
alembic revision -m "descripción del cambio"

# Crear una revisión con autogeneración
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar todas las migraciones
alembic upgrade head

# Aplicar hasta una revisión específica
alembic upgrade <revision_id>

# Revertir una migración
alembic downgrade -1

# Revertir a una revisión específica
alembic downgrade <revision_id>

# Revertir todas las migraciones
alembic downgrade base
```

### Validación

```bash
# Verificar si hay cambios no migrados
alembic check

# Generar SQL sin ejecutar (dry-run)
alembic upgrade head --sql
```

## Conceptos Clave

### Revision ID

Cada migración tiene un identificador único (por ejemplo, `53ac98ccbddc`). Este ID:

- Se genera automáticamente
- Es único en el historial de migraciones
- Se utiliza para referenciar la migración
- Se almacena en la tabla `alembic_version` de la base de datos

### Down Revision

El campo `down_revision` indica la migración anterior:

- `None`: Es la primera migración
- `'abc123'`: Esta migración sigue a la revisión `abc123`
- Forma una cadena lineal de migraciones

### Operaciones Comunes

Alembic proporciona operaciones para modificar el esquema:

**Tablas:**

```python
# Crear tabla
op.create_table('nombre_tabla',
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('nombre', sa.String(50))
)

# Eliminar tabla
op.drop_table('nombre_tabla')
```

**Columnas:**

```python
# Agregar columna
op.add_column('tabla', sa.Column('columna', sa.String()))

# Eliminar columna
op.drop_column('tabla', 'columna')

# Modificar columna
op.alter_column('tabla', 'columna', type_=sa.Integer())
```

**Índices:**

```python
# Crear índice
op.create_index('idx_nombre', 'tabla', ['columna'])

# Eliminar índice
op.drop_index('idx_nombre', 'tabla')
```

**Llaves foráneas:**

```python
# Agregar foreign key
op.create_foreign_key('fk_name', 'tabla_source', 'tabla_target', 
                      ['col_local'], ['col_remota'])

# Eliminar foreign key
op.drop_constraint('fk_name', 'tabla', type_='foreignkey')
```

## Ventajas de Usar Alembic

### 1. Control de Versiones del Esquema

- Cada cambio en la base de datos se documenta y versiona
- Historial completo de la evolución del esquema
- Integración natural con sistemas de control de versiones (Git)

### 2. Migraciones Reversibles

- Posibilidad de revertir cambios si algo sale mal
- Facilita el rollback en producción
- Permite probar cambios de esquema de forma segura

### 3. Trabajo en Equipo

- Múltiples desarrolladores pueden trabajar en paralelo
- Los cambios de esquema se comparten mediante Git
- Conflictos de migración detectables y resolubles

### 4. Despliegue Consistente

- Mismo proceso de migración en desarrollo, staging y producción
- Reduce errores humanos en aplicación de cambios
- Automatizable en pipelines de CI/CD

### 5. Preservación de Datos

- Las migraciones no destruyen datos existentes
- Permite transformaciones complejas de datos
- Soporte para valores por defecto en nuevas columnas

### 6. Auditoría y Documentación

- Cada migración incluye descripción y fecha
- Código de migración sirve como documentación
- Facilita auditorías de cambios en el esquema

## Buenas Prácticas

### 1. Mensajes Descriptivos

Usar mensajes claros y específicos al crear revisiones:

```bash
# Bien
alembic revision -m "Add phone_number column to users table"

# Mal
alembic revision -m "Update users"
```

### 2. Migraciones Atómicas

Cada migración debe hacer una cosa específica:

- Una migración = un cambio lógico
- Evitar agrupar cambios no relacionados
- Facilita la comprensión y el rollback

### 3. Probar en Desarrollo

Siempre probar las migraciones en un entorno de desarrollo antes de aplicarlas en producción:

```bash
# Aplicar
alembic upgrade head

# Verificar
# Probar la aplicación

# Si hay problemas, revertir
alembic downgrade -1
```

### 4. Hacer Backup

Siempre respaldar la base de datos antes de aplicar migraciones en producción:

```bash
# PostgreSQL
pg_dump dbname > backup.sql

# MySQL
mysqldump dbname > backup.sql

# SQLite
cp database.db database.db.backup
```

### 5. Documentar Cambios Complejos

Para migraciones complejas, incluir comentarios explicativos:

```python
def upgrade() -> None:
    """
    Migración de datos del campo 'name' a 'first_name' y 'last_name'.
    Se divide el nombre completo usando espacio como separador.
    """
    # Primero agregar las nuevas columnas
    op.add_column('users', sa.Column('first_name', sa.String()))
    op.add_column('users', sa.Column('last_name', sa.String()))
    
    # Luego migrar los datos
    # ... código de migración de datos ...
```

### 6. Usar --autogenerate con Precaución

La generación automática es útil pero debe revisarse:

```bash
alembic revision --autogenerate -m "Auto-detected changes"
```

- Revisar siempre el script generado
- Alembic no detecta todos los cambios (ej: cambios en índices)
- Puede generar código innecesario

## Integración con FastAPI

En un proyecto FastAPI con Alembic, el flujo típico es:

1. **Modificar los modelos** en `models.py`
2. **Crear la migración** con `alembic revision`
3. **Implementar upgrade/downgrade** en el script de migración
4. **Aplicar la migración** con `alembic upgrade head`
5. **Actualizar el código** de la aplicación para usar los nuevos campos
6. **Desplegar** la aplicación actualizada

**Importante:** No usar `Base.metadata.create_all()` en producción cuando se usa Alembic. Las migraciones deben gestionarse exclusivamente con Alembic.

## Ejemplo Completo: Agregar Campo phone_number

### Paso a Paso

**1. Modificar el modelo:**

```python
# models.py
class Users(Base):
    # ... campos existentes ...
    phone_number = Column(String)  # Nuevo campo
```

**2. Crear la revisión:**

```bash
alembic revision -m "Create phone number for user column"
```

**3. Implementar la migración:**

```python
# alembic/versions/53ac98ccbddc_....py
def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(length=15), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'phone_number')
```

**4. Aplicar la migración:**

```bash
alembic upgrade head
```

**5. Verificar:**

```bash
alembic current
```

## Instalación y Ejecución

### Requisitos

```bash
pip install fastapi uvicorn sqlalchemy alembic passlib python-jose python-multipart bcrypt
```

### Configuración Inicial

1. La base de datos se encuentra en `data/mi_base.db`
2. Alembic ya está configurado en `alembic.ini`
3. Las migraciones están en `alembic/versions/`

### Aplicar Migraciones

```bash
# Verificar estado actual
alembic current

# Aplicar todas las migraciones
alembic upgrade head

# Ver historial
alembic history
```

### Ejecutar la Aplicación

```bash
uvicorn main:app --reload
```

La aplicación estará disponible en `http://localhost:8000`

## Documentación Adicional

Para más información sobre Alembic:

- **Documentación oficial**: <https://alembic.sqlalchemy.org/>
- **Tutorial de Alembic**: <https://alembic.sqlalchemy.org/en/latest/tutorial.html>
- **Guía rápida del proyecto**: Ver `docs/Alembic-Fast-guide.md`

## Conclusión

Alembic es una herramienta esencial para cualquier proyecto que use SQLAlchemy y necesite gestionar cambios en el esquema de base de datos de forma profesional. Proporciona:

- Versionado claro del esquema de base de datos
- Proceso seguro y reversible de aplicación de cambios
- Integración perfecta con FastAPI y SQLAlchemy
- Facilita el trabajo en equipo y despliegues
- Reduce errores humanos en la gestión de bases de datos

Este proyecto demuestra la implementación básica de Alembic, sirviendo como base para gestionar migraciones más complejas en proyectos reales.
