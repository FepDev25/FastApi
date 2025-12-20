# Proyecto 1: Lógica de Métodos de Solicitud en FastAPI

## Descripción General

Este proyecto implementa una API RESTful básica para la gestión de una librería (Books). Se utilizan los cuatro verbos HTTP principales para manipular una lista de diccionarios en memoria.

## Operaciones CRUD

El sistema cubre el ciclo de vida completo de los datos mediante las siguientes operaciones:

* Create (Crear): Utiliza el método POST para agregar nuevos libros a la lista.
* Read (Leer): Utiliza el método GET para recuperar información (todos los libros, libros específicos o filtrados).
* Update (Actualizar): Utiliza el método PUT para modificar un libro existente.
* Delete (Eliminar): Utiliza el método DELETE para remover un libro de la lista.

## Manejo de Parámetros

### 1. Path Parameters (Parámetros de Ruta)

Son variables dinámicas integradas directamente en la URL. Se utilizan para identificar recursos específicos.

* Sintaxis: `/books/{book_title}`
* Uso en código: Permite buscar un libro específico por su título dinámico.

### 2. Query Parameters (Parámetros de Consulta)

Son pares clave-valor que aparecen al final de la URL después de un signo de interrogación `?`. Se utilizan habitualmente para filtrar datos.

* Sintaxis: `/books/?category=fiction`
* Uso en código: Permite filtrar la lista de libros mostrando solo los que coinciden con una categoría o autor específico.

### 3. Parámetros Mixtos

FastAPI permite combinar Path y Query parameters en una sola solicitud.

* Caso de uso: Filtrar por un autor específico (Path) y una categoría específica (Query) simultáneamente.

## Cuerpo de la Solicitud (Request Body)

Para los métodos POST y PUT, se utiliza `from fastapi import Body`. Esto permite al cliente enviar datos en formato JSON dentro del cuerpo de la solicitud HTTP, en lugar de en la URL.

* Implementación: `async def create_book(new_book=Body())` recibe el objeto JSON completo para procesarlo.

## Lógica de Programación e Implementación

### Normalización de Cadenas

Para evitar errores de búsqueda por mayúsculas o minúsculas, se utiliza el método `.casefold()` de Python. Esto asegura que "Harry Potter" y "harry potter" sean tratados como iguales durante las comparaciones.

### Modificación de Listas en Memoria (Update y Delete)

Para las operaciones de actualización y eliminación, es necesario modificar la lista original `BOOKS` y no una copia local de la variable iteradora.

* Uso de `enumerate()`: Se utiliza para obtener tanto el índice (`i`) como el objeto (`book`).
* Actualización Correcta: Se asigna el nuevo valor usando el índice: `BOOKS[i] = updated_book`.
* Eliminación Correcta: Se utiliza el índice para remover el elemento: `BOOKS.pop(i)`.

## Ejecución y Documentación Automática

* Servidor: La aplicación se ejecuta con Uvicorn:
`uvicorn books:app --reload`
* Swagger UI: FastAPI genera documentación interactiva automáticamente, disponible en:
`http://127.0.0.1:8000/docs`
