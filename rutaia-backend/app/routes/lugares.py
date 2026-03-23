from fastapi import APIRouter, Depends, Query, HTTPException, Path, Body, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.lugar    import Lugar as LugarModel
from app.schemas.lugares import Lugar, LugarCreate, LugarUpdate

router = APIRouter(prefix="/lugares", tags=["lugares"])

@router.get("/categorias", summary="Listar categorías disponibles")
def listar_categorias(db: Session = Depends(get_db)):
    from app.models.categoria import Categoria
    return db.query(Categoria).all()

@router.get("/", response_model=List[Lugar])
def listar_lugares(
    categoria_id: Optional[int] = Query(None),
    ciudad_id: Optional[int]    = Query(None),
    categoria:    Optional[str] = Query(None), # Legacy support
    db: Session = Depends(get_db),
):
    q = db.query(LugarModel)
    
    if categoria_id:
        q = q.filter(LugarModel.categoria_id == categoria_id)
    if ciudad_id:
        q = q.filter(LugarModel.ciudad_id == ciudad_id)
        
    # Legacy fallback: Filter by string category if provided and not by ID
    if categoria and not categoria_id:
        q = q.filter(LugarModel.categoria.ilike(f"%{categoria}%"))
        
    return q.order_by(LugarModel.nombre).all()

@router.get("/{lugar_id}", response_model=Lugar)
def obtener_lugar(lugar_id: int = Path(...), db: Session = Depends(get_db)):
    lugar = db.get(LugarModel, lugar_id)
    if not lugar:
        raise HTTPException(404, "Lugar no encontrado")
    return lugar

@router.post("/", response_model=Lugar, status_code=status.HTTP_201_CREATED)
def crear_lugar(payload: LugarCreate = Body(...), db: Session = Depends(get_db)):
    nuevo = LugarModel(**payload.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{lugar_id}", response_model=Lugar)
def actualizar_lugar(
    lugar_id: int = Path(...),
    payload: LugarUpdate = Body(...),
    db: Session = Depends(get_db)
):
    lugar = db.get(LugarModel, lugar_id)
    if not lugar:
        raise HTTPException(404, "Lugar no encontrado")
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(lugar, key, value)
    
    db.add(lugar)
    db.commit()
    db.refresh(lugar)
    return lugar

@router.delete("/{lugar_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_lugar(lugar_id: int = Path(...), db: Session = Depends(get_db)):
    lugar = db.get(LugarModel, lugar_id)
    if not lugar:
        raise HTTPException(404, "Lugar no encontrado")
    db.delete(lugar)
    db.commit()
    return None
