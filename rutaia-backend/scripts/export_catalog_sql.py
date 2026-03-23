# scripts/export_catalog_sql.py
import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

TABLES_TO_EXPORT = [
    "ciudades",
    "hospedajes",
    "catalog_categories",
    "catalog_items",
    "catalog_transport_segments",
    "destination_profiles",
    "catalog_events",
    "item_links"
]

def format_value(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (dict, list)):
        dumped = json.dumps(v, ensure_ascii=False)
        return "'" + dumped.replace("'", "''") + "'"
    if isinstance(v, datetime):
        return f"'{v.isoformat()}'"
    return "'" + str(v).replace("'", "''") + "'"

def export_sql():
    engine = create_engine(DATABASE_URL)
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "catalog_export.sql"))
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"-- RutaIA Catalog Module Export\n")
        f.write(f"-- Generated on: {datetime.now().isoformat()}\n\n")
        f.write("BEGIN;\n\n")
        
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        for table in TABLES_TO_EXPORT:
            if table not in existing_tables:
                f.write(f"-- Table {table} not found in database.\n\n")
                continue
                
            f.write(f"-- Table: {table}\n")
            
            # Get columns for INSERT
            columns = [col["name"] for col in inspector.get_columns(table)]
            col_names = ", ".join(columns)
            
            # Get data
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM {table}"))
                rows = result.fetchall()
                
                if not rows:
                    f.write(f"-- No data in {table}\n\n")
                    continue
                    
                for row in rows:
                    values = [format_value(getattr(row, col)) for col in columns]
                    v_str = ", ".join(values)
                    f.write(f"INSERT INTO {table} ({col_names}) VALUES ({v_str});\n")
            
            f.write("\n")
            
        f.write("COMMIT;\n")
    
    print(f"Export finished: {output_path}")

if __name__ == "__main__":
    export_sql()
