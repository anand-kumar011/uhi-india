# Cooling Scenario Generator
# Pre-defined "what-if" scenarios for common intervention types
# Each scenario uses the physics-informed model to predict cooling effect

import sys
import os
sys.path.append(os.path.abspath('../physics_model'))
sys.path.append(os.path.abspath('../simulation'))

from physics_ml import train_physics_informed_model, predict_lst
from simulate import derive_cooling_efficiency


SCENARIOS = {
    'A': {
        'name': 'Urban Greening',
        'description': 'Increase tree canopy and vegetation cover',
        'ndvi_increase': 0.20,
        'ndbi_change': 0,
        'ndwi_change': 0
    },
    'B': {
        'name': 'Cool Roofs',
        'description': 'Increase roof reflectivity (albedo 0.2 to 0.7)',
        'ndvi_increase': 0,
        'ndbi_change': -0.08,
        'ndwi_change': 0
    },
    'C': {
        'name': 'Green Roofs',
        'description': 'Vegetated rooftops increasing evapotranspiration',
        'ndvi_increase': 0.10,
        'ndbi_change': -0.03,
        'ndwi_change': 0
    },
    'D': {
        'name': 'Water Bodies',
        'description': 'Introduce urban ponds and blue corridors',
        'ndvi_increase': 0,
        'ndbi_change': 0,
        'ndwi_change': 0.15
    },
    'E': {
        'name': 'Hybrid Intervention',
        'description': 'Combination: tree cover + cool roofs + water features',
        'ndvi_increase': 0.15,
        'ndbi_change': -0.06,
        'ndwi_change': 0.05
    }
}


def run_scenario(scenario_key, baseline_drivers, physics_model=None):
    """
    Ek named scenario chalao (A-E) aur predicted LST reduction do

    baseline_drivers = {'ndvi': x, 'ndbi': y, 'ndwi': z, 'bsi': w}
    """
    if scenario_key not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_key}. Use A, B, C, D, or E")

    scenario = SCENARIOS[scenario_key]

    if physics_model is None:
        physics_model = train_physics_informed_model()

    baseline_lst = predict_lst(
        physics_model,
        baseline_drivers['ndvi'],
        baseline_drivers['ndbi'],
        baseline_drivers['ndwi'],
        baseline_drivers['bsi']
    )

    new_ndvi = baseline_drivers['ndvi'] + scenario['ndvi_increase']
    new_ndbi = baseline_drivers['ndbi'] + scenario['ndbi_change']
    new_ndwi = baseline_drivers['ndwi'] + scenario['ndwi_change']

    scenario_lst = predict_lst(
        physics_model,
        new_ndvi,
        new_ndbi,
        new_ndwi,
        baseline_drivers['bsi']
    )

    reduction = round(baseline_lst - scenario_lst, 2)
    reduction = max(0, reduction)

    return {
        'scenario': scenario_key,
        'name': scenario['name'],
        'description': scenario['description'],
        'baseline_lst': baseline_lst,
        'scenario_lst': round(baseline_lst - reduction, 2),
        'cooling_effect': reduction
    }


def run_all_scenarios(baseline_drivers, physics_model=None):
    """Saare 5 scenarios ek saath chalao, comparison ke liye"""
    if physics_model is None:
        physics_model = train_physics_informed_model()

    results = []
    for key in SCENARIOS.keys():
        result = run_scenario(key, baseline_drivers, physics_model)
        results.append(result)

    results.sort(key=lambda x: x['cooling_effect'], reverse=True)
    return results


if __name__ == "__main__":
    print("Training physics model...")
    model = train_physics_informed_model()

    jaipur_drivers = {
        'ndvi': 0.139,
        'ndbi': 0.016,
        'ndwi': -0.168,
        'bsi': 0.244
    }

    print("\nRunning all 5 cooling scenarios for Jaipur:\n")
    results = run_all_scenarios(jaipur_drivers, model)

    for r in results:
        print(f"Scenario {r['scenario']} - {r['name']}")
        print(f"  {r['description']}")
        print(f"  Baseline LST: {r['baseline_lst']}°C -> Scenario LST: {r['scenario_lst']}°C")
        print(f"  Cooling effect: -{r['cooling_effect']}°C\n")