# scripts/populate_aysen_localities.py
import os
import sys
from sqlalchemy import create_engine, text
from slugify import slugify
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

dataset = [
    # COYHAIQUE
    {"name": "Coyhaique", "type": "city", "comuna": "Coyhaique", "lat": -45.5750, "lng": -72.0660, "desc": "Capital regional y principal centro urbano de la Región de Aysén. Nodo administrativo, logístico y turístico de la Carretera Austral."},
    {"name": "Balmaceda", "type": "village", "comuna": "Coyhaique", "lat": -45.9167, "lng": -71.6890, "desc": "Localidad fronteriza conocida por el Aeropuerto Balmaceda, principal puerta aérea de la región."},
    {"name": "Villa Cerro Castillo", "type": "village", "comuna": "Río Ibáñez", "lat": -46.1200, "lng": -72.1200, "desc": "Pueblo ubicado junto al Parque Nacional Cerro Castillo, punto clave para trekking y acceso a la Patagonia interior."},
    {"name": "Valle Simpson", "type": "sector", "comuna": "Coyhaique", "lat": -45.5200, "lng": -72.3000, "desc": "Valle agrícola cercano a Coyhaique con estancias y paisajes rurales."},
    
    # AYSEN
    {"name": "Puerto Aysén", "type": "city", "comuna": "Aysén", "lat": -45.4000, "lng": -72.7000, "desc": "Ciudad portuaria ubicada en el fiordo Aysén y conectada a Puerto Chacabuco. Segundo centro urbano de la región."},
    {"name": "Puerto Chacabuco", "type": "port", "comuna": "Aysén", "lat": -45.4600, "lng": -72.8000, "desc": "Principal puerto marítimo de la región y punto de llegada de cruceros."},
    {"name": "Villa Mañihuales", "type": "town", "comuna": "Aysén", "lat": -45.1667, "lng": -72.1500, "desc": "Localidad rural situada en la Carretera Austral, con tradición ganadera y forestal."},
    {"name": "Puerto Cisnes", "type": "town", "comuna": "Cisnes", "lat": -44.7333, "lng": -72.7000, "desc": "Pueblo costero del canal Puyuhuapi con puerto pesquero y conectividad marítima."},
    {"name": "La Junta", "type": "town", "comuna": "Cisnes", "lat": -43.9700, "lng": -72.4200, "desc": "Puerta norte de la Carretera Austral en la región, punto de encuentro de ríos Rosselot y Palena."},
    {"name": "Puyuhuapi", "type": "village", "comuna": "Cisnes", "lat": -44.3200, "lng": -72.5600, "desc": "Pueblo fundado por colonos alemanes ubicado en el fiordo Puyuhuapi."},
    {"name": "Puerto Raúl Marín Balmaceda", "type": "village", "comuna": "Cisnes", "lat": -43.7800, "lng": -72.9600, "desc": "Localidad costera situada en la desembocadura del río Palena."},
    {"name": "Villa Amengual", "type": "village", "comuna": "Lago Verde", "lat": -44.1000, "lng": -71.7000, "desc": "Pequeña localidad rural ligada a la ganadería."},
    {"name": "Lago Verde", "type": "town", "comuna": "Lago Verde", "lat": -44.2300, "lng": -71.8500, "desc": "Localidad fronteriza cercana a Argentina y rodeada de estancias patagónicas."},
    
    # GENERAL CARRERA
    {"name": "Chile Chico", "type": "town", "comuna": "Chile Chico", "lat": -46.5500, "lng": -71.7200, "desc": "Ciudad ubicada a orillas del Lago General Carrera, conocida como la \"ciudad del sol\"."},
    {"name": "Puerto Guadal", "type": "village", "comuna": "Chile Chico", "lat": -46.7900, "lng": -72.0000, "desc": "Localidad turística a orillas del Lago General Carrera."},
    {"name": "Puerto Bertrand", "type": "village", "comuna": "Chile Chico", "lat": -46.8300, "lng": -72.7000, "desc": "Punto donde nace el río Baker desde el Lago Bertrand."},
    {"name": "Puerto Sánchez", "type": "village", "comuna": "Río Ibáñez", "lat": -46.4000, "lng": -72.3000, "desc": "Pequeña localidad lacustre del Lago General Carrera."},
    {"name": "Puerto Río Tranquilo", "type": "village", "comuna": "Río Ibáñez", "lat": -46.6200, "lng": -72.6700, "desc": "Base turística para visitar las Capillas de Mármol."},
    {"name": "Bahía Murta", "type": "village", "comuna": "Río Ibáñez", "lat": -46.5000, "lng": -72.6800, "desc": "Pueblo ribereño del Lago General Carrera."},
    {"name": "Puerto Ingeniero Ibáñez", "type": "town", "comuna": "Río Ibáñez", "lat": -46.2900, "lng": -71.9400, "desc": "Localidad portuaria del Lago General Carrera con conexión de ferry a Chile Chico."},
    
    # CAPITAN PRAT
    {"name": "Cochrane", "type": "town", "comuna": "Cochrane", "lat": -47.2600, "lng": -72.5700, "desc": "Centro urbano del sur de la región y puerta de entrada al Parque Patagonia."},
    {"name": "Caleta Tortel", "type": "town", "comuna": "Tortel", "lat": -47.8000, "lng": -73.5300, "desc": "Pueblo costero construido sobre pasarelas de ciprés."},
    {"name": "Puerto Yungay", "type": "port", "comuna": "Tortel", "lat": -47.3500, "lng": -72.8600, "desc": "Terminal de ferry que conecta con Río Bravo."},
    {"name": "Río Bravo", "type": "port", "comuna": "O'Higgins", "lat": -47.2500, "lng": -72.8400, "desc": "Punto de desembarque del ferry desde Puerto Yungay."},
    {"name": "Villa O’Higgins", "type": "town", "comuna": "O'Higgins", "lat": -48.4700, "lng": -72.5600, "desc": "Última localidad de la Carretera Austral."},
    
    # GUAITECAS
    {"name": "Melinka", "type": "town", "comuna": "Guaitecas", "lat": -43.9000, "lng": -73.7500, "desc": "Capital comunal del archipiélago de las Guaitecas."},
    {"name": "Repollal", "type": "village", "comuna": "Guaitecas", "lat": -43.9200, "lng": -73.7800, "desc": "Pequeño asentamiento pesquero cercano a Melinka."},
]

def populate_localities():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print(f"Starting population of Aysén localities ({len(dataset)} items)...")
        
        inserted = 0
        updated = 0
        
        for item in dataset:
            # Check existence
            res = conn.execute(text("SELECT id FROM localities WHERE name = :name"), {"name": item["name"]})
            existing = res.fetchone()
            
            # The 'params' dictionary was not used, removing it for consistency.
            # The 'description' key is already correctly mapped to 'item["desc"]' in the queries below.
            
            if existing:
                print(f"Updating: {item['name']}")
                conn.execute(text("""
                    UPDATE localities 
                    SET type = :type, comuna = :comuna, region = 'Aysén', 
                        lat = :lat, lng = :lng, description = :description
                    WHERE id = :id
                """), {
                    "type": item["type"],
                    "comuna": item["comuna"],
                    "lat": item["lat"],
                    "lng": item["lng"],
                    "description": item["desc"],
                    "id": existing.id
                })
                updated += 1
            else:
                print(f"Creating: {item['name']}")
                slug = slugify(item["name"])
                conn.execute(text("""
                    INSERT INTO localities (name, slug, type, region, comuna, lat, lng, description, is_active)
                    VALUES (:name, :slug, :type, 'Aysén', :comuna, :lat, :lng, :description, true)
                """), {
                    "name": item["name"],
                    "slug": slug,
                    "type": item["type"],
                    "comuna": item["comuna"],
                    "lat": item["lat"],
                    "lng": item["lng"],
                    "description": item["desc"]
                })
                inserted += 1
        
        conn.commit()
        print(f"Lote 1 Completed. {inserted} inserted, {updated} updated.")

if __name__ == "__main__":
    populate_localities()
