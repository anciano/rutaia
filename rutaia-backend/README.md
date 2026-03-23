# RutaIA Backend
Este directorio contiene la API FastAPI y lógica del sistema.

# Asesor IA Base

Proyecto base FastAPI con PostgreSQL para simular un chat tipo "asesor".

## Instrucciones

1. Crea un entorno virtual:
   ```
   python -m venv venv
   ```

2. Actívalo:
   - En Windows: `venv\Scripts\activate`
   - En Linux/Mac: `source venv/bin/activate`

3. Instala dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Renombra `.env.example` a `.env` y ajusta la cadena de conexión a tu base PostgreSQL.

5. Levanta el servidor:
   ```
   uvicorn app.main:app --reload
   ```

6. Prueba el endpoint:
   ```
   POST http://localhost:8000/chat
   Body: { "content": "¿Qué hay para hacer hoy en Coyhaique?" }
   ```