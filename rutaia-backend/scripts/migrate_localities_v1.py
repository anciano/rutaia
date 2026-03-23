# scripts/migrate_localities_v1.py
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Starting localities migration...")
        
        # 1. Create localities table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS localities (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL,
                type VARCHAR(50) NOT NULL,
                region VARCHAR(100) DEFAULT 'Aysén',
                comuna VARCHAR(100),
                lat FLOAT NOT NULL,
                lng FLOAT NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE NOT NULL,
                legacy_city_id INTEGER,
                legacy_item_id INTEGER
            )
        """))
        print("Created table: localities")

        # 2. Add locality_id to catalog_items
        conn.execute(text("ALTER TABLE catalog_items ADD COLUMN IF NOT EXISTS locality_id INTEGER REFERENCES localities(id) ON DELETE SET NULL"))
        print("Added locality_id to catalog_items")

        # 3. Modify destination_profiles
        conn.execute(text("ALTER TABLE destination_profiles ADD COLUMN IF NOT EXISTS locality_id INTEGER REFERENCES localities(id) ON DELETE CASCADE"))
        conn.execute(text("ALTER TABLE destination_profiles ALTER COLUMN catalog_item_id DROP NOT NULL"))
        # Ensure unique constraint on locality_id
        try:
            conn.execute(text("ALTER TABLE destination_profiles ADD CONSTRAINT destination_profiles_locality_id_key UNIQUE (locality_id)"))
        except:
            pass
        print("Updated destination_profiles")

        # 4. Modify catalog_events
        conn.execute(text("ALTER TABLE catalog_events ADD COLUMN IF NOT EXISTS locality_id INTEGER REFERENCES localities(id) ON DELETE CASCADE"))
        conn.execute(text("ALTER TABLE catalog_events ALTER COLUMN catalog_item_id DROP NOT NULL"))
        try:
            conn.execute(text("ALTER TABLE catalog_events ADD CONSTRAINT catalog_events_locality_id_key UNIQUE (locality_id)"))
        except:
            pass
        print("Updated catalog_events")

        # 5. Modify catalog_transport_segments
        conn.execute(text("ALTER TABLE catalog_transport_segments ADD COLUMN IF NOT EXISTS origin_locality_id INTEGER REFERENCES localities(id) ON DELETE SET NULL"))
        conn.execute(text("ALTER TABLE catalog_transport_segments ADD COLUMN IF NOT EXISTS destination_locality_id INTEGER REFERENCES localities(id) ON DELETE SET NULL"))
        print("Updated catalog_transport_segments")

        conn.commit()
        print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
