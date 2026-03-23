# scripts/seed_taxonomy_v2.py
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.database import SessionLocal
from app.models.catalog_category import CatalogCategory

def slugify(text):
    return text.lower().replace(" ", "-").replace("/", "-").replace("(", "").replace(")", "").replace("'", "").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")

def seed_taxonomy():
    db: Session = SessionLocal()
    try:
        structure = {
            "Naturaleza": {
                "icon": "pi-sun",
                "subs": [
                    "Glaciares", "Ríos", "Lagos", "Lagunas", "Cascadas", "Montañas", "Volcanes", "Fiordos", "Canales", 
                    "Campos de hielo", "Bosques", "Parques nacionales", "Reservas naturales", "Monumentos naturales", 
                    "Miradores naturales", "Formaciones geológicas", "Playas", "Cuevas", "Islas", "Bahías"
                ]
            },
            "Servicios": {
                "icon": "pi-wrench",
                "groups": {
                    "Gastronomía": ["Restaurante", "Cafetería", "Bar", "Pub", "Pastelería", "Heladería", "Cervecería artesanal", "Food truck"],
                    "Salud": ["Hospital", "Clínica", "CESFAM", "Posta rural", "Farmacia", "Centro dental", "Ambulancia"],
                    "Finanzas": ["Banco", "Cajero automático", "Caja vecina", "Cambio de moneda"],
                    "Comercio": ["Supermercado", "Minimarket", "Ferretería", "Tienda outdoor", "Tienda camping", "Panadería", "Carnicería", "Verdulería", "Mercado local"],
                    "Turismo": ["Agencia de turismo", "Centro de visitantes", "Información turística", "Guía turístico", "Arriendo de equipos"]
                }
            },
            "Infraestructura": {
                "icon": "pi-building",
                "groups": {
                    "Transporte": ["Terminal de buses", "Paradero", "Aeropuerto", "Aeródromo", "Helipuerto", "Puerto", "Embarcadero", "Terminal ferry", "Muelle turístico"],
                    "Servicios públicos": ["Municipalidad", "Registro civil", "Correos", "Aduana", "Oficina CONAF", "Oficina SAG"],
                    "Infraestructura pública": ["Baños públicos", "Área de descanso", "Zona picnic", "Camping municipal", "Estacionamiento público", "Punto reciclaje"]
                }
            },
            "Experiencias": {
                "icon": "pi-map",
                "subs": [
                    "Trekking", "Senderismo", "Kayak", "Rafting", "Cabalgata", "Escalada", "Pesca", "Ciclismo", "Mountain bike", 
                    "Observación de fauna", "Observación de aves", "Fotografía", "Navegación", "Expediciones", "Turismo científico", "Turismo aventura"
                ]
            },
            "Cultura": {
                "icon": "pi-book",
                "subs": [
                    "Museos", "Patrimonio histórico", "Monumentos", "Sitios arqueológicos", "Arquitectura patrimonial", "Pueblos históricos", 
                    "Iglesias", "Cultura local", "Ferias artesanales", "Artesanía", "Fiestas tradicionales"
                ]
            },
            "Logística": {
                "icon": "pi-truck",
                "groups": {
                    "Combustible": ["Gasolinera", "Punto combustible rural", "Carga eléctrica EV"],
                    "Movilidad": ["Taller mecánico", "Vulcanización", "Grúa", "Lavado vehículos", "Arriendo vehículos"],
                    "Servicios viajero": ["Lavandería", "Duchas públicas", "Taller bicicletas", "Arriendo bicicletas", "Venta gas", "Venta leña"],
                    "Servicios camper": ["Camper service", "Descarga aguas grises", "Carga agua potable", "Estacionamiento camper"],
                    "Comunicaciones": ["Wifi público", "Zona señal móvil", "Zona sin señal", "Torre telecomunicaciones"]
                }
            }
        }

        print("Seeding full taxonomy structure...")
        
        for root_name, root_data in structure.items():
            # 1. Create Root
            root_slug = slugify(root_name)
            root = db.query(CatalogCategory).filter_by(slug=root_slug).first()
            if not root:
                root = CatalogCategory(name=root_name, slug=root_slug, root_block=root_name, icon=root_data.get("icon"))
                db.add(root)
                db.flush()
                print(f"Created Root: {root_name}")
            
            # 2. Handle sub-categories (flat)
            if "subs" in root_data:
                for sub_name in root_data["subs"]:
                    sub_slug = f"{root_slug}-{slugify(sub_name)}"
                    sub = db.query(CatalogCategory).filter_by(slug=sub_slug).first()
                    if not sub:
                        sub = CatalogCategory(name=sub_name, slug=sub_slug, parent_id=root.id, root_block=root_name)
                        db.add(sub)
            
            # 3. Handle groups (hierarchical)
            if "groups" in root_data:
                for group_name, child_names in root_data["groups"].items():
                    group_slug = f"{root_slug}-{slugify(group_name)}"
                    group = db.query(CatalogCategory).filter_by(slug=group_slug).first()
                    if not group:
                        group = CatalogCategory(name=group_name, slug=group_slug, parent_id=root.id, root_block=root_name)
                        db.add(group)
                        db.flush()
                    
                    for child_name in child_names:
                        child_slug = f"{group_slug}-{slugify(child_name)}"
                        child = db.query(CatalogCategory).filter_by(slug=child_slug).first()
                        if not child:
                            child = CatalogCategory(name=child_name, slug=child_slug, parent_id=group.id, root_block=root_name)
                            db.add(child)

        db.commit()
        print("Taxonomy seeding completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding taxonomy: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_taxonomy()
