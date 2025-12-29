from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
from fastapi.testclient import TestClient
import pytest
from ..models import Todos, Users
from ..routers.auth import bcrypt_context

# Configurar bases de datos de pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine( # Motor de la base de datos
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine) # Crear tablas definidas en los modelos

# Sobre escritura de inyeccion de dependencias
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username': 'FepDev25', 'id': 1, 'user_role': 'admin'}

# Cliente de pruebas
client = TestClient(app)

# Fixtures
# Crean una tarea, usuario, los guardan y los entregan al test.
# Después de cada test que use los fixtures, se ejecuta un 
# bloque para vaciar la tabla de todos.

@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn FastAPI",
        description="Need to learn everyday",
        priority=5,
        complete=False,
        owner_id=1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    yield todo

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

@pytest.fixture
def test_user():
    user = Users(
        username="FepDev25",
        email="felipe@gmail.com",
        first_name="Felipe",
        last_name="Peralta",
        hashed_password=bcrypt_context.hash("test123"),
        role="admin",
        phone_number="0987654321"
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()