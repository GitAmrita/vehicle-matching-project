import requests

BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"

def fetch_all_makes():
    """Fetch all vehicle makes"""
    url = f"{BASE_URL}/GetAllMakes?format=json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json().get("Results", [])

def fetch_models_for_make_year(make_id, year):
    """Fetch all models for a given make_id and year"""
    url = f"{BASE_URL}/GetModelsForMakeIdYear/makeId/{make_id}/modelyear/{year}?format=json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json().get("Results", [])
