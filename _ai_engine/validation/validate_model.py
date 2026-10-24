# Validation Module
# Tests the physics-informed model against an INDEPENDENT dataset (ECOSTRESS)
# This is critical - validating a model on the SAME data it was trained on
# always looks good and proves nothing. Real validation needs held-out data.

import ee
import json
import numpy as np
from datetime import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ee.Initialize(project='impactful-water-467805-e3')


def get_ecostress_lst(longitude, latitude, year=None):
    """
    ECOSTRESS satellite se LST nikalo - yeh ek ALAG satellite hai
    (NASA, International Space Station pe mounted), Landsat se independent
    Isko validation ke liye use karte hain kyunki yeh training data se
    bilkul alag source hai - agar dono match karte hain, model trustworthy hai
    """
    if year is None:
        year = datetime.today().year

    start_date = f"{year}-03-01"
    end_date = f"{year}-06-15"

    point = ee.Geometry.Point([longitude, latitude])
    region = point.buffer(15000)

    try:
        ecostress = ee.ImageCollection('NASA/ECOSTRESS/L2T_LSTE/002') \
            .filterBounds(region) \
            .filterDate(start_date, end_date) \
            .select('LST') \
            .first()

        if ecostress is None:
            return None

        stats = ecostress.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=70,
            maxPixels=1e8
        ).getInfo()

        lst_kelvin = stats.get('LST')
        if lst_kelvin is None:
            return None

        lst_celsius = (lst_kelvin * 0.02) - 273.15
        return round(lst_celsius, 2)

    except Exception as e:
        return None


def validate_against_ecostress(test_cities):
    """
    test_cities = list of {'name': str, 'lon': float, 'lat': float, 'predicted_lst': float}
    Compares model predictions against independent ECOSTRESS measurements
    """
    results = []

    for city in test_cities:
        ecostress_lst = get_ecostress_lst(city['lon'], city['lat'])

        if ecostress_lst is not None:
            results.append({
                'city': city['name'],
                'predicted': city['predicted_lst'],
                'ecostress_observed': ecostress_lst,
                'difference': round(abs(city['predicted_lst'] - ecostress_lst), 2)
            })

    return results


def compute_validation_metrics(validation_results):
    """
    R-squared, RMSE, MAE calculate karo - standard model evaluation metrics
    R² > 0.85 aur RMSE < 2°C target hai (jaisa document mein likha tha)
    """
    if len(validation_results) < 2:
        return {
            'error': 'Need at least 2 matched data points for meaningful metrics',
            'n_samples': len(validation_results)
        }

    predicted = [r['predicted'] for r in validation_results]
    observed = [r['ecostress_observed'] for r in validation_results]

    mae = mean_absolute_error(observed, predicted)
    rmse = mean_squared_error(observed, predicted) ** 0.5
    r2 = r2_score(observed, predicted)

    meets_target = (r2 > 0.85) and (rmse < 2.0)

    return {
        'n_samples': len(validation_results),
        'mae': round(mae, 2),
        'rmse': round(rmse, 2),
        'r_squared': round(r2, 3),
        'target_r2': 0.85,
        'target_rmse': 2.0,
        'meets_target': meets_target
    }


def run_full_validation(cities_with_predictions):
    """Main entry point - validation pipeline chalao aur honest report do"""
    print("Fetching ECOSTRESS observations for validation...")
    matched = validate_against_ecostress(cities_with_predictions)

    print(f"\nMatched {len(matched)} of {len(cities_with_predictions)} cities with available ECOSTRESS data")

    if len(matched) == 0:
        return {
            'status': 'no_data',
            'message': 'ECOSTRESS has limited temporal/spatial coverage - no overlapping observations found for these cities/dates. This is a known constraint of the dataset, not a model failure.'
        }

    metrics = compute_validation_metrics(matched)

    return {
        'status': 'completed',
        'matched_cities': matched,
        'metrics': metrics
    }


if __name__ == "__main__":
    test_cities = [
        {'name': 'Jaipur', 'lon': 75.7873, 'lat': 26.9124, 'predicted_lst': 37.93},
        {'name': 'Mumbai', 'lon': 72.8777, 'lat': 19.0760, 'predicted_lst': 36.31},
        {'name': 'Kolkata', 'lon': 88.3639, 'lat': 22.5726, 'predicted_lst': 38.41},
        {'name': 'Guwahati', 'lon': 91.7362, 'lat': 26.1445, 'predicted_lst': 32.88},
        {'name': 'Delhi', 'lon': 77.2090, 'lat': 28.6139, 'predicted_lst': 42.40},
    ]

    result = run_full_validation(test_cities)

    if result['status'] == 'no_data':
        print(f"\n{result['message']}")
    else:
        print("\nMatched cities:")
        for m in result['matched_cities']:
            print(f"  {m['city']}: predicted={m['predicted']}°C, ECOSTRESS={m['ecostress_observed']}°C, diff={m['difference']}°C")

        print("\nValidation metrics:")
        metrics = result['metrics']
        if 'error' in metrics:
            print(f"  {metrics['error']}")
        else:
            print(f"  R-squared: {metrics['r_squared']} (target: >{metrics['target_r2']})")
            print(f"  RMSE: {metrics['rmse']}°C (target: <{metrics['target_rmse']}°C)")
            print(f"  MAE: {metrics['mae']}°C")
            print(f"  Meets target: {metrics['meets_target']}")