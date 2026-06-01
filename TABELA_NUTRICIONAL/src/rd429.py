class RD429Formatter:
    """Formata tabela nutricional conforme RDC 429 ANVISA"""
    
    # Valores de Referência Diária (VRD) - RDC 429
    VRD_VALUES = {
        "energy_kcal": 2000,
        "carbohydrate": 300,
        "protein": 50,
        "total_fat": 78,
        "saturated_fat": 20,
        "trans_fat": None,
        "fiber": 25,
        "sodium": 2400,
        "sugars": None
    }
    
    # Limite de destaque para alertas
    HIGHLIGHT_THRESHOLDS = {
        "sugars": 15,
        "saturated_fat": 4,
        "sodium": 300
    }
    
    # Definições dos nutrientes
    NUTRIENT_DEFINITIONS = [
        {"key": "energy_kcal", "label": "Valor energético", "unit": "kcal"},
        {"key": "energy_kj", "label": "Valor energético", "unit": "kJ"},
        {"key": "carbohydrate", "label": "Carboidratos", "unit": "g"},
        {"key": "sugars", "label": "Açúcares totais", "unit": "g"},
        {"key": "protein", "label": "Proteínas", "unit": "g"},
        {"key": "total_fat", "label": "Gorduras totais", "unit": "g"},
        {"key": "saturated_fat", "label": "Gorduras saturadas", "unit": "g"},
        {"key": "trans_fat", "label": "Gorduras trans", "unit": "g"},
        {"key": "fiber", "label": "Fibra alimentar", "unit": "g"},
        {"key": "sodium", "label": "Sódio", "unit": "mg", "multiplier": 1000},
    ]
    
    def format_table(self, calculation_result, serving_type="100g", servings_per_package=None):
        """
        Formata resultado do cálculo conforme RDC 429
        
        Args:
            calculation_result: Dict com nutrientes totais
            serving_type: "100g" ou "100ml"
            servings_per_package: Número de porções por embalagem
        
        Returns:
            Dict{
                "portion": str,
                "servings_per_package": int,
                "rows": List[{
                    "nutrient": str,
                    "value_per_serving": float,
                    "unit": str,
                    "daily_value_percent": float or None,
                    "mandatory": bool
                }],
                "highlights": List[str]
            }
        """
        total_weight = calculation_result.get("total_weight", 0) or 0
        nutrients = calculation_result.get("nutrients", {}) or {}
        proportion = 100 / total_weight if total_weight > 0 else 0

        rows = []
        for nutrient_def in self.NUTRIENT_DEFINITIONS:
            key = nutrient_def["key"]
            label = nutrient_def["label"]
            unit = nutrient_def["unit"]
            multiplier = nutrient_def.get("multiplier", 1)

            value = (nutrients.get(key, 0) or 0) * proportion * multiplier
            display_value = self._round_label(value, key)
            vd = self._calculate_vd_percent(key, value)

            rows.append({
                "nutrient": label,
                "value_per_serving": display_value,
                "unit": unit,
                "daily_value_percent": vd,
                "mandatory": key in self.VRD_VALUES
            })

        highlights = self._build_highlights(nutrients, proportion)

        return {
            "portion": serving_type,
            "servings_per_package": servings_per_package,
            "rows": rows,
            "highlights": highlights
        }

    def _calculate_vd_percent(self, nutrient_key, value):
        """Calcula %VD conforme RDC 429"""
        vrd = self.VRD_VALUES.get(nutrient_key)
        if vrd is None:
            return None
        percent = (value / vrd) * 100
        return round(percent, 0) if percent >= 5 else None  # %VD só se >= 5%
    
    def _round_label(self, value, nutrient_key):
        """
        Arredonda o valor para exibição
        """
        if nutrient_key in ["energy_kcal", "energy_kj"]:
            return round(value / 5) * 5
        if nutrient_key in ["protein", "carbohydrate", "total_fat", "saturated_fat", "trans_fat"]:
            return round(value, 1) if value < 5 else round(value, 0)
        if nutrient_key == "fiber":
            return round(value, 1) if value < 1 else round(value, 0)
        if nutrient_key == "sodium":
            return round(value, 0)
        return round(value, 2)

    def _build_highlights(self, nutrients, proportion):
        labels = []
        sugars = (nutrients.get("sugars", 0) or 0) * proportion
        saturated = (nutrients.get("saturated_fat", 0) or 0) * proportion
        sodium = (nutrients.get("sodium", 0) or 0) * proportion * 1000

        if sugars >= self.HIGHLIGHT_THRESHOLDS["sugars"]:
            labels.append("Alto teor de açúcares")
        if saturated >= self.HIGHLIGHT_THRESHOLDS["saturated_fat"]:
            labels.append("Alto teor de gorduras saturadas")
        if sodium >= self.HIGHLIGHT_THRESHOLDS["sodium"]:
            labels.append("Alto teor de sódio")

        return labels