#aca se guardan los 3 comportamientos por default, un ejemplo podria ser:

comportamiento_defender = """
def comportamiento1(primitivas):
    posicion_pelota = primitivas.direccionPelota()
    arco_propio = primitivas.direccionArcoPropio()

    if primitivas.pelotaCerca():
        primitivas.patear(primitivas.direccionArcoRival())
    else:
        primitivas.correr(arco_propio)
"""