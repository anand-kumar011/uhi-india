# Hotspot Mapping Module
# City ko grid mein baant ke har grid cell ka LST nikalta hai
# Yeh visual heat map ke liye data deta hai - sirf single number nahi

import ee
from datetime import datetime

ee.Initialize(project='impactful-water-467805-e3')


def generate_hotspot_grid(longitude, latitude, grid_size_km=2, radius_km=15, year=None):
    """
    City ke around ek grid banata hai, har cell ka average LST nikalta hai
    
    grid_size_km: har grid cell ka size (2km x 2km default)
    radius_km: kitna bada area cover karna hai city ke around
    """
    if year is None:
        year = datetime.today().year

    start_date = f"{year}-03-01"
    end_date = f"{year}-06-15"

    city_point = ee.Geometry.Point([longitude, latitude])
    region = city_point.buffer(radius_km * 1000)

    landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
        .filterBounds(region) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUD_COVER', 20)) \
        .sort('CLOUD_COVER') \
        .first()

    lst = landsat.select('ST_B10') \
        .multiply(0.00341802).add(149.0).subtract(273.15)

    # Grid banane ke liye - lat/lon degrees mein convert karo
    grid_size_deg = grid_size_km / 111.0  # roughly 111km per degree
    steps = int((radius_km * 2) / grid_size_km)

    grid_data = []
    half_steps = steps // 2

    for i in range(-half_steps, half_steps + 1):
        for j in range(-half_steps, half_steps + 1):
            cell_lon = longitude + (i * grid_size_deg)
            cell_lat = latitude + (j * grid_size_deg)

            cell_point = ee.Geometry.Point([cell_lon, cell_lat])
            cell_region = cell_point.buffer(grid_size_km * 500)  # half of cell size in meters

            try:
                stats = lst.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=cell_region,
                    scale=30,
                    maxPixels=1e8
                ).getInfo()

                temp = stats.get('ST_B10')
                if temp is not None:
                    grid_data.append({
                        'lat': round(cell_lat, 4),
                        'lon': round(cell_lon, 4),
                        'temp': round(temp, 2)
                    })
            except Exception:
                continue

    return grid_data


def get_hottest_zones(grid_data, top_n=5):
    """Sabse garam N zones nikalo grid data se"""
    sorted_data = sorted(grid_data, key=lambda x: x['temp'], reverse=True)
    return sorted_data[:top_n]


if __name__ == "__main__":
    print("Jaipur ka hotspot grid generate kar rahe hain...")
    grid = generate_hotspot_grid(longitude=75.7873, latitude=26.9124, grid_size_km=3, radius_km=12)

    print(f"\nTotal grid cells: {len(grid)}")

    hottest = get_hottest_zones(grid, top_n=5)
    print("\nTop 5 hottest zones:")
    for zone in hottest:
        print(f"  Lat: {zone['lat']}, Lon: {zone['lon']}, Temp: {zone['temp']}°C")