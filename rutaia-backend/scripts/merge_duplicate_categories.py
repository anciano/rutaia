# scripts/merge_duplicate_categories.py
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def merge_duplicates():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Starting taxonomy consolidation...")
        
        while True:
            # 1. Get all categories
            res = conn.execute(text("SELECT id, name, parent_id FROM catalog_categories"))
            categories = res.fetchall()
            
            # 2. Group by (parent_id, normalized_name)
            groups = {}
            found_any = False
            for row in categories:
                # Normalize name: lower, strip, and remove trailing s for plural/singular basic normalization
                norm_name = row.name.lower().strip()
                if norm_name.endswith('s') and len(norm_name) > 4: 
                    # basic plural check to catch extra/Extras or similar, but be careful
                    pass # Don't do it automatically for now to avoid 'Buses' -> 'Buse'
                
                key = (row.parent_id, norm_name)
                if key not in groups:
                    groups[key] = []
                groups[key].append(row)
                
            merged_this_pass = 0
            for key, members in groups.items():
                if len(members) > 1:
                    found_any = True
                    # Sort by ID descending (prefer newest)
                    members_sorted = sorted(members, key=lambda x: x.id, reverse=True)
                    master = members_sorted[0]
                    redundants = members_sorted[1:]
                    
                    print(f"Merging {len(redundants)} duplicates for '{key[1]}' under parent {key[0]} (Master ID: {master.id})")
                    
                    for red in redundants:
                        # Update items
                        conn.execute(text("UPDATE catalog_items SET category_id = :master_id WHERE category_id = :red_id"), 
                                     {"master_id": master.id, "red_id": red.id})
                        # Update child categories
                        conn.execute(text("UPDATE catalog_categories SET parent_id = :master_id WHERE parent_id = :red_id"), 
                                     {"master_id": master.id, "red_id": red.id})
                        # Delete redundant category
                        conn.execute(text("DELETE FROM catalog_categories WHERE id = :red_id"), 
                                     {"red_id": red.id})
                        merged_this_pass += 1
            
            if not found_any:
                break
            
            conn.commit()
            print(f"Pass completed. Merged {merged_this_pass} categories. Repeating...")
        
        print("Consolidation completed.")

if __name__ == "__main__":
    merge_duplicates()
