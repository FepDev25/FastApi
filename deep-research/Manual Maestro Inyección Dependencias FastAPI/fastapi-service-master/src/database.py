from collections.abc import AsyncGenerator
from typing import Annotated
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends
from src.config import get_settings

settings = get_settings()

# Crear el motor de la base de datos asíncrona
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG_MODE,
    future=True
)

# Factoría de sesiones (no es la sesión en sí, es el creador de sesiones)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency Injection Core
# Esta función es un Generador Asíncrono.
# FastAPI ejecutará lo que está ANTES del yield al iniciar el request.
# Entregará la sesión al endpoint.
# Ejecutará lo que está DESPUÉS del yield al finalizar el request (incluso si hubo error)
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Funciones para gestionar el ciclo de vida de la base de datos
async def create_db_and_tables():
    # Crear todas las tablas en la base de datos
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def close_db_connection():
    # Cerrar la conexión con la base de datos
    await async_engine.dispose()

# Type alias para dependency injection
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]