"""
Excepciones personalizadas para la logica del juego.
Describen errores especificos que pueden ocurrir durante la gestion de partidas y jugadores.
"""


class EmailInvalido(Exception):
    pass

class EmailRegistrado(Exception):
    pass