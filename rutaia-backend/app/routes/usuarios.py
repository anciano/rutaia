# app/routes/usuarios.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateRole

router = APIRouter(prefix="/usuarios", tags=["usuarios"], redirect_slashes=False)

@router.get("", response_model=List[UserResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    """
    Lista todos los usuarios registrados (Admin only - validación simple por ahora).
    """
    return db.query(User).order_by(User.creado_en.desc()).all()

@router.patch("/{user_id}/role", response_model=UserResponse)
def actualizar_rol(user_id: str, payload: UserUpdateRole, db: Session = Depends(get_db)):
    """
    Actualiza el rol de un usuario.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    
    if payload.role not in ["admin", "gestor", "user"]:
        raise HTTPException(400, "Rol inválido")
    
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user
