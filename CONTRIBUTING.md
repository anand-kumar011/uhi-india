# Contributing to UHI-India

Thanks for taking an interest. This project measures urban heat islands in Indian
cities from satellite data, and there is plenty of room for help — whether you know
remote sensing, Python, or just front-end work.

## Ways to help

You do not need a background in climate science. Useful contributions include:

- **Add a city.** `_data/cities.py` holds the city list with coordinates. Adding a
  city is a single entry plus a regenerated training row.
- **Front-end.** The dashboard in `_dashboard/frontend/` is plain HTML, CSS and
  Leaflet. Mobile layout, loading states and chart readability all need work.
- **Validation.** `_ai_engine/validation/validate_model.py` cross-checks predictions
  against ECOSTRESS. More independent checks, or error reporting per city, would
  strengthen it.
- **Documentation.** If a step in the setup did not work for you, that is a bug in
  the docs. Please report it.
- **Tests.** There are none yet. Even a few tests around
  `_data/cities.py` and the simulation maths would help.

## Getting set up

```bash
git clone https://github.com/anand-kumar011/uhi-india.git
cd uhi-india
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
earthengine authenticate
cp .env.example .env     # then put your own Google Cloud project id in it
export EE_PROJECT=your-gcp-project-id
cd _dashboard/backend && python app.py
```

Earth Engine access is free but needs its own registration, and the satellite
queries are the slow part of the project. Front-end and documentation changes can
usually be made without it.

## Submitting a change

1. Fork the repo and create a branch: `git checkout -b add-pune-city`.
2. Keep each pull request to one change. A small PR gets reviewed; a large one stalls.
3. Say in the description what you changed and how you checked it.
4. If your change touches the model or the physics, please say what the numbers
   looked like before and after. Accuracy claims in this project are meant to be
   checkable.

## Reporting a bug

Open an issue with: what you ran, what you expected, what happened, and your Python
version. If it is an Earth Engine error, please paste the full message — those errors
are usually about project registration rather than this code.

## A note on scope

This project aims to be scientifically honest over impressive. The optimizer reports
quantities, not exact land parcels, and the README says so. Pull requests that
increase apparent precision without the data to support it will not be merged.
