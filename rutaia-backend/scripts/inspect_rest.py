# scripts/inspect_rest.py
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
        print(f"\n--- {f} ---")
        try:
            df = pd.read_excel(path)
            print("COLUMNS:", df.columns.tolist())
            if not df.empty:
                print("SAMPLE ROW 1:")
                for col, val in df.iloc[0].to_dict().items():
                    print(f"  {col}: {val}")
        except Exception as e:
            print(f"ERROR: {e}")
