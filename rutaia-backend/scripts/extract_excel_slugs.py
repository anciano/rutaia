# scripts/extract_excel_slugs.py
import os
import pandas as pd

directory = r"c:\Proyectos\asesor"
files = [
    "rutaia_archivo5_abastecimiento_aysen.xlsx",
    "rutaia_archivo7_hospedajes_aysen.xlsx",
    "rutaia_archivo8_atractivos_naturales_aysen.xlsx",
    "rutaia_transporte_aysen.xlsx"
]

for f in files:
    path = os.path.join(directory, f)
    if os.path.exists(path):
        df = pd.read_excel(path)
        print(f"\n--- {f} ---")
        print(df['category'].dropna().unique().tolist())
