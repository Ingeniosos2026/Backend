from .estados import EstadoPartido, Coordenada, JugadorEstado, Arco
from .auxiliares import calcular_distancia, calcular_direccion, calcular_velocidad

FRICCION_PELOTA = 2.0

RADIO_JUGADOR = 0.5
RADIO_PELOTA = 0.2

class FisicaPartido:
    def __init__(self, estado: EstadoPartido):
        self.estado = estado

        # guardamos las posiciones iniciales de los jugadores para poder volver a ellas despues de un gol
        self.posiciones_iniciales = {}
        for clave, jugador in estado.jugadores.items():
            posicion = Coordenada(jugador.posicion.x, jugador.posicion.y)
            self.posiciones_iniciales[clave] = posicion

    def actualizar(self, t: float) -> None:
        self.actualizar_jugadores(t)
        self.actualizar_pelota(t)

        self.resolver_colisiones_jugadores()
        self.resolver_colisiones_pelota()

    def actualizar_jugadores(self, t: float) -> None:
        for jugador in self.estado.jugadores.values():

            if jugador.destino is None:
                continue

            distancia = calcular_distancia(jugador.posicion, jugador.destino)

            velocidad = calcular_velocidad(jugador.velocidad)
            distancia_movimiento = velocidad * t

            # Si llegamos al destino durante este tick, coloco al jugador en el destino
            if distancia <= distancia_movimiento:
                jugador.posicion = Coordenada(x=jugador.destino.x, y=jugador.destino.y)
                jugador.destino = None
                continue

            direccion = calcular_direccion(jugador.posicion, jugador.destino)

            jugador.posicion = Coordenada(x=jugador.posicion.x + direccion.x * distancia_movimiento, 
                                          y=jugador.posicion.y + direccion.y * distancia_movimiento)

    def actualizar_pelota(self, t: float) -> None:
        pelota = self.estado.pelota

        pelota.posicion = Coordenada(x=pelota.posicion.x + pelota.velocidad.x * t, y=pelota.posicion.y + pelota.velocidad.y * t)

        self.aplicar_friccion_pelota(t)
        self.bordes_pelota()

    def bordes_pelota(self) -> None:
        pelota = self.estado.pelota
        cancha = self.estado.cancha

        # borde inferior
        if pelota.posicion.y <= 0:
            pelota.posicion.y = 0
            pelota.velocidad.y = abs(pelota.velocidad.y)

        # borde superior
        elif pelota.posicion.y >= cancha.alto:
            pelota.posicion.y = cancha.alto
            pelota.velocidad.y = -abs(pelota.velocidad.y)

        # Borde izquierdo
        if pelota.posicion.x <= 0:
            if self.esta_dentro_arco(pelota.posicion.y, cancha.arco_izquierdo):
                self.registrar_gol("izquierdo")
            else:
                # no es gol, rebota la pelota
                pelota.posicion.x = 0
                pelota.velocidad.x = abs(pelota.velocidad.x)

        # Borde derecho
        elif pelota.posicion.x >= cancha.ancho:
            if self.esta_dentro_arco(pelota.posicion.y, cancha.arco_derecho):
                self.registrar_gol("derecho")
            else:
                # no es gol, rebota la pelota
                pelota.posicion.x = cancha.ancho
                pelota.velocidad.x = -abs(pelota.velocidad.x)

    def esta_dentro_arco(self, y: float, arco) -> bool:
        return (arco.poste_inferior.y <= y <= arco.poste_superior.y)

    def registrar_gol(self, lado_arco: str) -> None:
        # registra un gol y reinicia las posiciones del partido
        if lado_arco == "izquierdo": 
            self.estado.goles_derecho += 1
        elif lado_arco == "derecho":
            self.estado.goles_izquierdo += 1

        self.reiniciar_posiciones()

    def aplicar_friccion_pelota(self, t: float) -> None:
        pelota = self.estado.pelota

        velocidad = calcular_distancia(Coordenada(0, 0), pelota.velocidad)

        if velocidad == 0:
            return

        nueva_velocidad = max(0, velocidad - FRICCION_PELOTA * t)

        # mantiene la misma direccion de la pelota pero reduce la velocidad
        factor = nueva_velocidad / velocidad

        pelota.velocidad = Coordenada(x=pelota.velocidad.x * factor, y=pelota.velocidad.y * factor)

    def reiniciar_posiciones(self) -> None:
        for clave, posicion_inicial in self.posiciones_iniciales.items(): 
            jugador = self.estado.jugadores.get(clave)

            if jugador is None: 
                continue

            jugador.posicion = Coordenada(x=posicion_inicial.x, y=posicion_inicial.y)

            # dejamos de perseguir cualquier destino anterior
            jugador.destino = None

            # el tiempo del ultimo pateo se reinicia
            jugador.ultimo_pateo = -10.0


        pelota = self.estado.pelota 
        cancha = self.estado.cancha

        # la pelota vuelve al centro de la cancha
        pelota.posicion = Coordenada(x=cancha.ancho/2, y=cancha.alto/2)
        # La pelota queda quieta
        pelota.velocidad = Coordenada(x=0, y=0)


    def resolver_colisiones_jugadores(self) -> None: 
        # detecta y resuelve las colisiones entre jugadores (o eso deberia de hacer, tengo que testearlo y ver)
        jugadores = list(self.estado.jugadores.values()) 
        for i in range(len(jugadores)): 
            for j in range(i + 1, len(jugadores)):
                jugador_a = jugadores[i]
                jugador_b = jugadores[j] 
                distancia = calcular_distancia(jugador_a.posicion, jugador_b.posicion) 
                distancia_minima = RADIO_JUGADOR + RADIO_JUGADOR
                if distancia >= distancia_minima: 
                    continue 
                self.resolver_colision_jugadores(jugador_a, jugador_b, distancia)

    
    def resolver_colision_jugadores(self, jugador_a, jugador_b, distancia: float) -> None:
        # separa dos jugadores que se estan por cruzar. El jugador con mayor fuerza recibe un menor desplazamiento hacia atras
        # dos jugadores exactamente en la misma posicion (un caso borde podria pasar) 
        if distancia == 0: 
            direccion = Coordenada(1, 0) 
            distancia = 0
        else: 
            direccion = calcular_direccion(jugador_a.posicion, jugador_b.posicion) 
            
        distancia_minima = RADIO_JUGADOR + RADIO_JUGADOR

        cerca = distancia_minima - distancia
            
        fuerza_a = jugador_a.fuerza 
        fuerza_b = jugador_b.fuerza

        suma_fuerzas = fuerza_a + fuerza_b

        # El jugador mas fuerte retrocede menos 
        porcentaje_a = fuerza_b / suma_fuerzas 
        porcentaje_b = fuerza_a / suma_fuerzas
        
        desplazamiento_a = cerca * porcentaje_a 
        desplazamiento_b = cerca * porcentaje_b
        
        jugador_a.posicion = Coordenada(x=jugador_a.posicion.x - direccion.x * desplazamiento_a, y=jugador_a.posicion.y - direccion.y * desplazamiento_a)
        jugador_b.posicion = Coordenada(x=jugador_b.posicion.x + direccion.x * desplazamiento_b, y=jugador_b.posicion.y + direccion.y * desplazamiento_b)


    def resolver_colisiones_pelota(self) -> None:
        # detecta colisiones entre la pelota y los jugadores 
        pelota = self.estado.pelota 
        for jugador in self.estado.jugadores.values():
            distancia = calcular_distancia(jugador.posicion, pelota.posicion) 
            distancia_minima = RADIO_JUGADOR + RADIO_PELOTA
            
            if distancia >= distancia_minima: 
                continue
        
            self.resolver_colision_jugador_pelota(jugador, distancia)
    

    def resolver_colision_jugador_pelota(self, jugador, distancia: float) -> None:
        # resuelve la colision entre un jugador y la pelota
        # Si el jugador acaba de patear, no modifica la velocidad producida por el pateo (digamos que podria ser un caso borde)
        # si no se patea, la pelota rebota separandose del jugador
    
        pelota = self.estado.pelota

        # separar jugador de la pelota
        distancia_minima = RADIO_JUGADOR + RADIO_PELOTA
        cerca = distancia_minima - distancia

        tiempo_desde_pateo = (self.estado.tiempo - jugador.ultimo_pateo) 
        if tiempo_desde_pateo <= 0.05:
            return

        # Direccipn desde el jugador hacia la pelota
        if distancia == 0:
            direccion = Coordenada(1, 0)
        else:
            direccion = calcular_direccion(jugador.posicion, pelota.posicion)

        pelota.posicion = Coordenada(x=pelota.posicion.x + direccion.x * cerca, y=pelota.posicion.y + direccion.y * cerca)

        velocidad = calcular_distancia(Coordenada(0, 0), pelota.velocidad)

        # si la pelota no se estaba moviendo, le doy una velocidad inicial de rebote
        if velocidad == 0:
            velocidad_rebote = 1.0
        else:
            velocidad_rebote = velocidad

        pelota.velocidad = Coordenada(x=direccion.x * velocidad_rebote, y=direccion.y * velocidad_rebote)