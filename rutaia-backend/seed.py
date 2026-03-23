# seed.py

from app.seeds.ciudades        import cargar_ciudades
from app.seeds.preferencias    import cargar_preferencias
from app.seeds.users           import seed_users
from app.seeds.lugares         import seed_lugares
from app.seeds.hospedajes      import seed_hospedajes
from app.seeds.actividades     import seed_actividades
from app.seeds.transportes     import seed_transportes

if __name__ == "__main__":
    print("🌱 Sembrando datos maestros…")
    cargar_ciudades()
    cargar_preferencias()
    seed_lugares()
    seed_hospedajes()
    seed_actividades()
    seed_transportes()
    seed_users()
    print("✅ Seeds completados.")