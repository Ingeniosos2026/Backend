# Backend

## Requisitos y ejecución

### 1) Crear y activar entorno
```
python -m venv .venv
source .venv/bin/activate
```

### 2) Instalar dependencias
```
pip install -r requirements.txt
```

### 3) Levantar el servidor
```
uvicorn app.main:app --reload
```

## Tests

Dentro de un entorno virtual para correr los test ejecutamos lo siguiente:

```
$ pytest -v
```

Preferentemente, para ver mas detalle sobre coverage en cada parte del proyecto usamos los flags **--cov** y
**--cov-report=term-missing**

```
$ pytest -v --cov --cov-report=term-missing
```

## Modelo de capas
Utilizamos una arquitectura por capas inspirada en "código bonito" para separar como trabajan distintas partes de la API.

- Capa 0: Definición de base de datos (app/capa_0_definicion_bd)
    - En esta capa definimos modelos SQLAlchemy y la configuracion de la bd. (/models), (/base_datos_sqlalchemy.py)

- Capa 1: Acceso a datos (app/capa_1_acceso_datos)
    - Realiza operaciones sobre la base de datos

- Capa 2: Lógica de negocio (app/capa_2_logica)
    - Aca se realiza la logica del sistema tal como validar datos, crear jugadores, verificar comportamientos, entre otras cosas.
    - (/servicios.py) Gran parte de la logica se encuentra aca
    - (/errores.py), (/resultados.py) Contienen excepciones y dataclasses para el retorno de algunas funciones respectivamente

- Capa 3: API ( app/capa_3_api )
    - Se exponen endpoints, recibe requests y validan las entradas para la llamada a los servicios.
    - (/dtos) DTOs para la entrada/salida de endpoints
    - (/routers) Endpoints breves que van a llamar a los servicios para que realicen la logica.

- Ademas separamos el motor del partido (/app/partido). Aca se ubica gran parte de la simulacion para los partidos. Cosas como las fisicas, motor del juego, ejecucion de comportamientos. (/motor.py), (/fisicas.py), (ejecutar_comportamiento.py).
