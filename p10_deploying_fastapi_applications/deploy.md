# Deply FastAPI Applications

Se describe las estrategias más comunes y recomendadas para llevar una aplicación FastAPI de `localhost` a un entorno de producción (Production).

---

## Introducción

Desplegar una aplicación FastAPI en producción implica varios pasos y consideraciones para asegurar que la aplicación sea segura, escalable y eficiente. Aquí te presento las opciones más comunes y recomendadas:

## Opción A: Docker (El Estándar de la Industria)

La forma más robusta y portable. Creas una "imagen" de tu app que funciona igual en cualquier lado (AWS, Azure, DigitalOcean, tu servidor local).

### Dockerfile Básico

Crea un archivo llamado `Dockerfile` en la raíz:

```dockerfile
# 1. Imagen base ligera de Python
FROM python:3.10-slim

# 2. Establecer directorio de trabajo
WORKDIR /app

# 3. Evitar que Python genere archivos .pyc y buffer de salida
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 4. Instalar dependencias del sistema (si usas Postgres)
# RUN apt-get update && apt-get install -y libpq-dev gcc

# 5. Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 6. Copiar el código fuente
COPY . .

# 7. Comando de ejecución (Usando FastAPI CLI o Uvicorn directo)
# Opción Simple:
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

# Opción Robusta (Gunicorn + Uvicorn Workers):
# CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]

```

### Comandos para correrlo

```bash
docker build -t mi-fastapi-app .
docker run -d -p 80:80 --env-file .env mi-fastapi-app

```

---

## Opción B: Plataformas PaaS (Rápido y Fácil)

Ideal si no quieres administrar servidores (Linux, seguridad, actualizaciones). Conectas tu GitHub y listo.

### 1. Railway / Render / Fly.io

Son muy populares para FastAPI.

- Configuración: Detectan automáticamente que es Python.
- Comando de inicio: Debes especificar el comando en su panel:
`uvicorn main:app --host 0.0.0.0 --port $PORT`
- Base de Datos: Suelen ofrecer PostgreSQL gestionado con un clic.
- Ventaja: HTTPS automático (candadito verde) y CI/CD integrado (deploy al hacer git push).

---

## Opción C: Servidor VPS (Linux Tradicional - DigitalOcean/Linode/EC2)

Si prefieres control total y menor costo por recursos. Requiere configurar Linux manualmente.

### Arquitectura Típica

Nginx (Proxy Reverso) -> Gunicorn (Process Manager) -> Uvicorn (Workers) -> Tu App

- Instalar dependencias: Python, Pip, Venv, Nginx, Git.
- Clonar repo y entorno virtual.
- Configurar Systemd (para que la app reviva si se cae o reinicia el servidor):
Archivo:

`/etc/systemd/system/fastapi_app.service`

```ini
[Unit]
Description=Gunicorn instance to serve FastAPI
After=network.target

[Service]
User=usuario
Group=www-data
WorkingDirectory=/home/usuario/mi_proyecto
Environment="PATH=/home/usuario/mi_proyecto/venv/bin"
EnvironmentFile=/home/usuario/mi_proyecto/.env
ExecStart=/home/usuario/mi_proyecto/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 main:app

[Install]
WantedBy=multi-user.target

```

- Configurar Nginx: Para recibir el tráfico del puerto 80/443 y pasarlo al 8000.

---

## Checklist de Seguridad para Producción

- HTTPS (SSL/TLS): Obligatorio. Si usas Docker/VPS, usa Traefik o Certbot (Let's Encrypt). En PaaS es automático.
- Documentación: ¿Quieres que todo el mundo vea tu Swagger?
Para desactivarlo en producción:

```python
app = FastAPI(docs_url=None, redoc_url=None) # O condicional según env var

```

- Secrets: Asegúrate de que `SECRET_KEY` (para JWT) sea una cadena larga, aleatoria y segura, inyectada como variable de entorno.
- Workers: La regla general para Gunicorn es: `(2 x CPU Cores) + 1`.

---

## Resumen: ¿Cuál elijo?

| Necesidad | Recomendación |
| --- | --- |
| Quiero desplegar YA, sin configurar servidores | Render o Railway |
| Quiero el estándar profesional y escalable | Docker (luego subido a AWS ECS o Google Cloud Run) |
| Quiero aprender Linux y gestionar todo | VPS (DigitalOcean + Ubuntu + Nginx) |
| Tengo tráfico impredecible (Serverless) | AWS Lambda (usando Mangum) |
