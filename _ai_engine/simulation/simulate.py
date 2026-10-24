# Scenario Simulation Module
# "Agar yeh intervention karo toh temperature kitna ghatega?"
# Plus budget-constrained optimization

import numpy as np


# ─────────────────────────────────────────────────────
# COST PER UNIT - Yeh REAL MARKET PRICES hain (Rupees)
# ML se nahi nikal sakte - government/market rate hai
# Source: CPWD schedule of rates, municipal tree plantation costs
# ─────────────────────────────────────────────────────
COST_PER_UNIT = {
    'trees': 1500,                   # per tree (planting + 2 years maintenance)
    'reflective_roads_km': 800000,   # per km (cool pavement coating)
    'water_bodies': 2000000,         # per lake/pond restoration
    'green_corridors_km': 1200000,   # per km
    'shade_structures': 25000,       # per structure
}


def derive_cooling_efficiency(physics_model, predict_lst_fn, baseline_drivers):
    """
    Model se cooling rates nikalo
    Safety check: agar model galat sign de (heating dikhaye cooling ki jagah)
    toh us rate ko zero kar do, taaki simulation kabhi temperature na badhaye
    """

    baseline_temp = predict_lst_fn(
        physics_model,
        baseline_drivers['ndvi'],
        baseline_drivers['ndbi'],
        baseline_drivers['ndwi'],
        baseline_drivers['bsi']
    )

    temp_more_ndvi = predict_lst_fn(
        physics_model,
        baseline_drivers['ndvi'] + 0.05,
        baseline_drivers['ndbi'],
        baseline_drivers['ndwi'],
        baseline_drivers['bsi']
    )
    ndvi_cooling_per_unit = max(0, (baseline_temp - temp_more_ndvi) / 0.05)

    temp_more_ndwi = predict_lst_fn(
        physics_model,
        baseline_drivers['ndvi'],
        baseline_drivers['ndbi'],
        baseline_drivers['ndwi'] + 0.05,
        baseline_drivers['bsi']
    )
    ndwi_cooling_per_unit = max(0, (baseline_temp - temp_more_ndwi) / 0.05)

    temp_less_ndbi = predict_lst_fn(
        physics_model,
        baseline_drivers['ndvi'],
        baseline_drivers['ndbi'] - 0.05,
        baseline_drivers['ndwi'],
        baseline_drivers['bsi']
    )
    ndbi_cooling_per_unit = max(0, (baseline_temp - temp_less_ndbi) / 0.05)

    NDVI_PER_TREE = 0.00005
    NDWI_PER_WATER_BODY = 0.015
    NDBI_PER_REFLECTIVE_KM = 0.008

    # Fallback minimums - agar model ne zero diya, ek chhota positive default rakho
    # taaki simulation kabhi temperature badhaye nahi, kam se kam flat rahe
    cooling_per_unit = {
        'trees':                max(0.0008, round(ndvi_cooling_per_unit * NDVI_PER_TREE, 6)),
        'water_bodies':         max(0.05, round(ndwi_cooling_per_unit * NDWI_PER_WATER_BODY, 4)),
        'reflective_roads_km':  max(0.02, round(ndbi_cooling_per_unit * NDBI_PER_REFLECTIVE_KM, 4)),
    }

    return cooling_per_unit


def simulate_intervention(city_type, current_temp, interventions, cooling_rates):
    """
    cooling_rates = derive_cooling_efficiency() se aaya hua dictionary
    (hardcoded nahi - model se nikla hua)
    """
    temp_reduction = 0.0

    for intervention_type, quantity in interventions.items():
        rate = cooling_rates.get(intervention_type, 0)
        temp_reduction += quantity * rate

    future_temp = round(current_temp - temp_reduction, 2)
    years_to_achieve = 3 if city_type == 'DESERT' else 5

    return {
        'current_temp':    current_temp,
        'future_temp':     future_temp,
        'temp_reduction':  round(temp_reduction, 2),
        'years':           years_to_achieve
    }


def optimize_under_budget(cooling_rates, budget_inr, relevant_interventions, ward_priority_score=1.0):
    """
    Limited budget mein sabse zyada cooling kaise milegi?
    cooling_rates ML model se aaya hai, COST_PER_UNIT market price hai
    """
    efficiency = {}
    for item in relevant_interventions:
        cost = COST_PER_UNIT[item]
        cooling = cooling_rates.get(item, 0)
        if cost > 0:
            efficiency[item] = cooling / cost

    sorted_items = sorted(efficiency.items(), key=lambda x: x[1], reverse=True)

    remaining_budget = budget_inr
    allocation = {}
    total_cooling = 0.0

    for item, eff in sorted_items:
        unit_cost = COST_PER_UNIT[item]
        units_possible = int(remaining_budget // unit_cost)

        if units_possible > 0:
            allocation[item] = units_possible
            remaining_budget -= units_possible * unit_cost
            total_cooling += units_possible * cooling_rates.get(item, 0)

    total_cooling *= ward_priority_score

    return {
        'allocation':         allocation,
        'budget_used':        budget_inr - remaining_budget,
        'budget_remaining':   remaining_budget,
        'estimated_cooling':  round(total_cooling, 2)
    }


if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.abspath('../physics_model'))
    from physics_ml import train_physics_informed_model, predict_lst

    # Sample data - REAL use mein driver_analysis.py se aayega
    sample_drivers = [
        {'vegetation_ndvi': 0.05, 'builtup_ndbi': 0.30, 'water_ndwi': -0.15, 'baresoil_bsi': 0.32},
        {'vegetation_ndvi': 0.45, 'builtup_ndbi': 0.10, 'water_ndwi': 0.20, 'baresoil_bsi': 0.05},
        {'vegetation_ndvi': 0.15, 'builtup_ndbi': 0.20, 'water_ndwi': -0.05, 'baresoil_bsi': 0.15},
        {'vegetation_ndvi': 0.30, 'builtup_ndbi': 0.15, 'water_ndwi': 0.35, 'baresoil_bsi': 0.06},
        {'vegetation_ndvi': 0.08, 'builtup_ndbi': 0.28, 'water_ndwi': -0.12, 'baresoil_bsi': 0.30},
        {'vegetation_ndvi': 0.50, 'builtup_ndbi': 0.08, 'water_ndwi': 0.25, 'baresoil_bsi': 0.04},
    ]
    sample_lst = [48.0, 30.5, 42.0, 29.0, 47.0, 28.5]

    print("Physics-informed model train kar rahe hain...")
    model = train_physics_informed_model(sample_drivers, sample_lst)

    baseline = {'ndvi': 0.20, 'ndbi': 0.18, 'ndwi': 0.0, 'bsi': 0.12}

    print("\nModel se cooling rates nikal rahe hain...")
    rates = derive_cooling_efficiency(model, predict_lst, baseline)
    print(f"  Cooling rates: {rates}")

    print("\nTest simulation:")
    result = simulate_intervention(
        city_type='SEMI_ARID',
        current_temp=42.0,
        interventions={'trees': 500, 'water_bodies': 2, 'reflective_roads_km': 10},
        cooling_rates=rates
    )
    print(f"  Current: {result['current_temp']}°C -> Future: {result['future_temp']}°C")
    print(f"  Reduction: {result['temp_reduction']}°C in {result['years']} years")

    print("\nBudget optimization (50 lakh):")
    optimal = optimize_under_budget(
        cooling_rates=rates,
        budget_inr=5000000,
        relevant_interventions=['trees', 'water_bodies', 'reflective_roads_km'],
        ward_priority_score=1.2
    )
    print(f"  Allocation: {optimal['allocation']}")
    print(f"  Budget used: ₹{optimal['budget_used']:,.0f}")
    print(f"  Estimated cooling: {optimal['estimated_cooling']}°C")