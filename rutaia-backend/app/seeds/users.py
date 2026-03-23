from app.models.database import SessionLocal
from app.models.user import User
from passlib.hash import bcrypt

def seed_users():
    session = SessionLocal()

    # Admin local
    admin = User(
        id="f67c19c2-8e4e-408e-b35a-fd037c5cfe6c1",
        nombre="Administrador",
        correo="admin@rutaia.cl",
        password_hash=bcrypt.hash("123"),
        role="admin",
        provider="local"
    )
    session.merge(admin)

    # Usuario local
    user = User(
        id="f67c19c2-8e4e-408e-b35a-fd037c5cfe6c2",
        nombre="Usuario Normal",
        correo="user@rutaia.cl",
        password_hash=bcrypt.hash("123"),
        role="user",
        provider="local"
    )
    session.merge(user)

    session.commit()
    session.close()
    print("✅ Usuarios seedados (admin + user).")

if __name__ == "__main__":
    seed_users()
