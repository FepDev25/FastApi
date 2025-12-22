# SQLite Prompt Cookbook

---

## 1. Los "Dot Commands" (Meta-comandos)

En SQLite usas `.` (punto). Estos no llevan punto y coma `;` al final.

| Comando | Descripción | Equivalente Postgres |
| --- | --- | --- |
| `.open archivo.db` | Abre una conexión a un archivo database. | `\c` (más o menos) |
| `.tables` | Lista las tablas. | `\dt` |
| `.schema [tabla]` | Muestra el `CREATE TABLE` de una (o todas). | `\d nombre_tabla` |
| `.databases` | Muestra los archivos DB adjuntos (path físico). | `\l` |
| `.quit` o `.exit` | Salir de la shell. | `\q` |
| `.help` | Muestra todos los comandos disponibles. | `\?` |
| `.system [cmd]` | Ejecuta un comando de shell (ej: `.system ls -la`). | `\!` |

---

## 2. Formato Visual (Human Friendly)

Por defecto, SQLite es feo (separado por `|` sin alineación). Hay versiones recientes que soportan `box`.

```sql
-- El mejor formato para leer (tipo tabla de MySQL/Postgres moderna)
.mode box

-- Si tu versión es vieja y no tiene box:
.mode column
.headers on

-- Ver el plan de ejecución (Query Plan)
.eqp on

```

---

## 3. Administración y Tunning (Los `PRAGMA`)

En SQLite no hay `postgresql.conf`. La configuración se hace con comandos SQL especiales llamados `PRAGMA`.

```sql
-- 1. Activar Claves Foráneas (IMPORTANTE: Vienen apagadas por defecto)
PRAGMA foreign_keys = ON;

-- 2. Modo WAL (Concurrencia: permite leer y escribir a la vez)
PRAGMA journal_mode = WAL;

-- 3. Sincronización (NORMAL es seguro y rápido, FULL es paranoico y lento)
PRAGMA synchronous = NORMAL;

-- 4. Ver información detallada de una tabla (Columnas, tipos, nulos)
PRAGMA table_info(nombre_tabla);

-- 5. Ver índices de una tabla
PRAGMA index_list(nombre_tabla);

```

---

## 4. Importar y Exportar Datos (ETL Rápido)

SQLite es una bestia para convertir CSVs a SQL y viceversa.

Importar un CSV:

```sql
.mode csv
.import /ruta/al/archivo.csv nombre_tabla
-- Si la tabla no existe, SQLite la crea basándose en el header del CSV.

```

Exportar a CSV:

```sql
.headers on
.mode csv
.output data_export.csv
SELECT * FROM usuarios WHERE activo = 1;
.output stdout  -- Regresar la salida a la pantalla
.mode box       -- Regresar al modo visual bonito

```

Dump completo (Backup lógico):

```sql
.output backup.sql
.dump
.output stdout

```

---

## 5. Manejo de Fechas (El gran dolor de cabeza)

SQLite no tiene tipo de dato DATE o DATETIME. Se guardan como TEXT (ISO8601), REAL (Julianday) o INTEGER (Unix Epoch).
*Recomendación:* Usa siempre TEXT en formato `YYYY-MM-DD HH:MM:SS`.

```sql
-- Insertar fecha actual
INSERT INTO logs (mensaje, fecha) VALUES ('Error 500', datetime('now'));

-- Insertar fecha actual en zona horaria local (por defecto usa UTC)
INSERT INTO logs (mensaje, fecha) VALUES ('Login', datetime('now', 'localtime'));

-- Calcular diferencia (ej: usuarios registrados hace más de 7 días)
SELECT * FROM usuarios 
WHERE fecha_registro < date('now', '-7 days');

```

---

## 6. JSON (Power User)

SQLite tiene soporte nativo para JSON. Muy útil para guardar respuestas de APIs sin normalizar todo.

```sql
-- Extraer un valor de un campo JSON
-- Supongamos campo 'metadata' = {"theme": "dark", "retries": 3}
SELECT json_extract(metadata, '$.theme') FROM configs;

-- O usando la sintaxis de flecha (versiones recientes)
SELECT metadata->>'theme' FROM configs;

```

---

## 7. Mantenimiento (El comando `VACUUM`)

Como es un archivo único, cuando borras datos, el archivo no se reduce de tamaño automáticamente (queda fragmentado).

```sql
-- Reconstruye la base de datos entera para liberar espacio en disco
VACUUM;

```
