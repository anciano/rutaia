# app/routes/auth_google.py
from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta

from app.services.oauth import oauth
from app.models.database import get_db
from app.models.user import User
from app.settings import settings, JWT_SECRET   # cualquiera de las dos formas

router = APIRouter(prefix='/auth', tags=['auth'])

from app.settings import (
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI, JWT_SECRET
)

@router.get('/google')
async def login_google(request: Request):
    # Forzar el uso estricto de la URL segura definida en .env para evitar cualquier fallo de proxy
    return await oauth.google.authorize_redirect(request, redirect_uri=GOOGLE_REDIRECT_URI)

@router.get('/google/callback')
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token  = await oauth.google.authorize_access_token(request)
    data   = token.get('userinfo')
    if not data:
        raise HTTPException(400, 'No se pudo obtener perfil de Google')

    # 1) crear usuario si no existe
    user = db.query(User).filter_by(correo=data['email']).first()
    if not user:
        user = User(id=data['sub'], nombre=data['name'], correo=data['email'])
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2) emitir JWT propio
    jwt_data = {
        'sub': str(user.id),
        'role': 'user',
        'exp': datetime.utcnow() + timedelta(hours=12)
    }
    access_token = jwt.encode(jwt_data, JWT_SECRET, algorithm='HS256')

    # 3) redirigir al frontend con el token (query o fragment)
    url_front = f"{request.headers.get('origin', 'http://localhost:5173')}/login?token={access_token}"
    return RedirectResponse(url_front)