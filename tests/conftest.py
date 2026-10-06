import pytest

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base, get_db
from app.main import app

from app.capa_0_definicion_bd.models.usuarios_modelos import Usuario
from app.capa_0_definicion_bd.models.comportamientos_modelos import Comportamiento
from app.capa_0_definicion_bd.models.jugadores_modelos import Jugador
from app.capa_0_definicion_bd.models.equipo_modelos import Equipo
from app.capa_0_definicion_bd.models.liga_modelos import Liga
from app.capa_0_definicion_bd.models.partidos_modelos import Partido

DATABASE_URL = "sqlite:///:memory:"
engine_test = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

@event.listens_for(engine_test, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


TestingSessionLocal = sessionmaker(bind=engine_test)


@pytest.fixture
def db_test():
    # antes de cada test se crean las tablas
    Base.metadata.create_all(engine_test)

    # crear sesion para el test
    session = TestingSessionLocal()

    yield session

    # Despues de cada test se cierra la sesion
    session.close()

    # Despues de cada test se eliminan las tablas
    Base.metadata.drop_all(engine_test)


# prepara un cliente de FastAPI que usa la BD de prueba, se la entrega al test y cuando termina se restaura la configuracion original.
@pytest.fixture
def client(db_test):

    def override_get_db():
        yield db_test

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()