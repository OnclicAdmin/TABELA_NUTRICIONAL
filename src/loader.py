import pandas as pd
import os
import unicodedata
from pathlib import Path

def normalize_text(value: str) -> str:
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.replace("(", "").replace(")", "").replace("%", "").replace(":", "")
    text = text.replace("/", "_").replace("-", "_").replace(" ", "_")
    while "__" in text:
        text = text.replace("__", "_")
    return text.strip("_")

def build_header_from_rows(header_df: pd.DataFrame) -> list[str]:
    columns = []
    header_df = header_df.fillna("").astype(str)
    for col in range(header_df.shape[1]):
        parts = []
        for row in range(header_df.shape[0]):
            value = header_df.iat[row, col].strip()
            if value and "unnamed" not in value.lower():
                parts.append(normalize_text(value))
        if not parts:
            parts = [f"col_{col}"]
        columns.append("_".join(parts))
    return columns

class TacoLoader:
    def __init__(self, csv_path: str | None = None):
        project_root = Path(__file__).resolve().parent.parent
        tried = []

        if csv_path:
            p = Path(csv_path)
            if not p.is_absolute():
                p = (project_root / csv_path).resolve()
            tried.append(str(p))
            if p.exists():
                return self._load(str(p))

        env_path = os.getenv("TACO_PATH")
        if env_path:
            p = Path(env_path)
            if not p.is_absolute():
                p = (project_root / env_path).resolve()
            tried.append(str(p))
            if p.exists():
                return self._load(str(p))

        default_csv = project_root / "taco" / "taco.csv"
        tried.append(str(default_csv))
        if default_csv.exists():
            return self._load(str(default_csv))

        for candidate in project_root.rglob("*taco*.csv"):
            tried.append(str(candidate))
            if candidate.exists():
                return self._load(str(candidate))

        raise FileNotFoundError(
            "Arquivo TACO não encontrado.\n"
            f"Locais verificados: {tried}\n\n"
            "Coloque taco.csv em taco/taco.csv ou defina TACO_PATH."
        )

    def _read_raw(self, path: str) -> pd.DataFrame:
        raw = pd.read_csv(path, header=None, encoding="utf-8-sig", low_memory=False)
        if raw.shape[0] >= 3:
            header_df = raw.iloc[:3, :]
            cols = build_header_from_rows(header_df)
            data = raw.iloc[3:, :].copy()
            data.columns = cols
        else:
            data = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
            data.columns = [normalize_text(c) for c in data.columns]
        return data

    def _load(self, path: str):
        self.path = path
        raw_df = self._read_raw(path)
        self.df = self._prepare_dataframe(raw_df)
        self.food_col = self._detect_food_column()
        self.df["__food_norm"] = self.df[self.food_col].astype(str).map(normalize_text)
        print(f"✓ TACO carregado: {len(self.df)} registros ({self.path})")
        print(f"  Colunas: {list(self.df.columns)}")
        print(f"  Coluna usada como nome: {self.food_col}")
        return None

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(how="all").reset_index(drop=True)

        if "descricao_dos_alimentos" in df.columns:
            df = df[df["descricao_dos_alimentos"].astype(str).str.strip() != ""]
        else:
            first_text_col = df.select_dtypes(include="object").columns[:1]
            if len(first_text_col) > 0:
                df = df[df[first_text_col[0]].astype(str).str.strip() != ""]

        df = df.dropna(how="all", axis=1)
        df = df.reset_index(drop=True)
        return df

    def _detect_food_column(self) -> str:
        if "descricao_dos_alimentos" in self.df.columns:
            return "descricao_dos_alimentos"
        for col in self.df.columns:
            norm = normalize_text(col)
            if "descricao" in norm or "descr" in norm or "food" in norm or "nome" in norm:
                return col
        return self.df.columns[0]

    def get_all_foods(self):
        return self.df[self.food_col].astype(str).unique().tolist()

    def search(self, query: str):
        query_norm = normalize_text(query)
        mask = self.df["__food_norm"].str.contains(query_norm, na=False)
        return self.df[mask]

    def get_by_index(self, idx):
        return self.df.iloc[idx].to_dict()

    def get_nutrients(self, food_name: str):
        if not food_name:
            return None
        query_norm = normalize_text(food_name)
        exact = self.df[self.df["__food_norm"] == query_norm]
        if not exact.empty:
            return exact.iloc[0].to_dict()
        contains = self.df[self.df["__food_norm"].str.contains(query_norm, na=False)]
        if not contains.empty:
            return contains.iloc[0].to_dict()
        try:
            from rapidfuzz import process, fuzz
            match = process.extractOne(query_norm, self.df["__food_norm"].tolist(), scorer=fuzz.WRatio)
            if match and match[1] >= 60:
                found = self.df[self.df["__food_norm"] == match[0]]
                if not found.empty:
                    return found.iloc[0].to_dict()
        except Exception:
            pass
        return None