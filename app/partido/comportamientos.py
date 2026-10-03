#aca se guardan los 3 comportamientos por default, un ejemplo podria ser:

comportamiento_defender = """
def comportamiento1(primitivas):
    arco_propio = primitivas.direccionArcoPropio()

    if primitivas.pelotaCerca():
        primitivas.patear(primitivas.direccionArcoRival())
    else:
        primitivas.correr(arco_propio)
"""


comportamiento_atacar = """
def comportamiento2(primitivas):
    if primitivas.pelotaCerca():
        primitivas.patear(primitivas.direccionArcoRival())
        primitivas.correr(primitivas.direccionPelota())
    else:
        primitivas.correr(primitivas.direccionPelota())
"""


comportamiento_pasar_compañero = """
def comportamiento3(primitivas):
    compañeros = primitivas.direccionCompañeros()
    compañero = compañeros[0]
    
    if primitivas.pelotaCerca():
        primitivas.patear(compañero)
        primitivas.correr(primitivas.direccionArcoRival())
    else:
        primitivas.correr(primitivas.direccionPelota())
"""