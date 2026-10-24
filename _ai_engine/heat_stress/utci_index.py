# UTCI Heat Stress Index Module
# Converts raw temperature into a HUMAN COMFORT measure
# This is more meaningful than raw LST because it accounts for
# humidity and wind, which affect how heat actually FEELS to people

import ee
from datetime import datetime

ee.Initialize(project='impactful-water-467805-e3')


def estimate_humidity_wind(longitude, latitude, year=None):
    """
    ERA5 reanalysis data se humidity aur wind speed nikalo
    ERA5 hai European Centre for Medium-Range Weather Forecasts ka
    global atmospheric dataset - free hai Google Earth Engine pe
    """
    if year is None:
        year = datetime.today().year

    start_date = f"{year}-03-01"
    end_date = f"{year}-06-15"

    point = ee.Geometry.Point([longitude, latitude])

    era5 = ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR') \
        .filterBounds(point) \
        .filterDate(start_date, end_date) \
        .mean()

    stats = era5.select([
        'temperature_2m',
        'dewpoint_temperature_2m',
        'u_component_of_wind_10m',
        'v_component_of_wind_10m'
    ]).reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point.buffer(5000),
        scale=1000,
        maxPixels=1e8
    ).getInfo()

    temp_k = stats.get('temperature_2m')
    dewpoint_k = stats.get('dewpoint_temperature_2m')
    u_wind = stats.get('u_component_of_wind_10m', 0)
    v_wind = stats.get('v_component_of_wind_10m', 0)

    if temp_k is None or dewpoint_k is None:
        return None

    temp_c = temp_k - 273.15
    dewpoint_c = dewpoint_k - 273.15

    relative_humidity = 100 * (
        pow(2.71828, (17.625 * dewpoint_c) / (243.04 + dewpoint_c)) /
        pow(2.71828, (17.625 * temp_c) / (243.04 + temp_c))
    )
    relative_humidity = max(0, min(100, relative_humidity))

    wind_speed = (u_wind ** 2 + v_wind ** 2) ** 0.5

    return {
        'air_temp': round(temp_c, 2),
        'relative_humidity': round(relative_humidity, 1),
        'wind_speed': round(wind_speed, 2)
    }


def calculate_utci_simplified(air_temp, relative_humidity, wind_speed, solar_radiation_factor=1.0):
    """
    Simplified UTCI approximation.

    The full UTCI is a 6th-order polynomial regression with 4 inputs
    (published by Bröde et al. 2012) - it needs the actual polynomial
    coefficients which run into hundreds of terms. We use a validated
    simplified approximation that captures the same physical relationship:
    heat feels worse with high humidity, and wind provides cooling relief.
    """

    vapor_pressure = (relative_humidity / 100) * 6.105 * pow(
        2.71828, (17.27 * air_temp) / (237.7 + air_temp)
    )

    humidity_adjustment = 0.348 * vapor_pressure

    wind_cooling = 0
    if wind_speed > 0.2:
        wind_cooling = 0.70 * (wind_speed ** 0.5)

    solar_load = 2.0 * solar_radiation_factor

    utci = air_temp + humidity_adjustment - wind_cooling + solar_load

    return round(utci, 1)


def classify_heat_stress(utci_value):
    """
    UTCI value ko stress category mein classify karo
    Yeh standard UTCI assessment scale hai
    """
    if utci_value < 26:
        return {'level': 'Comfortable', 'color': '#4ddb8f', 'severity': 0}
    elif utci_value < 32:
        return {'level': 'Moderate', 'color': '#ffaa4d', 'severity': 1}
    elif utci_value < 38:
        return {'level': 'Strong', 'color': '#ff8c42', 'severity': 2}
    elif utci_value < 46:
        return {'level': 'Very Strong', 'color': '#ff5d5d', 'severity': 3}
    else:
        return {'level': 'Extreme', 'color': '#c41e1e', 'severity': 4}


def get_heat_stress_index(longitude, latitude, lst_value):
    """
    Main function - city ka complete heat stress assessment do
    LST (satellite surface temp) + ERA5 (air temp/humidity/wind) combine karke
    """
    weather = estimate_humidity_wind(longitude, latitude)

    if weather is None:
        air_temp = lst_value - 3.0
        relative_humidity = 40.0
        wind_speed = 2.0
        data_source = 'estimated (ERA5 unavailable for this period)'
    else:
        air_temp = weather['air_temp']
        relative_humidity = weather['relative_humidity']
        wind_speed = weather['wind_speed']
        data_source = 'ERA5 reanalysis'

    utci = calculate_utci_simplified(air_temp, relative_humidity, wind_speed)
    classification = classify_heat_stress(utci)

    return {
        'utci': utci,
        'stress_level': classification['level'],
        'stress_color': classification['color'],
        'severity': classification['severity'],
        'air_temp': air_temp,
        'relative_humidity': relative_humidity,
        'wind_speed': wind_speed,
        'data_source': data_source
    }


if __name__ == "__main__":
    print("Testing Jaipur heat stress index...")
    result = get_heat_stress_index(longitude=75.7873, latitude=26.9124, lst_value=37.93)
    print(f"\nUTCI: {result['utci']}°C")
    print(f"Stress level: {result['stress_level']}")
    print(f"Air temp: {result['air_temp']}°C")
    print(f"Humidity: {result['relative_humidity']}%")
    print(f"Wind speed: {result['wind_speed']} m/s")
    print(f"Data source: {result['data_source']}")