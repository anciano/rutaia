# app/routes/planificacion.py
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, conint
from datetime import date
from typing import List, Optional
from uuid import uuid4
from app.models.database import get_db
from app.models.user_plan import UserPlan
from app.models.preferencia import Preferencia
from app.models.ciudad import Ciudad
from app.schemas.plan import PlanInput, PlanOutput  # PlanOutput es opcional, si quieres un schema de salida

router = APIRouter(prefix="/planificacion", tags=["planificacion"])

# ✅ Esquema de entrada (solo los campos editables)
class PlanUpdateSchema(BaseModel):
    presupuesto: Optional[int] = None
    total_days: Optional[conint(ge=1)] = None

@router.post("/guardar")
def guardar_plan(plan: PlanInput, db: Session = Depends(get_db)):
    # … validaciones …
    existentes = {
        str(p[0]) for p in db.query(Preferencia.id).filter(Preferencia.id.in_(plan.preferencias)).all()
    }
    faltantes = set(plan.preferencias) - existentes
    if faltantes:
        raise HTTPException(400, detail=f"Preferencias no válidas: {faltantes}")
    # Serializa los participantes a dicts
    participantes_serializados = [
        p.model_dump()    # o p.dict() si usas Pydantic v1
        for p in plan.participantes
    ]

    nuevo = UserPlan(
        id=str(uuid4()),
        user_id=plan.user_id,
        origen_id=plan.origen_id,
        dias=plan.dias,
        presupuesto=plan.presupuesto,
        budget_clp=plan.presupuesto,       # Sync budget_clp with presupuesto
        total_days=plan.dias,               # Sync total_days with dias
        participantes=participantes_serializados,  # ahora sí son JSON serializable
        preferencias=plan.preferencias,
        fecha_inicio=plan.fecha_inicio,
        fecha_fin=plan.fecha_fin,
        transport_mode=plan.transport_mode,
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"ok": True, "plan_id": nuevo.id}


@router.get("/planificaciones", response_model=List[PlanOutput])
def listar_planificaciones(user_id: str = Query(...), db: Session = Depends(get_db)):
    planes = (
        db.query(UserPlan)
          .filter(UserPlan.user_id == user_id)
          .order_by(UserPlan.fecha_inicio.desc())
          .all()
    )
    resultados = []
    for p in planes:
        # -- Aquí corregimos la obtención del nombre de la ciudad --
        ciudad_obj = db.get(Ciudad, p.origen_id)
        ciudad_nombre = ciudad_obj.nombre if ciudad_obj else None

        resultados.append({
            "id": p.id,
            "origen_id": p.origen_id,
            "origen": ciudad_nombre,
            "participantes": p.participantes,
            "preferencias": p.preferencias,
            "dias": p.dias,
            "presupuesto": p.presupuesto,
            "fecha_inicio": p.fecha_inicio,
            "fecha_fin": p.fecha_fin,
            "transport_mode": p.transport_mode,
            "estado": p.estado
        })
    return resultados

@router.get("/planificaciones/activa", response_model=Optional[PlanOutput], summary="Obtener la planificación activa del usuario")
def obtener_planificacion_activa(user_id: str = Query(..., description="ID del usuario"), db: Session = Depends(get_db)):
    # Busca el primer plan con estado 'activo' para este usuario
    plan = db.query(UserPlan).filter(
        UserPlan.user_id == user_id,
        UserPlan.estado == "activo"
    ).order_by(UserPlan.fecha_inicio.desc()).first()
    
    if not plan:
        return None  # Retornamos null con 200 OK para que el frontend maneje el caso "sin plan"

    # Carga nombre de ciudad
    ciudad = db.get(Ciudad, plan.origen_id)
    nombre_ciudad = ciudad.nombre if ciudad else None

    return {
        "id"            : plan.id,
        "origen_id"     : plan.origen_id,
        "origen"        : nombre_ciudad,
        "participantes" : plan.participantes,
        "preferencias"  : plan.preferencias,
        "dias"          : plan.dias,
        "presupuesto"   : plan.presupuesto,
        "fecha_inicio"  : plan.fecha_inicio,
        "fecha_fin"     : plan.fecha_fin,
        "transport_mode": plan.transport_mode,
        "estado"        : plan.estado
    }

@router.get(
    "/planificaciones/{plan_id}",
    response_model=PlanOutput,
    summary="Obtener detalle de una planificación"
)
def obtener_plan(
    plan_id: str = Path(..., description="ID de la planificación"),
    user_id: str = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    # Busca el plan y comprueba que pertenezca al usuario
    plan = db.query(UserPlan).filter(
        UserPlan.id == plan_id,
        UserPlan.user_id == user_id
    ).first()
    if not plan:
        raise HTTPException(404, "Planificación no encontrada")

    # Carga nombre de ciudad
    ciudad = db.get(Ciudad, plan.origen_id)
    nombre_ciudad = ciudad.nombre if ciudad else None

    return {
        "id"            : plan.id,
        "origen_id"     : plan.origen_id,
        "origen"        : nombre_ciudad,
        "participantes" : plan.participantes,
        "preferencias"  : plan.preferencias,
        "dias"          : plan.dias,
        "presupuesto"   : plan.presupuesto,
        "fecha_inicio"  : plan.fecha_inicio,
        "fecha_fin"     : plan.fecha_fin,
        "transport_mode": plan.transport_mode,
        "estado"        : plan.estado
    }

@router.patch("/planificaciones/activar/{plan_id}")
def activar_planificacion(
    plan_id: str = Path(...),
    user_id: str = Query(...),
    db: Session = Depends(get_db)
):
    plan = db.query(UserPlan).filter(
        UserPlan.id == plan_id, UserPlan.user_id == user_id
    ).first()
    if not plan:
        raise HTTPException(404, "Planificación no encontrada")

    # Finalizar las otras activas
    db.query(UserPlan).filter(
        UserPlan.user_id == user_id,
        UserPlan.estado == "activo",
        UserPlan.id != plan_id
    ).update({UserPlan.estado: "finalizado"})
    plan.estado = "activo"
    db.commit()
    db.refresh(plan)

    return {"ok": True, "plan_activado": plan.id}

@router.patch("/planificaciones/{plan_id}", summary="Actualizar presupuesto o días de una planificación")
def update_plan_fields(
    plan_id: str = Path(..., description="ID de la planificación"),
    payload: PlanUpdateSchema = Body(...),
    db: Session = Depends(get_db),
):
    plan = db.query(UserPlan).filter(UserPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    updated = False
    if payload.presupuesto is not None:
        plan.presupuesto = payload.presupuesto
        updated = True
    if payload.total_days is not None:
        plan.total_days = payload.total_days
        updated = True
    if not updated:
        raise HTTPException(status_code=400, detail="No se enviaron campos válidos para actualizar")

    db.commit()
    db.refresh(plan)
    return plan

@router.delete("/planificaciones/{plan_id}", status_code=204, summary="Eliminar una planificación")
def delete_plan(
    plan_id: str = Path(...),
    db: Session = Depends(get_db)
):
    plan = db.query(UserPlan).filter(UserPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    db.delete(plan)
    db.commit()
    return