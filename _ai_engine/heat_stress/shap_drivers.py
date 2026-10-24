# SHAP Driver Analysis Module
# Explainable AI - tells you EXACTLY how much each factor
# (vegetation, buildings, water, bare soil) contributes to heat
# This is more rigorous than simple correlation - it accounts for
# interactions between features, not just one-at-a-time relationships

import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


def load_training_data(json_path='../../_data/training_data.json'):
    """Real satellite data load karo - 47 cities ka actual measured data"""
    with open(json_path, 'r') as f:
        records = json.load(f)

    X = []
    y = []
    for r in records:
        X.append([r['ndvi'], r['ndbi'], r['ndwi'], r['bsi']])
        y.append(r['lst'])

    return np.array(X), np.array(y)


def train_explainable_model(json_path='../../_data/training_data.json'):
    """
    Random Forest train karo - yeh wahi model hai jo LST predict karta hai,
    lekin ab humne SHAP wrapper add kiya hai isko explain karne ke liye
    """
    X, y = load_training_data(json_path)

    model = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42)
    model.fit(X, y)

    os.makedirs('saved', exist_ok=True)
    joblib.dump(model, 'saved/shap_model.pkl')

    return model, X


def calculate_shap_importance(model, X):
    """
    SHAP values calculate karo - har feature ka exact contribution
    Returns: percentage contribution of each driver to LST
    """
    feature_names = ['Vegetation (NDVI)', 'Built-up (NDBI)', 'Water (NDWI)', 'Bare soil (BSI)']

    if not SHAP_AVAILABLE:
        importances = model.feature_importances_
        total = sum(importances)
        result = {}
        for name, imp in zip(feature_names, importances):
            result[name] = round((imp / total) * 100, 1)
        return result, 'fallback (feature_importances_, SHAP library not installed)'

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    total = mean_abs_shap.sum()

    result = {}
    for name, val in zip(feature_names, mean_abs_shap):
        result[name] = round((val / total) * 100, 1)

    result = dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    return result, 'SHAP TreeExplainer'


def get_driver_contribution(city_ndvi, city_ndbi, city_ndwi, city_bsi, model=None, training_X=None):
    """
    Ek specific city ke liye driver contribution nikalo
    Yeh poore dataset ka average pattern + is city ke specific values dono use karta hai
    """
    if model is None or training_X is None:
        model, training_X = train_explainable_model()

    global_importance, method = calculate_shap_importance(model, training_X)

    if SHAP_AVAILABLE:
        explainer = shap.TreeExplainer(model)
        city_features = np.array([[city_ndvi, city_ndbi, city_ndwi, city_bsi]])
        city_shap = explainer.shap_values(city_features)[0]

        feature_names = ['Vegetation (NDVI)', 'Built-up (NDBI)', 'Water (NDWI)', 'Bare soil (BSI)']
        total_abs = np.abs(city_shap).sum()

        city_specific = {}
        for name, val in zip(feature_names, city_shap):
            pct = round((abs(val) / total_abs) * 100, 1) if total_abs > 0 else 0
            direction = 'increases heat' if val > 0 else 'decreases heat'
            city_specific[name] = {'contribution_pct': pct, 'effect': direction}

        return {
            'global_pattern': global_importance,
            'this_city': city_specific,
            'method': method
        }

    return {
        'global_pattern': global_importance,
        'this_city': None,
        'method': method
    }


if __name__ == "__main__":
    print("Training explainable model on real 47-city dataset...")
    model, X = train_explainable_model()

    print("\nGlobal driver importance (across all cities):")
    importance, method = calculate_shap_importance(model, X)
    for driver, pct in importance.items():
        print(f"  {driver}: {pct}%")
    print(f"\nMethod used: {method}")

    print("\n--- Jaipur-specific analysis ---")
    result = get_driver_contribution(
        city_ndvi=0.139, city_ndbi=0.016, city_ndwi=-0.168, city_bsi=0.244,
        model=model, training_X=X
    )
    if result['this_city']:
        for driver, info in result['this_city'].items():
            print(f"  {driver}: {info['contribution_pct']}% ({info['effect']})")