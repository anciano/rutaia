# /tmp/dump_localities.py
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    res = conn.execute(text('SELECT id, name, slug FROM localities ORDER BY id'))
    for row in res:
        print(f"{row[0]}|{row[1]}|{row[2]}")
