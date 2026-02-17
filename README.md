# FastAPI Learning

Repositorio de aprendizaje completo para FastAPI, combinando un curso estructurado con investigaciones profundas y ejercicios prácticos por habilidad.

---

## Certificación

**Curso**: [FastAPI - The Complete Course 2026 (Beginner + Advanced)](https://www.udemy.com/course/fastapi-the-complete-course/)  
**Plataforma**: Udemy  
**ID del certificado**: UC-544830ff-951a-449d-bea7-a317792a0efb

![Certificado](<FastAPI - The Complete Course/img/UC-544830ff-951a-449d-bea7-a317792a0efb.jpg>)

---

## Estructura

```
fastapi-learning/
├── FastAPI - The Complete Course/    # Curso completo con proyectos evolutivos
├── fastapi-gym-drills/               # Ejercicios por habilidad
├── deep-research/                    # Referencia técnica
└── pyproject.toml                    # Dependencias con uv
```

---

## FastAPI - The Complete Course

Progresión a través de 10 proyectos que construyen una aplicación TodoApp evolutiva.

| Proyecto | Contenido | Entregable |
|----------|-----------|------------|
| p01-p02 | Python Refresher | Fundamentos y POO |
| p03 | FastAPI Overview | Setup y endpoints iniciales |
| p04 | HTTP Methods | API de libros (CRUD básico) |
| p05 | Validation | Validación con Pydantic |
| p06 | REST API + Auth | TodoApp v1: JWT, SQLAlchemy, routers |
| p07 | Alembic | TodoApp v1.5: Migraciones de BD |
| p08 | Testing | TodoApp v2: Tests con pytest |
| p09 | Full Stack | TodoApp v3: Jinja2 + Bootstrap |
| p10 | Deployment | TodoApp en Render |

**Demo**: [https://fastapi-deployfepdev25.onrender.com/](https://fastapi-deployfepdev25.onrender.com/)

---

## FastAPI Gym Drills

Ejercicios aislados para practicar conceptos específicos.

| Drill | Tema | Estado |
|-------|------|--------|
| 01 | Input Validation | Completo |
| 02 | Dependency Injection | Pendiente |
| 03 | Async & Background Tasks | Pendiente |
| 04 | Upload & File Handling | Pendiente |
| 05 | Middleware | Pendiente |
| 06 | ORM | Pendiente |
| 07 | APIRouter & Project Structure | Pendiente |
| 08 | OAuth2 & JWT | Pendiente |
| 09 | Testing | Pendiente |
| 10 | WebSockets | Pendiente |
| 11 | Database Migrations - Alembic | Pendiente |
| 12 | Caching - Redis | Pendiente |
| 13 | Message Broker | Pendiente |
| 14 | Observability | Pendiente |

---

## Deep Research

Investigaciones técnicas profundas:

- Manual Maestro: Inyección de Dependencias FastAPI
- Manual Maestro: FastAPI SQLAlchemy
- Manual Maestro: Arquitectura FastAPI
- Manual Maestro: Jinja en FastAPI
- Autenticación y Autorización Web: FastAPI y Spring
- Teoría de FastAPI sin código

---

## Instalación

Requisitos: Python 3.12, uv

```bash
uv sync
source .venv/bin/activate
```

### Ejecutar proyecto

```bash
cd "FastAPI - The Complete Course/p06_project_3_complete_restful_apis"
uv run uvicorn main:app --reload
```

### Ejecutar tests

```bash
uv run pytest
```

---

## Stack

- FastAPI, Uvicorn, Pydantic v2
- SQLAlchemy 2.0, Alembic
- python-jose, passlib, python-multipart
- Jinja2
- pytest, httpx, pytest-asyncio

---

**Autor**: Felipe P.  
**Última actualización**: Febrero 2026
