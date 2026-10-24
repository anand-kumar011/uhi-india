# City Climate Lookup
# Cities.py mein already known data hai - ML predict karne ki zaroorat nahi
# Yeh sirf reliable lookup karta hai

import sys
import os
sys.path.append(os.path.abspath('../../_data'))
from cities import get_city, get_all_cities


def get_city_climate_type(city_name):
    """
    Known city database se climate type lookup karo
    Reliable hai kyunki yeh actual ground-truth data hai
    """
    city_data = get_city(city_name)
    return city_data['climate']


def get_mitigation_strategy(climate_type):
    """
    Climate type ke hisaab se best mitigation strategy
    """
    strategies = {
        'DESERT': {
            'primary': 'Shade structures, reflective surfaces',
            'reason': 'Paani kam hai, trees lagana mushkil. Cool pavements aur shade zyada effective.'
        },
        'SEMI_ARID': {
            'primary': 'Tree plantation, reflective roads, water body restoration',
            'reason': 'Moderate water available. Combination approach best results deta hai.'
        },
        'HUMID': {
            'primary': 'Wind corridors, water body restoration, urban ventilation',
            'reason': 'Vegetation already dense hai. Asli problem humidity + heat trap hai, isliye air circulation chahiye.'
        },
        'COASTAL': {
            'primary': 'Sea breeze corridors, building orientation optimization',
            'reason': 'Natural cooling source (sea) available hai - usse city mein channel karna sabse efficient hai.'
        }
    }
    return strategies.get(climate_type, {'primary': 'General greening', 'reason': 'Unknown climate type'})


if __name__ == "__main__":
    test_city = "Jaipur"
    climate = get_city_climate_type(test_city)
    strategy = get_mitigation_strategy(climate)

    print(f"{test_city} ka climate type: {climate}")
    print(f"Suggested strategy: {strategy['primary']}")
    print(f"Reason: {strategy['reason']}")