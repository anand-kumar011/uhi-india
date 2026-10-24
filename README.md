# UHI-India — Urban Heat Intelligence Platform

A full-stack web app that measures, explains and simulates **urban heat islands** across Indian cities using real satellite data.

Pick a city on the map and the platform shows how hot it actually gets, *why* it is hot, and how much cooler it could get with trees, cool roofs, green roofs or water bodies — within a budget.

**Stack:** Python · Flask · Google Earth Engine (Landsat 8, ECOSTRESS, ERA5) · scikit-learn · SHAP · pymoo · JavaScript · Leaflet

---

## What it does

| Feature | How it works |
| --- | --- |
| **Heat detection** | Land Surface Temperature from Landsat 8 thermal band, fixed March–June window so cities are compared in the same season |
| **Heat drivers** | NDVI (vegetation), NDBI (built-up), NDWI (water) and BSI (bare soil) extracted per city |
| **Physics-informed ML** | A Random Forest that takes the raw drivers **plus** a surface-energy-balance physics estimate as a feature, trained on real data from 47 cities |
| **Explainability** | SHAP shows which driver pushes each city's temperature up or down |
| **City classification** | Groups cities by climate type and recommends the mitigation strategy that suits it |
| **Hotspot map** | 3 km grid over a 12 km radius, with the five hottest zones highlighted |
| **Heat stress (UTCI)** | Converts raw temperature into how heat *feels* to people, using ERA5 humidity and wind |
| **What-if simulator** | Projects future temperature for a chosen mix of interventions |
| **Cooling scenarios** | Compares five named intervention scenarios side by side |
| **Budget optimizer** | A genetic algorithm (pymoo) finds the intervention mix that maximizes cooling for a given budget in INR, then maps it onto the hottest grid cells |
| **Validation** | Checks predictions against ECOSTRESS, an independent NASA satellite, instead of the training data |

## Architecture

```
_dashboard/
  frontend/index.html     Leaflet map + dashboard (calls the API on localhost:5000)
  backend/app.py          Flask REST API, 11 endpoints
_ai_engine/
  detection/              LST + hotspot grid (Earth Engine)
  drivers/                NDVI / NDBI / NDWI / BSI extraction
  physics_model/          Physics-informed Random Forest
  heat_stress/            UTCI index + SHAP explanations
  city_type/              Climate-type classifier
  simulation/             What-if intervention simulator
  scenarios/              Five cooling scenarios
  optimization/           Genetic-algorithm budget optimizer
  validation/             ECOSTRESS cross-check
_data/
  cities.py               City list with coordinates
  generate_training_data.py   Pulls real satellite data for every city
  training_data.json      Generated dataset (47 cities)
```

## API

| Method | Endpoint | Returns |
| --- | --- | --- |
| GET | `/cities` | All supported cities |
| POST | `/heat` | Current LST, vegetation, built-up index |
| POST | `/trend` | Six-year temperature trend |
| POST | `/drivers` | All heat-driver indices |
| POST | `/classify` | Climate type + recommended strategy |
| POST | `/hotspots` | Hotspot grid + hottest zones |
| POST | `/heat-stress` | UTCI heat-stress index |
| POST | `/driver-importance` | SHAP contribution per driver |
| POST | `/simulate` | Temperature after chosen interventions |
| POST | `/scenarios` | Five cooling scenarios compared |
| POST | `/optimize`, `/optimize-map` | Best intervention plan for a budget, and where to place it |

POST endpoints take JSON like `{"city": "Delhi"}`.

## Run it locally

You need a Google Earth Engine account and a Google Cloud project with the Earth Engine API enabled.

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
earthengine authenticate
```

Replace the project ID in the `ee.Initialize(project=...)` lines under `_ai_engine/` with your own Cloud project, then:

```bash
cd _dashboard/backend
python app.py        # API on http://localhost:5000
```

Open `_dashboard/frontend/index.html` in a browser.

## How I built it

I built this with AI coding tools (Claude, Cursor, GitHub Copilot) and treated their output as a first draft, not a finished answer. The parts I had to steer and correct myself were mostly about scientific honesty:

- **Validation on independent data.** Testing a model on the data it was trained on always looks good. Validation uses ECOSTRESS, a different satellite, so the error numbers mean something.
- **Physics as a feature, not a replacement.** The surface-energy-balance estimate is fed into the model as an input, so the ML learns corrections to the physics rather than ignoring it.
- **Honest limits.** The optimizer outputs quantities (for example, number of trees), not exact land parcels. `/optimize-map` spreads them over the hottest third of the grid and says so in its response, rather than pretending to precision it doesn't have.

## Author

Anand Kumar — Bachelor's in Data Science & Artificial Intelligence, IIT Guwahati · [GitHub](https://github.com/anand-kumar011) · [LinkedIn](https://linkedin.com/in/anandk0040)
