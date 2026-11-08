from .estados import EstadoPartido
from .primitivas_dt import PrimitivasDT


def ejecutar_comportamiento_dt(estado: EstadoPartido, id_usuario: int, codigo: str) -> None:

    primitivas = PrimitivasDT(estado=estado, id_usuario=id_usuario)

    entorno = {}
    exec(codigo, entorno)

    comportamiento = entorno.get("comportamiento")

    if comportamiento is None:
        raise ValueError("El comportamiento DT debe definir una funcion llamada 'comportamiento(primitivas)'")

    comportamiento(primitivas)