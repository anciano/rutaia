# scripts/sample_excel_files.py
import os
import pandas as pd

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
        print(f"\n--- Sampling {f} ---")
        try:
            df = pd.read_excel(path)
            print("Columns:", df.columns.tolist())
            print("Row 1 Sample:", df.iloc[0].to_dict() if not df.empty else "Empty")
        except Exception as e:
            print(f"Error reading {f}: {e}")
    else:
        print(f"File not found: {f}")
