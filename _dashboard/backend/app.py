from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

sys.path.append(os.path.abspath('../../_data'))
sys.path.append(os.path.abspath('../../_ai_engine/detection'))
sys.path.append(os.path.abspath('../../_ai_engine/drivers'))
sys.path.append(os.path.abspath('../../_ai_engine/city_type'))
sys.path.append(os.path.abspath('../../_ai_engine/physics_model'))
sys.path.append(os.path.abspath('../../_ai_engine/simulation'))
sys.path.append(os.path.abspath('../../_ai_engine/heat_stress'))
sys.path.append(os.path.abspath('../../_ai_engine/scenarios'))
sys.path.append(os.path.abspath('../../_ai_engine/optimization'))
sys.path.append(os.path.abspath('../../_ai_engine/validation'))

from cities import get_city, get_all_cities
from heat_detection import get_city_heat, get_heat_trend
from driver_analysis import extract_all_drivers
from classify_city import get_city_climate_type, get_mitigation_strategy
from physics_ml import train_physics_informed_model, predict_lst
from simulate import simulate_intervention, derive_cooling_efficiency
from hotspot_map import generate_hotspot_grid, get_hottest_zones
from utci_index import get_heat_stress_index
from shap_drivers import train_explainable_model, get_driver_contribution
from cooling_scenarios import run_all_scenarios
from optimizer import optimize_intervention_plan

app = Flask(__name__)
CORS(app)

_physics_model_cache = None
_shap_model_cache = None
_shap_training_X_cache = None


def get_physics_model():
    global _physics_model_cache
    if _physics_model_cache is None:
        _physics_model_cache = train_physics_informed_model()
    return _physics_model_cache


def get_shap_model():
    global _shap_model_cache, _shap_training_X_cache
    if _shap_model_cache is None:
        _shap_model_cache, _shap_training_X_cache = train_explainable_model()
    return _shap_model_cache, _shap_training_X_cache


@app.route('/cities', methods=['GET'])
def cities():
    return jsonify({'cities': get_all_cities()})


@app.route('/heat', methods=['POST'])
def heat():
    data = request.json
    city_name = data.get('city')

    city = get_city(city_name)
    if not city:
        return jsonify({'error': 'City not found'}), 404

    result = get_city_heat(city['lon'], city['lat'])

    return jsonify({
        'city': city_name,
        'lat': city['lat'],
        'lon': city['lon'],
        'temperature': result['temperature'],
        'vegetation': result['vegetation'],
        'buildings': result['buildings'],
        'date_range': result['date_range']
    })


@app.route('/classify', methods=['POST'])
def classify():
    data = request.json
    city_name = data.get('city')

    try:
        climate = get_city_climate_type(city_name)
        strategy = get_mitigation_strategy(climate)
    except ValueError:
        return jsonify({'error': 'City not found'}), 404

    return jsonify({
        'city': city_name,
        'city_type': climate,
        'strategy': strategy['primary'],
        'reason': strategy['reason']
    })


@app.route('/drivers', methods=['POST'])
def drivers():
    data = request.json
    city_name = data.get('city')

    city = get_city(city_name)
    if not city:
        return jsonify({'error': 'City not found'}), 404

    result = extract_all_drivers(city['lon'], city['lat'])
    return jsonify(result)


@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    city_name = data.get('city')
    interventions = data.get('interventions', {})

    city = get_city(city_name)
    if not city:
        return jsonify({'error': 'City not found'}), 404

    climate = get_city_climate_type(city_name)
    heat_data = get_city_heat(city['lon'], city['lat'])

    model = get_physics_model()
    baseline = extract_all_drivers(city['lon'], city['lat'])

    cooling_rates = derive_cooling_efficiency(
        model, predict_lst,
        {
            'ndvi': baseline['vegetation_ndvi'],
            'ndbi': baseline['builtup_ndbi'],
            'ndwi': baseline['water_ndwi'],
            'bsi': baseline['baresoil_bsi']
        }
    )

    result = simulate_intervention(
        city_type=climate,
        current_temp=heat_data['temperature'],
        interventions=interventions,
        cooling_rates=cooling_rates
    )

    return jsonify({
        'city': city_name,
        'city_type': climate,
        'current_temp': result['current_temp'],
        'future_temp': result['future_temp'],
        'temp_reduction': result['temp_reduction'],
        'years': result['years']
    })


@app.route('/trend', methods=['POST'])
def trend():
    data = request.json
    city_name = data.get('city')

    city = get_city(city_name)
    if not city:
        return jsonify({'error': 'City not found'}), 404

    result = get_heat_trend(city['lon'], city['lat'], years=6)

    return jsonify({
        'city': city_name,
        'trend': result
    })


@app.route('/hotspots', methods=['POST'])
def hotspots():
    data = request.json
    city_name = data.get('city')

    city = get_city(city_name)
    if not city:
        return jsonify({'error': 'City not found'}), 404

    grid = generate_hotspot_grid(
        longitude=city['lon'],
        latitude=city['lat'],
        grid_size_km=3,
        radius_km=12
    )

    hottest = get_hottest_zones(grid, top_n=5)

    return jsonify({
        'city': city_name,
        'grid': grid,
        'hottest_zones': hottest
    })


@app.route('/heat-stress', methods=['POST'])
def heat_stress():
    """UTCI Heat Stress Index - human comfort, not just raw temperature"""
    data = request.json
    city_name = data.get('city')

    city = get_city(city_name)
    if not city:
        return jsonify({'error': 'City not found'}), 404

    heat_data = get_city_heat(city['lon'], city['lat'])
    result = get_heat_stress_index(city['lon'], city['lat'], heat_data['temperature'])

    return jsonify({
        'city': city_name,
        'lst': heat_data['temperature'],
        **result
    })


@app.route('/driver-importance', methods=['POST'])
def driver_importance():
    """SHAP-based explainable driver analysis"""
    data = request.json
    city_name = data.get('city')

    city = get_city(city_name)
    if not city:
        return jsonify({'error': 'City not found'}), 404

    drivers_data = extract_all_drivers(city['lon'], city['lat'])
    model, X = get_shap_model()

    result = get_driver_contribution(
        city_ndvi=drivers_data['vegetation_ndvi'],
        city_ndbi=drivers_data['builtup_ndbi'],
        city_ndwi=drivers_data['water_ndwi'],
        city_bsi=drivers_data['baresoil_bsi'],
        model=model,
        training_X=X
    )

    return jsonify({
        'city': city_name,
        **result
    })


@app.route('/scenarios', methods=['POST'])
def scenarios():
    """Run all 5 named cooling scenarios (A-E)"""
    data = request.json
    city_name = data.get('city')

    city = get_city(city_name)
    if not city:
        return jsonify({'error': 'City not found'}), 404

    drivers_data = extract_all_drivers(city['lon'], city['lat'])
    model = get_physics_model()

    baseline = {
        'ndvi': drivers_data['vegetation_ndvi'],
        'ndbi': drivers_data['builtup_ndbi'],
        'ndwi': drivers_data['water_ndwi'],
        'bsi': drivers_data['baresoil_bsi']
    }

    results = run_all_scenarios(baseline, model)

    return jsonify({
        'city': city_name,
        'scenarios': results
    })


@app.route('/optimize', methods=['POST'])
def optimize():
    """Genetic algorithm budget-constrained optimization"""
    data = request.json
    budget = data.get('budget_inr', 5000000)

    result = optimize_intervention_plan(budget_inr=budget, generations=80, population_size=40)

    return jsonify(result)

@app.route('/optimize-map', methods=['POST'])
def optimize_map():
    """
    Runs the GA optimizer, then distributes the recommended
    interventions across the hottest grid cells of the city -
    so the plan becomes a visible map, not just a number.

    HONEST NOTE: the GA only outputs total quantities (e.g. 3302 trees).
    It does not solve for exact GPS placement - that would require
    parcel-level land suitability data we don't have. What we do here
    is a reasonable, transparent proxy: spread the recommended
    interventions across the hottest cells first, since that is
    where cooling is most needed.
    """
    data = request.json
    city_name = data.get('city')
    budget = data.get('budget_inr', 5000000)

    city = get_city(city_name)
    if not city:
        return jsonify({'error': 'City not found'}), 404

    plan = optimize_intervention_plan(budget_inr=budget, generations=80, population_size=40)
    if not plan['feasible']:
        return jsonify({'error': plan.get('message', 'No feasible plan found')}), 400

    grid = generate_hotspot_grid(
        longitude=city['lon'],
        latitude=city['lat'],
        grid_size_km=3,
        radius_km=12
    )

    sorted_grid = sorted(grid, key=lambda x: x['temp'], reverse=True)

    n_top_cells = max(1, len(sorted_grid) // 3)
    target_cells = sorted_grid[:n_top_cells]

    allocation = plan['allocation']
    placements = []

    cell_count = len(target_cells)
    for i, cell in enumerate(target_cells):
        placement = {
            'lat': cell['lat'],
            'lon': cell['lon'],
            'temp': cell['temp'],
            'trees': allocation['trees'] // cell_count,
            'cool_roofs_sqm': allocation['cool_roofs_sqm'] // cell_count,
            'green_roofs_sqm': allocation['green_roofs_sqm'] // cell_count,
            'water_bodies': 1 if (i < allocation['water_bodies']) else 0
        }
        placements.append(placement)

    return jsonify({
        'city': city_name,
        'total_allocation': allocation,
        'expected_cooling': plan['expected_cooling'],
        'budget_used': plan['budget_used'],
        'placements': placements,
        'method_note': 'Interventions are distributed across the hottest third of grid cells, proportional to total recommended quantities. This shows WHERE cooling is most needed, not an exact land-parcel optimization.'
    })

if __name__ == '__main__':
    print("Pre-loading physics model...")
    get_physics_model()
    print("Pre-loading SHAP model...")
    get_shap_model()
    print("Server ready!")
    app.run(debug=True, port=5000)