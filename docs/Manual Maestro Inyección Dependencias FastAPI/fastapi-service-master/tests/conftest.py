"""
Configuración de pytest y fixtures compartidos.

- Configuración de base de datos de pruebas (SQLite in-memory)
- Fixtures para crear sesiones de DB
- Fixtures para el cliente de pruebas de FastAPI
- Fixtures de datos de ejemplo
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from httpx import AsyncClient, ASGITransport

from main import app
from src.database import get_db_session
from src.tickets.models import Ticket


# Configuración de base de datos de pruebas (SQLite en memoria)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    # Crear motor de base de datos para tests (SQLite en memoria).
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    # Crear todas las tablas
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    # Limpiar después de los tests
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    # Crear sesión de base de datos para tests.
    async_session = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    
    # Cliente HTTP de pruebas con override de la dependencia de DB.
    # Esto asegura que todos los endpoints usen la base de datos de pruebas.
    
    # Override de la dependencia de base de datos
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    # Crear cliente HTTP para tests
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Limpiar overrides
    app.dependency_overrides.clear()


# Fixtures de datos de ejemplo

@pytest.fixture
def sample_ticket_data():
    # Datos de ejemplo para crear un ticket.
    return {
        "title": "Fix authentication bug",
        "description": "Users can't login with correct credentials",
        "priority": 3
    }


@pytest.fixture
def sample_critical_ticket_data():
    # Datos de ejemplo para un ticket crítico (activa lógica de negocio).
    return {
        "title": "CRITICAL: Production server down",
        "description": "All users experiencing 500 errors",
        "priority": 2  # Será overrideado a 5 por la lógica de negocio
    }


@pytest_asyncio.fixture
async def created_ticket(test_session: AsyncSession, sample_ticket_data) -> Ticket:
    # Crear un ticket en la base de datos de pruebas.
    ticket = Ticket(**sample_ticket_data)
    test_session.add(ticket)
    await test_session.commit()
    await test_session.refresh(ticket)
    return ticket


@pytest_asyncio.fixture
async def multiple_tickets(test_session: AsyncSession) -> list[Ticket]:
    # Crear múltiples tickets en la base de datos de pruebas.
    tickets_data = [
        {"title": "Bug in payment", "description": "Payment fails", "priority": 4},
        {"title": "Update docs", "description": "Add API examples", "priority": 1},
        {"title": "Refactor code", "description": "Clean up repository", "priority": 2},
    ]
    
    tickets = [Ticket(**data) for data in tickets_data]
    for ticket in tickets:
        test_session.add(ticket)
    
    await test_session.commit()
    
    for ticket in tickets:
        await test_session.refresh(ticket)
    
    return tickets


# Configuración adicional de pytest

@pytest.fixture(scope="session")
def anyio_backend():
    # Configurar anyio para usar asyncio.
    return "asyncio"


def pytest_configure(config):
    # Configuración global de pytest.
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio test"
    )
