# app/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta, datetime
import jwt  # pip install PyJWT
import bcrypt
from app.models.database import get_db
from app.models.user import User
from app.settings import settings

# Configura esto según tu secreto y algoritmo
JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class LoginRequest(BaseModel):
    correo: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 1) Busca el usuario por correo
    user = db.query(User).filter(User.correo == request.correo).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # 2) Verifica contraseña
    try:
        if not bcrypt.checkpw(request.password.encode('utf-8'), user.password_hash.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
    except Exception:
         # Fallback o captura de errores de formato en el hash
         raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # 3) Crea el JWT
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user.id,
        "role": user.role,
        "exp": expire.timestamp()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {"access_token": token}
