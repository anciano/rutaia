import os
import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = 'postgresql://postgres:26c453def@localhost:5432/rutaia'

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Regex to find:
# 1. Space followed by 2 or more digits at the end
# 2. Space followed by Roman numerals (II, III, IV, V, VI, VII, VIII, IX, X) at the end
RE_SUFFIX = re.compile(r'\s+([0-9]{2,}|[IVXLC]+)$', re.IGNORECASE)

def clean_name(name):
    if not name: return name
    
    original = name
    # Remove trailing generic suffix
    name = RE_SUFFIX.sub('', name)
    
    # Remove common redundancies if any (e.g. "Coyhaique Coyhaique")
    parts = name.split()
    if len(parts) >= 2 and parts[-1] == parts[-2]:
        name = ' '.join(parts[:-1])
        
    return name.strip()

try:
    # Fetch potentially problematic names
    query = text("""
        SELECT id, name FROM catalog_items 
        WHERE name ~ '\\s+([0-9]{2,}|[IVXLC]+)$'
    """)
    items = session.execute(query).fetchall()
    
    print(f"Analyzing {len(items)} items...")
    updates = 0
    
    for item_id, old_name in items:
        new_name = clean_name(old_name)
        if new_name != old_name:
            print(f"Updating ID {item_id}: '{old_name}' -> '{new_name}'")
            session.execute(
                text("UPDATE catalog_items SET name = :name WHERE id = :id"),
                {"name": new_name, "id": item_id}
            )
            updates += 1
            
    session.commit()
    print(f"Cleanup complete. Updated {updates} items.")
    
except Exception as e:
    print(f"Error: {e}")
    session.rollback()
finally:
    session.close()
