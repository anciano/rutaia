# scripts/inspect_all_excels.py
import os
import pandas as pd
import json

directory = r"c:\Proyectos\asesor"
files = [
    "rutaia_archivo1_localidades_aysen.xlsx",
    "rutaia_archivo2_salud_emergencia_aysen.xlsx",
    "rutaia_archivo3_combustible_aysen.xlsx",
    "rutaia_archivo4_finanzas_aysen.xlsx",
    "rutaia_archivo5_abastecimiento_aysen.xlsx",
    "rutaia_archivo7_hospedajes_aysen.xlsx",
    "rutaia_archivo8_atractivos_naturales_aysen.xlsx",
    "rutaia_transporte_aysen.xlsx"
]

for f in files:
    path = os.path.join(directory, f)
    if os.path.exists(path):
        print(f"\nFILE: {f}")
        try:
            df = pd.read_excel(path)
            print("COLUMNS:", df.columns.tolist())
            if not df.empty:
                # Convert first row to a readable format
                sample = df.iloc[0].to_dict()
                # Handle non-serializable types for cleaner printing
                clean_sample = {k: str(v) for k, v in sample.items()}
                print("SAMPLE:", json.dumps(clean_sample, indent=2))
            else:
                print("SAMPLE: Empty file")
        except Exception as e:
            print(f"ERROR: {e}")
