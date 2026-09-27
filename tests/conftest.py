import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.capa_0_definicion_bd.base_datos_sqlalchemy import Base


DATABASE_URL = "sqlite:///:memory:"
engine_test = create_engine(DATABASE_URL)
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