# Driver Analysis Module
# Yeh batata hai ki kaunsa factor kitna zimmedar hai garmi ke liye
# Fixed summer window (March-June) + cloud filter use karta hai

import ee
import numpy as np
from datetime import datetime

ee.Initialize(project='impactful-water-467805-e3')


def extract_all_drivers(longitude, latitude, year=None):
    """
    Sabhi heat drivers ek saath nikalo - fixed summer window se
    1. Land Use/Land Cover (Sentinel-2)
    2. Vegetation density (NDVI)
    3. Built-up density (NDBI)
    4. Bare soil index (BSI)
    5. Water presence (NDWI)
    """
    if year is None:
        year = datetime.today().year

    start_date = f"{year}-03-01"
    end_date = f"{year}-06-15"

    city_point = ee.Geometry.Point([longitude, latitude])
    region = city_point.buffer(15000)

    landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
        .filterBounds(region) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUD_COVER', 20)) \
        .sort('CLOUD_COVER') \
        .first()

    lst = landsat.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15)
    ndvi = landsat.normalizedDifference(['SR_B5', 'SR_B4'])
    ndbi = landsat.normalizedDifference(['SR_B6', 'SR_B5'])
    ndwi = landsat.normalizedDifference(['SR_B3', 'SR_B5'])
    bsi = landsat.normalizedDifference(['SR_B6', 'SR_B2'])

    sentinel = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(region) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
        .sort('CLOUDY_PIXEL_PERCENTAGE') \
        .first()

    sentinel_ndvi = sentinel.normalizedDifference(['B8', 'B4'])

    combined = ee.Image.cat([lst, ndvi, ndbi, ndwi, bsi, sentinel_ndvi])

    stats = combined.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=30,
        maxPixels=1e9
    ).getInfo()

    drivers = {
        'lst':            round(stats.get('ST_B10', 0), 2),
        'vegetation_ndvi': round(stats.get('nd', 0), 3),
        'builtup_ndbi':    round(stats.get('nd_1', 0), 3),
        'water_ndwi':      round(stats.get('nd_2', 0), 3),
        'baresoil_bsi':    round(stats.get('nd_3', 0), 3),
        'sentinel_ndvi':   round(stats.get('nd_4', 0), 3),
    }

    return drivers


def calculate_driver_importance(drivers_list, lst_values):
    """Quantify karo ki kaunsa driver kitna contribute karta hai LST mein"""
    if len(drivers_list) < 2:
        raise ValueError("Importance calculate karne ke liye kam se kam 2 locations chahiye")

    factor_names = ['vegetation_ndvi', 'builtup_ndbi', 'water_ndwi', 'baresoil_bsi']
    importance = {}
    lst_array = np.array(lst_values)

    for factor in factor_names:
        factor_array = np.array([d[factor] for d in drivers_list])
        if np.std(factor_array) > 0 and np.std(lst_array) > 0:
            correlation = np.corrcoef(factor_array, lst_array)[0, 1]
        else:
            correlation = 0.0
        importance[factor] = round(abs(correlation) * 100, 1)

    total = sum(importance.values())
    if total > 0:
        importance = {k: round((v / total) * 100, 1) for k, v in importance.items()}

    return importance


if __name__ == "__main__":
    print("Jaipur ke heat drivers (summer window):")
    drivers = extract_all_drivers(longitude=75.7873, latitude=26.9124)
    for key, value in drivers.items():
        print(f"  {key}: {value}")