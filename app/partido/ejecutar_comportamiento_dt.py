from .estados import EstadoPartido
from .primitivas_dt import PrimitivasDT


def ejecutar_comportamiento_dt(estado: EstadoPartido, id_usuario: int, codigo: str, posiciones_iniciales: dict, eventos: list) -> None:

    primitivas = PrimitivasDT(estado=estado, id_usuario=id_usuario, posiciones_iniciales=posiciones_iniciales, eventos=eventos)

    entorno = {}
    exec(codigo, entorno)

    comportamiento = entorno.get("comportamiento")

    if comportamiento is None:
        raise ValueError("El comportamiento DT debe definir una funcion llamada 'comportamiento(primitivas)'")

    comportamiento(primitivas)