from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///./data/mi_base.db'

# El motor
# check_same_thread=False es OBLIGATORIO en SQLite con FastAPI
# porque SQLite por defecto solo permite un hilo, y FastAPI usa varios.
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread' : False})

# Fabrica de sesiones
# una fábrica (una clase) que generará sesiones bajo demanda.
SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

# Base declarativa
# Es una clase de la cual heredarán todos los modelos
Base = declarative_base()

# Explicacion de cada componente:
# engine: El conductor del camión (sabe manejar SQLite).
# SessionLocal: La oficina de contratos (crea instancias temporales para cada petición).
# Base: El plano maestro (sabe qué forma deben tener los datos).