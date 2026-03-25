from datetime import date, timedelta
import bcrypt
from app.models.database import SessionLocal
from app.models.user import User
from app.models.user_plan import UserPlan

def seed_users():
    session = SessionLocal()

    def get_hash(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Admin local
    admin_id = "f67c19c2-8e4e-408e-b35a-fd037c5cfe6c1"
    admin = User(
        id=admin_id,
        nombre="Administrador",
        correo="admin@rutaia.cl",
        password_hash=get_hash("123"),
        role="admin",
        provider="local"
    )
    session.merge(admin)

    # Usuario local
    user_id = "f67c19c2-8e4e-408e-b35a-fd037c5cfe6c2"
    user = User(
        id=user_id,
        nombre="Usuario Normal",
        correo="user@rutaia.cl",
        password_hash=get_hash("123"),
        role="user",
        provider="local"
    )
    session.merge(user)

    # Gestor local
    gestor_id = "f67c19c2-8e4e-408e-b35a-fd037c5cfe6c3"
    gestor = User(
        id=gestor_id,
        nombre="Gestor Regional",
        correo="gestor@rutaia.cl",
        password_hash=get_hash("123"),
        role="gestor",
        provider="local"
    )
    session.merge(gestor)

    # Sample Plan for Admin
    sample_plan_id = "e1a1b2c3-d4e5-4f6a-b7c8-d9e0f1a2b3c4"
    if not session.query(UserPlan).filter_by(id=sample_plan_id).first():
        hoy = date.today()
        nuevo_plan = UserPlan(
            id=sample_plan_id,
            user_id=admin_id,
            origen_id=1, # Coyhaique (seeded in cargar_ciudades)
            participantes=[{"edad": 30, "discapacidad": False}],
            preferencias=["naturaleza", "aventura"],
            dias=5,
            presupuesto=500000,
            fecha_inicio=hoy + timedelta(days=7),
            fecha_fin=hoy + timedelta(days=12),
            transport_mode="auto_propio",
            estado="activo"
        )
        session.add(nuevo_plan)

    session.commit()
    session.close()
    print("✅ Usuarios y plan de ejemplo seedados.")

if __name__ == "__main__":
    seed_users()
