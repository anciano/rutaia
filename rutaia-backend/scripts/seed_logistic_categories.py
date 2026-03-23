# scripts/seed_logistic_categories.py
import sys
import os
from sqlalchemy.orm import Session

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.database import SessionLocal
from app.models.catalog_category import CatalogCategory

def seed_categories():
    db: Session = SessionLocal()
    try:
        # Define hierarchical structure
        structure = {
            "Servicios": {
                "icon": "pi-objects-column",
                "sub": {
                    "Combustible y movilidad": {
                        "icon": "pi-car",
                        "types": {
                            "gas_station": "Gasolinera",
                            "rural_fuel_point": "Punto de Combustible Rural",
                            "ev_charging_station": "Carga Eléctrica (EV)",
                            "mechanic_workshop": "Taller Mecánico",
                            "tire_repair": "Gomería / Vulcanización",
                            "roadside_assistance": "Asistencia en Ruta",
                            "vehicle_rental": "Arriendo de Vehículos",
                            "public_parking": "Estacionamiento Público"
                        }
                    },
                    "Abastecimiento y comercio": {
                        "icon": "pi-shopping-cart",
                        "types": {
                            "supermarket": "Supermercado",
                            "minimarket": "Minimarket / Almacén",
                            "rural_store": "Tienda Rural",
                            "bakery": "Panadería",
                            "butcher": "Carnicería",
                            "greengrocer": "Frutería y Verdulería",
                            "outdoor_store": "Tienda de Outdoor",
                            "camping_store": "Artículos de Camping",
                            "hardware_store": "Ferretería",
                            "gas_bottle_store": "Venta de Gas (Balón)"
                        }
                    },
                    "Gastronomía": {
                        "icon": "pi-map",
                        "types": {
                            "restaurant": "Restaurante",
                            "cafe": "Cafetería",
                            "bar": "Bar",
                            "pub": "Pub",
                            "brewery": "Cervecería Artesanal",
                            "pastry_shop": "Pastelería",
                            "ice_cream_shop": "Heladería",
                            "food_truck": "Carrito de Comida (Food Truck)"
                        }
                    },
                    "Salud y emergencias": {
                        "icon": "pi-heart-fill",
                        "types": {
                            "hospital": "Hospital",
                            "clinic": "Clínica",
                            "cesfam": "CESFAM / SAPU",
                            "rural_health_post": "Posta de Salud Rural",
                            "pharmacy": "Farmacia",
                            "dental_clinic": "Clínica Dental",
                            "ambulance_base": "Base de Ambulancias",
                            "police_station": "Carabineros / Policía",
                            "fire_station": "Bomberos",
                            "mountain_rescue": "Rescate de Montaña"
                        }
                    },
                    "Servicios financieros": {
                        "icon": "pi-credit-card",
                        "types": {
                            "atm": "Cajero Automático (ATM)",
                            "bank": "Banco",
                            "local_payment_point": "Punto de Pago Local (CajaVecina)",
                            "currency_exchange": "Casa de Cambio"
                        }
                    },
                    "Servicios turísticos": {
                        "icon": "pi-info-circle",
                        "types": {
                            "tour_agency": "Agencia de Turismo",
                            "visitor_center": "Centro de Visitantes",
                            "equipment_rental": "Arriendo de Equipamiento",
                            "local_guide": "Guía Local"
                        }
                    },
                    "Servicios logísticos del viajero": {
                        "icon": "pi-box",
                        "types": {
                            "laundry": "Lavandería",
                            "bicycle_repair": "Taller de Bicicletas",
                            "bicycle_rental": "Arriendo de Bicicletas",
                            "boat_repair": "Taller Naval / Lanchas",
                            "gas_supply": "Recarga de Gas (Primus/Isopropano)",
                            "firewood_store": "Venta de Leña"
                        }
                    }
                }
            },
            "Infraestructura": {
                "icon": "pi-building",
                "sub": {
                    "Transporte e infraestructura": {
                        "icon": "pi-map-marker",
                        "types": {
                            "bus_terminal": "Terminal de Buses",
                            "bus_stop": "Paradero / Refugio",
                            "ferry_terminal": "Terminal de Ferry / Rampa",
                            "pier": "Muelle / Embarcadero",
                            "harbor": "Puerto",
                            "airport": "Aeropuerto",
                            "airfield": "Aeródromo",
                            "heliport": "Helipuerto",
                            "transport_office": "Oficina de Transporte / Ventas"
                        }
                    },
                    "Servicios públicos": {
                        "icon": "pi-briefcase",
                        "types": {
                            "municipality": "Municipalidad",
                            "tourism_office": "Oficina de Información Turística",
                            "civil_registry": "Registro Civil",
                            "post_office": "Correos / Encomiendas",
                            "customs": "Aduana / Paso Fronterizo",
                            "national_park_office": "Oficina Conaf / Guardaparque"
                        }
                    },
                    "Infraestructura pública": {
                        "icon": "pi-bookmark",
                        "types": {
                            "public_restroom": "Baños Públicos",
                            "public_shower": "Duchas Públicas",
                            "picnic_area": "Zona de Picnic",
                            "rest_area": "Zona de Descanso",
                            "recycling_point": "Punto de Reciclaje / Punto Verde"
                        }
                    },
                    "Comunicaciones": {
                        "icon": "pi-wifi",
                        "types": {
                            "wifi_hotspot": "Zona WiFi Pública",
                            "telecom_tower": "Torre de Telecomunicaciones",
                            "phone_booth": "Teléfono Público",
                            "signal_zone": "Zona con Señal Celular",
                            "no_signal_zone": "Zona sin Señal (Sombra)"
                        }
                    },
                    "Servicios camper / overland": {
                        "icon": "pi-truck",
                        "types": {
                            "camper_service": "Servicio para Campers",
                            "greywater_dump": "Vaciado de Aguas Grises",
                            "potable_water_station": "Carga de Agua Potable",
                            "camper_parking": "Estacionamiento para Campers",
                            "technical_camping_area": "Zona de Camping Técnico"
                        }
                    }
                }
            }
        }

        for root_name, root_info in structure.items():
            # Get or create root
            root = db.query(CatalogCategory).filter_by(name=root_name).first()
            if not root:
                root = CatalogCategory(name=root_name, icon=root_info["icon"])
                db.add(root)
                db.flush()
            
            for group_name, group_info in root_info["sub"].items():
                group = db.query(CatalogCategory).filter_by(name=group_name, parent_id=root.id).first()
                if not group:
                    group = CatalogCategory(name=group_name, parent_id=root.id, icon=group_info["icon"])
                    db.add(group)
                    db.flush()
                
                for type_code, cat_name in group_info["types"].items():
                    cat = db.query(CatalogCategory).filter_by(name=cat_name, parent_id=group.id).first()
                    if not cat:
                        cat = CatalogCategory(name=cat_name, parent_id=group.id, icon=group_info["icon"])
                        db.add(cat)
        
        db.commit()
        print("Logistic categories seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding categories: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_categories()
