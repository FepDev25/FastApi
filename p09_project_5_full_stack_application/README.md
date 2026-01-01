# Full Stack Application - FastAPI with Jinja2 Templates

Este proyecto es una evolución de la aplicación de gestión de tareas que implementa una **interfaz de usuario completa** utilizando templates HTML renderizados por el servidor con **Jinja2**. Transforma la API REST pura en una aplicación web full stack con autenticación basada en cookies y páginas dinámicas.

## Descripción General

Este proyecto demuestra cómo construir una aplicación web completa con FastAPI, integrando:

- **Backend**: API REST con FastAPI y SQLAlchemy
- **Frontend**: Templates HTML dinámicos con Jinja2
- **Autenticación**: Sistema basado en cookies JWT
- **Estilos**: Bootstrap 4 para UI responsive
- **JavaScript**: Interacciones asíncronas con Fetch API

La aplicación mantiene toda la funcionalidad de la API REST del proyecto anterior mientras agrega una interfaz web completa para que los usuarios interactúen con el sistema sin necesidad de herramientas como Postman o cURL.

## Estructura del Proyecto

```bash
p09_project_5_full_stack_application/
├── main.py                    # Aplicación principal con montaje de static files
├── database.py                # Configuración de SQLAlchemy
├── models.py                  # Modelos de base de datos
├── routers/
│   ├── auth.py               # Autenticación + endpoints de páginas
│   ├── todos.py              # CRUD de tareas + endpoints de páginas
│   ├── admin.py              # Panel administrativo
│   └── users.py              # Gestión de usuarios
├── templates/                 # Templates Jinja2
│   ├── layout.html           # Template base
│   ├── navbar.html           # Barra de navegación
│   ├── login.html            # Página de login
│   ├── register.html         # Página de registro
│   ├── todo.html             # Lista de tareas
│   ├── add-todo.html         # Formulario para agregar tarea
│   └── edit-todo.html        # Formulario para editar tarea
├── static/                    # Archivos estáticos
│   ├── css/
│   │   ├── base.css          # Estilos personalizados
│   │   └── bootstrap.css     # Framework CSS
│   └── js/
│       ├── base.js           # JavaScript personalizado
│       ├── jquery-slim.js    # jQuery
│       ├── popper.js         # Popper.js (tooltips)
│       └── bootstrap.js      # Bootstrap JS
├── data/
│   └── mi_base.db           # Base de datos SQLite
└── test/                     # Suite de pruebas
```

## Jinja2 en FastAPI

### ¿Qué es Jinja2?

Jinja2 es un motor de templates moderno y potente para Python. Permite:

- **Renderizar HTML dinámico** con datos del servidor
- **Herencia de templates** para reutilizar estructuras
- **Condicionales y bucles** dentro del HTML
- **Filtros** para transformar datos
- **Includes** para modularizar el código

### Configuración de Jinja2

En los routers se configura Jinja2Templates:

```python
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
```

Esta instancia permite renderizar templates HTML con datos del backend.

### Renderizar Templates

Patrón básico para servir páginas HTML:

```python
@router.get("/login-page")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
```

**Componentes:**

- `request`: Objeto Request de FastAPI (requerido por Jinja2)
- `"login.html"`: Nombre del template
- `{"request": request}`: Contexto pasado al template

### Pasar Datos al Template

```python
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    user = await get_current_user(request.cookies.get('access_token'))
    todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
    
    return templates.TemplateResponse("todo.html", {
        "request": request,
        "todos": todos,
        "user": user
    })
```

Los datos (`todos`, `user`) están disponibles en el template para renderizado dinámico.

## Sistema de Templates

### Template Base (layout.html)

Define la estructura común de todas las páginas:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="{{ url_for('static', path='/css/base.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', path='/css/bootstrap.css') }}">
    <title>TodoApp</title>
</head>
<body>
    {% include 'navbar.html' %}
    
    {% block content %}
    {% endblock %}
    
    <script src="{{ url_for('static', path='/js/jquery-slim.js') }}"></script>
    <script src="{{ url_for('static', path='/js/bootstrap.js') }}"></script>
    <script src="{{ url_for('static', path='/js/base.js') }}" defer></script>
</body>
</html>
```

**Características:**

- **`url_for()`**: Genera URLs para archivos estáticos
- **`{% include %}`**: Incluye otros templates (navbar)
- **`{% block content %}`**: Define áreas que templates hijos pueden sobrescribir

### Herencia de Templates

Las páginas específicas extienden el layout base:

```html
{% include 'layout.html' %}

<div class="container">
    <!-- Contenido específico de la página -->
</div>
```

Esto permite:

- Reutilizar estructura HTML común
- Mantener consistencia visual
- Actualizar navbar/footer en un solo lugar

### Navbar Condicional (navbar.html)

Muestra elementos según el estado de autenticación:

```html
<nav class="navbar navbar-expand-md navbar-dark main-color fixed-top">
    <a class="navbar-brand" href="#">Todo App</a>
    <div class="collapse navbar-collapse">
        <ul class="navbar-nav">
            {% if user %}
            <li class="nav-item">
                <a class="nav-link" href="/todos/todo-page">Home</a>
            </li>
            {% endif %}
        </ul>
        
        <ul class="navbar-nav ml-auto">
            {% if user %}
            <li class="nav-item">
                <a class="btn btn-outline-light" onclick="logout()">Logout</a>
            </li>
            {% endif %}
        </ul>
    </div>
</nav>
```

**Condicional `{% if user %}`**: Solo muestra links si el usuario está autenticado.

## Páginas de la Aplicación

### 1. Página de Login (login.html)

Formulario para autenticar usuarios:

```html
<div class="container">
    <div class="card">
        <div class="card-header">Login</div>
        <div class="card-body">
            <form id="loginForm">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" class="form-control" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
            </form>
        </div>
        <div class="card-footer">
            <a href="/auth/register-page">Register?</a>
        </div>
    </div>
</div>
```

**Características:**

- Formulario Bootstrap responsive
- Validación HTML5 (`required`)
- JavaScript maneja el submit (en `base.js`)
- Link a página de registro

### 2. Página de Registro (register.html)

Formulario completo para crear cuenta:

```html
<form id="registerForm">
    <div class="form-row">
        <div class="form-group col-md-6">
            <label>Email</label>
            <input type="text" class="form-control" name="email" required>
        </div>
        <div class="form-group col-md-6">
            <label>Username</label>
            <input type="text" class="form-control" name="username" required>
        </div>
    </div>
    <div class="form-row">
        <div class="form-group col-md-6">
            <label>First Name</label>
            <input type="text" class="form-control" name="firstname" required>
        </div>
        <div class="form-group col-md-6">
            <label>Last Name</label>
            <input type="text" class="form-control" name="lastname" required>
        </div>
    </div>
    <!-- Más campos... -->
    <button type="submit" class="btn btn-primary">Sign in</button>
</form>
```

**Campos:**

- Email, Username
- First Name, Last Name
- Role, Phone Number
- Password, Verify Password

### 3. Lista de Tareas (todo.html)

Muestra todas las tareas del usuario con renderizado condicional:

```html
<table class="table table-hover">
    <thead>
        <tr>
            <th>#</th>
            <th>Info</th>
            <th>Priority</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
    {% for todo in todos %}
        {% if todo.complete == False %}
        <tr class="pointer">
            <td>{{loop.index}}</td>
            <td>{{todo.title}}</td>
            <td>{{todo.priority}}</td>
            <td>
                <button onclick="window.location.href='edit-todo-page/{{todo.id}}'"
                        class="btn btn-info">Edit</button>
            </td>
        </tr>
        {% else %}
        <tr class="pointer alert alert-success">
            <td>{{loop.index}}</td>
            <td class="strike-through-td">{{todo.title}}</td>
            <td>
                <button onclick="window.location.href='edit-todo-page/{{todo.id}}'"
                        class="btn btn-info">Edit</button>
            </td>
        </tr>
        {% endif %}
    {% endfor %}
    </tbody>
</table>
<a href="add-todo-page" class="btn btn-primary">Add a new todo!</a>
```

**Características de Jinja2:**

- **`{% for todo in todos %}`**: Itera sobre la lista de tareas
- **`{{loop.index}}`**: Número de iteración (1-indexed)
- **`{{todo.title}}`**: Accede a propiedades del objeto
- **`{% if todo.complete %}`**: Renderizado condicional
- **Clases CSS dinámicas**: `alert-success` para tareas completadas
- **`strike-through-td`**: Estilo para marcar como completado

### 4. Agregar Tarea (add-todo.html)

Formulario para crear nuevas tareas:

```html
<form id="todoForm">
    <div class="form-group">
        <label>Title</label>
        <input type="text" class="form-control" name="title" required>
    </div>
    <div class="form-group">
        <label>Description</label>
        <textarea class="form-control" rows="3" name="description" required></textarea>
    </div>
    <div class="form-group">
        <label>Priority</label>
        <select class="form-control" name="priority">
            <option>1</option>
            <option>2</option>
            <option>3</option>
            <option>4</option>
            <option>5</option>
        </select>
    </div>
    <button type="submit" class="btn btn-primary">Add new todo</button>
    <a href="/todos/todo-page" class="btn btn-success">Back</a>
</form>
```

**Validaciones:**

- HTML5 `required` en campos obligatorios
- Select para prioridad (1-5)
- JavaScript envía datos a API REST

### 5. Editar Tarea (edit-todo.html)

Formulario prellenado con datos de la tarea:

```html
<form id="editTodoForm">
    <div class="form-group">
        <label>Title</label>
        <input type="text" class="form-control" name="title" value="{{todo.title}}" required>
    </div>
    <div class="form-group">
        <label>Description</label>
        <textarea name="description" class="form-control" rows="3" required>{{todo.description}}</textarea>
    </div>
    <div class="form-group">
        <label>Priority</label>
        <select name="priority" class="form-control">
            <option {% if todo.priority == 1 %} selected="selected" {% endif %}>1</option>
            <option {% if todo.priority == 2 %} selected="selected" {% endif %}>2</option>
            <option {% if todo.priority == 3 %} selected="selected" {% endif %}>3</option>
            <option {% if todo.priority == 4 %} selected="selected" {% endif %}>4</option>
            <option {% if todo.priority == 5 %} selected="selected" {% endif %}>5</option>
        </select>
    </div>
    <div class="form-group form-check">
        <input type="checkbox" class="form-check-input" name="complete" 
               {% if todo.complete %} checked {% endif %}>
        <label class="form-check-label">Complete</label>
    </div>
    <button type="submit" class="btn btn-primary">Edit your todo</button>
    <button id="deleteButton" type="button" class="btn btn-danger">Delete</button>
    <a href="/todos/todo-page" class="btn btn-success">Back</a>
</form>
```

**Características:**

- **`value="{{todo.title}}"`**: Precargar valores
- **`selected="selected"`**: Opción seleccionada en dropdown
- **`{% if todo.complete %} checked {% endif %}`**: Checkbox condicional
- Botón de eliminar con confirmación

## Autenticación Basada en Cookies

### Diferencia con JWT en Headers

**API REST (proyecto anterior):**

```bash
Authorization: Bearer <token>
```

**Full Stack (este proyecto):**

```bash
Cookie: access_token=<token>
```

### Flujo de Autenticación

1. **Login**: Usuario envía credenciales
2. **Backend**: Valida y genera token JWT
3. **Cookie**: Token se guarda en cookie HTTP
4. **Requests**: Cookie se envía automáticamente
5. **Backend**: Extrae token de cookie para autenticar

### Implementación en el Router

```python
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        # Extraer token de la cookie
        user = await get_current_user(request.cookies.get('access_token'))
        
        if user is None:
            return redirect_to_login()
        
        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
        
        return templates.TemplateResponse("todo.html", {
            "request": request,
            "todos": todos,
            "user": user
        })
    except:
        return redirect_to_login()
```

**Manejo de errores:**

- Si el token es inválido o expirado → Redirige a login
- Cookie se elimina al hacer logout

### Función de Redirección

```python
def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", 
                                        status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response
```

**Acciones:**

1. Crea redirección HTTP 302 a página de login
2. Elimina la cookie del token
3. Usuario debe autenticarse nuevamente

## JavaScript del Cliente (base.js)

El archivo `base.js` maneja las interacciones del cliente con la API.

### Función para Obtener Cookies

```javascript
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
```

Extrae el valor de una cookie por nombre.

### Login

```javascript
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const data = new URLSearchParams(formData);
        
        const response = await fetch('/auth/token', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: data
        });
        
        if (response.ok) {
            const result = await response.json();
            // Guardar token en cookie
            document.cookie = `access_token=${result.access_token}; path=/`;
            window.location.href = '/todos/todo-page';
        } else {
            alert('Login failed!');
        }
    });
}
```

**Flujo:**

1. Prevenir submit por defecto
2. Recopilar datos del formulario
3. Enviar POST a `/auth/token`
4. Guardar token en cookie
5. Redirigir a página de tareas

### Logout

```javascript
function logout() {
    document.cookie = 'access_token=; Max-Age=0; path=/';
    window.location.href = '/auth/login-page';
}
```

**Acciones:**

- Elimina la cookie (Max-Age=0)
- Redirige a página de login

### Agregar Tarea

```javascript
const todoForm = document.getElementById('todoForm');
if (todoForm) {
    todoForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());
        
        const payload = {
            title: data.title,
            description: data.description,
            priority: parseInt(data.priority),
            complete: false
        };
        
        const response = await fetch('/todos/todo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getCookie('access_token')}`
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            window.location.href = '/todos/todo-page';
        } else {
            alert('Error creating todo');
        }
    });
}
```

**Pasos:**

1. Prevenir submit por defecto
2. Convertir FormData a objeto JavaScript
3. Construir payload JSON
4. Enviar POST a API REST con token en header
5. Redirigir si exitoso

### Editar Tarea

```javascript
const editTodoForm = document.getElementById('editTodoForm');
if (editTodoForm) {
    editTodoForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());
        
        // Extraer ID de la URL
        const url = window.location.pathname;
        const todoId = url.substring(url.lastIndexOf('/') + 1);
        
        const payload = {
            title: data.title,
            description: data.description,
            priority: parseInt(data.priority),
            complete: data.complete === "on"
        };
        
        const response = await fetch(`/todos/todo/${todoId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getCookie('access_token')}`
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            window.location.href = '/todos/todo-page';
        } else {
            alert('Error updating todo');
        }
    });
}
```

**Características:**

- Extrae ID de la tarea de la URL
- Maneja checkbox (`complete === "on"`)
- Envía PUT a API REST

### Eliminar Tarea

```javascript
document.getElementById('deleteButton').addEventListener('click', async function () {
    const url = window.location.pathname;
    const todoId = url.substring(url.lastIndexOf('/') + 1);
    
    if (confirm('Are you sure you want to delete this todo?')) {
        const response = await fetch(`/todos/todo/${todoId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getCookie('access_token')}`
            }
        });
        
        if (response.ok) {
            window.location.href = '/todos/todo-page';
        } else {
            alert('Error deleting todo');
        }
    }
});
```

**Seguridad:**

- Confirmación antes de eliminar
- DELETE request a API REST

### Registro

```javascript
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());
        
        // Validar contraseñas coinciden
        if (data.password !== data.password2) {
            alert('Passwords do not match!');
            return;
        }
        
        const payload = {
            username: data.username,
            email: data.email,
            first_name: data.firstname,
            last_name: data.lastname,
            password: data.password,
            role: data.role,
            phone_number: data.phone_number
        };
        
        const response = await fetch('/auth/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            window.location.href = '/auth/login-page';
        } else {
            alert('Registration failed!');
        }
    });
}
```

**Validaciones:**

- Verifica que las contraseñas coincidan
- Redirige a login tras registro exitoso

## Archivos Estáticos

### Configuración en main.py

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

**Funcionalidad:**

- Sirve archivos CSS, JavaScript, imágenes
- Accesibles en rutas como `/static/css/base.css`

### Referenciar en Templates

```html
<link rel="stylesheet" href="{{ url_for('static', path='/css/bootstrap.css') }}">
<script src="{{ url_for('static', path='/js/base.js') }}"></script>
```

**`url_for('static', path='...')`**: Genera URL correcta automáticamente.

## Flujo Completo de la Aplicación

### 1. Usuario No Autenticado

```bash
1. Usuario visita http://localhost:8000/
   ↓
2. main.py redirige a /todos/todo-page
   ↓
3. todos.py detecta ausencia de cookie
   ↓
4. Redirige a /auth/login-page
   ↓
5. Renderiza login.html
```

### 2. Login

```bash
1. Usuario ingresa credenciales
   ↓
2. JavaScript envía POST /auth/token
   ↓
3. Backend valida credenciales
   ↓
4. Genera token JWT
   ↓
5. JavaScript guarda token en cookie
   ↓
6. Redirige a /todos/todo-page
```

### 3. Visualizar Tareas

```bash
1. Browser envía GET /todos/todo-page + cookie
   ↓
2. Backend extrae token de cookie
   ↓
3. Valida token y obtiene user_id
   ↓
4. Query: SELECT * FROM todos WHERE owner_id = user_id
   ↓
5. Renderiza todo.html con datos
   ↓
6. Browser muestra lista de tareas
```

### 4. Agregar Tarea

```bash
1. Usuario hace clic en "Add a new todo!"
   ↓
2. GET /todos/add-todo-page
   ↓
3. Renderiza add-todo.html
   ↓
4. Usuario completa formulario y submit
   ↓
5. JavaScript envía POST /todos/todo + token
   ↓
6. Backend inserta en BD
   ↓
7. Redirige a /todos/todo-page
```

### 5. Editar Tarea

```bash
1. Usuario hace clic en "Edit"
   ↓
2. GET /todos/edit-todo-page/5
   ↓
3. Backend busca tarea con id=5
   ↓
4. Renderiza edit-todo.html con datos prellenados
   ↓
5. Usuario modifica y submit
   ↓
6. JavaScript envía PUT /todos/todo/5 + token
   ↓
7. Backend actualiza en BD
   ↓
8. Redirige a /todos/todo-page
```

### 6. Eliminar Tarea

```bash
1. Usuario hace clic en "Delete"
   ↓
2. JavaScript muestra confirmación
   ↓
3. Si confirma: DELETE /todos/todo/5 + token
   ↓
4. Backend elimina de BD
   ↓
5. Redirige a /todos/todo-page
```

### 7. Logout

```bash
1. Usuario hace clic en "Logout"
   ↓
2. JavaScript elimina cookie
   ↓
3. Redirige a /auth/login-page
```

## Ventajas de la Arquitectura Full Stack

### 1. Experiencia de Usuario Completa

- Interfaz gráfica intuitiva
- No requiere herramientas técnicas
- Feedback visual inmediato

### 2. Mantiene la API REST

- Endpoints API siguen funcionando
- Aplicaciones móviles pueden consumir la API
- Flexibilidad para múltiples clientes

### 3. Renderizado del Servidor (SSR)

- SEO friendly
- Carga inicial más rápida
- Menos JavaScript en el cliente

### 4. Arquitectura Híbrida

- Templates para páginas completas
- JavaScript para interactividad
- API REST para operaciones CRUD

### 5. Separación de Responsabilidades

- Backend: Lógica de negocio y datos
- Templates: Estructura y presentación
- JavaScript: Interacciones dinámicas
- CSS: Estilos y diseño

## Diferencias con SPA (Single Page Application)

### Este Proyecto (Server-Side Rendering)

**Ventajas:**

- SEO mejorado
- Carga inicial rápida
- Menos JavaScript complejo
- Estado manejado por servidor

**Desventajas:**

- Recargas de página
- Más tráfico de red
- Menos fluido que SPA

### SPA (React, Vue, Angular)

**Ventajas:**

- Experiencia más fluida
- Sin recargas de página
- Interactividad avanzada

**Desventajas:**

- Bundle JavaScript grande
- Complejidad adicional
- SEO requiere configuración especial

## Instalación y Ejecución

### Requisitos

```bash
pip install fastapi uvicorn sqlalchemy alembic jinja2 passlib python-jose python-multipart bcrypt
```

### Estructura de Archivos Estáticos

Asegurarse de que existan:

- `static/css/` con archivos CSS
- `static/js/` con archivos JavaScript
- `templates/` con todos los archivos HTML

### Ejecutar la Aplicación

```bash
uvicorn main:app --reload
```

La aplicación estará disponible en: `http://localhost:8000`

### Primera Visita

1. Navegar a `http://localhost:8000`
2. Será redirigido a `/auth/login-page`
3. Hacer clic en "Register?" para crear cuenta
4. Completar formulario de registro
5. Iniciar sesión con las credenciales
6. Acceder a la lista de tareas

## Estructura de Endpoints

### Páginas (Renderizado de Templates)

| Método | Ruta | Descripción |
| -------- | ------ | ------------- |
| GET | `/auth/login-page` | Página de login |
| GET | `/auth/register-page` | Página de registro |
| GET | `/todos/todo-page` | Lista de tareas |
| GET | `/todos/add-todo-page` | Formulario nueva tarea |
| GET | `/todos/edit-todo-page/{id}` | Formulario editar tarea |

### API REST (JSON Responses)

| Método | Ruta | Descripción |
| -------- | ------ | ------------- |
| POST | `/auth/` | Registrar usuario |
| POST | `/auth/token` | Login (obtener token) |
| GET | `/todos/` | Listar tareas |
| GET | `/todos/todo/{id}` | Obtener tarea |
| POST | `/todos/todo/` | Crear tarea |
| PUT | `/todos/todo/{id}` | Actualizar tarea |
| DELETE | `/todos/todo/{id}` | Eliminar tarea |

**Nota**: Los endpoints de páginas y API coexisten en la misma aplicación.

## Buenas Prácticas Implementadas

### 1. Separación de Páginas y API

```python
# Páginas (devuelven HTML)
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    return templates.TemplateResponse("todo.html", {...})

# API (devuelve JSON)
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    return db.query(Todos).all()
```

### 2. Manejo de Errores con Try-Except

```python
try:
    user = await get_current_user(request.cookies.get('access_token'))
    # Lógica de la página
except:
    return redirect_to_login()
```

Garantiza que tokens inválidos no rompan la aplicación.

### 3. Template Reutilizable

```html
{% include 'layout.html' %}
```

DRY (Don't Repeat Yourself) - No duplicar código HTML.

### 4. JavaScript No Intrusivo

```html
<form id="todoForm">
    <!-- Campos del formulario -->
</form>
```

JavaScript se adjunta mediante event listeners, no inline.

### 5. Validación en Múltiples Capas

- **Cliente**: HTML5 `required`, validaciones JavaScript
- **Servidor**: Pydantic models, validación de negocio
- **Base de Datos**: Constraints (unique, foreign keys)

## Testing de la Aplicación Full Stack

El proyecto mantiene la suite de tests del proyecto anterior, pero se pueden agregar tests específicos para páginas:

```python
def test_login_page_renders():
    response = client.get("/auth/login-page")
    assert response.status_code == 200
    assert b"Username" in response.content
    assert b"Password" in response.content

def test_todo_page_requires_authentication():
    response = client.get("/todos/todo-page")
    # Sin autenticación, debe redirigir
    assert response.status_code == 302
    assert "/auth/login-page" in response.headers["location"]
```

## Conclusión

Este proyecto demuestra una implementación completa de **aplicación web full stack** con FastAPI:

- **Backend robusto** con FastAPI y SQLAlchemy
- **Frontend dinámico** con Jinja2 templates
- **Autenticación completa** basada en cookies JWT
- **Interactividad** con JavaScript vanilla y Fetch API
- **UI responsive** con Bootstrap 4
- **Arquitectura híbrida** manteniendo API REST funcional

La aplicación combina lo mejor de ambos mundos:

- Renderizado del servidor para páginas completas
- Interacciones asíncronas para operaciones CRUD
- Mantiene compatibilidad con clientes API (móviles, etc.)

Esta arquitectura es ideal para aplicaciones que necesitan:

- Interfaz web para usuarios finales
- API REST para integraciones
- SEO y carga rápida
- Desarrollo con tecnologías Python conocidas

FastAPI con Jinja2 proporciona una solución poderosa y flexible para crear aplicaciones web modernas sin la complejidad de frameworks JavaScript frontend pesados, mientras mantiene la opción de evolucionar a una arquitectura más desacoplada en el futuro.
