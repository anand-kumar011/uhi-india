# India ki cities ka database - 50 cities, sab climate types cover
INDIAN_CITIES = {

    # ── DESERT (10 cities) ──
    "Jaisalmer": {"lat": 26.9157, "lon": 70.9083, "state": "Rajasthan", "climate": "DESERT"},
    "Barmer":    {"lat": 25.7521, "lon": 71.3967, "state": "Rajasthan", "climate": "DESERT"},
    "Bikaner":   {"lat": 28.0229, "lon": 73.3119, "state": "Rajasthan", "climate": "DESERT"},
    "Phalodi":   {"lat": 27.1314, "lon": 72.3672, "state": "Rajasthan", "climate": "DESERT"},
    "Churu":     {"lat": 28.2900, "lon": 74.9650, "state": "Rajasthan", "climate": "DESERT"},
    "Nagaur":    {"lat": 27.2020, "lon": 73.7339, "state": "Rajasthan", "climate": "DESERT"},
    "Pali":      {"lat": 25.7711, "lon": 73.3234, "state": "Rajasthan", "climate": "DESERT"},
    "Sirsa":     {"lat": 29.5321, "lon": 75.0280, "state": "Haryana",   "climate": "DESERT"},
    "Hanumangarh":{"lat": 29.5817, "lon": 74.3294, "state": "Rajasthan","climate": "DESERT"},
    "Kutch":     {"lat": 23.7337, "lon": 69.8597, "state": "Gujarat",   "climate": "DESERT"},

    # ── SEMI-ARID (15 cities) ──
    "Jaipur":    {"lat": 26.9124, "lon": 75.7873, "state": "Rajasthan",       "climate": "SEMI_ARID"},
    "Jodhpur":   {"lat": 26.2389, "lon": 73.0243, "state": "Rajasthan",       "climate": "SEMI_ARID"},
    "Delhi":     {"lat": 28.6139, "lon": 77.2090, "state": "Delhi",           "climate": "SEMI_ARID"},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714, "state": "Gujarat",         "climate": "SEMI_ARID"},
    "Nagpur":    {"lat": 21.1458, "lon": 79.0882, "state": "Maharashtra",     "climate": "SEMI_ARID"},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "state": "Telangana",       "climate": "SEMI_ARID"},
    "Lucknow":   {"lat": 26.8467, "lon": 80.9462, "state": "Uttar Pradesh",   "climate": "SEMI_ARID"},
    "Bhopal":    {"lat": 23.2599, "lon": 77.4126, "state": "Madhya Pradesh",  "climate": "SEMI_ARID"},
    "Indore":    {"lat": 22.7196, "lon": 75.8577, "state": "Madhya Pradesh",  "climate": "SEMI_ARID"},
    "Kanpur":    {"lat": 26.4499, "lon": 80.3319, "state": "Uttar Pradesh",   "climate": "SEMI_ARID"},
    "Pune":      {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra",     "climate": "SEMI_ARID"},
    "Vadodara":  {"lat": 22.3072, "lon": 73.1812, "state": "Gujarat",         "climate": "SEMI_ARID"},
    "Surat":     {"lat": 21.1702, "lon": 72.8311, "state": "Gujarat",         "climate": "SEMI_ARID"},
    "Amritsar":  {"lat": 31.6340, "lon": 74.8723, "state": "Punjab",          "climate": "SEMI_ARID"},
    "Chandigarh":{"lat": 30.7333, "lon": 76.7794, "state": "Chandigarh",      "climate": "SEMI_ARID"},

    # ── HUMID (15 cities) ──
    "Guwahati":    {"lat": 26.1445, "lon": 91.7362, "state": "Assam",       "climate": "HUMID"},
    "Shillong":    {"lat": 25.5788, "lon": 91.8933, "state": "Meghalaya",   "climate": "HUMID"},
    "Kolkata":     {"lat": 22.5726, "lon": 88.3639, "state": "West Bengal", "climate": "HUMID"},
    "Patna":       {"lat": 25.5941, "lon": 85.1376, "state": "Bihar",       "climate": "HUMID"},
    "Bhubaneswar": {"lat": 20.2961, "lon": 85.8245, "state": "Odisha",      "climate": "HUMID"},
    "Imphal":      {"lat": 24.8170, "lon": 93.9368, "state": "Manipur",     "climate": "HUMID"},
    "Agartala":    {"lat": 23.8315, "lon": 91.2868, "state": "Tripura",     "climate": "HUMID"},
    "Siliguri":    {"lat": 26.7271, "lon": 88.3953, "state": "West Bengal", "climate": "HUMID"},
    "Dibrugarh":   {"lat": 27.4728, "lon": 94.9120, "state": "Assam",       "climate": "HUMID"},
    "Cuttack":     {"lat": 20.4625, "lon": 85.8830, "state": "Odisha",      "climate": "HUMID"},
    "Ranchi":      {"lat": 23.3441, "lon": 85.3096, "state": "Jharkhand",   "climate": "HUMID"},
    "Gaya":        {"lat": 24.7955, "lon": 84.9994, "state": "Bihar",       "climate": "HUMID"},
    "Jorhat":      {"lat": 26.7509, "lon": 94.2037, "state": "Assam",       "climate": "HUMID"},
    "Itanagar":    {"lat": 27.0844, "lon": 93.6053, "state": "Arunachal Pradesh", "climate": "HUMID"},
    "Aizawl":      {"lat": 23.7271, "lon": 92.7176, "state": "Mizoram",     "climate": "HUMID"},

    # ── COASTAL (10 cities) ──
    "Mumbai":        {"lat": 19.0760, "lon": 72.8777, "state": "Maharashtra",    "climate": "COASTAL"},
    "Chennai":       {"lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu",     "climate": "COASTAL"},
    "Kochi":         {"lat": 9.9312,  "lon": 76.2673, "state": "Kerala",         "climate": "COASTAL"},
    "Visakhapatnam": {"lat": 17.6868, "lon": 83.2185, "state": "Andhra Pradesh", "climate": "COASTAL"},
    "Mangalore":     {"lat": 12.9141, "lon": 74.8560, "state": "Karnataka",      "climate": "COASTAL"},
    "Goa":           {"lat": 15.2993, "lon": 74.1240, "state": "Goa",            "climate": "COASTAL"},
    "Puducherry":    {"lat": 11.9416, "lon": 79.8083, "state": "Puducherry",     "climate": "COASTAL"},
    "Thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366, "state": "Kerala",     "climate": "COASTAL"},
    "Surat_Coast":   {"lat": 21.0250, "lon": 72.5714, "state": "Gujarat",        "climate": "COASTAL"},
    "Bhavnagar":     {"lat": 21.7645, "lon": 72.1519, "state": "Gujarat",        "climate": "COASTAL"},
}


def get_city(city_name):
    city = INDIAN_CITIES.get(city_name)
    if city is None:
        raise ValueError(f"'{city_name}' database mein nahi hai. Available cities: {list(INDIAN_CITIES.keys())}")
    return city


def get_all_cities():
    return list(INDIAN_CITIES.keys())


def get_cities_by_climate(climate_type):
    return [name for name, data in INDIAN_CITIES.items() if data["climate"] == climate_type]


if __name__ == "__main__":
    print(f"Total cities: {len(INDIAN_CITIES)}\n")
    for climate in ["DESERT", "SEMI_ARID", "HUMID", "COASTAL"]:
        cities = get_cities_by_climate(climate)
        print(f"{climate} ({len(cities)}): {cities}")