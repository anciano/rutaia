# scripts/cleanup_localities.py
import os
from sqlalchemy import create_engine, text
from slugify import slugify
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def cleanup():
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        print("Auditing localities...")
        res = conn.execute(text("SELECT id, name, slug FROM localities ORDER BY id"))
        all_locs = res.fetchall()
        
        # 1. Normalize and find duplicates
        name_to_id = {}
        to_delete = []
        
        for loc_id, name, slug in all_locs:
            norm_name = name.replace("’", "'").replace("‘", "'").strip()
            norm_slug = slugify(norm_name)
            
            if norm_slug in name_to_id:
                primary_id = name_to_id[norm_slug]
                print(f"Merge: {name} (ID {loc_id}) -> Primary ID {primary_id}")
                
                # Move items
                conn.execute(text("UPDATE catalog_items SET locality_id = :primary_id WHERE locality_id = :loc_id"), 
                             {"primary_id": primary_id, "loc_id": loc_id})
                to_delete.append(loc_id)
            else:
                name_to_id[norm_slug] = loc_id
                
                # Update name/slug if different
                if slug != norm_slug or name != norm_name:
                    print(f"Standardize: {name} ({slug}) -> {norm_name} ({norm_slug})")
                    # Use a temp slug if collision occurs (not likely here as we checked seen_slugs)
                    conn.execute(text("UPDATE localities SET name = :name, slug = :slug WHERE id = :id"), 
                                 {"name": norm_name, "slug": norm_slug, "id": loc_id})
        
        if to_delete:
            print(f"Deleting {len(to_delete)} duplicates...")
            conn.execute(text("DELETE FROM localities WHERE id IN :ids"), {"ids": tuple(to_delete)})
        
        print("Cleanup completed.")

if __name__ == "__main__":
    cleanup()
