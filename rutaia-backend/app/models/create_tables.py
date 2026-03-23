from app.models.database import Base, engine
from app.models.user import User
from app.models.user_plan import UserPlan
from app.models.ciudad import Ciudad
from app.models.plan_actividades import PlanActividad
from app.models.plan_hospedaje import PlanHospedaje
from app.models.plan_lugares import PlanLugar
from app.models.plan_transporte import PlanTransporte
from app.models.historia_viaje import HistoriaViaje

import app.models.user_plan_pref  # asegura la importación


# Muy importante: asegúrate de que TODAS las clases estén ya importadas antes de esta línea
Base.metadata.create_all(bind=engine)