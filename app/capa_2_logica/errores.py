"""
Excepciones personalizadas para la logica del juego.
Describen errores especificos que pueden ocurrir durante la gestion de partidas y jugadores.
"""
class EmailRegistrado(Exception):
    pass

class DatosInvalidos(Exception):
    pass

class CredencialesInvalidas(Exception):
    pass

class ComportamientoNoEncontrado(Exception):
    pass

class ComportamientosNoEncontrados(Exception):
    pass
  
class EquipoNoEncontrado(Exception):
    pass

class UsuarioNoEncontrado(Exception):
    pass

class JugadorNoEncontrado(Exception):
    pass

class JugadoresInsuficientes(Exception):
    pass

class PartidoNoEncontrado(Exception):
    pass

class PartidoNoDisponible(Exception):
    pass