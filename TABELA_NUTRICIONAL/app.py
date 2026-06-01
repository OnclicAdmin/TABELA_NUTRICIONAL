from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from src.loader import TacoLoader
from src.normalizer import Normalizer
from src.matcher import Matcher
from src.calculator import Calculator
from src.rd429 import RD429Formatter
import os
import math
import traceback
from datetime import datetime

app = Flask(__name__)
CORS(app)

taco_path = os.getenv("TACO_PATH", "taco/taco.csv")

def sanitize_json(value):
    if isinstance(value, dict):
        return {k: sanitize_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_json(v) for v in value]
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    return value

try:
    taco = TacoLoader(taco_path)
    normalizer = Normalizer()
    matcher = Matcher(taco)
    calculator = Calculator(taco)
    formatter = RD429Formatter()
except Exception as e:
    app.logger.error(f"Erro ao inicializar módulos: {e}")
    app.logger.error(traceback.format_exc())
    raise

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/calculate", methods=["POST"])
def calculate():
    try:
        payload = request.json or {}
        product_name = payload.get("product_name", "Produto")
        serving_type = payload.get("serving_type", "100g")
        ingredients = payload.get("ingredients", [])

        if not ingredients:
            return jsonify({"error": "Nenhum ingrediente fornecido"}), 400

        normalized = []
        for ing in ingredients:
            try:
                norm = normalizer.to_grams(ing.get("name"), ing.get("quantity"), ing.get("unit"))
                normalized.append(norm)
            except Exception as e:
                return jsonify({"error": f"Erro ao normalizar '{ing.get('name')}': {e}"}), 400

        if not normalized:
            return jsonify({"error": "Não foi possível normalizar nenhum ingrediente"}), 400

        matches = [matcher.best_match(norm["name"]) for norm in normalized]
        result = calculator.compute_recipe(normalized, matches, ingredients)
        formatted = formatter.format_table(result, serving_type)

        response = {
            "product_name": product_name,
            "portion": formatted["portion"],
            "servings_per_package": formatted["servings_per_package"],
            "total_weight_grams": result.get("total_weight", 0) or 0,
            "ingredients_used": [
                {
                    "original": ingredients[i]["name"],
                    "matched": matches[i]["match"],
                    "match_score": matches[i]["score"],
                    "quantity_grams": normalized[i]["grams"] or 0
                }
                for i in range(len(ingredients))
            ],
            "nutrition_table": formatted["rows"],
            "highlights": formatted["highlights"]
        }

        return jsonify(sanitize_json(response)), 200

    except Exception as e:
        tb = traceback.format_exc()
        app.logger.error(tb)
        return jsonify({"error": str(e), "trace": tb}), 500

@app.route("/api/search-ingredient", methods=["GET"])
def search_ingredient():
    query = request.args.get("q", "")
    if len(query) < 1:
        return jsonify([]), 200
    try:
        results = matcher.search_suggestions(query, limit=10)
        return jsonify(results), 200
    except Exception as e:
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
