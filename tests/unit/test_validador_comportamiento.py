import pytest

from app.partido.validador import *


@pytest.mark.parametrize("codigo",
    ["""def comportamiento(primitivas):
    primitivas.correr(primitivas.direccionPelota())""",
        """def comportamiento(primitivas):
    compañero = primitivas.direccionCompañeros()[0]
    if compañero.x > 0 and primitivas.pelotaCerca():
        primitivas.patear(primitivas.direccionArcoRival())
    else:
        primitivas.correr((compañero.x, compañero.y))"""])

def test_validar_codigo_comportamiento_acepta_codigo_permitido(codigo):
    assert validar_codigo_comportamiento(codigo) == codigo


@pytest.mark.parametrize("codigo", ["", " \n\t", None, 123])
def test_validar_codigo_comportamiento_rechaza_codigo_vacio_o_no_textual(codigo):
    with pytest.raises(CodigoComportamientoInvalido, match="no puede estar vacio"):
        validar_codigo_comportamiento(codigo)


def test_validar_codigo_comportamiento_rechaza_sintaxis_invalida():
    with pytest.raises(CodigoComportamientoInvalido, match="no tiene sintaxis"):
        validar_codigo_comportamiento("def comportamiento(primitivas)")


@pytest.mark.parametrize(
    ("codigo", "mensaje"),
    [("def comportamiento(primitivas):\n    pass\n" "def otra(primitivas):\n    pass", "unicamente la funcion"),
        ("def otra(primitivas):\n    pass", "llamar comportamiento"),
        ("def comportamiento(jugador):\n    pass", "firma debe ser"),
        ("def comportamiento(primitivas):\n    import os", "Construcción de python no permitida"),
        ("def comportamiento(primitivas):\n    abrir()", "llamadas a funciones arbitrarias"),
        ("def comportamiento(primitivas):\n    primitivas.despejar()", "Primitiva no permitida"),
        ("def comportamiento(primitivas):\n    primitivas.correr(destino)", "Variable no definida"),
        ("def comportamiento(primitivas):\n    primitivas = None", "No se puede sobrescribir"),
        ("def comportamiento(primitivas):\n    posicion = primitivas.__class__", "Atributo no permitido")]
)
def test_validar_codigo_comportamiento_rechaza_construcciones_no_permitidas(
    codigo, mensaje
):
    with pytest.raises(CodigoComportamientoInvalido, match=mensaje):
        validar_codigo_comportamiento(codigo)
