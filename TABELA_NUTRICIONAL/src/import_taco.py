import pandas as pd
from pathlib import Path
import sys

COMMON_NAME_KEYS = ['alimento', 'alimento (nome)', 'nome', 'food', 'food_name']

def choose_best_sheet(xlsx_path):
    sheets = pd.read_excel(xlsx_path, sheet_name=None, nrows=5)
    # escolher sheet com maior número de colunas e que contenha possível coluna de nome
    best = None
    best_score = -1
    for name, df in sheets.items():
        cols = [c.lower().strip() for c in df.columns.astype(str)]
        score = len(cols)
        has_name = any(k in cols for k in COMMON_NAME_KEYS)
        if has_name:
            score += 100
        if score > best_score:
            best = (name, df)
            best_score = score
    return best

def normalize_columns(df):
    cols = list(df.columns)
    mapping = {}
    for c in cols:
        key = c.lower().strip()
        # simplificar acentos e parênteses
        key = key.replace('(', '').replace(')', '')
        # tenta mapear para 'alimento' se contiver palavras-chave
        if any(k in key for k in ['alimento', 'alimento ', 'food', 'nome', 'descri']):
            mapping[c] = 'alimento'
        else:
            mapping[c] = key.replace(' ', '_')
    df = df.rename(columns=mapping)
    return df

def convert_xlsx_to_csv(xlsx_path, out_csv_path):
    xlsx = Path(xlsx_path)
    out = Path(out_csv_path)
    if not xlsx.exists():
        raise FileNotFoundError(f"Arquivo Excel não encontrado: {xlsx}")
    sheet_name, df_sample = choose_best_sheet(xlsx)
    # ler sheet escolhida completa
    df = pd.read_excel(xlsx, sheet_name=sheet_name, engine='openpyxl')
    df = normalize_columns(df)
    # garantir coluna 'alimento' existe
    if 'alimento' not in df.columns:
        # se houver coluna 'food' ou 'nome' já convertidas para food_name etc, pegar primeira coluna textual
        for c in df.columns:
            if df[c].dtype == object:
                df = df.rename(columns={c: 'alimento'})
                break
    # remover linhas totalmente nulas
    df = df.dropna(how='all')
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding='utf-8-sig')
    print(f"✓ Convertido: {xlsx} -> {out} (linhas: {len(df)})")
    return str(out)

if __name__ == "__main__":
    # uso: python -m src.import_taco <path-to-xlsx> [out-csv-path]
    args = sys.argv[1:]
    if not args:
        print("Uso: python src/import_taco.py <Taco-4a-Edicao.xlsx> [taco/taco.csv]")
        sys.exit(1)
    xlsx_path = args[0]
    out = args[1] if len(args) > 1 else "taco/taco.csv"
    convert_xlsx_to_csv(xlsx_path, out)