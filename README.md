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