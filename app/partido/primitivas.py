from .estados import EstadoPartido, Coordenada, Cancha, JugadorEstado, PelotaEstado
from .auxiliares import *

class Primitivas:
    def __init__(self,estado: EstadoPartido, id_usuario: int ,id_jugador: int):
        self.estado = estado
        self.id_usuario = id_usuario
        self.id_jugador = id_jugador


    def correr(self, destino: Coordenada) -> None:
       # el jugador actual se mueve al destino indicado
       if not posicion_valida(destino, self.estado.cancha):
        raise ValueError("El destino esta fuera de la cancha")
       
       jugador = obtener_jugador(self.estado, self.id_usuario, self.id_jugador)
       
       # las fisicas (cuando las implementemos) se encargara de moverlo progresivamente
       jugador.destino = destino


    def patear(self, direccion: Coordenada) -> bool:
        # devuelve True si el jugador pudo patear
        # devuelve False si no puede patear en ese momento.

        jugador = obtener_jugador(self.estado,self.id_usuario, self.id_jugador)
        pelota = self.estado.pelota
    
        # la pelota esta en mi alcance?
        alcance = calcular_alcance(jugador.control)
        distancia_pelota = calcular_distancia(jugador.posicion, pelota.posicion)

        if distancia_pelota > alcance:
            return False

        # puede patear?
        tiempo_espera = calcular_tiempo_pateo(jugador.agilidad)
        tiempo_desde_ultimo_pateo = (self.estado.tiempo - jugador.ultimo_pateo)
        if tiempo_desde_ultimo_pateo < tiempo_espera:
            return False

        direccion_pelota = calcular_direccion(pelota.posicion, direccion)

        # no puedo patear hacia la misma posicion
        if (direccion_pelota.x == 0 and direccion_pelota.y == 0):
            return False

        potencia = calcular_potencia(jugador.poder)
        pelota.velocidad = Coordenada(x=direccion_pelota.x * potencia, y=direccion_pelota.y * potencia)
        jugador.ultimo_pateo = self.estado.tiempo

        return True


    def direccionPelota(self) -> Coordenada:
        #devuelve la posicion actual de la pelota
        return self.estado.pelota.posicion


    def direccionCompañeros(self) -> list[Coordenada]:
        # devuelve las posiciones de los compañeros del jugador actual
        jugador_actual = obtener_jugador(self.estado, self.id_usuario, self.id_jugador)

        posiciones = []
        for jugador in self.estado.jugadores.values():
            if jugador.id_equipo == jugador_actual.id_equipo:
                if (jugador.id_jugador != self.id_jugador):
                    posiciones.append(jugador.posicion)

        return posiciones


    def direccionRivales(self) -> list[Coordenada]:
        # devuelve las posiciones de todos los jugadores rivales.
        jugador_actual = obtener_jugador(self.estado, self.id_usuario, self.id_jugador)

        posiciones = []
        for jugador in self.estado.jugadores.values():
            if jugador.id_equipo != jugador_actual.id_equipo:
                posiciones.append(jugador.posicion)

        return posiciones


    def pelotaCerca(self) -> bool:
        jugador = obtener_jugador(self.estado, self.id_usuario, self.id_jugador)
        alcance = calcular_alcance(jugador.control)
        distancia_pelota = calcular_distancia(jugador.posicion, self.estado.pelota.posicion)

        return distancia_pelota <= alcance


    def direccionArcoRival(self) -> Coordenada:
        if (self.id_usuario == self.estado.id_usuario_izquierdo):
            return self.estado.cancha.arco_derecho.centro
        
        if (self.id_usuario == self.estado.id_usuario_derecho):
            return self.estado.cancha.arco_izquierdo.centro

        raise ValueError("El usuario no pertenece al partido")


    def direccionArcoPropio(self) -> Coordenada: 
        if (self.id_usuario == self.estado.id_usuario_izquierdo):
            return self.estado.cancha.arco_izquierdo.centro

        if (self.id_usuario == self.estado.id_usuario_derecho):
            return self.estado.cancha.arco_derecho.centro

        raise ValueError("El usuario no pertenece al partido")

