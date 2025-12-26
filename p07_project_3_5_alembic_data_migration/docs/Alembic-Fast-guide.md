# Alembic Cook Guide: El Recetario Completo

## 1. Mise en place (Instalación e Inicialización)

Antes de empezar a cocinar, necesitas tener las herramientas listas.

| Comando | Descripción |
| --- | --- |
| `pip install alembic` | Instala la librería en tu entorno virtual. |
| `alembic init alembic` | **Crea el entorno de Alembic.** Genera la carpeta `/alembic` y el archivo `alembic.ini`. |
| `alembic init async` | (Variante) Úsalo si tu proyecto usa drivers asíncronos (ej. FastAPI con `asyncpg`). |

### El ingrediente secreto: Configuración inicial

Para que Alembic detecte tus tablas, debes editar dos archivos clave después del `init`:

1. **`alembic.ini`**: Busca la línea `sqlalchemy.url` y pon la dirección de tu base de datos.
2. **`alembic/env.py`**: Esto es crucial para el `--autogenerate`. Debes importar tu `Base` (tus modelos) y configurar `target_metadata`.

```python
# En alembic/env.py
from models import Base  # Importa tus modelos
target_metadata = Base.metadata # Asigna la metadata

```

---

## 2. El Ciclo Diario (El Flujo de Trabajo)

Estos son los comandos que usarás el 95% del tiempo. Apréndetelos de memoria.

### A. Preparar la receta (Crear Migración)

Cuando modificas tus modelos en Python (agregas columna, creas tabla), necesitas crear el archivo de migración.

| Comando | Descripción |
| --- | --- |
| `alembic revision --autogenerate -m "mensaje"` | **El más importante.** Compara tu código Python con la DB actual y crea el script de cambios automáticamente. |
| `alembic revision -m "mensaje"` | Crea una migración vacía. Útil si quieres escribir el SQL o la lógica de Python manualmente (ej. migración de datos, no de estructura). |

### B. Cocinar el plato (Aplicar Cambios)

Una vez revisado el archivo generado en `/alembic/versions`, toca impactar la base de datos.

| Comando | Descripción |
| --- | --- |
| `alembic upgrade head` | Aplica **todas** las migraciones pendientes hasta llegar a la más reciente. |
| `alembic upgrade +1` | Avanza solo **una** versión (útil para debugging paso a paso). |
| `alembic upgrade <revision_id>` | Avanza hasta una versión específica (copia el ID del archivo). |

---

## 3. Control de Calidad (Verificación e Historial)

Para saber en qué estado está tu cocina.

| Comando | Descripción |
| --- | --- |
| `alembic current` | Te dice en qué versión (ID) se encuentra tu base de datos actualmente. |
| `alembic history` | Muestra la lista de todas las migraciones creadas (orden cronológico). |
| `alembic history --verbose` | Muestra el historial con detalles completos y fechas. |
| `alembic heads` | Muestra cuál es la última versión disponible (la "punta" de la rama). |

---

## 4. Limpiando el desastre (Deshacer cambios)

¿Te equivocaste agregando una columna o la app explotó? Toca volver atrás.

| Comando | Descripción |
| --- | --- |
| `alembic downgrade -1` | Deshace **la última** migración aplicada. (Vuelve un paso atrás). |
| `alembic downgrade base` | Deshace **TODAS** las migraciones. Deja la base de datos vacía (sin tablas). **¡Cuidado!** |
| `alembic downgrade <revision_id>` | Regresa la base de datos al estado de ese ID específico. |

---

## 5. Recetas Avanzadas (Casos especiales)

### ⚠️ Caso: "Autogenerate no detecta mis cambios"

* **Causa:** Casi siempre es porque olvidaste importar tus modelos en el archivo `env.py` o no configuraste el `target_metadata`. Alembic necesita "ver" tus clases de Python para compararlas.

### ⚠️ Caso: "Tengo dos cabezas (Merge Heads)"

Si estás trabajando en equipo, tú creaste una migración y tu compañero otra, Alembic tendrá dos ramas separadas.

1. Ejecuta: `alembic merge heads -m "mergeo ramas"`
2. Esto crea una nueva migración que une ambas líneas.
3. Ejecuta: `alembic upgrade head`.

### ⚠️ Caso: "Quiero renombrar una tabla/columna"

Alembic (y SQL en general) suele interpretar un renombre como: "Borrar columna A" + "Crear columna B".

* **Solución:** Revisa siempre el archivo generado. Si ves un `op.drop_column` seguido de un `op.add_column`, perderás los datos.
* **Fix manual:** Edita el archivo generado y cambia esas líneas por `op.alter_column` o `op.rename_table`.

---

## Resumen del Chef (Cheat Sheet Rápido)

1. Haces cambios en `models.py`.
2. `alembic revision --autogenerate -m "nuevo cambio"`
3. (Opcional pero recomendado) Abres el archivo en `alembic/versions/` y verificas que el código se vea bien.
4. `alembic upgrade head`
5. ¡Listo! A servir. 🍽️
