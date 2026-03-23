import os
import sys
import pandas as pd
from decimal import Decimal
import re

# Add current directory to path
sys.path.append(os.getcwd())

from app.models.database import SessionLocal
from app.models.lugar import Lugar
from app.models.ciudad import Ciudad

def parse_duration(text):
    if pd.isna(text): return 60
    text = str(text).lower()
    # Match numbers
    nums = re.findall(r'\d+', text)
    if not nums: return 60
    
    val = int(nums[0])
    if 'noche' in text or 'día' in text or 'dia' in text:
        return val * 24 * 60 # Convert days to minutes for consistent logic
    if 'hora' in text:
        return val * 60
    return val

def import_from_excel(file_path):
    db = SessionLocal()
    try:
        print(f"Reading {file_path}...")
        df = pd.read_excel(file_path)
        
        # Mapping Excel -> Model
        # Categoría, Nombre del lugar, Descripción breve, Precio aprox., Ubicación, Calificación, Duración estimada, rango etario, Descripción breve 2
        
        # For simplicity, we assume these places belong to 'santiago' if city is not found
        # Or we can try to infer from 'Ubicación'
        
        cities = {c.nombre.lower(): c.id for c in db.query(Ciudad).all()}
        
        stats = {"added": 0, "updated": 0, "errors": 0}
        
        for _, row in df.iterrows():
            try:
                nombre = str(row['Nombre del lugar']).strip()
                if not nombre or nombre == 'nan': continue
                
                # Check for existing
                existing = db.query(Lugar).filter(Lugar.nombre == nombre).first()
                
                # Default city if not found in address
                city_id = 'santiago'
                loc_text = str(row.get('Ubicación', '')).lower()
                for c_name, c_id in cities.items():
                    if c_name in loc_text:
                        city_id = c_id
                        break
                
                price = 0
                try:
                    price_str = str(row.get('Precio aprox.', '0'))
                    price = int(re.sub(r'[^\d]', '', price_str)) if price_str != 'nan' else 0
                except: pass

                if existing:
                    # Update
                    existing.descripcion_breve = str(row.get('Descripción breve', '')) if not pd.isna(row.get('Descripción breve')) else existing.descripcion_breve
                    existing.categoria = str(row.get('Categoría', '')).lower() if not pd.isna(row.get('Categoría')) else existing.categoria
                    existing.precio_aprox = price
                    existing.direccion = str(row.get('Ubicación', '')) if not pd.isna(row.get('Ubicación')) else existing.direccion
                    
                    calif = row.get('Calificación')
                    if not pd.isna(calif):
                        try: existing.calificacion = float(calif)
                        except: pass
                        
                    existing.rango_etario = str(row.get('rango etario', '')) if not pd.isna(row.get('rango etario')) else existing.rango_etario
                    existing.accesibilidad = str(row.get('Descripción breve 2', '')) if not pd.isna(row.get('Descripción breve 2')) else existing.accesibilidad
                    existing.estimated_duration_minutes = parse_duration(row.get('Duración estimada'))
                    stats["updated"] += 1
                else:
                    # Create
                    calif = 4.0
                    raw_calif = row.get('Calificación')
                    if not pd.isna(raw_calif):
                        try: calif = float(raw_calif)
                        except: pass

                    new_lugar = Lugar(
                        nombre=nombre,
                        ciudad_id=city_id,
                        descripcion_breve=str(row.get('Descripción breve', '')) if not pd.isna(row.get('Descripción breve')) else '',
                        categoria=str(row.get('Categoría', 'cultura')).lower() if not pd.isna(row.get('Categoría')) else 'cultura',
                        precio_aprox=price,
                        direccion=str(row.get('Ubicación', '')) if not pd.isna(row.get('Ubicación')) else '',
                        calificacion=calif,
                        rango_etario=str(row.get('rango etario', '')) if not pd.isna(row.get('rango etario')) else '',
                        accesibilidad=str(row.get('Descripción breve 2', '')) if not pd.isna(row.get('Descripción breve 2')) else '',
                        estimated_duration_minutes=parse_duration(row.get('Duración estimada')),
                        latitud=Decimal("0.0"), 
                        longitud=Decimal("0.0")
                    )
                    db.add(new_lugar)
                    stats["added"] += 1
            except Exception as row_e:
                print(f"Error processing row {nombre}: {row_e}")
                stats["errors"] += 1
        
        db.commit()
        print(f"Import finished. Added: {stats['added']}, Updated: {stats['updated']}, Errors: {stats['errors']}")
        
    except Exception as e:
        db.rollback()
        print(f"Fatal error during import: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_from_excel("../LISTA.xlsx")
