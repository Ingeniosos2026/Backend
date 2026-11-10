class AdministradorPartidas:

    def __init__(self):
        self.partidas = {}

    def agregar(self, partido_id: int, ejecutor) -> None:
        self.partidas[partido_id] = ejecutor

    def obtener(self, partido_id: int):
        return self.partidas.get(partido_id)

    def eliminar(self, partido_id: int) -> None:
        self.partidas.pop(partido_id, None)



administrador_partidas = AdministradorPartidas()