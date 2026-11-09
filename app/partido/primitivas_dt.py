from app.partido.estados import EstadoPartido, Coordenada
from app.partido.comportamientos import comportamiento_atacar, comportamiento_defender
from app.partido.auxiliares import obtener_goles
import random


class PrimitivasDT:

    def __init__(self, estado: EstadoPartido, id_usuario: int, posiciones_iniciales: dict):
        self.estado = estado
        self.id_usuario = id_usuario
        self.posiciones_iniciales = posiciones_iniciales

    def cambiar_comportamiento_ataque(self) -> None:
        for clave in self.estado.jugadores:
            if clave[0] == self.id_usuario:
                self.estado.comportamientos[clave] = comportamiento_atacar

    def cambiar_comportamiento_defensa(self) -> None:
        for clave in self.estado.jugadores:
            if clave[0] == self.id_usuario:
                self.estado.comportamientos[clave] = comportamiento_defender

    def cambiar_jugador(self) -> None:
        if not self.estado.en_pausa:
            return
        
        if self.id_usuario == self.estado.id_usuario_izquierdo:
            id_equipo = self.estado.id_equipo_izquierdo

        elif self.id_usuario == self.estado.id_usuario_derecho:
            id_equipo = self.estado.id_equipo_derecho

        else:
            return
        
        if not 1 <= self.estado.pausas_realizadas <= 3:
            return
        
        if (self.estado.pausas_realizadas, id_equipo) in self.estado.equipos_que_cambiaron:
            return

        jugadores_equipo = [clave for clave in self.estado.jugadores if clave[0] == self.id_usuario]

        suplentes_equipo = [clave for clave in self.estado.suplentes if clave[0] == self.id_usuario]

        if not jugadores_equipo or not suplentes_equipo:
            return

        clave_sale = random.choice(jugadores_equipo)
        clave_entra = random.choice(suplentes_equipo)

        jugador_sale = self.estado.jugadores[clave_sale]
        jugador_entra = self.estado.suplentes[clave_entra]

        # el suplente ingresa en la posicion del jugador que sale
        jugador_entra.posicion = Coordenada(x=jugador_sale.posicion.x, y=jugador_sale.posicion.y)
        jugador_entra.destino = None

        posicion_inicial = self.posiciones_iniciales[clave_sale]
        self.posiciones_iniciales[clave_entra] = Coordenada(x=posicion_inicial.x, y=posicion_inicial.y)

        # intercambio los jugadores
        self.estado.jugadores[clave_entra] = jugador_entra
        self.estado.suplentes[clave_sale] = jugador_sale

        del self.estado.jugadores[clave_sale]
        del self.estado.suplentes[clave_entra]

        self.estado.equipos_que_cambiaron.add((self.estado.pausas_realizadas, id_equipo))
    
    def voy_perdiendo(self) -> bool:
        goles_propios, goles_rival = obtener_goles(self.estado, self.id_usuario)

        return goles_propios < goles_rival

    def voy_ganando(self) -> bool:
        goles_propios, goles_rival = obtener_goles(self.estado, self.id_usuario)

        return goles_propios > goles_rival

    def esta_empatado(self) -> bool:
        goles_propios, goles_rival = obtener_goles(self.estado, self.id_usuario)

        return goles_propios == goles_rival
    
    def es_pausa(self) -> bool:
        return self.estado.en_pausa