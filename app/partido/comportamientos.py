#aca se guardan los 3 comportamientos por default, un ejemplo podria ser:

comportamiento_defender = """
def comportamiento(primitivas):
    arco_propio = primitivas.direccionArcoPropio()

    if primitivas.pelotaCerca():
        primitivas.patear(primitivas.direccionArcoRival())
    else:
        primitivas.correr(arco_propio)
"""


comportamiento_atacar = """
def comportamiento(primitivas):
    if primitivas.pelotaCerca():
        primitivas.patear(primitivas.direccionArcoRival())
    else:
        primitivas.correr(primitivas.direccionPelota())
"""


comportamiento_pasar_compañero = """
def comportamiento(primitivas):
    compañeros = primitivas.direccionCompañeros()
    compañero = compañeros[0]
    
    if primitivas.pelotaCerca():
        primitivas.patear(compañero)
        primitivas.correr(primitivas.direccionArcoRival())
    else:
        primitivas.correr(primitivas.direccionPelota())
"""


comportamiento_dt_predeterminado = """
def comportamiento(primitivas):
    if primitivas.es_pausa():
        primitivas.cambiar_jugador()

    if primitivas.voy_perdiendo():
        primitivas.cambiar_comportamiento_ataque()

    if primitivas.voy_ganando():
        primitivas.cambiar_comportamiento_defensa()
"""



COMPORTAMIENTOS_PREDETERMINADOS = (
    ("Defender", comportamiento_defender),
    ("Atacar", comportamiento_atacar),
    ("Pasar compañero", comportamiento_pasar_compañero),
)


COMPORTAMIENTO_DT_PREDETERMINADO = (
    "DT predeterminado",
    comportamiento_dt_predeterminado
)