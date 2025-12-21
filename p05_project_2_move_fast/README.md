# Proyecto 2: Validación de Datos y Manejo de Errores en FastAPI

## Descripción General

Este proyecto representa una evolución significativa respecto a la primera API de libros. Mientras que el primer proyecto se centraba en la lógica básica de ruteo, este proyecto implementa prácticas profesionales para la validación de datos de entrada, manejo explícito de códigos de estado HTTP y gestión de excepciones.

El objetivo principal es asegurar la integridad de los datos y proporcionar respuestas estandarizadas al cliente.

## Nuevos Conceptos Implementados

### 1. Modelado de Datos con Pydantic

Se introduce la librería Pydantic para definir la estructura y validación de los datos que entran a la API.

* BaseModel: Se utiliza la clase `BookRequest` que hereda de `BaseModel`. Esto permite a FastAPI validar automáticamente el JSON recibido en las peticiones POST y PUT.
* Separación de Modelos: Se distingue entre la clase interna `Book` (usada para almacenar datos en el servidor) y el modelo `BookRequest` (usado para validar la entrada del usuario).

### 2. Validación de Campos (Field Validation)

Se utilizan validaciones estrictas dentro del modelo Pydantic usando `Field`. Esto previene que datos corruptos o ilógicos entren al sistema.

* Cadenas de texto: `min_length` y `max_length` aseguran que títulos y descripciones tengan longitudes coherentes.
* Numéricos: `gt` (greater than) y `lt` (less than) para restringir rangos.
* *Ejemplo:* El rating debe ser mayor a 0 y menor a 6.
* *Ejemplo:* El año de publicación debe estar entre 2000 y 2030.

* Documentación de Esquema: Se utiliza `model_config` y `json_schema_extra` para proporcionar un ejemplo de JSON por defecto en la interfaz de Swagger UI.

### 3. Validación de Parámetros de Ruta y Consulta

No solo se valida el cuerpo (Body), sino también los parámetros en la URL utilizando `Path` y `Query`.

* Path: Valida variables que forman parte de la ruta (ej. `/books/{book_id}`). Se asegura que el ID sea siempre un entero positivo (`gt=0`).
* Query: Valida variables opcionales (ej. `?rating=5`). Se aplican las mismas restricciones de rango que en el modelo de datos.

### 4. Códigos de Estado HTTP (HTTP Status Codes)

En lugar de devolver siempre un código 200 por defecto, se importan y utilizan códigos de estado explícitos desde `starlette.status` para cumplir con el estándar REST:

* HTTP_200_OK: Para peticiones GET exitosas.
* HTTP_201_CREATED: Específico para cuando se crea un recurso nuevo (POST).
* HTTP_204_NO_CONTENT: Utilizado en PUT y DELETE. Indica que la acción fue exitosa pero no hay contenido que devolver en el cuerpo de la respuesta.
* HTTP_404_NOT_FOUND: Cuando se busca un recurso que no existe.

### 5. Manejo de Excepciones (Error Handling)

Se implementa `HTTPException` para gestionar errores de lógica.

* En lugar de retornar un mensaje simple o `null` cuando no se encuentra un libro, el sistema interrumpe la ejecución y lanza una excepción HTTP 404.
* Esto permite al cliente (frontend u otra API) reaccionar programáticamente ante el error.

## Endpoints de la API

### Lectura (GET)

* `/books`: Retorna todos los libros (Status 200).
* `/books/{book_id}`: Busca por ID. Valida que el ID > 0 (Status 200 o 404).
* `/books/`: Filtra por rating. Valida rango 1-5 (Status 200).
* `/books/publish`: Filtra por año de publicación. Valida rango 2000-2030 (Status 200).

### Creación (POST)

* `/create-book`: Recibe un JSON validado por `BookRequest`. Asigna un ID automáticamente y convierte el modelo Pydantic a una instancia de la clase `Book` (Status 201).

### Actualización (PUT)

* `/books/update_book`: Recibe un JSON completo. Busca el libro por ID y reemplaza sus datos. Si no existe el ID, lanza error (Status 204).

### Eliminación (DELETE)

* `/books/{book_id}`: Elimina el libro si el ID existe. Si no, lanza error (Status 204).

## Cómo Ejecutar

Iniciar el servidor de desarrollo:

```bash
uvicorn books:app --reload

```

Acceder a la documentación interactiva:

```text
http://127.0.0.1:8000/docs

```
