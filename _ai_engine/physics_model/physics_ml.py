# Physics-Informed ML Model - REAL DATA se train hota hai
# Surface Energy Balance physics + actual satellite measurements

import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os


def calculate_physics_prior(ndvi, ndbi, ndwi):
    """
    Surface Energy Balance se physics-based LST estimate
    Vegetation cooling, built-up heating, water cooling effect
    """
    base_temp = 35.0
    vegetation_cooling = ndvi * 12.0
    builtup_heating = ndbi * 15.0
    water_cooling = max(ndwi, 0) * 10.0

    physics_lst = base_temp - vegetation_cooling + builtup_heating - water_cooling
    return physics_lst


def load_real_data(json_path='../../_data/training_data.json'):
    """REAL satellite data load karo - 50 cities ka actual measured data"""
    with open(json_path, 'r') as f:
        records = json.load(f)
    return records


def build_features(records):
    """Raw drivers + physics prior ko features mein convert karo"""
    X = []
    y = []

    for r in records:
        physics_estimate = calculate_physics_prior(
            ndvi=r['ndvi'],
            ndbi=r['ndbi'],
            ndwi=r['ndwi']
        )

        features = [
            r['ndvi'],
            r['ndbi'],
            r['ndwi'],
            r['bsi'],
            physics_estimate
        ]
        X.append(features)
        y.append(r['lst'])  # actual measured LST - target hai

    return np.array(X), np.array(y)


def train_physics_informed_model(json_path='../../_data/training_data.json'):
    """
    50 real cities ke data se train karo
    Model seekhega: NDVI/NDBI/NDWI/BSI + physics estimate -> actual LST
    """
    records = load_real_data(json_path)
    X, y = build_features(records)

    print(f"Total samples: {len(X)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Model Error (MAE): ±{mae:.2f}°C")

    feature_names = ['NDVI', 'NDBI', 'NDWI', 'BSI', 'Physics estimate']
    print("\nFeature Importance (LST predict karne ke liye):")
    for name, imp in zip(feature_names, model.feature_importances_):
        print(f"  {name}: {imp*100:.1f}%")

    os.makedirs('saved', exist_ok=True)
    joblib.dump(model, 'saved/physics_informed_model.pkl')
    print("\nModel saved (50 real cities se trained)!")

    return model


def predict_lst(model, ndvi, ndbi, ndwi, bsi):
    """Naye location ka LST predict karo"""
    physics_estimate = calculate_physics_prior(ndvi, ndbi, ndwi)
    features = np.array([[ndvi, ndbi, ndwi, bsi, physics_estimate]])
    prediction = model.predict(features)[0]
    return round(prediction, 2)


if __name__ == "__main__":
    print("50 real cities ke data se physics-informed model train kar rahe hain...\n")
    model = train_physics_informed_model()

    print("\nTest - Jaipur ka actual LST predict karo:")
    predicted = predict_lst(model, ndvi=0.139, ndbi=0.016, ndwi=-0.05, bsi=0.15)
    print(f"  Predicted LST: {predicted}°C (actual: 37.93°C)")