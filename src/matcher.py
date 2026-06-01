from rapidfuzz import process, fuzz
from src.loader import normalize_text

class Matcher:
    """Encontra correspondências fuzzy entre ingredientes e TACO"""
    
    def __init__(self, taco_loader):
        self.taco = taco_loader
        self.food_items = taco_loader.df[taco_loader.food_col].astype(str).tolist()
        self.food_norm = [normalize_text(item) for item in self.food_items]
        self.norm_to_original = {
            normalize_text(item): item
            for item in self.food_items
        }

    def best_match(self, ingredient_name, threshold=60):
        """
        Encontra melhor correspondência para um ingrediente
        
        Args:
            ingredient_name: Nome do ingrediente a buscar
            threshold: Score mínimo aceitável (0-100)
        
        Returns:
            {
                "query": str,
                "match": str,
                "score": int,
                "confidence": "alta|média|baixa"
            }
        """
        if not ingredient_name or not isinstance(ingredient_name, str):
            return {"query": str(ingredient_name), "match": None, "score": 0, "confidence": "nula"}

        query = ingredient_name.strip()
        query_norm = normalize_text(query)

        for original, normalized in zip(self.food_items, self.food_norm):
            if query_norm in normalized:
                return {"query": query, "match": original, "score": 100, "confidence": "alta"}

        match = process.extractOne(query_norm, self.food_norm, scorer=fuzz.WRatio, score_cutoff=threshold)
        if match:
            normalized_match = match[0]
            score = int(match[1])
            original = self.norm_to_original.get(normalized_match, normalized_match)
            confidence = "alta" if score >= 90 else "média" if score >= 75 else "baixa"
            return {"query": query, "match": original, "score": score, "confidence": confidence}

        return {"query": query, "match": None, "score": 0, "confidence": "nula"}

    def search_suggestions(self, query, limit=5):
        """Retorna top N sugestões de alimentos"""
        if not query:
            return []
        query_norm = normalize_text(query)
        results = []

        for original, normalized in zip(self.food_items, self.food_norm):
            if query_norm in normalized:
                results.append({"food": original, "score": 100})
                if len(results) >= limit:
                    return results

        fuzzy = process.extract(query_norm, self.food_norm, scorer=fuzz.WRatio, limit=limit * 3)
        for normalized_match, score, _ in fuzzy:
            original = self.norm_to_original.get(normalized_match, normalized_match)
            if score >= 50 and all(food["food"] != original for food in results):
                results.append({"food": original, "score": int(score)})
            if len(results) >= limit:
                break

        return results[:limit]