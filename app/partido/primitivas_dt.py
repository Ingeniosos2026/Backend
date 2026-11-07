from app.partido.estados import EstadoPartido
import random


class PrimitivasDT:

    def __init__(self, estado: EstadoPartido, id_usuario: int):
        self.estado = estado
        self.id_usuario = id_usuario

    def cambiar_comportamiento(self) -> None:
        jugadores_equipo = [clave for clave in self.estado.jugadores if clave[0] == self.id_usuario]

        if not jugadores_equipo:
            return

        disponibles = self.estado.comportamientos_disponibles.get(self.id_usuario, [])

        if not disponibles:
            return

        # eligo un jugador aleatorio
        clave = random.choice(jugadores_equipo)

        comportamiento_actual = self.estado.comportamientos.get(clave)

        # filtro los comportamientos diferentes al actual
        comportamientos_diferentes = [comportamiento for comportamiento in disponibles if comportamiento.codigo != comportamiento_actual]
        if not comportamientos_diferentes:
            return
        
        comportamiento = random.choice(comportamientos_diferentes)

        self.estado.comportamientos[clave] = comportamiento.codigo

    def cambiar_jugador(self) -> None:
        if not self.estado.en_pausa:
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
        jugador_entra.posicion = jugador_sale.posicion
        jugador_entra.destino = None

        # intercambio los jugadores
        self.estado.jugadores[clave_entra] = jugador_entra
        self.estado.suplentes[clave_sale] = jugador_sale

        del self.estado.jugadores[clave_sale]
        del self.estado.suplentes[clave_entra]
    
    def voy_perdiendo(self) -> bool:
        goles_propios, goles_rival = self.obtener_goles()

        return goles_propios < goles_rival

    def voy_ganando(self) -> bool:
        goles_propios, goles_rival = self.obtener_goles()

        return goles_propios > goles_rival

    def esta_empatado(self) -> bool:
        goles_propios, goles_rival = self.obtener_goles()

        return goles_propios == goles_rival

    def obtener_goles(self) -> tuple[int, int]:

        if self.id_usuario == self.estado.id_usuario_izquierdo:
            return (self.estado.goles_izquierdo, self.estado.goles_derecho)

        if self.id_usuario == self.estado.id_usuario_derecho:
            return (self.estado.goles_derecho, self.estado.goles_izquierdo)

        raise ValueError("el usuario no pertenece al partido")
    
    def es_pausa(self) -> bool:
        return self.estado.en_pausa