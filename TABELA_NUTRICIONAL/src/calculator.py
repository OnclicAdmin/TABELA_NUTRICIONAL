import pandas as pd
from src.loader import normalize_text

class Calculator:
    """Calcula nutrientes da receita agregando ingredientes"""
    
    # Mapa de colunas nutricionais esperadas na TACO
    NUTRIENT_COLUMNS = {
        "energy_kcal": ["energia_kcal", "energia_kcal", "kcal", "energia"],
        "energy_kj": ["energia_kj", "energia_kj", "kj"],
        "protein": ["proteina", "proteina_bruta", "protein"],
        "total_fat": ["lipidios", "lipidios_total", "gordura_total", "fat"],
        "saturated_fat": ["acido_graxo_saturado", "gordura_saturada", "saturated_fat"],
        "trans_fat": ["acido_graxo_trans", "gordura_trans", "trans_fat"],
        "carbohydrate": ["carboidrato", "carbo_idrato", "carbo", "carboidratos"],
        "fiber": ["fibra_alimentar", "fibra", "fiber"],
        "sodium": ["sodio", "sodium"],
        "sugars": ["acucar", "acucar_total", "sugars", "sugar"]
    }
    
    def __init__(self, taco_loader):
        self.taco = taco_loader
        self._detect_columns()

    def _detect_columns(self):
        self.mapped_columns = {}
        normalized_cols = {col: normalize_text(col) for col in self.taco.df.columns}
        for nutrient, aliases in self.NUTRIENT_COLUMNS.items():
            for col, normalized in normalized_cols.items():
                if any(alias in normalized for alias in aliases):
                    self.mapped_columns[nutrient] = col
                    break
        print(f"✓ Colunas detectadas: {self.mapped_columns}")

    def compute_recipe(self, normalized_ingredients, matches, original_ingredients):
        """
        Calcula nutrientes agregados da receita
        
        Args:
            normalized_ingredients: List[{"name": str, "grams": float}]
            matches: List[{"query": str, "match": str, "score": int}]
            original_ingredients: List original com detalhes
        
        Returns:
            {
                "total_weight": float,
                "nutrients": {nutrient: value},
                "ingredient_breakdown": []
            }
        """
        total_nutrients = {}
        total_weight = 0.0
        ingredient_breakdown = []

        for norm, match, orig in zip(normalized_ingredients, matches, original_ingredients):
            weight_g = norm["grams"]
            total_weight += weight_g
            ing_nutrients = {}

            if not match["match"]:
                ingredient_breakdown.append({
                    "ingredient": norm["name"],
                    "matched": None,
                    "weight_g": weight_g,
                    "match_score": 0,
                    "nutrients": {}
                })
                continue

            food_composition = self.taco.get_nutrients(match["match"])
            if food_composition is None:
                ingredient_breakdown.append({
                    "ingredient": norm["name"],
                    "matched": match["match"],
                    "weight_g": weight_g,
                    "match_score": match["score"],
                    "nutrients": {}
                })
                continue

            for nutrient, col in self.mapped_columns.items():
                try:
                    value_per_100g = float(food_composition.get(col, 0) or 0)
                except (ValueError, TypeError):
                    value_per_100g = 0.0
                scaled_value = (value_per_100g * weight_g) / 100.0
                ing_nutrients[nutrient] = round(scaled_value, 2)
                total_nutrients[nutrient] = total_nutrients.get(nutrient, 0.0) + scaled_value

            ingredient_breakdown.append({
                "ingredient": norm["name"],
                "matched": match["match"],
                "weight_g": weight_g,
                "match_score": match["score"],
                "nutrients": ing_nutrients
            })

        return {
            "total_weight": round(total_weight, 2),
            "nutrients": {k: round(v, 2) for k, v in total_nutrients.items()},
            "ingredient_breakdown": ingredient_breakdown
        }