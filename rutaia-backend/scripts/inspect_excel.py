import pandas as pd
import sys

try:
    df = pd.read_excel(r'C:\Proyectos\asesor\lista y categorias.xlsx', sheet_name=None)
    for sheet_name, data in df.items():
        print(f"\n{'='*60}")
        print(f"Sheet: {sheet_name}")
        print(f"Rows: {len(data)}")
        print(f"Columns: {data.columns.tolist()}")
        print(f"\nDtypes:\n{data.dtypes}")
        print(f"\nFirst 3 rows:")
        pd.set_option('display.max_colwidth', 60)
        pd.set_option('display.width', 200)
        print(data.head(3).to_string())
        print(f"\nUnique 'categoria' values: {data['categoria'].unique().tolist() if 'categoria' in data.columns else 'N/A'}")
except Exception as e:
    import traceback
    traceback.print_exc()
