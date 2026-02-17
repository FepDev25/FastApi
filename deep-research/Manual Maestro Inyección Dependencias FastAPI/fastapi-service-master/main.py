from contextlib import asynccontextmanager
from fastapi import FastAPI
from src import router
from src.database import create_db_and_tables, close_db_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionar el ciclo de vida de la aplicación"""
    # Startup: Crear tablas
    await create_db_and_tables()
    print("Database tables created")
    yield
    # Shutdown: Cerrar conexión
    await close_db_connection()
    print("Database connection closed")

app = FastAPI(
    title="ServiceMaster API",
    description="API de gestión de tickets con Dependency Injection",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)