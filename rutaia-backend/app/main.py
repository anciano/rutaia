# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# ── Configuración ──────────────────────────────────
from app.settings import settings               # instancia Settings
JWT_SECRET = settings.JWT_SECRET

# ── Importa los modelos para que SQLAlchemy los registre
import app.models                                # noqa: F401

# ── Routers ───────────────────────────────────────
from app.routes.chat          import router as chat_router
from app.routes.historial     import router as historial_router
from app.routes.ciudades      import router as ciudades_router
from app.routes.preferencias  import router as preferencias_router
from app.routes.planificacion import router as planificacion_router
from app.routes.plan_detalle  import router as plan_detalle_router
from app.routes.lugares       import router as lugares_router
from app.routes.hospedajes    import router as hospedajes_router
from app.routes.actividades   import router as actividades_router
from app.routes.transportes   import router as transportes_router
from app.routes.ia            import router as ia_router
from app.routes import auth_google

app = FastAPI(title="RutaIA Backend")

# 1️⃣  Middleware de sesión (requerido por Authlib)
app.add_middleware(
    SessionMiddleware,
    secret_key=JWT_SECRET,
    https_only=True,           # True en producción con HTTPS
    session_cookie="session",
    same_site="lax"
)

# 2️⃣  CORS (frontend en Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://rutaia.cl", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3️⃣  Registro de routers
app.include_router(chat_router)
app.include_router(historial_router)
app.include_router(ciudades_router)
app.include_router(preferencias_router)
app.include_router(lugares_router)
app.include_router(hospedajes_router)
app.include_router(actividades_router)
app.include_router(transportes_router)

app.include_router(planificacion_router)
app.include_router(plan_detalle_router)
app.include_router(ia_router)

from app.routes.auth import router as auth_router
app.include_router(auth_router)

app.include_router(auth_google.router)   # OAuth con Google al final (orden no crítico)

# Stage 9 — Admin Catalog API
from app.routes.admin import router as admin_router
app.include_router(admin_router)
