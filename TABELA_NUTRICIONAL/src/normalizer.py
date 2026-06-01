from pint import UnitRegistry

class Normalizer:
    """Normaliza unidades para gramas/ml"""
    
    # Mapa de conversão para ingredientes que usam unidades volumétricas
    DENSITY_MAP = {
        'farinha': 0.59,
        'açúcar': 0.80,
        'sal': 1.20,
        'óleo': 0.92,
        'azeite': 0.92,
        'leite': 1.03,
        'água': 1.00,
        'mel': 1.40,
        'manteiga': 0.96,
        'sorvete': 0.54,
    }
    
    # Mapa de unidades customizadas (colher, xícara, etc)
    CUSTOM_UNITS = {
        'colher': 15,  # ml
        'colher de chá': 5,  # ml
        'xícara': 240,  # ml
        'copo': 250,  # ml
        'tigela': 500,  # ml
        'pitada': 0.5,  # g (aproximado)
    }
    
    def __init__(self):
        self.ureg = UnitRegistry()
        self.ureg.define('colher = 15 * milliliter')
        self.ureg.define('colher_cha = 5 * milliliter')
        self.ureg.define('xicara = 240 * milliliter')
        self.ureg.define('copo = 250 * milliliter')
    
    def to_grams(self, ingredient_name, quantity, unit):
        """
        Converte quantidade de qualquer unidade para gramas
        
        Args:
            ingredient_name: Nome do ingrediente
            quantity: Quantidade (número)
            unit: Unidade (g, kg, ml, colher, xícara, etc)
        
        Returns:
            {"name": str, "grams": float}
        """
        try:
            quantity = float(quantity)
        except (ValueError, TypeError):
            raise ValueError(f"Quantidade inválida: {quantity}")
        
        unit = str(unit).lower().strip()
        
        # Tentar com pint primeiro (g, kg, mg, ml, l)
        try:
            q = self.ureg.Quantity(quantity, unit)
            if 'gram' in str(q.units) or 'kilogram' in str(q.units):
                grams = q.to('gram').magnitude
            elif 'liter' in str(q.units) or 'milliliter' in str(q.units):
                # Se for volume, estimar densidade
                ml = q.to('milliliter').magnitude
                density = self._get_density(ingredient_name)
                grams = ml * density
            else:
                grams = quantity
        except Exception:
            # Fallback: usar mapa customizado
            if unit in self.CUSTOM_UNITS:
                ml = quantity * self.CUSTOM_UNITS[unit]
                density = self._get_density(ingredient_name)
                grams = ml * density
            else:
                # Se nada funcionar, assumir como gramas
                grams = quantity
        
        return {
            "name": ingredient_name,
            "grams": round(grams, 2),
            "original_unit": unit
        }
    
    def _get_density(self, ingredient_name):
        """Retorna densidade estimada do ingrediente em g/ml"""
        ing_lower = ingredient_name.lower()
        for key, density in self.DENSITY_MAP.items():
            if key in ing_lower:
                return density
        return 1.0  # Padrão: água