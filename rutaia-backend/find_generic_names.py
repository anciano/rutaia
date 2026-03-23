import os
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

# Patterns to find:
# 1. Names with numbers >= 10 at the end (e.g., Baker Camping 113)
# 2. Names with Roman numerals II, III, IV, V at the end
# 3. Specific patterns mentioned by user

query = text("""
    SELECT id, name, item_type 
    FROM catalog_items 
    WHERE name ~ '[^0-9]([1-9][0-9]+| [IVXLC]+)$'
    LIMIT 500
""")

try:
    result = session.execute(query).fetchall()
    print(f"Found {len(result)} potentially generic names:")
    for r in result:
        print(f"ID: {r[0]} | Type: {r[2]} | Name: {r[1]}")
except Exception as e:
    print(f"Error: {e}")
finally:
    session.close()
