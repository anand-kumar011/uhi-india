# Heat Detection Module
# Landsat 8 satellite se Land Surface Temperature (LST) nikalta hai
# Fixed summer window (March-June) use karta hai - consistency ke liye

import ee
from datetime import datetime

ee.Initialize(project='impactful-water-467805-e3')


def get_city_heat(longitude, latitude, year=None):
    """
    Kisi bhi city ke coordinates do
    Fixed summer window (1 March - 15 June) se data nikalega
    Yeh consistency deta hai - sab cities same season mein compare hoti hain
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

    if landsat is None:
        raise ValueError("Is location/date ke liye clear satellite image nahi mili")

    lst = landsat.select('ST_B10') \
        .multiply(0.00341802) \
        .add(149.0) \
        .subtract(273.15)

    ndvi = landsat.normalizedDifference(['SR_B5', 'SR_B4'])
    ndbi = landsat.normalizedDifference(['SR_B6', 'SR_B5'])

    stats = ee.Image.cat([lst, ndvi, ndbi]).reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=30,
        maxPixels=1e9
    ).getInfo()

    return {
        'temperature': round(stats.get('ST_B10', 0), 2),
        'vegetation':  round(stats.get('nd', 0), 3),
        'buildings':   round(stats.get('nd_1', 0), 3),
        'date_range':  f"{start_date} to {end_date}"
    }


def get_heat_trend(longitude, latitude, years=6):
    """Pichle N saalon ka summer LST trend"""
    city_point = ee.Geometry.Point([longitude, latitude])
    region = city_point.buffer(15000)

    current_year = datetime.today().year
    trend_data = []

    for year_offset in range(years):
        year = current_year - year_offset
        start = f"{year}-03-01"
        end = f"{year}-06-15"

        try:
            landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
                .filterBounds(region) \
                .filterDate(start, end) \
                .filter(ee.Filter.lt('CLOUD_COVER', 20)) \
                .sort('CLOUD_COVER') \
                .first()

            lst = landsat.select('ST_B10') \
                .multiply(0.00341802).add(149.0).subtract(273.15)

            stats = lst.reduceRegion(
                reducer=ee.Reducer.mean(), geometry=region,
                scale=30, maxPixels=1e9
            ).getInfo()

            temp = stats.get('ST_B10')
            if temp is not None:
                trend_data.append({'year': year, 'avg_temp': round(temp, 2)})
        except Exception:
            continue

    return sorted(trend_data, key=lambda x: x['year'])


if __name__ == "__main__":
    print("Testing Jaipur ka summer heat data:")
    result = get_city_heat(longitude=75.7873, latitude=26.9124)
    print(result)